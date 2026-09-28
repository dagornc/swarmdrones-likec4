# RAPPORT_TRACABILITE_COMPLETE — SPEC-13 / LikeC4

**Carte** : LIKEC4-TRACE (t_8bc71fb2)
**Auteur** : architecte (profil architecte)
**Date** : 2026-09-28
**Périmètre** : les 13 algorithmes manquants (SPEC-13), leurs 3 artefacts
(spec PDF v1, spec SysML v2, portage Rust) et la cohérence des métadonnées
dans `algorithms.c4` / `views.c4` du dépôt `dagornc/swarmdrones-likec4`.

---

## 1. Conclusion (synthèse)

- **Liens vérifiés : 40/40 existants** (HTTP 200 via GitHub API) — 13 PDF de
  spec + 13 fichiers `.sysml` + 13 dépôts Rust `alg-<slug>` + 1 dépôt principal
  `SwarmDrones`. Aucun lien mort.
- **Métadonnées corrigées : 6 cartes** portaient encore `statut 'REJETEE
  (publiee malgre rejet)'` en contradiction avec leur propre description
  (CONFORME). Corrigées en `statut 'PUBLIE'` + note de validation RÉELLE lue
  dans les rapports `validation_<slug>_v1.md`.
- **Écart détecté pendant l'audit (au-delà des 6 cartes) :** la note RÉELLE
  diffère du tableau de la carte pour 4 algorithmes, et `nav_gnss_degrade`
  (non listé) était lui aussi faux (« conforme » alors que le rapport
  indépendant dit 14/20 PUBLIABLE SOUS RÉSERVE). Toutes ces métadonnées ont
  été alignées sur les rapports réels (voir §3).
- **Aucune note inventée** : chaque note provient du fichier
  `/home/hermesagent/workspace/spec13/<slug>/validation_<slug>_v1.md`.

---

## 2. Matrice des liens — 13 algorithmes × 3 artefacts

| Algorithme | spec PDF v1 | SysML v2 | Portage Rust | Statut lien |
|---|---|---|---|---|
| ALG_FORMATION_CONTROL | OK | OK | OK (alg-formation-control) | 3/3 |
| ALG_LEADER_ELECTION | OK | OK | OK (alg-leader-election) | 3/3 |
| ALG_PERCEPTION_FUSION | OK | OK | OK (alg-perception-fusion) | 3/3 |
| ALG_NAV_GNSS_DEGRADE | OK | OK | OK (alg-nav-gnss-degrade) | 3/3 |
| ALG_COLLISION_AVOIDANCE | OK | OK | OK (alg-collision-avoidance) | 3/3 |
| ALG_SAFETY_RULES | OK | OK | OK (alg-safety-rules) | 3/3 |
| ALG_PATH_PLANNING | OK | OK | OK (alg-path-planning) | 3/3 |
| ALG_HEALTH_MONITORING | OK | OK | OK (alg-health-monitoring) | 3/3 |
| ALG_ENERGY_AWARE | OK | OK | OK (alg-energy-aware) | 3/3 |
| ALG_EVENT_TRIGGERED_COMM | OK | OK | OK (alg-event-triggered-comm) | 3/3 |
| ALG_COOPERATIVE_LOCALIZATION | OK | OK | OK (alg-cooperative-localization) | 3/3 |
| ALG_FAULT_TOLERANT_CONTROL_ALLOC | OK | OK | OK (alg-fault-tolerant-control-alloc) | 3/3 |
| ALG_JAMMING_RESILIENT_MODE | OK | OK | OK (alg-jamming-resilient-mode) | 3/3 |

**Vérification d'existence réelle** (pas seulement la présence du lien) :
`gh api repos/dagornc/swarmdrones-likec4/contents/{specification, sysml}/...`
pour chaque PDF/sysml, et `gh api repos/dagornc/alg-<slug>` pour chaque dépôt.
Résultat : 40/40 HTTP 200. Détail des URLs au §5.

**URLs (patrons)** :
- PDF : `https://github.com/dagornc/swarmdrones-likec4/blob/master/specification/Spec_ALG_<ID>_v1.pdf`
- SysML : `https://github.com/dagornc/swarmdrones-likec4/blob/master/sysml/ALG_<ID>.sysml`
- Rust : `https://github.com/dagornc/alg-<slug>`

---

## 3. Notes de validation réelles (source : `validation_<slug>_v1.md`)

| Algorithme | Note réelle | Verdict | Validateur | Métadonnée `validation` (cible) |
|---|---|---|---|---|
| formation_control | 20/20 | CONFORME | mathematique | PUBLIE — conforme (déjà correct) |
| **leader_election** | **15/20** | **PUBLIABLE SOUS RÉSERVE** | mathematique | `PUBLIABLE SOUS RESERVE — 15/20` |
| perception_fusion | 20/20 | CONFORME | mathematique | PUBLIE — conforme (déjà correct) |
| **nav_gnss_degrade** | **14/20** | **PUBLIABLE SOUS RÉSERVE** | mathematique | `PUBLIABLE SOUS RESERVE — 14/20` |
| collision_avoidance | 19/20 | CONFORME | mathematique | PUBLIE — conforme (déjà correct) |
| safety_rules | 17/20 | CONFORME | orchestrateur | `CONFORME — 17/20` |
| path_planning | 20/20 | CONFORME | mathematique | PUBLIE — conforme (déjà correct) |
| health_monitoring | 20/20 | CONFORME | orchestrateur | `CONFORME — 20/20` |
| energy_aware | 20/20 | CONFORME | orchestrateur | `CONFORME — 20/20` |
| event_triggered_comm | 17/20 | CONFORME | orchestrateur | `CONFORME — 17/20` |
| cooperative_localization | 20/20 | CONFORME | mathematique | PUBLIE — conforme (déjà correct) |
| fault_tolerant_control_alloc | n/a | APPROVED (integration review) | orchestrateur | PUBLIE — conforme (pas de note /20) |
| jamming_resilient_mode | 20/20 | CONFORME | orchestrateur | `CONFORME — 20/20` |

**Écarts vs tableau de la carte t_8bc71fb2 (corrigés) :**

| Carte | Tableau de la carte | Note réelle lue |
|---|---|---|
| specLeaderElection | « Reproduite, 20/20 » | **15/20 — PUBLIABLE SOUS RÉSERVE (2 défauts MAJEURS)** |
| specHealthMonitoring | « 18/20 » | **20/20 — CONFORME** |
| specEnergyAware | « 17/20 » | **20/20 — CONFORME** |
| specEventTriggeredComm | « 18/20 » | **17/20 — CONFORME** |
| specNavigationGNSSDegrade | (non listé, « conforme ») | **14/20 — PUBLIABLE SOUS RÉSERVE (2 défauts MAJEURS)** |

Les 5 autres notes du tableau (safety_rules 17, jamming 20) étaient exactes.

---

## 4. Corrections appliquées

Dans `algorithms.c4` :
1. **6 titres** : « (v1 — REJETEE par validation) » → « (v1) ».
2. **6 `statut`** : `REJETEE (publiee malgre rejet)` → `PUBLIE`.
3. **6 `validation`** : note REJETEE obsolète → note réelle (cf §3).
4. **6 `specPdf`** des cartes `src<X>` : mention REJETEE → `(PUBLIE — <verdict> <note>)`.
5. **description specLeaderElection** : « CONFORME 20/20 » → « PUBLIABLE SOUS
   RESERVE — 15/20 ».
6. **specNavigationGNSSDegrade** (découvert en audit) : `validation`
   « PUBLIEE — conforme » → « PUBLIABLE SOUS RESERVE — 14/20 », description et
   `specPdf` alignés.
7. **Commentaire d'en-tête SPEC-13-LIKE** : « 7 VALIDEES ; 6 REJETEES » →
   « 11/13 CONFORMES ; 2/13 PUBLIABLES SOUS RESERVE ».

Dans `views.c4` (cohérence des vues avec le nouveau statut) :
8. **algorithmCatalog** et **algorithmSpecTraceability** : le texte
   « 7 VALIDEES et 6 REJETEES (statut REJETEE) » → « 11 CONFORMES,
   2 PUBLIABLES SOUS RESERVE (leader_election 15/20, nav_gnss_degrade 14/20),
   note réelle lue dans validation_<slug>_v1.md ».

Note de contexte : les changements 1–7 d'`algorithms.c4` ont été committés par
un travail parallèle (commit `ebf9458`, rattachement scientifique SCI-12..14)
qui a englobé le fichier `algorithms.c4` pendant que ce correctif était en
cours. Les changements 8 (`views.c4`) sont committés par la présente carte,
avec ce rapport.

---

## 5. Détail des URLs vérifiées (HTTP 200)

PDF (`specification/`) :
```
Spec_ALG_FORMATION_CONTROL_v1.pdf
Spec_ALG_LEADER_ELECTION_v1.pdf
Spec_ALG_PERCEPTION_FUSION_v1.pdf
Spec_ALG_NAV_GNSS_DEGRADE_v1.pdf
Spec_ALG_COLLISION_AVOIDANCE_v1.pdf
Spec_ALG_SAFETY_RULES_v1.pdf
Spec_ALG_PATH_PLANNING_v1.pdf
Spec_ALG_HEALTH_MONITORING_v1.pdf
Spec_ALG_ENERGY_AWARE_v1.pdf
Spec_ALG_EVENT_TRIGGERED_COMM_v1.pdf
Spec_ALG_COOPERATIVE_LOCALIZATION_v1.pdf
Spec_ALG_FAULT_TOLERANT_CONTROL_ALLOC_v1.pdf
Spec_ALG_JAMMING_RESILIENT_MODE_v1.pdf
```

SysML (`sysml/`) :
```
ALG_FORMATION_CONTROL.sysml
ALG_LEADER_ELECTION.sysml
ALG_PERCEPTION_FUSION.sysml
ALG_NAV_GNSS_DEGRADE.sysml
ALG_COLLISION_AVOIDANCE.sysml
ALG_SAFETY_RULES.sysml
ALG_PATH_PLANNING.sysml
ALG_HEALTH_MONITORING.sysml
ALG_ENERGY_AWARE.sysml
ALG_EVENT_TRIGGERED_COMM.sysml
ALG_COOPERATIVE_LOCALIZATION.sysml
ALG_FAULT_TOLERANT_CONTROL_ALLOC.sysml
ALG_JAMMING_RESILIENT_MODE.sysml
```

Dépôts Rust (`dagornc/alg-<slug>`) :
```
alg-formation-control
alg-leader-election
alg-perception-fusion
alg-nav-gnss-degrade
alg-collision-avoidance
alg-safety-rules
alg-path-planning
alg-health-monitoring
alg-energy-aware
alg-event-triggered-comm
alg-cooperative-localization
alg-fault-tolerant-control-alloc
alg-jamming-resilient-mode
```

Dépôt principal : `https://github.com/dagornc/SwarmDrones` (OK).

---

## 6. Vérification de cohérence croisée

- `algorithms.c4` : 13 `specDoc` (spec<X>) + 13 `sourceCode` (src<X>) définis ;
  relations `alg-[documentedBy]->specDoc` (13), `src-[implements]->alg` (13),
  `src-[documentedBy]->specDoc` (13) présentes.
- `sysml.c4` : 15 `specDoc` SysML v2 (13 nouveaux + TASK_ALLOCATION + CONSENSUS),
  relations `alg-[documentedBy]->sysml` portées par ce fichier (non dupliquées).
- `e20-audit-completeness.c4` : déclare 4 des 13 algorithmes
  (event-triggered-comm, cooperative-localization, fault-tolerant-control-alloc,
  jamming-resilient-mode) ; les 9 autres sont dans `algorithms.c4`. Chacun des
  13 a bien ses 3 artefacts liés — **aucun algorithme incomplet**.

---

## 7. Validation

`git clone -q . /tmp/lc_trace && cd /tmp/lc_trace && npx likec4 validate`
→ attendu `✓ Valid (20 files)`. (voir journal d'exécution de la carte)
