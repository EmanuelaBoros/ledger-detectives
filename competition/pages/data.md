# Données

Téléchargez le kit de démarrage et `public_data`. Tous les fichiers sont des CSV en UTF-8 avec une ligne d'en-tête.

## Phase 1 : `public_data/phase1_direction/`
`train.csv` (59 lignes) et `dev.csv` (14) sont étiquetés ; `test_inputs.csv` (19) ne l'est pas.
Colonnes : `row_id`, `domain` (`GA` assemblée générale / `PRESSE`), `pre_context`, `span_text`, `post_context`, `e1_event`, `e2_event`, et `rel_type` (fichiers étiquetés). Les événements sont les étiquettes courtes des annotateurs, dans l'ordre de mention. Classes très déséquilibrées : la plupart des lignes sont `CAUSES`.

## Phase 2 : `public_data/phase2_stance/`
`train.csv` (77), `dev.csv` (29), `test_inputs.csv` (23). Mêmes colonnes de texte, étiquette `stance` dans {`LEGITIMATE`, `NA`}.
Une troisième étiquette, `ILLEGITIMATE`, existe dans le schéma d'annotation, mais il n'y a qu'un seul exemple : elle est écartée de ce pilote.

## Phase 3 : `public_data/phase3_actors/`
`{train,dev}_texts.csv` et `test_texts.csv` contiennent `row_id`, `domain` et `text` (contexte avant, passage et contexte après, séparés par une ligne vide). `{train,dev}_spans.csv` donnent les spans de référence sous forme de décalages de caractères `start`, `end` dans `text` (fin exclue, premier caractère = 0), avec la chaîne du span.
Ces spans sont les **preuves citées** par les annotateurs pour les acteurs de chaque événement. Ce sont des segments (médiane d'environ 40 caractères), parfois des groupes nominaux comme « la clientèle », parfois des propositions plus longues. Ce ne sont pas des annotations exhaustives d'entités : les autres acteurs du texte ne sont pas marqués. La catégorie d'un span n'est pas évaluée.

## Lire les données
`NA` est une vraie étiquette, pas une valeur manquante. Avec pandas : `pd.read_csv(chemin, keep_default_na=False)`. Les textes sont des transcriptions historiques corrigées après OCR et peuvent contenir des erreurs.

## Limites connues
- Les passages au texte identique restent dans le même découpage, mais 119 des 159 lignes sources viennent d'une seule assemblée générale de 1934 : l'entraînement et le test partagent donc des documents.
- Les étiquettes proviennent d'un classeur d'annotation antérieur à la version 2 du guide ; elles ont été normalisées par les organisateurs et certaines étaient incohérentes.
