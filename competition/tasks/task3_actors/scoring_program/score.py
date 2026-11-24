"""Scoring program (results submission, span extraction). Standard library only.

predictions.csv: row_id,start,end   (character offsets into `text`, end exclusive; a row with
no spans is simply absent). Reference rows are the annotated actor-evidence spans.
A predicted span matches a reference span in the same row if IoU >= 0.5; each span is used once.
Writes span_f1 (main), span_precision, span_recall, span_exact_f1.
"""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

pred_dir, ref_dir, out_dir = map(Path, sys.argv[1:4])


def read(path, what):
    if not path.exists():
        sys.exit(f"{what} manquant : {path.name} attendu")
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def spans(rows, what):
    out = defaultdict(set)
    for r in rows:
        try:
            a, b = int(r["start"]), int(r["end"])
        except (KeyError, TypeError, ValueError):
            sys.exit(f"{what} : start et end doivent être des entiers (row_id={r.get('row_id')})")
        if not 0 <= a < b:
            sys.exit(f"{what} : span invalide {a}-{b} pour {r.get('row_id')}")
        out[r["row_id"]].add((a, b))
    return out


ref = spans(read(ref_dir / "test_labels.csv", "reference"), "reference")
valid_ids = {r["row_id"] for r in read(ref_dir / "test_rows.csv", "reference rows")}
pred = spans(read(pred_dir / "predictions.csv", "predictions"), "predictions")
unknown = set(pred) - valid_ids
if unknown:
    sys.exit(f"row_id inconnu(s) : {sorted(unknown)[:5]}")


def iou(x, y):
    inter = max(0, min(x[1], y[1]) - max(x[0], y[0]))
    return inter / ((x[1] - x[0]) + (y[1] - y[0]) - inter)


def f1(tp, n_pred, n_ref):
    p = tp / n_pred if n_pred else 0.0
    r = tp / n_ref if n_ref else 0.0
    return p, r, (2 * p * r / (p + r) if p + r else 0.0)


n_pred = sum(len(v) for v in pred.values())
n_ref = sum(len(v) for v in ref.values())
tp_soft = tp_exact = 0
for rid in valid_ids:
    cand = sorted(((iou(p, g), p, g) for p in pred.get(rid, ()) for g in ref.get(rid, ())), reverse=True)
    used_p, used_g = set(), set()
    for score, p, g in cand:
        if score >= 0.5 and p not in used_p and g not in used_g:
            used_p.add(p); used_g.add(g); tp_soft += 1
    tp_exact += len(pred.get(rid, set()) & ref.get(rid, set()))
p, r, f = f1(tp_soft, n_pred, n_ref)
scores = {"span_f1": f, "span_precision": p, "span_recall": r, "span_exact_f1": f1(tp_exact, n_pred, n_ref)[2]}
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / "scores.json").write_text(json.dumps(scores))
print(scores)
