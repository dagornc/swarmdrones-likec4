# Rapport de validation globale — E12

> Epic **E12** · Carte `t_6264167c` · Outils : `tools/qa/quality_gate.py`, `tools/qa/integrity_check.py`

## 1. Verdict

| Mesure | E00 (initial) | Maintenant | Delta |
|---|---|---|---|
| Score qualité | **31/100** | **97/100** | **+66** |
| Contrôles d'intégrité | — | **7/7 OK** | — |
| Validation syntaxique | Valid (2 files) | **Valid (14 files)** | +12 fichiers |
| Éléments | 97 | **285** | +188 |
| Relations | 239 (0 typées) | **544 (27 kinds)** | +305 |
| Vues | 22 (5 mortes) | **48 (0 morte)** | +26 |

**GATE : PASS** (cible ≥ 90).

## 2. Score détaillé — 11 critères, tous calculés

| Critère | Poids | E00 | Maintenant | Justification mesurée |
|---|---|---|---|---|
| Validité syntaxique | 10 | 10 | **10** | `Valid (14 files, 0 errors)` |
| Identifiants uniques | 10 | 8 | **9** | 285 éléments, 93 % conformes |
| Type des éléments | 10 | 5 | **10** | 38 kinds, **6/6 familles** couvertes |
| Type des relations | 15 | **0** | **15** | 544 relations, **27 kinds** distincts |
| Complétude documentaire | 10 | 7 | **10** | 285/285 descriptions (100 %) |
| Couverture algorithmique | 10 | 2 | **9** | 18 algorithmes, 4,7 champs riches |
| Couverture messages | 10 | **0** | **10** | 13 messages objets |
| Couverture matérielle | 10 | **0** | **9** | 9 éléments matériels |
| Couverture déploiement | 10 | 6 | **10** | 5 unités + chaîne typée |
| Vues et navigation | 5 | 4 | **5** | 48 vues, **0 vide**, 12 `navigateTo` |
| Traçabilité / preuves | 10 | 4 | **10** | 7 faits, 8 éléments scientifiques, 88 sourcés |

## 3. Les 7 contrôles d'intégrité — ce que `validate` ne voit pas

- **I-1 Intégrité référentielle** — 544 relations, **0 arc cassé**
- **I-2 Éléments orphelins** — **0 orphelin**
- **I-3 Chaîne CAPACITÉ→FONCTION→ALGORITHME** — 20 liens, **20 avec algorithme rattaché**
- **I-4 Contrat de simulation** — contrat présent, 5 invariants nommés
- **I-5 Garde-fous World Model** — 6 règles, **6 portent un test**
- **I-6 Aucune valeur inventée** — **0 valeur chiffrée non sourcée**
- **I-7 Cohérence scientifique** — 8 constats = 4 verdicts sourcés + 4 gaps

## 4. Défauts RÉELS trouvés et corrigés par E12

E12 n'était pas une formalité — le contrôle a révélé des trous que 13 epics
avaient laissés passer :

1. **7 éléments orphelins** : les décisions matérielles DE-05..DE-10 portaient
   leur cible dans un champ texte `metadata.bloque`, **sans relation réelle**.
   Le graphe ne les reliait à rien. → 7 relations `justifie` créées.
2. **Toutes les cibles de `bloque` étaient FAUSSES** (`onboard.flightCtrl`,
   `onboard.companion`, `onboard.imu`, `onboard.power`, `onboard.saeSensor`,
   `refDrone.*`) : aucun de ces identifiants n'existe. Les vrais sont dans
   `refDrone.*` (hardware.c4) et `cloud.twin`. **Ces valeurs n'avaient jamais
   été confrontées au modèle.** → vérifiées et corrigées une par une.
3. **`chCloud`** (canal cloud) n'était relié à rien. → relation `uses` vers `cloud.twin`.

## 5. Défauts de MESURE corrigés dans les outils

Un quality gate qui mesure faux est pire que pas de gate. Trois bugs de
mesure ont été trouvés et corrigés :

1. **`Validité syntaxique = 0`** alors que le modèle était valide : la sortie
   du conteneur contient des **codes ANSI** (`\x1b[32m✓ Valid\x1b[39m`) entre
   `Valid` et `(14 files` — le regex échouait. → suppression ANSI avant parsing.
2. **`Vues = 4/5`** : le critère portait sur la **navigation et la santé des
   vues**, pas sur leur nombre (E00 notait 4/5 pour 22 vues dont 5 mortes).
   → le critère compte désormais les vues vides et les `navigateTo`.
3. **`I-3` et `I-7`** cherchaient les mauvais champs : la relation
   fonction→composant est `realizes` (pas `implements`), et les GAP-* sont des
   constats **sans verdict par construction** (aucun article trouvé). Comparer
   8 findings à 4 verdicts était une erreur de mesure, pas un défaut du modèle.

## 6. Ce que le modèle déclare ne PAS prouver

La validation ne maquille pas les trous — elle les certifie :

- **4 GAP-* nommés** : « AUCUN ARTICLE TROUVÉ » pour CBBA sous partition
  persistante, CBF hétérogène > 30, CRDT en vol sous brouillage RF, fusion
  EKF ≥ 100 plateformes
- **DE-07 (énergie) NON DÉTERMINÉE** → la règle REG-2 interdit au consommateur
  3D d'afficher une valeur d'énergie
- **CBF à 30 agents = UNSUPPORTED** en conditions réelles (réel = 5 robots)
- **Validation réelle plafonne à 26** → REG-4 exige la mention « N=30 NON PROUVÉ »

## 7. Reproductibilité

```
docker exec likec4 likec4 validate /data     # ✓ Valid (14 files)
python3 tools/qa/quality_gate.py             # 97/100 — GATE: PASS
python3 tools/qa/integrity_check.py          # 7/7 controles OK
```
