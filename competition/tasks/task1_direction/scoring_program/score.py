"""Scoring program (results submission, classification). Standard library only.

Codabench mounts <input>/res (submission) and <input>/ref (reference_data).
Writes scores.json with rel_macro_f1 (main) and rel_accuracy.
"""
import csv
import json
import sys
from pathlib import Path

LABELS = set("CAUSES,IS_CAUSED_BY".split(","))
COL = "rel_type"
PFX = "rel"
pred_dir, ref_dir, out_dir = map(Path, sys.argv[1:4])


def read(path, what):
    if not path.exists():
        sys.exit(f"{what} manquant : {path.name} attendu")
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


truth = {r["row_id"]: r[COL] for r in read(ref_dir / "test_labels.csv", "reference")}
pred = {}
for r in read(pred_dir / "predictions.csv", "predictions"):
    if r.get("row_id") in pred:
        sys.exit(f"row_id en double : {r['row_id']}")
    if r.get(COL) not in LABELS:
        sys.exit(f"Valeur invalide pour {COL} : {r.get(COL)!r} (row_id {r.get('row_id')}) ; valeurs permises : {sorted(LABELS)}")
    pred[r["row_id"]] = r[COL]
if set(pred) != set(truth):
    sys.exit(f"row_id incohérents : {len(set(truth) - set(pred))} manquants, {len(set(pred) - set(truth))} inconnus")

f1s = []
for lab in sorted(set(truth.values())):          # classes present in the reference
    tp = sum(1 for k, v in truth.items() if v == lab and pred[k] == lab)
    fp = sum(1 for k, v in truth.items() if v != lab and pred[k] == lab)
    fn = sum(1 for k, v in truth.items() if v == lab and pred[k] != lab)
    f1s.append(2 * tp / (2 * tp + fp + fn) if tp else 0.0)
scores = {f"{PFX}_macro_f1": sum(f1s) / len(f1s),
          f"{PFX}_accuracy": sum(pred[k] == v for k, v in truth.items()) / len(truth)}
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / "scores.json").write_text(json.dumps(scores))
print(scores)
