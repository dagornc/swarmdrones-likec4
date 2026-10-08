# SWARM-3D — Modèle LikeC4 comme source de vérité sémantique

Ce dépôt contient le **modèle sémantique** d'un essaim de 30 plateformes
autonomes (26 aériens + 4 de surface), destiné à alimenter un
**environnement pédagogique** et un **simulateur Web 3D** (Blender + moteur 3D).

> **Principe fondateur** — LikeC4 est la **source de vérité sémantique**.
> Blender et le moteur 3D en sont des **consommateurs**. Le modèle ne contient
> **aucune coordonnée 3D** : il décrit *ce qui existe, ce que ça fait, et ce
> qui est prouvé*. La spatialisation appartient au consommateur.

## Démarrage rapide

```bash
# Validation (obligatoire avant toute livraison)
docker exec likec4 likec4 validate /data          # attendu : ✓ Valid (14 files)

# Qualité : 11 critères calculés, score /100 (cible ≥ 90)
python3 tools/qa/quality_gate.py                  # attendu : 97/100 — GATE: PASS

# Intégrité : 7 contrôles que la syntaxe ne voit pas
python3 tools/qa/integrity_check.py               # attendu : 7/7 OK

# Artefact pour le moteur 3D
python3 tools/export/export_scene.py          # écrit export/scene.json
python3 tools/export/export_scene.py --check  # vérifie l'artefact (INV-4, 30+1)
```

## État actuel — **16 epics sur 16 livrés**

| Mesure | Départ (E00) | Maintenant |
|---|---|---|
| Score qualité | 31/100 | **97/100** |
| Éléments | 97 | **285** |
| Relations typées | 239 (0 typée) | **544 (27 kinds)** |
| Vues | 22 (5 mortes) | **48 (0 morte)** |
| Fichiers `.c4` | 2 | **14** |

## Carte des fichiers du modèle

- **`architecture.c4`** (~1630 l.) — architecture fonctionnelle et logique d'origine. Le socle. **Non réécrit.**
- **`metamodel.c4`** — le métamodèle : 38 kinds d'éléments, 27+ kinds de relations, tags et couleurs. **Le contrat de forme du modèle.**
- **`hardware.c4`** — drone de référence : capteurs, actionneurs, nœuds de calcul, radios.
- **`messages.c4`** — 13 messages objets, canaux, protocoles, criticité.
- **`algorithms.c4`** — 18 algorithmes, 15+ champs chacun (entrées, sorties, hypothèses, verdict).
- **`facts.c4`** — 7 faits sourcés (fiches matérielles).
- **`decisions_hw.c4`** — décisions matérielles DE-05..DE-10, **ancrées sur les éléments qu'elles bloquent**.
- **`functional.c4`** — 8 capacités, 19 fonctions, traçabilité `realizes`.
- **`deployment.c4`** — chaîne complète Algorithme→Composant→Runtime→Nœud.
- **`scenarios.c4`** — 10 scénarios dérivés des événements réels, 16 étapes.
- **`simulation.c4`** — le **contrat de simulation** : ce que le modèle promet, et 5 invariants.
- **`science.c4`** — 7 sources primaires, 4 constats-verdicts, **4 gaps nommés**.
- **`worldmodel.c4`** — World Model : 6 zones, 7 entités, 10 états, **6 règles de représentation**.
- **`views.c4`** — 48 vues, 12 `navigateTo`, aucune vue morte.

## Ce que ce modèle refuse d'affirmer

Le modèle est **honnête sur ses trous** — c'est une propriété, pas une faiblesse :

- **4 GAP-* nommés** « AUCUN ARTICLE TROUVÉ » (CBBA sous partition persistante,
  CBF hétérogène >30, CRDT en vol sous brouillage RF, fusion EKF ≥100)
- **CBF à 30 agents = UNSUPPORTED** en conditions réelles : la source primaire
  donne **5 robots réels**, 30 en simulation. L'affirmation d'origine a été
  **dégradée**, pas maquillée.
- **DE-07 énergie NON DÉTERMINÉE** → la règle **REG-2** interdit au
  consommateur 3D d'afficher une valeur d'énergie
- **Validation réelle plafonne à 26 plateformes** → **REG-4** exige la mention
  « N=30 NON PROUVÉ »
- **Portées radio = annonces commerciales non vérifiées** → **REG-3** interdit
  d'afficher une portée chiffrée

## Pour le consommateur 3D (Blender / moteur Web)

1. Lire **`export/scene.json`** — l'artefact machine-lisible (34 instances nommées)
2. Ne **jamais inventer d'identifiant** : tout `id_likec4` vient de la table
3. Respecter les **6 règles de représentation** (`REG-1`..`REG-6`) — chacune
   porte un test vérifiable
4. Population : **UAV-R ×18 + UAV-F ×8 + USV ×4 = 30** + 1 maquette de
   référence **visuellement distincte**

Détail complet : [`docs/world-model-spec.md`](docs/world-model-spec.md) et
[`docs/simulation-contract.md`](docs/simulation-contract.md).

## Documentation

- [`docs/audit-likec4.md`](docs/audit-likec4.md) — audit initial (31/100)
- [`docs/qa-report.md`](docs/qa-report.md) — validation globale (97/100)
- [`docs/metamodel.md`](docs/metamodel.md) — contrat de forme
- [`docs/relations-typing.md`](docs/relations-typing.md) — typage des 239 arcs
- [`docs/functional.md`](docs/functional.md) — capacités et fonctions
- [`docs/algorithms.md`](docs/algorithms.md) — catalogue algorithmique
- [`docs/communications.md`](docs/communications.md) — messages et canaux
- [`docs/deployment.md`](docs/deployment.md) — déploiement
- [`docs/scenarios.md`](docs/scenarios.md) — scénarios dynamiques
- [`docs/simulation-contract.md`](docs/simulation-contract.md) — contrat de simulation
- [`docs/science.md`](docs/science.md) — référentiel scientifique
- [`docs/world-model-spec.md`](docs/world-model-spec.md) — spécification World Model

## Page d'accueil du site

`likec4.config.json` porte `"landingPage": { "redirect": true }` : la racine
de <https://likec4.breizh.ai/> redirige vers la vue **`index`**
(`/view/index/`), l'URL affichée restant `/`. La vue `index` est la carte
d'entrée du modèle — paysage des zones de déploiement, avec navigation vers
les vues de zone.

Le comportement est implémenté côté frontend LikeC4 : la route `/` redirige
vers `/view/index/` **uniquement** si le projet est unique et que
`landingPage.redirect` est présent. En multi-projets, la racine mène à la
liste des projets.

Pour revenir à la grille de toutes les vues, retirer la clé `landingPage`
(ou la remplacer par `{"include": [...]}` / `{"exclude": [...]}` pour
filtrer la grille).

## Outils

- `tools/audit_inventory.py` — inventaire initial
- `tools/arc_classify.py` / `tools/arc_apply.py` — typage des relations
- `tools/qa/quality_gate.py` — score qualité /100 (11 critères calculés)
- `tools/qa/integrity_check.py` — 7 contrôles d'intégrité structurelle

## Invariants à ne jamais violer

1. **INV-1** — La mission nominale ne dépend pas du cloud
2. **INV-2** — La sûreté reste locale : perte de C2 ≠ perte de sûreté
3. **INV-3** — La validation à 30 plateformes reste **non prouvée**
4. **INV-4** — **Aucune 3D dans le modèle sémantique**
5. **INV-5** — Toute affirmation scientifique est reliée à une source, ou
   déclarée non prouvée
