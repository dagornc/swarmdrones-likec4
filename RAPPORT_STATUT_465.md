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
| 3   | 25       | 4 findings | 4 | 17 | SCI-36..39 |
| 4   | 25       | 2 findings | 2 | 21 | SCI-40..41 |
| 5   | 25       | 3 findings | 2 | 20 | SCI-42..44 |

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

---

## LOT 3 (2026-09-29)

### RATTACHEE (nouveaux verdicts)
| # | Titre | Alg(s) | specDoc | Finding |
|---|-------|--------|---------|---------|
| 309 | Feasibility-Enhanced CBF (FECBF) multi-UAV collision avoidance | algCollisionAvoidance + algSafetyRules | srcFECBF | SCI-36 |
| 594 | TriSAR task coordination + collision avoidance (5 UAV) | algTaskAllocation + algCollisionAvoidance | srcTriSAR | SCI-37 |
| 2293 | Robust multi-objective UAV routing (Peukert battery) | algEnergyAware + algPathPlanning | srcPeukertRouting | SCI-38 |
| 2306 | Energy-conserving swarm formation (Hamiltonian + RK) | algFormationControl + algEnergyAware | srcHamiltonianFormation | SCI-39 |

### DEJA_RATTACHEE
| # | Titre | specDoc existant | Finding existant |
|---|-------|------------------|------------------|
| 138 | CBF multi-fixed-wing pursuit | srcCBFMultiFixed | SCI-16 |
| 147 | Multi-UAV formation RL | srcFormationRL | SCI-18 |
| 917 | Multi-UAV formation RL (doublon de #147) | srcFormationRL | SCI-18 |
| 221 | UUV cooperative autonomy survey | srcUUV | SCI-4 |

### ECARTEE (17)
| # | Titre | Raison |
|---|-------|--------|
| 2030 | Mission-critical ISAC + WPT | pas-algorithme-canonique — ISAC / transfert d'énergie sans fil |
| 2154 | D2D aerial-ground networks | pas-algorithme-canonique — D2D cellulaire |
| 2200 | EH-SWADS agricultural WSN | hors-perimetre — WSN agricole |
| 2276 | AUV battery temperature (LSTNet) | hors-perimetre — batterie AUV |
| 383 | Graph-attention MARL safe separation | paradigme-exclu — politique MARL apprise |
| 378 | Hybrid APF + ST-Transformer AUV path planning | hors-perimetre — AUV sous-marins |
| 964 | Tether-aware avoidance USV-HROV | hors-perimetre — HROV sous-marin remorqué |
| 1439 | Obstacle avoidance 3 range sensors (PPO) | paradigme-exclu — politique DRL apprise |
| 1817 | Lyapunov trajectory UAV relay (EET) | deja-couvert — APF déjà couvert SCI-14/srcVAPF |
| 1828 | Multi-sensor fusion obstacle avoidance | non-verifiable — résumé non vérifié par l'éditeur |
| 2087 | Paying for Space (VCG incentive) | paradigme-exclu — mécanisme d'incitation économique |
| 2262 | Paying for Space (DOI, doublon #2087) | doublon |
| 2251 | MATLAB-Simulink benchmark framework | non-primaire — framework de benchmark |
| 380 | MADRL end-to-end formation | deja-couvert — formation RL couverte SCI-18 |
| 914 | GCBF+ neural graph CBF | paradigme-exclu — certificat CBF appris par GNN |
| 916 | End-to-end DRL swarm collision avoidance | paradigme-exclu — politique DRL apprise |
| 919 | FECBF (doublon de #309) | doublon |

## Validation lot 3
- `likec4 validate` sur clone propre `/tmp/lc_v7` : ✓ Valid (20 fichiers)
- 50 specDocs / 36 findings, 0 doublon, SCI jusqu'à 39


---

## LOT 4 (2026-09-29)

### RATTACHEE (nouveaux verdicts)
| # | Titre | Alg(s) | specDoc | Finding |
|---|-------|--------|---------|---------|
| 310 | Perception-aware communication-free multi-UAV coordination | algCollisionAvoidance + algSafetyRules | srcCommFreeCoord | SCI-40 |
| 625 | Distributed consensus particle filter target tracking (USV) | algConsensus + algPerceptionFusion | srcConsensusPF | SCI-41 |

### DEJA_RATTACHEE
| # | Titre | specDoc existant | Finding existant |
|---|-------|------------------|------------------|
| 961 | Heterogeneous UAV-USV formation | srcHeteroUAVUSV | SCI-11 |
| 205 | SwarmRaft consensus GNSS-degraded | srcSwarmRaft | SCI-5 |

### ECARTEE (21)
| # | Titre | Raison |
|---|-------|--------|
| 930 | i-MADSAC formation multi-target tracking | paradigme-exclu — MADRL appris |
| 1159 | Information-guided safe RL gas localization | pas-algorithme-canonique — RL appris |
| 1274 | AirAnchor aerial VLN | pas-algorithme-canonique — VLN mono-drone |
| 1803 | FALCON-MASAC MARL + CBF shield | paradigme-exclu — MARL appris |
| 2175 | Range-aided SLAM init (AUV) | hors-perimetre — AUV |
| 2206 | Fixed-time tracking multi-AUV | hors-perimetre — AUV |
| 2258 | Coverage path planning AUV | hors-perimetre — AUV |
| 225 | Scaling swarm coordination GNNs | paradigme-exclu — GNN appris |
| 228 | Clustered consensus bundle (CBBA) | deja-couvert — CBBA SCI-1 |
| 279 | Load-aware adaptive CBBA | deja-couvert — CBBA SCI-1 |
| 954 | Hierarchical optimal consensus path planning | non-verifiable |
| 935 | Agricultural CPS multi-robot | hors-perimetre — agriculture |
| 945 | Semantic control manifolds LLM | pas-algorithme-canonique — LLM appris |
| 971 | SoC-embedded GNN task allocation | paradigme-exclu — GNN appris |
| 997 | T-CARE temporal coordination RL | paradigme-exclu — RL appris |
| 998 | Large-scale swarm coordination survey | non-primaire — survey |
| 1009 | ATAC k-truss agentic AI | pas-algorithme-canonique — framework IA |
| 1015 | Swarm UAV control strategies (chapter) | non-primaire — chapitre de livre |
| 2290 | Internet of Sentience TGA (chapter) | non-primaire — chapitre |
| 79 | Centralized task allocation constraint table | paradigme-exclu — allocation centralisee |
| 104 | Multi-task trajectory prediction | pas-algorithme-canonique — prediction apprise |

## Validation lot 4
- `likec4 validate` sur clone propre `/tmp/lc_v7` : ✓ Valid (20 fichiers)
- SCI jusqu'a 41


---

## LOT 5 (2026-09-29)

### RATTACHEE (nouveaux verdicts)
| # | Titre | Alg(s) | specDoc | Finding |
|---|-------|--------|---------|---------|
| 211 | Event-Driven CBBA (reduced communication) | algTaskAllocation + algEventTriggeredComm | srcEventDrivenCBBA | SCI-42 |
| 1590 | CC-OPI online distributed task allocation under comm constraints | algTaskAllocation | srcCCOPI | SCI-43 |
| 2278 | Assignment-Preserving Replanning (APR) | algTaskAllocation | srcAPR | SCI-44 |

### DEJA_RATTACHEE
| # | Titre | specDoc existant | Finding existant |
|---|-------|------------------|------------------|
| 200 | Vortex APF local minima | srcVAPF | SCI-14 |
| 311 | ImpedanceDiffusion path planning | srcImpedanceDiffusion | SCI-14 |

### ECARTEE (20)
| # | Titre | Raison |
|---|-------|--------|
| 937 | Multi-threaded best-first search allocation | non-verifiable |
| 943 | Allocation collaborative + precedence | non-verifiable |
| 956 | Coalition auction ISAC | pas-algorithme-canonique — ISAC |
| 957 | UAV crowd counting (media) | pas-algorithme-canonique — comptage de foule |
| 959 | Homogeneous vs heterogeneous allocation | non-verifiable (facteurs humains) |
| 1010 | Survival-probability clustering allocation | non-verifiable |
| 1029 | Chaos + adaptive GA allocation | non-verifiable |
| 1032 | ViTDrone explainable ViT steering | paradigme-exclu — perception apprise ViT |
| 1040 | Helicopter rescue NSGA-II scheduling | hors-perimetre — hélicoptères |
| 1757 | AgenticSwarm semantic allocation | pas-algorithme-canonique — framework LLM |
| 1797 | DPP-GCMARL patrol MEC | paradigme-exclu — MARL + MEC |
| 1800 | Marine UAV task assignment (metaheuristiques) | deja-couvert — SCI-1/SCI-14 |
| 2115 | FlockDiffusion diffusion allocation | paradigme-exclu — diffusion apprise |
| 2192 | CC-OPI (doublon #1590) | doublon |
| 2263 | FlockDiffusion (doublon #2115) | doublon |
| 2289 | Pattern-aware assignment multi-AUV | hors-perimetre — AUV |
| 912 | Trajectory + resource MEC (MADRL) | paradigme-exclu — MADRL + MEC |
| 931 | USV path planning A*+DWA | deja-couvert — SCI-14 |
| 947 | Amphibious UAV simultaneous arrival (PSO) | deja-couvert — SCI-14 |
| 977 | MSGSO 3D path planning | deja-couvert — SCI-14 |

## Validation lot 5
- `likec4 validate` sur clone propre `/tmp/lc_v7` : ✓ Valid (20 fichiers)
- SCI jusqu'a 44
