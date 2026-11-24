# Ledger Detectives

A three-phase student competition on French business texts (shareholder meetings and press, 1907-1950), hosted on [Codabench](https://www.codabench.org). The passages come from a research annotation project.

| Phase | Task | Metric |
|---|---|---|
| 1 | Cause or caused-by (`CAUSES` / `IS_CAUSED_BY`) | macro-F1 |
| 2 | Profit stance (`LEGITIMATE` / `NA`) | macro-F1 |
| 3 | Actor evidence spans (character offsets) | span F1 (IoU >= 0.5) |

The competition itself is in French.

## Repository layout

```
competition/   Codabench bundle (competition.yaml, pages, scoring programs, starting kit)
data/          data processing: scripts that build the dataset and the bundle
viewer/        generator for a local HTML browser of the data and annotations
docs/          student guide (LaTeX / Overleaf)
```

## What is not in this repository

The corpus data, the derived tables and the hidden test labels are **not** committed (see `.gitignore`):
`data/v0.1/`, `competition/public_data/`, `competition/tasks/*/input_data/`, `competition/tasks/*/reference_data/`,
and the generated `viewer/index.html`. Keeping them out stops participants from reading the test answers here.
The code is complete: with the source workbook you can rebuild everything.

## Rebuilding

Needs Python 3.10+ with `openpyxl` and `Pillow` (logo only); the baselines also need `pandas` and `scikit-learn`.

```sh
# 1. place the source workbook at data/v0.1/raw/ANR.xlsx
python3 -I data/scripts/build_dataset.py data/v0.1   # normalised tables + split
python3 -I data/scripts/make_bundle.py               # competition files + dist/bundle.zip
python3 -I viewer/make_viewer.py                     # optional: viewer/index.html
python3 -I data/scripts/make_logo.py                 # optional: competition/logo.png
```

Then upload `dist/bundle.zip` in Codabench (Benchmarks > Management > Upload).

## Scoring and baselines

Each phase has a standard-library scorer in `competition/tasks/*/scoring_program/score.py`.
`competition/starting_kit/baselines.py` has one baseline per phase.

## Licence

MIT, see `LICENSE`. The licence covers the code only; the corpus and its annotations are not included and are not covered by it.
