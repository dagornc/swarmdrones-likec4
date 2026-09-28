# RAPPORT_AUDIT_FINAL_LIKEC4.md

Audit final de cohérence des cartes et liens du modèle LikeC4 SwarmDrones.
Date : 2026-09-28 (UTC). Profil : architecte. Carte kanban : t_7af1c246.

## 0. État de référence

- Dépôt local : `~/workspace/swarmdrones_likec4` (remote `origin` = `https://github.com/dagornc/swarmdrones-likec4.git`).
- HEAD audité : `4590f59` (précédé de `b6db44a` LIKEC4-ALGO-LINKS, `6adff59` DOI placeholders, `f27e190` métadonnées, `ebf9458` rattachement scientifique).
- `npx likec4 validate` sur clone propre (`git clone . /tmp/lc_aud*`) → **`✓ Valid (20 files)`**, exit 0 (vérifié à 4590f59, avant ET après la correction `repository`).
- Graphe résolu extrait via `likec4 export json` (source de vérité) : **405 éléments, 771 relations, 0 référence pendante** (aucune cible fantôme).

## 1. Cohérence interne des cartes (statut / validation)

### 1.1 Les 13 specDoc PDF SPEC-13 — aucune contradiction

Chaque carte `spec<Algo>` porte `statut = PUBLIE` et une note de validation lue dans le rapport réel `validation_<slug>_v1.md`. Vérification croisée :

| Algorithme | Note carte (validation) | Rapport disque (verdict réel) | Cohérent |
|---|---|---|---|
| energy_aware | CONFORME — 20/20 | CONFORME 20/20 | oui |
| event_triggered_comm | CONFORME — 17/20 | CONFORME 17/20 | oui |
| health_monitoring | CONFORME — 20/20 | CONFORME 20/20 | oui |
| jamming_resilient_mode | CONFORME — 20/20 | CONFORME 20/20 | oui |
| safety_rules | CONFORME — 17/20 | CONFORME 17/20 | oui |
| leader_election | RENFORCEE v2 (v1 15/20 SOUS RESERVE) | 15/20 PUBLIABLE SOUS RESERVE (v1) | oui |
| nav_gnss_degrade | RENFORCEE v2 (v1 14/20 SOUS RESERVE) | 14/20 PUBLIABLE SOUS RESERVE (v1) | oui |
| collision_avoidance | PUBLIEE — conforme (SPEC-13-PUBLISH) | CONFORME 19/20 | oui |
| cooperative_localization | PUBLIEE — conforme | CONFORME 20/20 | oui |
| formation_control | PUBLIEE — conforme | CONFORME 20/20 | oui |
| path_planning | PUBLIEE — conforme | CONFORME 20/20 | oui |
| perception_fusion | PUBLIEE — conforme | CONFORME 20/20 | oui |
| fault_tolerant_control_alloc | PUBLIEE — conforme | APPROVED for integration review (template différent, sans /20) | oui (aucune note inventée) |

Conclusion : **aucune contradiction statut/validation**. Les 6 cartes « PUBLIEE conforme » (lot SPEC-13-PUBLISH) ne citent pas de score, mais celui-ci est 19-20/20 CONFORME sur disque — non contradictoire. `fault_tolerant_control_alloc` suit un template de validation différent (pas de verdict /20) ; sa carte ne cite aucun score inventé.

### 1.2 Les 2 specDoc « implémentés » (cycle de vie distinct)

- `specTaskAllocation` : `statut = DISPONIBLE`, sans champ `validation`, 4 versions (v1.1→v4), PDF servis sur likec4.breizh.ai.
- `specConsensus` : `statut = DISPONIBLE`, sans champ `validation`, 5 versions (v1.0→v5.0), note réelle v5 = 19,1/20 PUBLIABLE SANS RESERVE portée dans la description.

Ces deux cartes suivent un cycle de vie multi-versions distinct du lot SPEC-13. `statut DISPONIBLE` ≠ PUBLIE est cohérent avec leur mode de publication (hébergement likec4.breizh.ai, pas de PDF unique dans specification/). Aucune note inventée.

### 1.3 Contradiction détectée et CORRIGÉE : champ `repository`

13 cartes `algorithm` portaient `repository 'TBD'` alors que leur carte `sourceCode` liée (`-[implements]->`) a un dépôt Rust réel et public (`dagornc/alg-<slug>`, statut PUBLIE). Seuls `algTaskAllocation` et `algConsensus` (implémentés) portaient le bon URL. **Correction mécanique appliquée** : les 13 `repository 'TBD'` pointent désormais vers le dépôt réel (`algorithms.c4` ×9, `e20-audit-completeness.c4` ×4).

| Algorithme | repository corrigé |
|---|---|
| algFormationControl | https://github.com/dagornc/alg-formation-control |
| algLeaderElection | https://github.com/dagornc/alg-leader-election |
| algPerceptionFusion | https://github.com/dagornc/alg-perception-fusion |
| algNavigationGNSSDegrade | https://github.com/dagornc/alg-nav-gnss-degrade |
| algCollisionAvoidance | https://github.com/dagornc/alg-collision-avoidance |
| algSafetyRules | https://github.com/dagornc/alg-safety-rules |
| algPathPlanning | https://github.com/dagornc/alg-path-planning |
| algHealthMonitoring | https://github.com/dagornc/alg-health-monitoring |
| algEnergyAware | https://github.com/dagornc/alg-energy-aware |
| algEventTriggeredComm | https://github.com/dagornc/alg-event-triggered-comm |
| algCooperativeLocalization | https://github.com/dagornc/alg-cooperative-localization |
| algFaultTolerantControlAlloc | https://github.com/dagornc/alg-fault-tolerant-control-alloc |
| algJammingResilientMode | https://github.com/dagornc/alg-jamming-resilient-mode |

## 2. Intégrité des liens

206 URLs uniques extraites du modèle. Résultat brut (`curl -L`, UA navigateur) :

| Hôte | Total | 200 | 202 | 403 | 404 | 429 | 000 |
|---|---|---|---|---|---|---|---|
| aast.edu | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| acrs-aars.org | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| apl.uw.edu | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| arxiv.org | 35 | 35 | 0 | 0 | 0 | 0 | 0 |
| csc.ucdavis.edu | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| docs.px4.io | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| doi.org | 87 | 42 | 13 | 30 | 2 | 0 | 0 |
| github.com | 45 | 17 | 0 | 0 | 21 | 7 | 0 |
| holybro.com | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| ink.library.smu.edu.sg | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| likec4.breizh.ai | 10 | 10 | 0 | 0 | 0 | 0 | 0 |
| maritimerobotics.ams3.digitaloceanspaces.com | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| ojs.aaai.org | 2 | 2 | 0 | 0 | 0 | 0 | 0 |
| pmc.ncbi.nlm.nih.gov | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| proceedings.neurips.cc | 2 | 2 | 0 | 0 | 0 | 0 | 0 |
| www.ccom.unh.edu | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| www.edgetech.com | 1 | 0 | 0 | 1 | 0 | 0 | 0 |
| www.exail.com | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| www.ifaamas.org | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| www.kongsberg.com | 4 | 4 | 0 | 0 | 0 | 0 | 0 |
| www.mdpi.com | 2 | 0 | 0 | 2 | 0 | 0 | 0 |
| www.scitepress.org | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| www.sintrones.com | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| www.techscience.com | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| www.usenix.org | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| www.youtube.com | 1 | 0 | 0 | 0 | 0 | 1 | 0 |
| yadda.icm.edu.pl | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| **Total** | **206** | **128** | **13** | **33** | **23** | **8** | **1** |

### 2.1 PROBLÈME MAJEUR — 28 liens GitHub pointent vers un dépôt privé/inexistant

**`github.com/dagornc/swarmdrones-likec4` n'est pas accessible publiquement** : `https://github.com/dagornc/swarmdrones-likec4` → 404, `api.github.com/repos/dagornc/swarmdrones-likec4` → 404, et il est absent de la liste des 42 dépôts publics de `dagornc`. Le dépôt est donc PRIVÉ ou n'existe pas sous ce nom.

Conséquence : les **28 URLs `blob/master/...`** du modèle (13 PDF de spec + 15 fichiers SysML) renvoient **404** pour tout lecteur non authentifié. Les **17 dépôts `alg-*` + `SwarmDrones` répondent 200** (publics) — le problème est circonscrit au dépôt du modèle lui-même.

**Tous ces artefacts sont pourtant servis en 200 sur likec4.breizh.ai** (vérifié : 13/13 PDF + 15/15 SysML).

**Correction requise (décision humaine, non appliquée ici)** : soit (a) rendre le dépôt `swarmdrones-likec4` public, soit (b) rebrancher les 28 liens sur `https://likec4.breizh.ai/<fichier>` (fonctionne aujourd'hui), soit (c) déplacer le modèle dans un dépôt public existant. Je n'ai pas l'autorité ni les credentials pour trancher.

Liste des 28 URLs mortes :

| Type | Fichier |
|---|---|
| specification | specification/Spec_ALG_COLLISION_AVOIDANCE_v1.pdf |
| specification | specification/Spec_ALG_COOPERATIVE_LOCALIZATION_v1.pdf |
| specification | specification/Spec_ALG_ENERGY_AWARE_v1.pdf |
| specification | specification/Spec_ALG_EVENT_TRIGGERED_COMM_v1.pdf |
| specification | specification/Spec_ALG_FAULT_TOLERANT_CONTROL_ALLOC_v1.pdf |
| specification | specification/Spec_ALG_FORMATION_CONTROL_v1.pdf |
| specification | specification/Spec_ALG_HEALTH_MONITORING_v1.pdf |
| specification | specification/Spec_ALG_JAMMING_RESILIENT_MODE_v1.pdf |
| specification | specification/Spec_ALG_LEADER_ELECTION_v2.pdf |
| specification | specification/Spec_ALG_NAV_GNSS_DEGRADE_v2.pdf |
| specification | specification/Spec_ALG_PATH_PLANNING_v1.pdf |
| specification | specification/Spec_ALG_PERCEPTION_FUSION_v1.pdf |
| specification | specification/Spec_ALG_SAFETY_RULES_v1.pdf |
| sysml | sysml/ALG_COLLISION_AVOIDANCE.sysml |
| sysml | sysml/ALG_CONSENSUS.sysml |
| sysml | sysml/ALG_COOPERATIVE_LOCALIZATION.sysml |
| sysml | sysml/ALG_ENERGY_AWARE.sysml |
| sysml | sysml/ALG_EVENT_TRIGGERED_COMM.sysml |
| sysml | sysml/ALG_FAULT_TOLERANT_CONTROL_ALLOC.sysml |
| sysml | sysml/ALG_FORMATION_CONTROL.sysml |
| sysml | sysml/ALG_HEALTH_MONITORING.sysml |
| sysml | sysml/ALG_JAMMING_RESILIENT_MODE.sysml |
| sysml | sysml/ALG_LEADER_ELECTION.sysml |
| sysml | sysml/ALG_NAV_GNSS_DEGRADE.sysml |
| sysml | sysml/ALG_PATH_PLANNING.sysml |
| sysml | sysml/ALG_PERCEPTION_FUSION.sysml |
| sysml | sysml/ALG_SAFETY_RULES.sysml |
| sysml | sysml/ALG_TASK_ALLOCATION.sysml |

### 2.2 2 DOI morts (404)

| DOI | Carte référente |
|---|---|
| https://doi.org/10.1109/LRA.2022.3145678 | srcCBFSwarm (rattaché à sciSafetyRules) |
| https://doi.org/10.22541/au.172457058.83855084 | srcHeteroRetrieval (source ORPHELINE) |

### 2.3 Codes non concluants (à interpréter avec prudence, PAS des liens morts)

- **30 DOI → 403** (MDPI, Wiley, ACM, SAGE, Preprints.org) : mur anti-bot Cloudflare — le DOI est probablement valide mais non vérifiable par robot.
- **13 DOI IEEE → 202** : résolution correcte vers `ieeexplore.ieee.org/document/…` (les DOI IEEE renvoient 202 au bot, la page document existe).
- **1 apl.uw.edu → 000** (timeout) ; **1 youtube.com → 429** (rate-limit) : à re-vérifier manuellement.

## 3. Couverture des 15 algorithmes × 3 artefacts

| # | Algorithme | Spec PDF | SysML v2 | Rust (dagornc/alg-*) |
|---|---|---|---|---|
| algTaskAllocation | likec4.breizh.ai (v1.1-v4) | ALG_TASK_ALLOCATION.sysml | alg-task-allocation (200) |
| algConsensus | likec4.breizh.ai (v1-v5) | ALG_CONSENSUS.sysml | alg-consensus (200) |
| algFormationControl | Spec_ALG_FORMATION_CONTROL_v1.pdf | ALG_FORMATION_CONTROL.sysml | alg-formation-control (200) |
| algLeaderElection | Spec_ALG_LEADER_ELECTION_v2.pdf | ALG_LEADER_ELECTION.sysml | alg-leader-election (200) |
| algPerceptionFusion | Spec_ALG_PERCEPTION_FUSION_v1.pdf | ALG_PERCEPTION_FUSION.sysml | alg-perception-fusion (200) |
| algNavigationGNSSDegrade | Spec_ALG_NAV_GNSS_DEGRADE_v2.pdf | ALG_NAV_GNSS_DEGRADE.sysml | alg-nav-gnss-degrade (200) |
| algCollisionAvoidance | Spec_ALG_COLLISION_AVOIDANCE_v1.pdf | ALG_COLLISION_AVOIDANCE.sysml | alg-collision-avoidance (200) |
| algSafetyRules | Spec_ALG_SAFETY_RULES_v1.pdf | ALG_SAFETY_RULES.sysml | alg-safety-rules (200) |
| algPathPlanning | Spec_ALG_PATH_PLANNING_v1.pdf | ALG_PATH_PLANNING.sysml | alg-path-planning (200) |
| algHealthMonitoring | Spec_ALG_HEALTH_MONITORING_v1.pdf | ALG_HEALTH_MONITORING.sysml | alg-health-monitoring (200) |
| algEnergyAware | Spec_ALG_ENERGY_AWARE_v1.pdf | ALG_ENERGY_AWARE.sysml | alg-energy-aware (200) |
| algEventTriggeredComm | Spec_ALG_EVENT_TRIGGERED_COMM_v1.pdf | ALG_EVENT_TRIGGERED_COMM.sysml | alg-event-triggered-comm (200) |
| algCooperativeLocalization | Spec_ALG_COOPERATIVE_LOCALIZATION_v1.pdf | ALG_COOPERATIVE_LOCALIZATION.sysml | alg-cooperative-localization (200) |
| algFaultTolerantControlAlloc | Spec_ALG_FAULT_TOLERANT_CONTROL_ALLOC_v1.pdf | ALG_FAULT_TOLERANT_CONTROL_ALLOC.sysml | alg-fault-tolerant-control-alloc (200) |
| algJammingResilientMode | Spec_ALG_JAMMING_RESILIENT_MODE_v1.pdf | ALG_JAMMING_RESILIENT_MODE.sysml | alg-jamming-resilient-mode (200) |

**15/15 algorithmes complets** sur les 3 artefacts. Dépôt supplémentaire hors périmètre des 15 : `alg-protocole` (H-Zip) = statut CIBLE (dépôt à créer).

## 4. Orphelins et liens morts

### 4.1 11 sources scientifiques (specDoc) jamais référencées par aucune relation

`srcAPFWall`, `srcAUVFaultDiag`, `srcCBFMultiFixed`, `srcCoverageCentral`, `srcCrossDomainASW`, `srcDigitalTwinZEST`, `srcExplainableMARL`, `srcFormationRL`, `srcHMARLCBF`, `srcHeteroRetrieval`, `srcSwarmUSV` (toutes dans `science.c4`).

Ces 11 sources sont déclarées mais non rattachées à un algorithme (le rattachement scientifique t_4f8a3ca4 en a laissé 11 non utilisées). Décision de rattachement ou de suppression à arbitrer — je ne les rattache pas d'autorité. Note : `srcHeteroRetrieval` porte en plus un DOI mort (voir 2.2).

### 4.2 Liens vers des éléments inexistants

**Aucun** : `likec4 validate` ✓ + 0 dangling dans le graphe exporté (771 relations toutes résolues). Le « dangling » `views.c4:1059` signalé par un auditeur antérieur est un faux positif (texte dans une `description` triple-quoted, pas une relation).

## 5. Points non résolus (avec justification)

1. **28 liens GitHub vers dépôt privé/inexistant `swarmdrones-likec4`** → décision de Christophe requise (rendre public / rebrancher sur likec4.breizh.ai / déplacer). Non corrigé : acte d'infrastructure + credentials que je n'ai pas.
2. **2 DOI morts** (10.1109/LRA.2022.3145678, 10.22541/au.172457058.83855084) → recherche d'un DOI de remplacement requise. Non corrigé : interdiction d'inventer une source.
3. **11 sources scientifiques orphelines** → arbitrage rattachement/suppression. Non corrigé : décision de contenu.
4. **Publication (git push)** → bloqué : aucune credential GitHub dans cette session (`gh` non authentifié, pas de clé SSH, pas de GH_TOKEN). Le commit de correction est prêt localement mais n'a pas pu être poussé.

## 6. Corrections appliquées dans ce run

- `algorithms.c4` : 9 `repository 'TBD'` → URL réel du dépôt Rust.
- `e20-audit-completeness.c4` : 4 `repository 'TBD'` → URL réel du dépôt Rust.
- `likec4 validate` re-passé ✓ Valid (20 files) après correction.

## 7. Annexes

- Résultats bruts des 206 URLs : `/tmp/lc_url_results.tsv` (copie attachée au run).
- Graphe résolu : `likec4.json` exporté depuis le clone propre (`likec4 export json`).