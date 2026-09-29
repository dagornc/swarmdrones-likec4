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
| 6   | 25       | 3 findings | 2 (1 rattachee + 1 ecartee) | 20 | SCI-45..47 |
| 7   | 25       | 0 | 3 | 22 | — |
| 8   | 25       | 1 findings | 0 | 24 | SCI-48 |
| 9   | 25       | 1 findings | 1 | 23 | SCI-49 |
| 10  | 25       | 1 findings | 0 | 24 | SCI-50 |
| 11  | 25       | 0 | 0 | 25 | — |
| 12  | 25       | 0 | 0 | 25 | — |
| 13  | 25       | 1 findings | 1 | 23 | SCI-51 |
| 14  | 25       | 1 findings | 0 | 24 | SCI-52 |
| 15  | 25       | 0 | 1 | 24 | — |
| 16  | 25       | 2 findings | 2 | 21 | SCI-53..54 |
| 17  | 25       | 0 | 0 | 25 | — |
| 18  | 25       | 1 findings | 0 | 24 | SCI-55 |
| 19  | 15       | 0 | 0 | 15 | — |

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


---

## LOT 6 (2026-09-29)

### RATTACHEE (nouveaux verdicts)
| # | Titre | Alg(s) | specDoc | Finding |
|---|-------|--------|---------|---------|
| 1796 | Risk-bounded certificate feedback allocation->path planning | algPathPlanning + algSafetyRules | srcCertFeedbackPath | SCI-45 |
| 105 | Fully onboard SLAM distributed mapping nano-drones | algNavigationGNSSDegrade + algPerceptionFusion | srcOnboardSLAMNano | SCI-46 |
| 177 | Ultra-lightweight scalable planner large aerial swarms | algPathPlanning | srcUltraLightPlanner | SCI-47 |

### DEJA
| # | Titre | specDoc existant | Statut |
|---|-------|------------------|--------|
| 996 | Comparative path planning medical UAV | srcPathMedUAV | RATTACHEE (SCI-14) |
| 134 | ZEST digital twin | srcDigitalTwinZEST | DEJA ECARTEE (statut ECARTEE) |

### ECARTEE (20)
| # | Titre | Raison |
|---|-------|--------|
| 1042 | MSCEGWO 3D trajectory | deja-couvert — SCI-14 |
| 1491 | UDAV VLM waypoint planner | pas-algorithme-canonique — VLM appris |
| 1498 | LAMDE WSN path planning | pas-algorithme-canonique — optimisation apprise |
| 1793 | UCA-PPO USV path planning | paradigme-exclu — PPO appris |
| 1801 | NSGA-II + BOA bank-to-turn | deja-couvert — SCI-14 |
| 1815 | DPC-MOEA simultaneous arrival | deja-couvert — SCI-14 |
| 1829 | NMCS Monte Carlo trajectory | deja-couvert — SCI-14 |
| 1830 | R*WOA whale + RRT* | deja-couvert — SCI-14 |
| 2279 | RL-JSO group-level path planning | paradigme-exclu — RL appris |
| 2287 | MI-PSO-Adaptive waypoint | deja-couvert — SCI-14 |
| 2294 | SA-ALNS-2OPT container yard | deja-couvert — SCI-14 |
| 89 | FANET routing protocol | pas-algorithme-canonique — routage FANET |
| 94 | Survey unmanned marine vehicles | non-primaire — survey |
| 181 | AttentionSwarm RL + CBF | paradigme-exclu — RL appris |
| 190 | Depth Transfer sim-to-real | paradigme-exclu — RL + sim2real |
| 191 | Movable antenna wireless | pas-algorithme-canonique — réseau sans fil |
| 195 | Cryptography underwater acoustic review | non-primaire — revue UUV |
| 197 | MARL coral reef collection | hors-perimetre — collecte corail MARL |
| 201 | MAPPO+BCTD target tracking | paradigme-exclu — MAPPO appris |
| 202 | RL interception prioritization | paradigme-exclu — RL appris |

## Validation lot 6
- `likec4 validate` sur clone propre `/tmp/lc_v7` : ✓ Valid (20 fichiers)
- SCI jusqu'a 47

---

## LOT 7 (2026-09-29)

### DEJA_RATTACHEE (déjà statués — pas de doublon)
| # | Titre | specDoc existant | Finding existant |
|---|-------|------------------|------------------|
| 212 | Hierarchical Reinforcement Learning with Low-Level MPC for Multi-Agent | srcHRLMPC | SCI-14 |
| 315 | Safe Swarm Navigation in Constrained Environments- A Dynamic Tube-Base | srcDMPCTube | SCI-14 |
| 356 | Diffusion-based 4D Trajectory Prediction and Distributed Control for U | srcDiff4D | SCI-14 |

### ECARTEE (22)
| # | Titre | Raison |
|---|-------|--------|
| 217 | Curriculum-Based Iterative Self-Play for Scalable Multi-Drone Racing - | paradigme-exclu — CRUISE = curriculum self-play (RL), politique apprise de course, pas un des 15 algos |
| 236 | A Comprehensive Review of Path-Planning Algorithms for Multi-UAV Swarm | non-primaire — revue complete d algorithmes de planification de chemin multi-UAV |
| 239 | MultiUAV-Plat- An LLM-Oriented Platform, Benchmark and Framework for M | paradigme-exclu — plateforme LLM (MultiUAV-Plat), orchestration par LLM |
| 240 | Autonomous Navigation at the Nano-Scale- Algorithms, Architectures, an | non-primaire — survol/tutoriel navigation nano-UAV (matériel + architectures), pas une source primaire d algorithme |
| 246 | Agentic AI Meets Edge Computing in Autonomous UAV Swarms - arXiv | paradigme-exclu — agentic AI + LLM (LangGraph) pour essaim UAV |
| 249 | Communication-Free Collective Navigation for a Swarm of UAVs via LiDAR | paradigme-exclu — navigation collective par LiDAR + DRL (politique apprise) |
| 261 | Integrated Sensing, Communication and Control enabled Agile UAV Swarm  | pas-algorithme-canonique — ISCC (sensing/communication/contrôle intégrés), couche réseau |
| 277 | DTVIRM-Swarm- A Distributed and Tightly Integrated Visual-Inertial ... | deja-couvert — famille VI-odométrie/SLAM déjà sourcée par SCI-5 (srcSlamSurvey) |
| 290 | Learning-Based Multi-Robot Active SLAM- A Conceptual Framework and Sur | non-primaire — survey/framework conceptuel de SLAM actif multi-robots |
| 291 | Curriculum Reinforcement Learning for Quadrotor Racing with Random Obs | paradigme-exclu — curriculum RL pour course de quadrirotors (politique apprise) |
| 293 | Learning Agile Quadrotor Flight in the Real World - arXiv | paradigme-exclu — vol agile appris (RL, apprentissage résiduel de dynamique) |
| 312 | A Classification of Heterogeneity in Uncrewed Vehicle Swarms and the E | non-primaire — classification/taxonomie de l hétérogénéité des essaims, pas une source primaire |
| 314 | Multi-AUV Cooperative Target Tracking Based on Supervised Diffusion-Ai | hors-perimetre — suivi de cible multi-AUV sous-marins (diffusion MARL), hors flotte aérien+surface |
| 317 | APF-Driven Lightweight UAV Swarm Trajectory Optimization in GNSS-Denie | deja-couvert — famille APF (champ de potentiel) déjà sourcée par srcVAPF (#200) |
| 328 | Multi-Agent Reinforcement Learning for Multi-UAV Pursuit with Full Pla | paradigme-exclu — MARL pour poursuite multi-UAV (politique apprise) |
| 337 | Say the Mission, Execute the Swarm- Agent-Enhanced LLM Reasoning in th | paradigme-exclu — exécution de mission par LLM (Web-of-Drones, MCP) |
| 338 | Secure UAV Swarms in Low-Altitude Wireless Networks- Challenges and So | non-primaire — article défis+solutions sécurité réseau (position paper), pas une source primaire d algorithme |
| 340 | Cooperative UAV Swarm Communication Networks for Rapid Disaster Assess | pas-algorithme-canonique — réseaux de communication d essaim en GPS-denied (couche réseau) |
| 351 | Autonomous Cooperative Drone Swarms for Countering Drones via Multi-Ag | paradigme-exclu — MADRL de contre-mesure de drones (politique apprise) |
| 375 | Dec-MARVEL- Decentralized Multi-Agent Exploration without Communicatio | paradigme-exclu — Dec-MARVEL = exploration MARL décentralisée sans communication |
| 376 | LLM-Centric Agentic AI for UAV Swarms- Architecture, Enabling Technolo | paradigme-exclu — LLM agentique pour essaim UAV (LAUS) |
| 437 | The Evolving Landscape of Unmanned Aircraft Systems- A Review of Curre | non-primaire — revue du paysage UAS (défis et scénarios futurs) |


---

## LOT 8 (2026-09-29)

### RATTACHEE (nouveaux verdicts)
| # | Titre | Alg(s) | specDoc | Finding |
|---|-------|--------|---------|---------|
| 915 | EGO-Swarm: A Fully Autonomous and Decentralized Quadrotor Swarm System | algPathPlanning + algCollisionAvoidance | srcEGOSwarm | SCI-48 |

### ECARTEE (24)
| # | Titre | Raison |
|---|-------|--------|
| 586 | Fleets Need a Context Plane- Rethinking Cooperative Perception for Aut | pas-algorithme-canonique — partage de features pour perception coopérative (bande passante), pas un des 15 algos |
| 592 | Evaluating Multimodal LLMs as Generalist Vision-Language-Action Agents | paradigme-exclu — MLLM comme agent de contrôle de drone (DroneCATS) |
| 600 | Quantum-Based k-Coverage Optimization for UAV-Aided Search and Rescue  | pas-algorithme-canonique — optimisation quantique QUBO pour k-couverture RF |
| 601 | KSG-Net- Key-Sparse and Global-Context Learning for Maritime 3D Ship D | hors-perimetre — détection 3D de navires maritime (perception mono-capteur), pas d essaim |
| 604 | From Multi-Fisheye Sensing to Panoramic Perception- A Parallax-Aware O | pas-algorithme-canonique — plateforme caméra fisheye panoramique embarquée |
| 606 | Advancing Accessible Underwater Robotics- The Mini-Girona I-AUV at RAM | hors-perimetre — plateforme I-AUV sous-marine (Mini-Girona) |
| 607 | Evaluating Graph Neural Networks for Change-Criticality Classification | paradigme-exclu — GNN pour classification de cartes marines (ENC), hors essaim |
| 610 | Air-Ground Collaborative Vision-and-Language Navigation via Shared Bir | paradigme-exclu — navigation air-sol par VLM (AGC-VLN) |
| 620 | DroneGround- Open-Vocabulary Drone Payload Characterization Using Synt | pas-algorithme-canonique — caractérisation de charge utile par vision-langage (détection) |
| 621 | Learning to Fly- Stable Vision-Guided UAV Servoing with Compact Target | paradigme-exclu — asservissement visuel par RL (politique apprise) |
| 624 | EgoSIS- From Factorized Visual Ego-Transitions to Motion-Canonical Spa | pas-algorithme-canonique — réponse visuelle à questions vidéo (EgoSIS), perception seule |
| 631 | Multi-Agent Reinforcement Learning for Autonomous UAV Exploration in W | paradigme-exclu — MARL/DRL pour surveillance de feux de forêt (politique apprise) |
| 632 | Coastal Environment Generation with HoloOcean - arXiv | pas-algorithme-canonique — génération d environnement de simulation côtière (HoloOcean) |
| 913 | SwarmNxt- Open-source Software-Hardware Platform for Fast and Agile Ae | pas-algorithme-canonique — plateforme matérielle/logicielle d essaim (SwarmNxt) |
| 918 | AttentionSwarm- Reinforcement Learning with Attention Control Barier F | paradigme-exclu — AttentionSwarm = CBF + attention + RL (politique apprise) |
| 932 | DETERRENCE BY ASSETS- HOW UAV LOCALIZATION UNDER SAUDI VISION 2030 RES | hors-perimetre — analyse géopolitique de localisation de drones (Vision 2030) |
| 938 | Model Predictive Control for Multimodal Intelligent Transportation Sys | non-primaire — revue MPC inter-domaines (transport) |
| 941 | An Omnidirectional Perception Framework for Distributed Unmanned Syste | non-verifiable — abstract non vérifié (DOI chapitre Springer), contenu primaire non lisible |
| 951 | Visual perception for autonomous surface vehicles in complex waterway  | non-primaire — revue de perception visuelle pour véhicules de surface en voies navigables |
| 975 | Space & Defense Volume 17 No. 1 Whole issue - DOI | hors-perimetre — numéro complet de revue Space & Defense (politique spatiale) |
| 978 | Autonomous UAVs in Critical Infrastructure Inspection- Empirical Evalu | pas-algorithme-canonique — évaluation empirique d inspection d infrastructures (application) |
| 980 | Algorithms in Battle- AI, International Relations, and Future Warfare  | hors-perimetre — analyse géopolitique IA et guerre (relations internationales) |
| 982 | Landing of an Aerial Robot Swarm via UWB-Based Localization and Convex | pas-algorithme-canonique — atterrissage d essaim par UWB + optimisation convexe (abstract non vérifié) |
| 985 | Lightweight UAV aerial small object detection based on YOLOv12 via att | pas-algorithme-canonique — détection de petits objets YOLOv12 (modèle de détection) |

## Validation lot 8
- `likec4 validate` sur clone propre `/tmp/lc_v7` : ✓ Valid (20 fichiers)
- Intégrité I-1 (référentiel) : 0 arc cassé ; I-2 (orphelins) : 0 ; I-7 : tous findings sourcés
- SCI jusqu'à 48

---

## LOT 9 (2026-09-29)

### RATTACHEE (nouveaux verdicts)
| # | Titre | Alg(s) | specDoc | Finding |
|---|-------|--------|---------|---------|
| 1023 | A hierarchical navigation decision-making method for UAV swarms in unk | algPathPlanning + algCollisionAvoidance | srcHierNavDecision | SCI-49 |

### DEJA_RATTACHEE (déjà statués — pas de doublon)
| # | Titre | specDoc existant | Finding existant |
|---|-------|------------------|------------------|
| 1037 | A Sensor-Centric Survey of SLAM and Odometry for GPS-Denied Environmen | srcSlamSurvey | SCI-5 |

### ECARTEE (23)
| # | Titre | Raison |
|---|-------|--------|
| 986 | An improved RT-DETR algorithm for small-object detection in UAV aerial | pas-algorithme-canonique — détection de petits objets RT-DETR (modèle de détection) |
| 988 | Overview of Recent Advances in Cooperative Optimized Navigation of Mul | non-primaire — revue de navigation coopérative optimisée multi-USV |
| 994 | AquaBEV- Monocular Underwater BEV Occupancy with 3D Sonar Supervision  | hors-perimetre — occupation BEV sous-marine monoculaire (AquaBEV), sonar |
| 999 | Ocean-aware deep learning for civilian maritime object detection and t | non-primaire — revue de détection/suivi maritime par deep learning |
| 1001 | Adaptive Localization for Underwater Nodes in Uncertain Environments-  | hors-perimetre — localisation de nœuds sous-marins par RL multi-étapes |
| 1004 | An Integrated IoT–AI–UAV Swarm Architecture for Intelligent Autonomous | non-primaire — architecture de référence IoT-AI-UAV pour sécurité aéroportuaire (review) |
| 1005 | Automated monitoring and geometric quantification of mining-induced gr | hors-perimetre — quantification de fissures minières par imagerie UAV (application géotechnique) |
| 1013 | Editorial- Advanced integration of large language models for autonomou | non-primaire — éditorial sur l intégration de LLM dans les systèmes autonomes |
| 1016 | Active sonar-based perception and wall following for AUV operations in | hors-perimetre — perception sonar active et suivi de paroi pour AUV |
| 1031 | An Efficient and Lightweight YOLO-based Framework for Real-time Insula | pas-algorithme-canonique — détection de défauts d isolateurs YOLO (application réseau électrique) |
| 1034 | Vision-Based Perception of UAV Targets Under Synthetic Fog- A Task-Ori | pas-algorithme-canonique — évaluation de perception sous brouillard synthétique (détection) |
| 1038 | GMD-YOLO26- A Lightweight Detector with Cooperative Three-Stage Featur | pas-algorithme-canonique — détection de petits objets GMD-YOLO26 (modèle de détection) |
| 1039 | Autonomous navigation and active perception with complex articulated A | hors-perimetre — navigation et perception active d AUV articulés |
| 1155 | AquaBEV- Monocular Underwater BEV Occupancy with 3D Sonar Supervision  | doublon — même article que #994 (AquaBEV, arXiv 2609.04411) |
| 1168 | How do LLMs Evaluate Perceived Moral Agency- Investigating Moral Decis | hors-perimetre — étude HCI sur l agence morale perçue des LLM |
| 1208 | One Model, Two Worlds- Bidirectional Sonar-Optical Translation - arXiv | hors-perimetre — traduction sonar-optique bidirectionnelle (perception sous-marine) |
| 1210 | Adapting Vision Foundation Models to Acoustics for Pose-Free 3D Sonar  | hors-perimetre — adaptation de modèles de fondation visuels au sonar 3D |
| 1243 | KODAMA- Multimodal Digital Twin Reconstruction for Urban RF Propagatio | pas-algorithme-canonique — jumeau numérique de propagation RF (KODAMA) |
| 1262 | Mini-Batch Risk-Averse Deep Q-Learning- A Robot Navigation Case Study  | paradigme-exclu — DQN averse au risque (RL, politique apprise) |
| 1266 | Dual-Layer Semantic-Spatial Belief Mapping for Aerial Object Goal Navi | paradigme-exclu — navigation par croyance sémantique VLM (AeroBelief) |
| 1300 | An Autonomous GeoAI Agent for Arctic Eco-Navigation - arXiv | hors-perimetre — routage arctique multi-critères (agent GeoAI, navire seul) |
| 1301 | Experimental Validation of Combined Imaging and Vibration Mitigation f | pas-algorithme-canonique — imagerie et atténuation de vibrations pour HAPS (plateforme) |
| 1305 | Adaptive Distributed Physical-Layer Authentication and Attack Detectio | pas-algorithme-canonique — authentification couche physique 6G par méta-apprentissage |

## Validation lot 9
- `likec4 validate` sur clone propre `/tmp/lc_v7` : ✓ Valid (20 fichiers)
- Intégrité I-1 (référentiel) : 0 arc cassé ; I-2 (orphelins) : 0 ; I-7 : tous findings sourcés
- SCI jusqu'à 49

---

## LOT 10 (2026-09-29)

### RATTACHEE (nouveaux verdicts)
| # | Titre | Alg(s) | specDoc | Finding |
|---|-------|--------|---------|---------|
| 1401 | Distributed Stochastic Optimal Control for Pattern-Oriented Swarms (20 | algFormationControl + algCollisionAvoidance | srcGRFSwarmOptCtrl | SCI-50 |

### ECARTEE (24)
| # | Titre | Raison |
|---|-------|--------|
| 1321 | ScopeMamba-YOLO- Widening the Perceptual Scope Inward and Outward for  | pas-algorithme-canonique — détection petits objets ScopeMamba-YOLO (modèle de détection) |
| 1323 | Distributed ToA Localization of Acoustic Sources with Unknown Time of  | hors-perimetre — localisation distribuée de sources acoustiques SOUS-MARINES (ToA) |
| 1350 | HGSQ- Heatmap-Guided Sparse Query Detector for Real-Time Aerial Small  | pas-algorithme-canonique — détecteur HGSQ (détection aérienne) |
| 1363 | EVPeriscope- Extended Perception across Aerial and Ground Vehicles wit | pas-algorithme-canonique — suivi d hélices par caméra événementielle (perception) |
| 1381 | PATH- Continuous Target Sensing among Autonomous Cooperative Drones -  | pas-algorithme-canonique — handoff de cible entre UAV (PATH), mécanisme de perception |
| 1396 | Parameter Sensitivity Analysis for Aerial LiDAR-Inertial Odometries in | pas-algorithme-canonique — analyse de sensibilité de paramètres LIO/SLAM (réglage) |
| 1423 | Quantum-Gated LiteSSD- A Parameter-Efficient Lightweight Hybrid Quantu | hors-perimetre — détection sonar quantique (LiteSSD), perception sous-marine |
| 1426 | SafePG- Safe and Globally Optimal Reinforcement Learning with Hard Con | paradigme-exclu — RL avec contraintes dures (SafePG, politique apprise) |
| 1441 | PRI-Net- A Lightweight Multimodal Framework for 3D UAV Localization -  | pas-algorithme-canonique — localisation UAV par fusion multimodale profonde (réseau) |
| 1444 | Language-Grounded Semantic Target Navigation for Autonomous Surface Ve | paradigme-exclu — navigation ASV guidée par langage + PPO |
| 1445 | Small Object Detection in Drone Aerial Imagery with LAF-YOLOv10 - arXi | pas-algorithme-canonique — détection petits objets LAF-YOLOv10 |
| 1452 | An Adaptive Fixed-Time Line-of-Sight Guidance Scheme for 3D Path Follo | hors-perimetre — guidage LOS à temps fixe pour AUV sous-marins |
| 1476 | Volumetric Harmonic Field Navigation for Quadrotors - arXiv | deja-couvert — navigation mono-quadrirotor par champ harmonique, famille planification déjà sourcée (SCI-14) |
| 1481 | DuctAM- A Duct-Assisted Quadrotor-Based Aerial Manipulator Enabling Hi | pas-algorithme-canonique — manipulateur aérien à soufflantes (DuctAM), plateforme |
| 1513 | Waggle Dance Inspired Motion Communication for Multiple UAVs in MuJoCo | pas-algorithme-canonique — communication par mouvement (danse des abeilles) en simulation |
| 1524 | TIO-Former- Ultra-Lightweight 6-Directional ToF-Inertial Odometry for  | pas-algorithme-canonique — odométrie ToF-inertielle pour nano-UAV (TIO-Former), matériel |
| 1541 | Set-membership localization of intermittent RF sources using a fleet o | pas-algorithme-canonique — localisation de sources RF par flotte (set-membership) |
| 1546 | Multi-Session Multimodal Underwater Mapping with Acoustic and Optical  | hors-perimetre — cartographie sous-marine multimodale multi-sessions (factor graph) |
| 1552 | Characterizing Refraction-Induced Ranging Bias in Underwater Collabora | hors-perimetre — biais de télémétrie par réfraction en localisation sous-marine |
| 1559 | Multi-View Mixture-of-Experts with Vision-Language Reranking for Cross | pas-algorithme-canonique — géo-localisation cross-view (MVLGeo), perception |
| 1566 | Understanding Dynamic Scenes at Gigapixel Scale- Wide-Area Spatio-Temp | pas-algorithme-canonique — dataset gigapixel de perception spatio-temporelle (HARD) |
| 1578 | UAVs Meet Embodied Intelligence- Bridging Human Intents and Flying Dyn | non-primaire — cadre 5+5 d intelligence incarnée UAV (position paper) |
| 1587 | From Pixels to Semantics- Edge AI for UAV-Based Critical Infrastructur | non-primaire — catégorisation d architectures d inspection par edge AI (survey) |
| 1588 | VLM-MPPI- Grounding Natural Language in Behaviorally Diverse Trajector | paradigme-exclu — navigation par VLM + MPPI (sélection de trajectoire par VLM) |

## Validation lot 10
- `likec4 validate` sur clone propre `/tmp/lc_v7` : ✓ Valid (20 fichiers)
- Intégrité I-1 (référentiel) : 0 arc cassé ; I-2 (orphelins) : 0 ; I-7 : tous findings sourcés
- SCI jusqu'à 50

---

## LOT 11 (2026-09-29)

### ECARTEE (25)
| # | Titre | Raison |
|---|-------|--------|
| 1596 | AeroWeaver- An Embodied-Agent Harness for Weaving Aerial Skills into D | paradigme-exclu — AeroWeaver = harnais d agents LLM pour essaim |
| 1609 | Body-Motion Control of a Simulated Aerial Swarm from a First-Person Vi | pas-algorithme-canonique — téléopération par mouvement corporel (interface HCI) |
| 1610 | SOL-SLAM- Inverse Compositional Gauss-Newton Direct Registration for F | hors-perimetre — SLAM local sonar seul (SOL-SLAM), sous-marin |
| 1635 | AURORA- A Natural Language-Driven Agentic Framework for Understanding, | paradigme-exclu — AURORA = génération de scénarios par LLM agentique |
| 1639 | PerSeM- Persistent Semantic Memory for Long-Horizon Open-Vocabulary UA | pas-algorithme-canonique — mémoire sémantique persistante pour cartographie (PerSeM) |
| 1648 | Towards Active Cross-View Object Geo-Localization - arXiv | pas-algorithme-canonique — géo-localisation cross-view active (ActiveGeo) |
| 1652 | Equivariant Filter Design for Acoustic and Depth Aided Inertial Naviga | hors-perimetre — filtre équivariant pour navigation inertielle AUV |
| 1654 | HEROIC- Heterogeneous Evidential Reasoning for Open-Vocabulary Identif | paradigme-exclu — coordination multi-agents en langage naturel uniquement (HEROIC) |
| 1657 | TADreamer- Zero-Shot Language-Guided 3D Navigation for Terrestrial-Aer | paradigme-exclu — navigation 3D par imagination vidéo VLM (TADreamer) |
| 1660 | Socialized UAV Cross-Task Learning- Towards Cross-Granularity Collabor | pas-algorithme-canonique — benchmark d apprentissage inter-tâches (CrossUAV) |
| 1685 | RTK-Vision PPO for Autonomous Micro UAV Recovery on an Airborne Carrie | paradigme-exclu — récupération micro-UAV par PPO (RTK-Vision) |
| 1691 | Towards Scaling Marine Perception with Synthetic Data - arXiv | hors-perimetre — génération de données synthétiques pour perception sous-marine |
| 1692 | Custom PX4 firmware for autonomous hybrid aerial-marine missions - arX | pas-algorithme-canonique — firmware PX4 pour missions hybrides aérien-marin |
| 1695 | Underwater Visual Target Tracking with Target-Specific Depth Estimatio | hors-perimetre — suivi visuel sous-marin par MPC (AUV) |
| 1703 | ASGARD- Action-Space Guard for UAV Resilience via Reinforcement Learni | paradigme-exclu — garde d espace d action pour RL (ASGARD, politique apprise) |
| 1706 | Project SCOUT- Interceptor Drone for Perimeter Defense - arXiv | pas-algorithme-canonique — interception anti-UAV (Project SCOUT), perception embarquée |
| 1708 | Towards Effective Visual-Inertial SLAM with Passive-Only Sensors for L | hors-perimetre — VI-SLAM pour AUV low-cost |
| 1714 | LoRA Enhanced Contrastive Learning with SAS Vision Transformers - arXi | hors-perimetre — reconnaissance de cibles sonar SAS (LoRA ViT) |
| 1781 | Multi-source UAV remote sensing for cotton Verticillium wilt resistanc | hors-perimetre — notation de résistance du coton par imagerie UAV (agriculture) |
| 1790 | Parameter Sensitivity Analysis for Aerial LiDAR-Inertial Odometries in | doublon — même article que #1396 (Parameter Sensitivity LIO, arXiv 2609.12837) |
| 1792 | Distributed Stochastic Optimal Control for Pattern-Oriented Swarms - D | doublon — même article que #1401 (Distributed Stochastic Optimal Control, arXiv 2609.12959) |
| 1799 | Bridging the Scale Gap- A Multi-Scale Feature Enhancement Framework fo | pas-algorithme-canonique — détection petits objets MSF-DETR |
| 1805 | Resource-Aware Small-UAV Perception under Annotation and Compute Const | non-verifiable — abstract non vérifié (preprint), contenu primaire non lisible |
| 1811 | UAV-LiteDet- A Lightweight Small Object Detection Network for Low-Alti | pas-algorithme-canonique — détection petits objets UAV-LiteDet |
| 1814 | A Multi-UAV Cooperative Navigation Method Based on Policy Decompositio | paradigme-exclu — GS-MADDPG = GNN + MADDPG pour navigation coopérative |

