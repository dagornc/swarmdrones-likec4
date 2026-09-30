# Rapport de rattachement des 16 sources fondatrices aux algorithmes canoniques

- Généré le : 2026-09-30 (UTC)
- Carte : t_742d39d4 (Carte C — rattachement)
- Dépend de : t_7e2b6f14 (Carte A — ingestion corpus)
- Corpus : /home/hermesagent/swarmdrone-research/catalog.json (entrées 2434..2449)
- Blocs proposés : tools/pending_promotion/rattachement_fondatrices.c4 (SCI-61..71, NON insérés)
- science.c4 : NON modifié (md5 identique avant/après, cf. §5)

## Verdict global

16 sources → 5 déjà rattachées (aucun bloc, documentées) + 11 rattachées ici (SCI-61..71) + 0 écartée.

Sur les 11 rattachées : 8 référencent des éléments `scientificPaper` (paperXXX) déjà déclarés dans hzip.c4, 3 reçoivent un nouveau `specDoc` (aucun élément n'existait).

## Tableau de décision

| # | Source | Algorithme(s) proposé(s) | Décision | Confiance | Preuve lue |
|---|--------|--------------------------|----------|-----------|------------|
| 2434 | SwarmRaft (2508.00622) | algNavigationGNSSDegrade | DÉJÀ RATTACHÉE — SCI-5 (sciGnssDegraded, e20.c4). Consensus couvert par le lien direct de algConsensus + spec ALG_LEADER_ELECTION | HAUTE | PDF intégral |
| 2435 | Perception-Aware (2603.08379) | algCollisionAvoidance, algSafetyRules | DÉJÀ RATTACHÉE — SCI-40 (sciCommFreeCoord) | HAUTE | PDF intégral |
| 2436 | LiDAR DRL (2601.13657) | algNavigationGNSSDegrade, algFormationControl, algCollisionAvoidance | RATTACHÉE — SCI-61 (nouveau srcLiDARDRLNav) | HAUTE | PDF intégral |
| 2437 | SLAM nano-drones (2309.03678) | algNavigationGNSSDegrade, algPerceptionFusion | DÉJÀ RATTACHÉE — SCI-46 (sciOnboardSLAMNano) | HAUTE | PDF intégral |
| 2438 | Formation retardée (978-981-19-6613) | algFormationControl | RATTACHÉE — SCI-62 (nouveau srcDelayFeedbackForm) | BASSE | Métadonnées Crossref (pas d'abstract) |
| 2439 | IDS fédéré (2607.17025) | algJammingResilientMode | RATTACHÉE — SCI-63 (nouveau srcFederatedIDS) | HAUTE | PDF intégral |
| 2440 | Khatib 1986 | algCollisionAvoidance, algPathPlanning | RATTACHÉE — SCI-64 (paperKhatib1986) | MOYENNE-HAUTE | Abstract Crossref |
| 2441 | Kennedy & Eberhart 1995 (PSO) | algTaskAllocation, algPathPlanning | RATTACHÉE — SCI-65 (paperKennedy1995) | MOYENNE | Métadonnées Crossref (pas d'abstract) + hzip.c4 |
| 2442 | Dimarogonas 2012 | algEventTriggeredComm | RATTACHÉE — SCI-66 (paperDimarogonas2012) | HAUTE | Métadonnées Crossref + hzip.c4 |
| 2443 | Tseng 2002 | algEventTriggeredComm | RATTACHÉE — SCI-67 (paperTseng2002) | MOYENNE-HAUTE | Métadonnées Crossref + hzip.c4 |
| 2444 | Akyildiz 2005 | algEventTriggeredComm (transfert) | RATTACHÉE AVEC RÉSERVE — SCI-68 (paperAkyildiz2005) | BASSE | Métadonnées Crossref + hzip.c4 |
| 2445 | Olfati-Saber 2007 | algConsensus, algFormationControl | RATTACHÉE — SCI-69 (paperOlfatiSaber2007) | HAUTE | Métadonnées Crossref + hzip.c4 |
| 2446 | Hu & Yan 2007 | algConsensus | RATTACHÉE — SCI-70 (paperHuYan2007) | MOYENNE | Métadonnées Crossref + hzip.c4 |
| 2447 | Reynolds 1987 | algFormationControl, algCollisionAvoidance | RATTACHÉE — SCI-71 (paperReynolds1987) | MOYENNE-HAUTE | Abstract Crossref |
| 2448 | Couverture central/décentral (2408.06553) | algFormationControl, algTaskAllocation | DÉJÀ RATTACHÉE — SCI-20 (sciCentralVsDecentral) | HAUTE | PDF intégral |
| 2449 | APF hybride wall-follower (2409.10332) | algCollisionAvoidance | DÉJÀ RATTACHÉE — SCI-17 (sciApfWallFollower) | HAUTE | PDF intégral |

## Justifications détaillées

### Déjà rattachées (aucun bloc — constat)

- **2434 SwarmRaft** : déjà liée par le patron 2 sauts via SCI-5 `sciGnssDegraded -[uses]-> srcSwarmRaft -[evidences]-> algNavigationGNSSDegrade` (e20-audit-completeness.c4). La dimension consensus est couverte par le lien direct de `algConsensus` (algorithms.c4:78) et par la spec ALG_LEADER_ELECTION v2. L'hypothèse « SwarmRaft → algConsensus » est donc satisfaite par un chemin existant, pas par un bloc nouveau. Aucune duplication créée.
- **2435 Perception-Aware** : SCI-40 `sciCommFreeCoord` → algCollisionAvoidance + algSafetyRules. Hypothèse confirmée par la lecture (LiDAR anisotrope 3D, coordination sans communication, réel CTU Prague).
- **2437 SLAM nano-drones** : SCI-46 `sciOnboardSLAMNano` → algNavigationGNSSDegrade + algPerceptionFusion. Confirmé par l'abstract (SLAM embarqué 192 kB, mapping distribué, 4 nano-UAV réels).
- **2448 Couverture** : SCI-20 `sciCentralVsDecentral` → algFormationControl + algTaskAllocation. Confirmé (comparaison empirique centralisé/décentralisé, UAV superviseurs).
- **2449 APF+WF** : SCI-17 `sciApfWallFollower` → algCollisionAvoidance. Confirmé (APF hybride + suivi de mur anti-minima).

### Rattachements proposés (SCI-61..71)

- **SCI-61 (2436, LiDAR DRL)** — l'abstract/Pdf démontre une navigation collective SANS communication ET SANS GNSS (leader-follower implicite, LiDAR + EKF, 5 UAV réels) : preuve directe pour algNavigationGNSSDegrade, avec flocking (algFormationControl) et évitement appris (algCollisionAvoidance). Confiance HAUTE ; limite : échelle 5 UAV vs N=30.
- **SCI-62 (2438, formation retardée)** — chapitre Springer, pas d'abstract Crossref. Le rattachement à algFormationControl repose sur le titre + la citation modele (architecture.c4 autopilot), d'où verdict CONDITIONAL et confiance BASSE. À confirmer par lecture du chapitre.
- **SCI-63 (2439, IDS fédéré)** — IDS par apprentissage fédéré léger (knowledge distillation), Raspberry Pi 4 + dataset drone réel, 98,6 %. Front-end de détection cyber alimentant algJammingResilientMode. Confiance HAUTE.
- **SCI-64 (2440, Khatib)** — APF temps réel pour l'évitement d'obstacles (abstract Crossref complet) : algCollisionAvoidance (évitement réactif) + algPathPlanning (APF distribué entre niveaux de contrôle). Confiance MOYENNE-HAUTE.
- **SCI-65 (2441, PSO)** — métaheuristique générique ; algTaskAllocation + algPathPlanning comme optimiseurs alternatifs. Confiance MOYENNE (pas d'abstract Crossref ; hzip.c4 route déjà PSO vers la couche stratégique — cf. divergence ci-dessous).
- **SCI-66 (2442, Dimarogonas)** — contrôle événementiel distribué (seuil, borne Zeno) : fondement direct de algEventTriggeredComm. Confiance HAUTE.
- **SCI-67 (2443, Tseng)** — tempête de broadcast : justification NÉGATIVE de algEventTriggeredComm (ne pas inonder le canal). Confiance MOYENNE-HAUTE.
- **SCI-68 (2444, Akyildiz)** — contrainte de débit acoustique extrême → communication parcimonieuse = algEventTriggeredComm par TRANSFERT MÉTHODOLOGIQUE. Verdict CONDITIONAL/TRANSFERT, confiance BASSE. **Divergence assumée** : l'hypothèse « algCooperativeLocalization » est ÉCARTÉE — la source (survey de défis) ne fournit aucun mécanisme de localisation coopérative. Christophe peut également choisir d'écarter la source entière (flag transfer-candidate du corpus).
- **SCI-69 (2445, Olfati-Saber)** — cadre unifié consensus + flocking en réseau : algConsensus (primaire) + algFormationControl. Confiance HAUTE.
- **SCI-70 (2446, Hu & Yan)** — robustesse de stabilité sous pertes de paquets : borne de perte admissible pour algConsensus en lien intermittent. Confiance MOYENNE (résultat NCS générique).
- **SCI-71 (2447, Reynolds)** — boids (séparation/alignement/cohésion) : algFormationControl (flocking) + algCollisionAvoidance (règle de séparation). Confiance MOYENNE-HAUTE.

## Divergences avec les hypothèses de départ

1. **Akyildiz 2005** : l'hypothèse « algEventTriggeredComm + algCooperativeLocalization » est ramenée à algEventTriggeredComm seul ; algCooperativeLocalization écarté (aucun mécanisme dans la source).
2. **SwarmRaft** : l'hypothèse « algConsensus + algNavigationGNSSDegrade » est satisfaite sans bloc nouveau (SCI-5 pour la navigation + lien direct algConsensus existant). Pas de bloc SCI créé pour éviter un doublon.
3. **Olfati-Saber** : ajout de algFormationControl en plus de algConsensus (le papier couvre explicitement flocking/rendez-vous par consensus).
4. **PSO** : maintenu algTaskAllocation + algPathPlanning (hypothèse), mais signalé que hzip.c4 route déjà PSO vers algFormationControl/algConsensus via la couche stratégique — à arbitrer par Christophe si un seul chemin doit être retenu.

## Vérifications effectuées

1. **Algorithmes cibles existants** — les 15 `alg*` canoniques vérifiés présents : algTaskAllocation, algConsensus, algFormationControl, algLeaderElection, algPerceptionFusion, algNavigationGNSSDegrade, algCollisionAvoidance, algSafetyRules, algPathPlanning, algHealthMonitoring, algEnergyAware (algorithms.c4) ; algEventTriggeredComm, algCooperativeLocalization, algFaultTolerantControlAlloc, algJammingResilientMode (e20-audit-completeness.c4).
2. **Éléments source référencés** — les 8 `paperXXX` existent dans hzip.c4 (noms exacts vérifiés) ; les 3 nouveaux `srcXXX` sont déclarés dans le fichier de blocs.
3. **Syntaxe/sémantique LikeC4** — `likec4 validate` (image 1.59.2) sur le modèle complet + blocs proposés : **✓ Valid (21 fichiers, 0 erreur)**. Les 33 relations (evidences/uses) résolvent vers des éléments existants.
4. **Numérotation SCI** — SCI-61..71 sans collision (SCI-60 est le max actuel, cf. tools/pending_promotion/README.md).
5. **science.c4 non modifié** — md5 avant = après (cf. §5).

## Fichiers produits

- tools/pending_promotion/rattachement_fondatrices.c4 — 3 specDoc + 11 sciFinding (SCI-61..71) + 33 relations, au format exact des blocs existants (référence SCI-56..60 / pending_lot01_additions.c4). À INSÉRER dans le bloc `model { }` de science.c4, uniquement après validation de Christophe.
- tools/pending_promotion/rapport_rattachement_fondatrices.md — ce rapport.

## Décision attendue de Christophe

- Valider l'insertion des blocs SCI-61..71 dans science.c4 (étape séparée, hors carte C).
- Arbitrer SCI-65 (PSO : garder les deux chemins ou un seul) et SCI-68 (Akyildiz : transfert conditionnel ou écarter).
