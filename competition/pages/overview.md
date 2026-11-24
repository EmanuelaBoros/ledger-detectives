# Les Détectives du Grand Livre

Quand une entreprise française se vante de ses bénéfices en 1934, s'agit-il d'un profit légitime ou de quelque chose de plus suspect ? Enfilez votre chapeau de détective et épluchez les comptes. Les passages de cette compétition viennent d'articles de presse et d'assemblées générales d'actionnaires français (1907-1950), annotés par des chercheurs qui étudient la manière dont on débattait de la légitimité du profit.

La compétition comporte trois phases consécutives, chacune avec ses données et sa métrique :

| Phase | Dates (déc. 2026) | Tâche | Métrique |
|---|---|---|---|
| 1 | 1-10 | **Cause ou causé par** : l'événement 1 cause-t-il l'événement 2 (`CAUSES`) ou en résulte-t-il (`IS_CAUSED_BY`) ? | macro-F1 |
| 2 | 11-20 | **Position sur le profit** : le texte juge-t-il un profit légitime (`LEGITIMATE`) ou ne donne-t-il aucun jugement (`NA`) ? | macro-F1 |
| 3 | 21-31 | **Spans de preuve des acteurs** : retrouver les passages que les annotateurs ont cités comme preuve des acteurs de chaque événement. | F1 sur spans |

**Il s'agit d'un petit pilote.** Les jeux de test ne comptent que 19, 23 et 20 passages selon la phase. Les écarts entre équipes seront bruités : considérez le classement comme un exercice d'apprentissage.

*Les textes sont en français ; les étiquettes (`CAUSES`, `LEGITIMATE`, `NA`...) sont des codes en anglais, repris tels quels des consignes d'annotation.*
