"""Create competition files for the three phases from data/v0.1 and zip the Codabench bundle.

Usage (repo root): python3 -I data/scripts/make_bundle.py   (after build_dataset.py)
"""
import csv
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMP = ROOT / "competition"   # Codabench bundle root (competition.yaml lives here)
SRC = ROOT / "data/v0.1"
ann = list(csv.DictReader(open(SRC / "annotations_v0.1.csv", encoding="utf-8")))
act = list(csv.DictReader(open(SRC / "actors_v0.1.csv", encoding="utf-8")))
SPLITS = ("train", "dev", "test")


def write(path, cols, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def classification(task_dir, pub, label_src, label_col, keep, in_cols, sample_label):
    rows = [dict(r, **{label_col: r[label_src]}) for r in ann if keep(r)]
    for sp in SPLITS:
        part = [r for r in rows if r["split"] == sp]
        if sp == "test":
            write(pub / "test_inputs.csv", in_cols, part)
            write(COMP / "tasks" / task_dir / "input_data/test_inputs.csv", in_cols, part)
            write(COMP / "tasks" / task_dir / "reference_data/test_labels.csv", ["row_id", label_col], part)
            write(COMP / "starting_kit" / f"sample_submission_{task_dir}.csv", ["row_id", label_col],
                  [dict(r, **{label_col: sample_label}) for r in part])
        else:
            write(pub / f"{sp}.csv", in_cols + [label_col], part)
        print(task_dir, sp, len(part))


base = ["row_id", "domain", "pre_context", "span_text", "post_context"]
classification("task1_direction", COMP / "public_data/phase1_direction", "rel_type_v2", "rel_type",
               lambda r: r["rel_type_v2"], base + ["e1_event", "e2_event"], "CAUSES")
classification("task2_stance", COMP / "public_data/phase2_stance", "stance_v2", "stance",
               lambda r: r["in_stance_task"] == "True", base, "NA")

# Phase 3: texts and span offsets (offsets index into `text`, end exclusive).
pub3 = COMP / "public_data/phase3_actors"
texts = {}
for r in ann:
    if r["in_actor_task"] == "True":
        texts[r["row_id"]] = r
text_of = {a["row_id"]: a["text"] for a in act}
for sp in SPLITS:
    ids = [i for i, r in texts.items() if r["split"] == sp]
    trows = [{"row_id": i, "domain": texts[i]["domain"], "text": text_of[i]} for i in ids]
    srows = [a for a in act if a["split"] == sp]
    if sp == "test":
        write(pub3 / "test_texts.csv", ["row_id", "domain", "text"], trows)
        write(COMP / "tasks/task3_actors/input_data/test_texts.csv", ["row_id", "domain", "text"], trows)
        write(COMP / "tasks/task3_actors/reference_data/test_labels.csv", ["row_id", "start", "end"], srows)
        write(COMP / "tasks/task3_actors/reference_data/test_rows.csv", ["row_id"], trows)
        write(COMP / "starting_kit/sample_submission_task3_actors.csv", ["row_id", "start", "end"], [])
    else:
        write(pub3 / f"{sp}_texts.csv", ["row_id", "domain", "text"], trows)
        write(pub3 / f"{sp}_spans.csv", ["row_id", "start", "end", "span"], srows)
    print("task3_actors", sp, len(trows), "rows", len(srows), "spans")

dist = ROOT / "dist"
dist.mkdir(exist_ok=True)
include = ["competition.yaml", "logo.png", "pages", "tasks", "starting_kit", "public_data"]
with zipfile.ZipFile(dist / "bundle.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for item in include:
        p = COMP / item
        for f in ([p] if p.is_file() else sorted(p.rglob("*"))):
            if f.is_file() and f.name != ".DS_Store":
                z.write(f, f.relative_to(COMP))
print("wrote", dist / "bundle.zip")
