"""Systèmes de référence pour les trois phases. Nécessite pandas et scikit-learn (phases 1-2).

    python baselines.py phase1 ../public_data predictions.csv
    python baselines.py phase2 ../public_data predictions.csv
    python baselines.py phase3 ../public_data predictions.csv

Phases 1-2 : TF-IDF et régression logistique entraînés sur train+dev. Phase 3 : heuristique
naïve qui prédit chaque suite de mots capitalisés. À vous de faire mieux.
"""
import re
import sys
from pathlib import Path

import pandas as pd

phase, data, out = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
# keep_default_na=False : l'étiquette "NA" ne doit pas être lue comme une valeur manquante.
read = lambda p: pd.read_csv(p, keep_default_na=False)


def classify(folder, label, cols):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    d = data / folder
    train = pd.concat([read(d / "train.csv"), read(d / "dev.csv")])
    test = read(d / "test_inputs.csv")
    text = lambda df: df[cols].agg(" || ".join, axis=1)
    model = make_pipeline(TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True),
                          LogisticRegression(max_iter=1000, class_weight="balanced"))
    model.fit(text(train), train[label])
    pd.DataFrame({"row_id": test["row_id"], label: model.predict(text(test))}).to_csv(out, index=False)


if phase == "phase1":
    classify("phase1_direction", "rel_type", ["span_text", "e1_event", "e2_event"])
elif phase == "phase2":
    classify("phase2_stance", "stance", ["span_text"])
elif phase == "phase3":
    rows = []
    for _, r in read(data / "phase3_actors" / "test_texts.csv").iterrows():
        for m in re.finditer(r"\b[A-ZÉÈ][\w'’-]+(?:\s+(?:de|du|des|la|le|d')?\s*[A-ZÉÈ][\w'’-]+)*", r["text"]):
            rows.append({"row_id": r["row_id"], "start": m.start(), "end": m.end()})
    pd.DataFrame(rows, columns=["row_id", "start", "end"]).to_csv(out, index=False)
else:
    sys.exit("la phase doit être phase1, phase2 ou phase3")
