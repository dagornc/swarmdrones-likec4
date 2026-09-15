# Matrice de traçabilité — E00 → E13

Chaque epic, son livrable, sa preuve vérifiable, et sa carte Kanban.
**Aucun epic n'est DONE sans preuve reproductible.**

| Epic | Objet | Livrable | Preuve | Carte |
|---|---|---|---|---|
| **E00** | Audit initial | `docs/audit-like4.md` (331 l.) + `tools/audit_inventory.py` | 239 arcs non typés, **score 31/100** | `t_5542ae1d` |
| **E01** | Métamodèle | `metamodel.c4` + `docs/metamodel.md` | 56 kinds, 37 relations ; 97/239/22 inchangés | `t_b6b0fb55` |
| **E02** | Architecture fonctionnelle | `functional.c4` + `docs/functional.md` | 8 capacités, 19 fonctions, 0 orphelin | `t_4e4ec60b` |
| **E03** | Typage des relations | `tools/arc_classify.py`, `arc_apply.py` + `docs/relations-typing.md` | **142 `unknown` → 0** ; 239 arcs typés | `t_5f46d5aa` |
| **E04** | Catalogue algorithmique | `algorithms.c4` + `docs/algorithms.md` | 18 algorithmes, 15+ champs, 0 orphelin | `t_83ae834a` |
| **E05** | Architecture matérielle | `hardware.c4` (244 l.) | Drone de référence : capteurs, actionneurs, calcul | `t_0028effd` |
| **E05-INTEG** | Intégration matérielle | `facts.c4`, `decisions_hw.c4` | 7 faits sourcés, 6 décisions ; corrections épistémiques | `t_72dfb8c1` |
| **E06** | Messages et canaux | `messages.c4` + `docs/communications.md` | 13 messages, 0 orphelin ; `radio` 16→3 | `t_f7a97194` |
| **E07** | Déploiement | `deployment.c4` + `docs/deployment.md` | **11/11 chaînes** Algorithm→Component→Runtime→Node | `t_de7c0750` |
| **E08** | Référentiel scientifique | `science.c4` + `docs/science.md` | 7 sources primaires, 4 verdicts, **4 gaps nommés** | `t_0e42fc2a` |
| **E09** | Scénarios dynamiques | `scenarios.c4` + `docs/scenarios.md` | 10 scénarios, 16 étapes, 0 orphelin | `t_361b3beb` |
| **E10** | Contrat de simulation | `simulation.c4` + `docs/simulation-contract.md` | 22 éléments de contrat, 5 invariants, 0 orphelin | `t_6641b537` |
| **E11** | World Model | `worldmodel.c4` + `export/world-model.json` | 33 éléments, **30 opérationnels + 1 maquette**, **0 coordonnée** | `t_ab3002bd` |
| **E12** | Validation globale | `tools/qa/*` + `docs/qa-report.md` | **97/100**, **7/7 intégrité**, 0 orphelin | `t_6264167c` |
| **E13** | Documentation | `README.md` + cette matrice | Point d'entrée, invariants, traçabilité | `t_a46252dc` |
| E08-RECH | Recherche SwarmDrone | `claim-fidelity-audit.md` (14 510 c.) | Audit de fidélité des affirmations | `t_81787f59` |
| TBD | Fiche matérielle | `E05-TBD_materiel_drone_reference.md` | 618 l. sourcées | `t_699fc55f` |

## Chaînes de traçabilité vérifiées

**Chaîne complète (E12, I-3)** — 20 liens capacité→fonction, 20 avec algorithme :

```
CAPACITÉ μcapDecide
  → FONCTION fnCollisionAvoidance      (realizes)
    → ALGORITHME algCollisionAvoidance (implements)
      → COMPOSANT onboard.safety       (implements)
        → RUNTIME rtFlight             (runsOn)
          → NŒUD refDrone.flightCtrl   (deployedOn)
```

**Chaîne de déploiement (E07)** — 11/11 complètes, 0 orphelin.

**Dérivation du World Model (E11)** :

```
id_likec4 (stable) → role_scene → categorie_visuelle → population
```

## Corrections épistémiques majeures (traçables)

| Affirmation | Statut | Preuve |
|---|---|---|
| CBF garantit la non-collision à **30 agents en réel** | **UNSUPPORTED** — dégradé | Source : 5 robots réels, 30 simulé ; 5,1 violations/essai |
| Validation à 30 plateformes | **NON PROUVÉE** | Réel plafonné à 26 ; `riskR3` |
| Budget énergie | **NON DÉTERMINÉ** | DE-07 ; REG-2 interdit l'affichage |
| Portées radio publiées | **ANNONCES NON VÉRIFIÉES** | REG-3 interdit l'affichage chiffré |
| CBBA / CRDT / EKF à l'échelle | **4 gaps « AUCUN ARTICLE TROUVÉ »** | GAP-1..GAP-4 |

## Défauts corrigés par E12 (que 13 epics avaient laissés passer)

1. **7 éléments orphelins** — les décisions DE-05..DE-10 déclaraient leur cible
   dans un champ texte `metadata.bloque`, **sans relation réelle dans le graphe**
2. **Toutes ces cibles étaient fausses** — `onboard.flightCtrl`,
   `onboard.companion`, `onboard.imu`, `onboard.power`, `onboard.saeSensor`,
   `refDrone.*` : **aucun de ces identifiants n'existe**. Jamais confrontés au
   modèle. Corrigés en `refDrone.flightCtrl` / `companion` / `radioLnk` /
   `netMesh` / `power` / `imu` / `saeSensor` + `cloud.twin`, **vérifiés un par un**.
3. **`chCloud`** relié à rien → ancré sur `cloud.twin`

## Reproductibilité

```bash
docker exec likec4 likec4 validate /data    # ✓ Valid (14 files)
python3 tools/qa/quality_gate.py            # 97/100 — GATE: PASS
python3 tools/qa/integrity_check.py         # 7/7 controles OK
```

## Sauvegardes

`backup_v1`..`backup_v20` + `point4` — chaque epic a son point de restauration.
**Aucune information utile n'a été supprimée** : tout a été ajouté par surcouche.
