# Évaluation

Déposez une archive zip contenant `predictions.csv`. Le format dépend de la phase ; un fichier invalide fait échouer la soumission. Chaque phase a un fichier `sample_submission_*.csv` dans le kit de démarrage.

**Phase 1** - colonnes `row_id,rel_type` ; une ligne par `row_id` de `test_inputs.csv` ; étiquettes `CAUSES` ou `IS_CAUSED_BY`. Métrique : macro-F1 sur les classes présentes dans les étiquettes cachées (*P1 macro-F1*), plus l'exactitude.

**Phase 2** - colonnes `row_id,stance` ; étiquettes `LEGITIMATE` ou `NA`. Métrique : macro-F1 (*P2 macro-F1*), plus l'exactitude.

**Phase 3** - colonnes `row_id,start,end` ; une ligne par span prédit, avec des décalages de caractères dans le `text` de cette ligne (fin exclue). Les lignes sans span peuvent être omises. Un span prédit correspond à un span de référence de la même ligne lorsque leur intersection sur union est d'au moins 0,5 ; chaque span ne correspond qu'une fois. Métrique : F1 sur les spans appariés (*P3 F1 spans*), avec la précision, le rappel et un F1 strict (correspondance exacte) à titre indicatif.
