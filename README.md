# SWARM-3D — Modèle LikeC4 comme source de vérité sémantique

Ce dépôt contient le **modèle sémantique** d'un essaim de 30 plateformes
autonomes (26 aériens + 4 de surface), destiné à alimenter un
**environnement pédagogique** et un **simulateur Web 3D** (Blender + moteur 3D).

> **Principe fondateur** — LikeC4 est la **source de vérité sémantique**.
> Blender et le moteur 3D en sont des **consommateurs**. Le modèle ne contient
> **aucune coordonnée 3D** : il décrit *ce qui existe, ce que ça fait, et ce
> qui est prouvé*. La spatialisation appartient au consommateur.

> **Propriété distinctive de ce dépôt** — la chaîne de consommation n'est pas
> *décrite* : elle est **exécutable et falsifiable**. Un modèle qui se contente
> d'exporter du JSON est une promesse ; ici, chaque promesse porte un test qui
> **échoue** quand elle est violée.

## Démarrage rapide

```bash
# Validation (obligatoire avant toute livraison)
docker exec likec4 likec4 validate /data          # attendu : ✓ Valid (14 files)

# Qualité : 11 critères calculés, score /100 (cible ≥ 90)
python3 tools/qa/quality_gate.py                  # attendu : 97/100 — GATE: PASS

# Intégrité : 7 contrôles que la syntaxe ne voit pas
python3 tools/qa/integrity_check.py               # attendu : 7/7 OK

# Artefact pour le moteur 3D
python3 tools/export/export_scene.py          # écrit export/scene.json + viewer/scene.json
python3 tools/export/export_scene.py --check  # vérifie l'artefact (INV-4, 30+1, cohérence des copies)
```

## La chaîne consommateur (exécutable et falsifiable)

Le modèle est consommé par un **viewer 3D** et par des **assets Blender**.
Ces trois maillons sont vérifiables indépendamment :

```bash
# 1. Contrat consommateur — 6 obligations + 6 garde-fous REG-1..REG-6
python3 tools/export/test_consumer_contract.py
#   attendu : 8/8 contrôles, 7/7 mutations DÉTECTÉES (le test échoue si on viole le contrat)

# 2. Logique du viewer (sans navigateur, sous Node)
node viewer/test_viewer_logic.js
#   attendu : 8/8 contrôles + 6/6 mutations

# 3. Rendu 3D réellement mesuré (navigateur headless, readPixels)
#    Prérequis : le viewer doit être servi en HTTP, et la commande s'exécute
#    DANS le conteneur (le script référence le Chromium du conteneur).
python3 -m http.server 8931 --bind 0.0.0.0 &        # sert viewer/
docker cp tools/export/verify_final.js mcp-playwright:/tmp/vf.js
docker exec mcp-playwright node /tmp/vf.js
#   attendu : 74% de pixels non-fond (nonBlackPixels=532443), 93 couleurs,
#             8/8 contrôles (fail=0), 0 erreur JS

# 4. Assets glTF alignés sur le modèle, traçabilité embarquée
blender --background --python tools/assets/build_assets.py -- --check
#   attendu : 7 assets, catégories alignées, aucune dimension physique revendiquée

# 5. Rendu des assets — échoue si l'image est vide
python3 tools/assets/test_preview.py assets/preview.png
```

**Ce que « falsifiable » veut dire ici** : chaque test a été validé *contre une
mutation*. Quand on retire une obligation du contrat, quand on injecte une
classe inexistante, quand on falsifie une copie de `scene.json`, le test
**échoue avec un code non nul**. Un test qui ne peut pas échouer ne prouve rien.

## Ce que la chaîne garantit

- **Le modèle ne ment pas sur l'espace** — INV-4 tenu : `transform: null`
  partout, `coords=0` vérifié à l'export.
- **Le consommateur ne peut pas inventer** — un `class_id` absent du modèle est
  détecté (REG-1) ; une valeur interdite (énergie, portée radio) est détectée
  (REG-2/REG-3) ; la mention « N=30 NON PROUVÉ » est exigée (REG-4).
- **Les assets sont traçables** — chaque GLB porte `source_category` et
  `source_class` **dans son binaire**. Aucune dimension physique n'y est
  revendiquée : l'échelle est une convention de scène.
- **La sortie ne diverge pas du code** — `export_scene.py --check` échoue si
  `export/scene.json` et `viewer/scene.json` diffèrent.

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
- [`docs/viewer-3d.md`](docs/viewer-3d.md) — viewer 3D : contrat vérifié et rendu mesuré
- [`docs/assets-3d.md`](docs/assets-3d.md) — assets Blender : génération traçable
- [`docs/versionnement.md`](docs/versionnement.md) — ce qui est versionné, et pourquoi

## Outils

- `tools/audit_inventory.py` — inventaire initial
- `tools/arc_classify.py` / `tools/arc_apply.py` — typage des relations
- `tools/qa/quality_gate.py` — score qualité /100 (11 critères calculés)
- `tools/qa/integrity_check.py` — 7 contrôles d'intégrité structurelle
- `tools/export/export_scene.py` — génère l'artefact `scene.json` (+ `--check`)
- `tools/export/test_consumer_contract.py` — contrat consommateur + mutations
- `tools/export/verify_final.js` — preuve de rendu (navigateur headless)
- `tools/assets/build_assets.py` — génère les 7 assets glTF (+ `--check`)
- `tools/assets/render_preview.py` + `test_preview.py` — rendu et test falsifiable
- `viewer/index.html` — viewer 3D (three.js) avec moteur de vérification intégré
- `viewer/test_viewer_logic.js` — test de la logique viewer sous Node

## Limites assumées (démonstrateur, pas outil opérationnel)

Ce dépôt **démontre une méthode** : comment un modèle sémantique devient une
chaîne de consommation vérifiable. Il n'est **pas** un simulateur opérationnel.

- **Les formations sont illustratives** — anneaux déterministes montrant la
  population, pas une dynamique de vol. Aucun modèle aérodynamique.
- **Aucune temporalité** — pas d'horloge de simulation, pas d'état qui évolue.
- **Les assets 3D ne sont pas chargés par le viewer** — la chaîne actuelle
  (formes procédurales) et la chaîne Blender (7 GLB traçables) existent
  séparément. Leur intégration est une étape distincte, non faite.
- **La 2D de repli n'a été exercée qu'en test** — jamais sur une machine
  réellement dépourvue de WebGL.
- **Le rendu validé est logiciel** (SwiftShader) — un GPU réel n'a pas été
  testé.

Ces limites sont **nommées**, pas dissimulées : c'est la même discipline que le
modèle applique à ses propres `GAP-*`.

## Invariants à ne jamais violer

1. **INV-1** — La mission nominale ne dépend pas du cloud
2. **INV-2** — La sûreté reste locale : perte de C2 ≠ perte de sûreté
3. **INV-3** — La validation à 30 plateformes reste **non prouvée**
4. **INV-4** — **Aucune 3D dans le modèle sémantique**
5. **INV-5** — Toute affirmation scientifique est reliée à une source, ou
   déclarée non prouvée
