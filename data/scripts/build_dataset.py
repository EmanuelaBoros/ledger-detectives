"""Build the normalised pilot dataset (v0.1) from the raw ANR.xlsx workbook.

Usage: python3 -I data/scripts/build_dataset.py data/v0.1

Reads  <out>/raw/ANR.xlsx   (never modified)
Writes <out>/annotations_v0.1.csv   every row: text, raw + normalised labels, flags, split
       <out>/actors_v0.1.csv        one row per aligned actor-evidence span (phase 3)

One split is shared by all phases. Rows with the same document and span text are kept
together so identical passages never straddle train and test.
"""
import csv
import random
import re
import sys
from collections import Counter
from pathlib import Path

from openpyxl import load_workbook

SKIP_SHEETS = {"annotation guideline"}
MISSING = {"", "na", "n/a", "none", "nan", "implicite", "implicit"}
STANCE_MAP = {"LEGITIME": "LEGITIMATE", "ILLEGITIME": "ILLEGITIMATE", "NA": "NA"}
REL_MAP = {"CAUSES": "CAUSES", "CAUSE": "CAUSES",
           "IS_CAUSED_BY": "IS_CAUSED_BY", "CAUSED BY": "IS_CAUSED_BY"}
DOC_FIX_BY_DATE = {"1936-11-21": "JE SUIS PARTOUT_19361121"}
FRACTIONS = (0.6, 0.2, 0.2)   # train / dev / test, by rows


def s(x):
    return "" if x is None else str(x).strip()


def present(x):
    return s(x).casefold() not in MISSING


def read_rows(path):
    book = load_workbook(path, read_only=True, data_only=True)
    for sheet in book:
        if sheet.title.casefold() in SKIP_SHEETS:
            continue
        rows = sheet.iter_rows(values_only=True)
        headers = [s(h) for h in next(rows)]
        for n, row in enumerate(rows, 2):
            d = {h: s(v) for h, v in zip(headers, row) if h}
            span = d.get("SPAN_TEXT") or d.get("TEXT_SPAN", "")
            if span:
                yield sheet.title, n, d, span


def norm(text):
    """Casefold and normalise quotes/whitespace, keeping a map back to original offsets."""
    chars, offs = [], []
    for i, ch in enumerate(text):
        ch = ch.translate(str.maketrans({"’": "'", "‘": "'", " ": " "})).casefold()
        for c in ch:
            if c.isspace():
                if chars and chars[-1] == " ":
                    continue
                c = " "
            chars.append(c)
            offs.append(i)
    return "".join(chars), offs


def evidence_excerpts(evidence):
    """Quoted excerpts (« », " ", “ ”), else the whole cell. Elided excerpts are dropped."""
    found = re.findall(r'"([^"\n]+)"|«([^»]+)»|“([^”]+)”', evidence)
    out = [next(x for x in m if x).strip() for m in found] or [evidence.strip()]
    return [e for e in out if present(e) and "..." not in e and "…" not in e]


def actor_spans(text, evidence):
    hay, offs = norm(text)
    spans = []
    for ex in evidence_excerpts(evidence):
        needle = norm(ex)[0].strip()
        i = hay.find(needle) if needle else -1
        if i >= 0:
            spans.append((offs[i], offs[i + len(needle) - 1] + 1))
    return spans


def assign_splits(records, key_fn, ok_fn):
    """Seeded group split; first seed where dev and test hold both classes of phases 1 and 2."""
    groups = {}
    for r in records:
        groups.setdefault(key_fn(r), []).append(r)
    keys = sorted(groups)
    total = len(records)
    for seed in range(500):
        rng = random.Random(seed)
        order = keys[:]
        rng.shuffle(order)
        split, counts = {}, [0, 0, 0]
        for k in order:
            tgt = 2 if counts[2] < FRACTIONS[2] * total else 1 if counts[1] < FRACTIONS[1] * total else 0
            counts[tgt] += len(groups[k])
            split[k] = ("train", "dev", "test")[tgt]
        for r in records:
            r["split"] = split[key_fn(r)]
        if ok_fn(records):
            return seed
    raise SystemExit("no acceptable split found")


def split_ok(records):
    for name in ("dev", "test"):
        part = [r for r in records if r["split"] == name]
        if {r["rel_type_v2"] for r in part if r["rel_type_v2"]} != {"CAUSES", "IS_CAUSED_BY"}:
            return False
        if {r["stance_v2"] for r in part if r["in_stance_task"]} != {"LEGITIMATE", "NA"}:
            return False
        if sum(r["n_actor_spans"] for r in part) < 15:
            return False
    return True


def main(out):
    out = Path(out)
    records = []
    for sheet, n, d, span in read_rows(out / "raw" / "ANR.xlsx"):
        date = d.get("DOC_DATE", "")[:10]
        doc = DOC_FIX_BY_DATE.get(date, d.get("DOC_ID", ""))
        stance_raw, rel_raw, seg = d.get("STANCE_PROFIT", ""), d.get("REL_TYPE", ""), d.get("SEG_TYPE", "")
        stance = STANCE_MAP.get(stance_raw.upper()) if stance_raw else "NA"
        flags = []
        if stance is None:
            flags.append("stance_unmappable")
        if rel_raw and rel_raw.upper() != "NA" and rel_raw.upper() not in REL_MAP:
            flags.append("rel_type_not_v2")
        if len(span) > 2000:
            flags.append("window_not_span")
        causal = seg.upper() == "NARR" or (not seg and rel_raw.upper() in REL_MAP)

        # Joined text for phase 3; offsets refer to this exact string.
        text = ""
        for part in (d.get("PRE_CONTEXT", ""), span, d.get("POST_CONTEXT", "")):
            if present(part):
                text += ("\n\n" if text else "") + part
        spans = []
        for ev in ("E1", "E2"):
            if present(d.get(f"ACTORS_{ev}")):
                spans += [(a, b, ev) for a, b in actor_spans(text, d.get(f"EVIDENCE_ACTORS_{ev}", ""))]
        spans = sorted({(a, b) for a, b, _ in spans})

        records.append({
            "source_sheet": sheet, "source_row": n, "doc_id": doc, "doc_date": date,
            "domain": "GA" if "_AG_" in doc else "PRESSE", "annotator": d.get("AUTHOR", ""),
            "pre_context": d.get("PRE_CONTEXT", "") if present(d.get("PRE_CONTEXT")) else "",
            "span_text": span,
            "post_context": d.get("POST_CONTEXT", "") if present(d.get("POST_CONTEXT")) else "",
            "e1_event": d.get("E1_EVENT", ""), "e2_event": d.get("E2_EVENT", ""),
            "rel_type_raw": rel_raw, "rel_type_v2": REL_MAP.get(rel_raw.upper(), "") if causal else "",
            "seg_type_raw": seg, "is_causal": causal,
            "stance_raw": stance_raw, "stance_v2": stance or "", "flags": ";".join(flags),
            "text": text, "actor_spans": spans, "n_actor_spans": len(spans),
            # Stance phase: causal, mappable, a real span. ILLEGITIMATE is held back (1 example).
            "in_stance_task": causal and stance in ("LEGITIMATE", "NA") and "window_not_span" not in flags,
            "held_illegitimate": stance == "ILLEGITIMATE",
        })
    for i, r in enumerate(records):
        r["row_id"] = f"R{i + 1:04d}"
    for r in records:
        r["in_actor_task"] = r["n_actor_spans"] > 0 and "window_not_span" not in r["flags"]
        if not r["in_actor_task"]:
            r["actor_spans"], r["n_actor_spans"] = [], 0
    seed = assign_splits(records, lambda r: (r["doc_id"], r["span_text"][:200].casefold()), split_ok)

    cols = ["row_id", "source_sheet", "source_row", "doc_id", "doc_date", "domain", "annotator",
            "pre_context", "span_text", "post_context", "e1_event", "e2_event",
            "rel_type_raw", "rel_type_v2", "seg_type_raw", "is_causal", "stance_raw", "stance_v2",
            "flags", "in_stance_task", "held_illegitimate", "in_actor_task", "n_actor_spans", "split"]
    with open(out / "annotations_v0.1.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(records)
    with open(out / "actors_v0.1.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["row_id", "split", "text", "start", "end", "span"])
        for r in records:
            for a, b in r["actor_spans"]:
                w.writerow([r["row_id"], r["split"], r["text"], a, b, r["text"][a:b]])

    print("split seed:", seed, "| rows:", len(records))
    for name in ("train", "dev", "test"):
        p = [r for r in records if r["split"] == name]
        print(f"{name:5} rows={len(p)} rel={dict(Counter(r['rel_type_v2'] for r in p if r['rel_type_v2']))} "
              f"stance={dict(Counter(r['stance_v2'] for r in p if r['in_stance_task']))} "
              f"actor_rows={sum(r['in_actor_task'] for r in p)} actor_spans={sum(r['n_actor_spans'] for r in p)}")


if __name__ == "__main__":
    main(sys.argv[1])
