# RAPPORT — Statut des 465 articles « direct + A-primary-candidate » (carte t_3f3134cc)

Campagne d'arbitrage du corpus de veille : 465 articles `scope.level == "direct"` ET `trust == "A-primary-candidate"`.
Chaque article reçoit un statut explicite et traçable : `RATTACHEE` (specDoc + finding + evidences) ou `ECARTEE` (raison documentée), ou `DEJA_RATTACHEE` (déjà statué par une carte antérieure).

- Patron 2 sauts : `srcXXX -[uses]<- sciFinding -[evidences]-> algYYY`
- Un lot = 25 articles = 1 commit science.c4 + mise à jour de ce rapport.
- Numérotation des findings : suite de SCI-23 (existant), donc SCI-24, SCI-25, ...
- Sources déjà présentes (audit e20-audit-completeness.c4, science.c4) : réutilisées, jamais dupliquées.

## Vocabulaire des verdicts ECARTEE
- `hors-perimetre` : domaine hors flotte SWARM-3D (sous-marin, maritime non-essaim, non-UAV)
- `pas-algorithme-canonique` : pas un des 15 algorithmes (hardware, réseau, MEC, atterrissage…)
- `paradigme-exclu` : politique apprise / mécanisme exclu du modèle (le modèle exclut les politiques apprises)
- `non-primaire` : revue/survey/éditorial, pas une source primaire
- `deja-couvert` : famille déjà sourcée par un finding existant, pas d'apport distinct

## Avancement global
| Lot | Articles | RATTACHEE (nouveaux) | DEJA_RATTACHEE | ECARTEE | SCI créés |
|-----|----------|----------------------|----------------|---------|-----------|
| 1   | 25       | 9 (8 findings + 1 complétion SCI-8) | 5 | 11 | SCI-24..31 |
| 2   | 25       | 5 (4 findings + 1 complétion SCI-6) | 2 | 18 | SCI-32..35 |

---

## LOT 1 (2026-09-29)

### RATTACHEE (nouveaux verdicts)
| # | Titre | Alg(s) | specDoc | Finding |
|---|-------|--------|---------|---------|
| 1454 | Belief-Adaptive Online Autonomy (GNSS degradation) | algNavigationGNSSDegrade | srcBeliefAdaptiveEKF | SCI-24 |
| 1782 | Multi-UAV Adaptive Cooperative Localization | algCooperativeLocalization | srcMultiUAVCL | SCI-25 |
| 2124 | Quasi-Static FTC under Rotor Failure (provable safety) | algFaultTolerantControlAlloc + algSafetyRules | srcRotorFailQSF | SCI-26 |
| 995 | Meta policy switching under GNSS spoofing | algJammingResilientMode | srcMetaPolicySpoof | SCI-27 |
| 307 | Formation Control with CBF, switched topologies | algFormationControl + algSafetyRules | srcFormationCBF | SCI-28 |
| 357 | DMPC with Adaptive Safety Zones (multi-fleet) | algCollisionAvoidance + algPathPlanning | srcDMPCSafetyZones | SCI-29 |
| 936 | 3D-TSPN + RRT multi-UAV trajectory planning | algPathPlanning | srcTrajMECDisaster | SCI-30 |
| 1528 | Escape-Aware CBF under body-rate limits | algSafetyRules + algCollisionAvoidance | srcEscapeCBF | SCI-31 |
| 965 | Multi-USV formation FTC (actuator faults) | algFormationControl + algFaultTolerantControlAlloc | srcUSVFormationFTC | complétion SCI-8 (specDoc ajouté, rattaché à sciFaultTolerantCtrl) |

### DEJA_RATTACHEE (déjà statués par des cartes antérieures — pas de doublon)
| # | Titre | specDoc existant | Finding existant |
|---|-------|------------------|------------------|
| 593 | Vision-Based Leader-Follower Formation (GPS-degraded) | srcVisFormGPSDeg (e20) | SCI-5 + SCI-11 |
| 284 | ST-DCL cooperative localization | srcSTDCL (e20) | SCI-7 |
| 972 | USV cooperative localization (consensus) | srcUSVCoopLoc (e20) | SCI-7 |
| 966 | FTC allocation USV (HITL) | srcFTCAllocUSV (e20) | SCI-8 |
| 929 | ADMOS (jamming resilience) | srcADMOS (e20) | SCI-9 |

### ECARTEE
| # | Titre | Raison |
|---|-------|--------|
| 614 | SeaCausal-FL maritime IoT fault diagnosis | hors-perimetre — moteurs marins, pas de drone/essaim |
| 963 | Huber UKF multi-AUV cooperative localization | hors-perimetre — AUV sous-marins, hors flotte (aérien+surface) |
| 1700 | AeRove bimodal aerial-terrestrial drone | pas-algorithme-canonique — conception mécanique mono-drone |
| 122 | SUB-PLAY adversarial policies vs MARL | paradigme-exclu — attaques adverses MARL, pas un des 15 algos |
| 991 | Task offloading multi-UAV MEC networks | pas-algorithme-canonique — allocation ressources réseau MEC/NOMA |
| 1002 | DeepMUSIC MADRL spectrum allocation | pas-algorithme-canonique — allocation spectrale |
| 1393 | HARL quad-copter landing (maritime) | pas-algorithme-canonique — atterrissage, politique apprise |
| 2183 | Anti-jamming UAV swarms: systematic review | non-primaire — revue systématique |
| 2217 | 6G base station cooperative sensing | pas-algorithme-canonique — réseautage 6G |
| 292 | High-speed vision flight, safety-shielded RL | paradigme-exclu — politique apprise + filtre CBF (cf. HMARL-CBF), mono-drone |
| 1022 | DR-TC-SLAM visual-LiDAR-inertial SLAM | deja-couvert — famille SLAM déjà sourcée par SCI-5 (srcSlamSurvey) |

## Validation lot 1
- `likec4 validate` sur clone propre `/tmp/lc_v7` : ✓ Valid (20 fichiers)
- Intégrité I-1 (référentiel) : 0 arc cassé ; I-2 (orphelins) : 0 (vérifié sur export JSON du clone)
- Intégrité active 7/7 (baseline) : TOUS OK ; cohérence interne C-4 : OK (l'accès dépôts Rust FAIL=15 est pré-existant — `gh` non authentifié, indépendant de cette carte)

---

## LOT 2 (2026-09-29)

### RATTACHEE (nouveaux verdicts)
| # | Titre | Alg(s) | specDoc | Finding |
|---|-------|--------|---------|---------|
| 1622 | Feasibility & Singularity in High-Order Safety-Critical Control (quadrotor teams) | algCollisionAvoidance + algSafetyRules | srcCBFQuadFeasibility | SCI-32 |
| 282 | Dynamic Event-Triggered UAV swarm adaptive target enclosing | algFormationControl + algEventTriggeredComm | srcTargetEnclosing | SCI-33 |
| 322 | Adaptive ET consensus QUAV formation (disturbances + state constraints) | algFormationControl + algEventTriggeredComm | srcQUAVConsensusCstr | SCI-34 |
| 371 | Dynamic ET consensus formation multi-leader (delay) | algFormationControl + algEventTriggeredComm | srcMultiLeaderDelay | SCI-35 |
| 968 | Event-triggered prescribed-time formation heterogeneous multi-USVs | algEventTriggeredComm | srcETFormUSV | complétion SCI-6 (specDoc ajouté, rattaché à sciEventTriggered) |

### DEJA_RATTACHEE
| # | Titre | specDoc existant | Finding existant |
|---|-------|------------------|------------------|
| 121 | Adaptive Event-Triggered Consensus | srcEventTrigConsensus (e20) | SCI-6 |
| 1026 | ET-PBBA event-triggered bid assignment | srcETPBBA (e20) | SCI-6 + SCI-10 |

### ECARTEE (18)
| # | Titre | Raison |
|---|-------|--------|
| 1538 | CALOS safety layer for DRL | paradigme-exclu — couche sûreté pour politique apprise |
| 1810 | XS-ABILITY nuclear multi-robot fleet | hors-perimetre — décontamination nucléaire, robots terrestres |
| 2274 | Zero Trust governance review | non-primaire — revue systématique |
| 335 | ET consensus economic dispatch microgrids | hors-perimetre — microgrids |
| 958 | Digital twin neural bandit relay selection | pas-algorithme-canonique — relais radio |
| 1355 | UAV propagation channel vegetation/lake | pas-algorithme-canonique — canal radio |
| 1512 | AeroLat latent semantic communication | pas-algorithme-canonique — comm sémantique |
| 2150 | AnalogDepth FPV depth | pas-algorithme-canonique — pipeline perception mono |
| 2180 | Observer-based ET formation multi-AUV | hors-perimetre — AUV sous-marins |
| 302 | AUV swarm energy-aware federated meta-transfer | hors-perimetre — AUV sous-marins |
| 597 | Curriculum RL energy-efficient UAV-ISAC | pas-algorithme-canonique — ISAC appris |
| 1021 | 3D user clustering MIMO-NOMA | pas-algorithme-canonique — cellulaire |
| 1044 | Energy-efficient secured UAV IoT architecture | pas-algorithme-canonique — réseau IoT |
| 1471 | Monopedal hopping quadcopter RL | pas-algorithme-canonique — locomotion mono |
| 1785 | Sensing-communication co-optimization ISAC | pas-algorithme-canonique — ISAC |
| 1786 | POGS-QMIX persistent coverage | deja-couvert — énergie/allocation déjà couverte SCI-10 |
| 1789 | RF energy harvesting FANET clustering | pas-algorithme-canonique — FANET |
| 1809 | GEMS-DQN charging scheduling | pas-algorithme-canonique — ordonnancement charge appris |

## Validation lot 2
- `likec4 validate` sur clone propre `/tmp/lc_v7` : ✓ Valid (20 fichiers)
- Intégrité I-1 : 0 arc cassé ; I-2 : 0 orphelin (export JSON du clone, 441 éléments / 832 relations)
