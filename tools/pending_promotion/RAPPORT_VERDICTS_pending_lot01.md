# RAPPORT — Verdicts du circuit pending -> LikeC4 (carte t_1ce6f331)

Lot : PENDING LOT 01 (2026-09-29, carte t_1ce6f331) — 5 rattachees / 1 specdoc_only (completion SCI-29) / 3 deja rattachees / 36 ecartees
Date : 2026-09-29 — architecte

## Objet

Ce rapport statue chacune des 45 propositions `pending` de `impact-proposals.json` (etage 2 du circuit de promotion). AUCUNE ecriture n'a ete faite dans `science.c4` : les blocs LikeC4 correspondants aux rattachements sont fournis separement, a inserer uniquement apres validation de Christophe (etage 3).

## Synthese

| Verdict | Nombre |
|---------|--------|
| RATTACHEE (nouveau finding) | 5 |
| RATTACHEE (completion d'un finding existant) | 1 |
| DEJA_RATTACHEE (source deja presente) | 3 |
| ECARTEE | 36 |
| **Total** | **45** |

## 1. RATTACHEE — nouveaux findings proposes (SCI-56..SCI-60)

Patron 2 sauts : `srcXXX <-[uses]- sciFinding -[evidences]-> algYYY`.

### SCI-56 — Controle hybride event-triggered energy-aware pour micro-drones

- Source : Energy-Aware Hybrid Event-Triggered Control for Micro-Drones (IMAV 2025)
- specDoc : `srcHETCEnergyAware` | finding : `sciHETCEnergyAware`
- Algorithme(s) cible(s) : algEventTriggeredComm, algEnergyAware
- Lien : https://www.imavs.org/papers/2025/15.pdf
- Justification : srcHETCEnergyAware documente le couplage algEventTriggeredComm x algEnergyAware : le declenchement hybride (timer de surete + seuil adaptatif) reduit a la fois le trafic de communication et la consommation d energie, sans sacrifier la surete. Complement de SCI-6 (event-triggered generique) : ici l angle energie ET la borne Zeno par timer fixe. VERDICT : SUPPORTED pour le mecanisme (HETC energy-aware) ; CONDITIONAL — simulation 6-DOF, echelle a confronter a N=30.

### SCI-57 — Planification de trajectoire multi-UAV par Jump Point Search ameliore

- Source : Path Planning Technology for Unmanned Aerial Vehicle Swarm Based on Improved Jump Point Algorithm (2025)
- specDoc : `srcJumpPointSwarm` | finding : `sciJumpPointSwarm`
- Algorithme(s) cible(s) : algPathPlanning
- Lien : https://thesai.org/Downloads/Volume16No4/Paper_26-Path_Planning_Technology_for_Unmanned_Aerial_Vehicle_Swarm.pdf
- Justification : srcJumpPointSwarm documente algPathPlanning par JPS ameliore + fenetre dynamique + champs de collision pour la planification collaborative d essaim, avec evitement d obstacles et re-planification face aux minima locaux. Complement de la famille path planning (A*/RRT/RHCR) : ici JPS ameliore a cout borne. VERDICT : SUPPORTED pour le mecanisme (JPS + DWA + champs de collision) ; CONDITIONAL — simulation sur grille 29x29 m, echelle a confronter.

### SCI-58 — Detection de collision neuromorphique par camera evenementielle

- Source : Bioinspired framework for real-time collision detection with dynamic obstacles in cluttered outdoor environments (2025)
- specDoc : `srcBioEventCollision` | finding : `sciBioEventCollision`
- Algorithme(s) cible(s) : algCollisionAvoidance
- Lien : https://doi.org/10.1049/csy2.70006
- Justification : srcBioEventCollision documente le front-end de PERCEPTION d algCollisionAvoidance : detection temps-reel d obstacles dynamiques par camera evenementielle bioinspiree (97 % en reel), alimentant l evitement. Complement de la famille collision avoidance (CBF/collision cone) : ici le capteur et la detection, pas la loi d evitement. VERDICT : SUPPORTED pour le mecanisme (detection neuromorphique de menace de collision) ; CONDITIONAL — mono-capteur, integration a la boucle d evitement a valider.

### SCI-59 — Collision cone CBF ameliore avec rayon de relaxation temps-variant

- Source : Improved Collision Cone Control Barrier Functions for Dynamic Obstacle Avoidance of UAVs (2025)
- specDoc : `srcIC3BF` | finding : `sciIC3BF`
- Algorithme(s) cible(s) : algCollisionAvoidance, algSafetyRules
- Lien : https://doi.org/10.1109/YAC66630.2025.11150122
- Justification : srcIC3BF documente algCollisionAvoidance + algSafetyRules : le rayon de relaxation temps-variant resout le conflit contraintes de surete / limites d actionneurs (optimisation insoluble), en relachant partiellement le C3BF sous stabilisation CLF. Complement de la famille CBF (SCI-28/SCI-31) : ici la gestion des limites d actionneurs. VERDICT : SUPPORTED pour le mecanisme (IC3BF temps-variant) ; CONDITIONAL — simulation, validation en vol a confirmer.

### SCI-60 — Critere de stabilite sous retard pour la formation d essaim a voilure fixe

- Source : Stability Analysis of Fixed-Wing UAV Swarms Under Time-Delayed Tracking Control Law (2025)
- specDoc : `srcDelayStability` | finding : `sciDelayStability`
- Algorithme(s) cible(s) : algFormationControl
- Lien : https://doi.org/10.3390/axioms14070519
- Justification : srcDelayStability documente algFormationControl sous l angle de la STABILITE : critere dependant du retard (Routh-Hurwitz + equation transcendante) avec seuil de retard critique pour le maintien de formation. Complement de la famille formation sous retard (srcMultiLeaderDelay) : ici la preuve de stabilite formelle, pas le declenchement. VERDICT : SUPPORTED pour le mecanisme (critere de stabilite sous retard) ; CONDITIONAL — analyse theorique, transposition au controleur embarque a valider.

## 2. RATTACHEE — completion d'un finding existant (specdoc only)

- Distributed Model Predictive Formation Control for UAVs and Cooperative Capability Evaluation of Swarm (2025)
  - specDoc : `srcDMPCFormationEval` -> complete `sciDMPCSafetyZones`
  - note : complete SCI-29 (DMPC formation + evitement) — apport : metriques d evaluation de capacite cooperative

## 3. DEJA_RATTACHEE — deja sources, aucun doublon a creer

- #177 An Ultra-lightweight and Scalable Planner for Large-scale Aerial Swarms - arXiv 
  - specDoc existant : `srcUltraLightPlanner` | finding : `sciUltraLightPlanner`

- #200 Addressing Local Minima in Path Planning for Drones with RL-Based Vortex Artific
  - specDoc existant : `srcVAPF` | finding : `sciPathPlanning`

- #205 SwarmRaft - Leveraging Consensus for Robust Drone Swarm Coordination in GNSS-Deg
  - specDoc existant : `srcSwarmRaft` | finding : `sciGnssDegraded`

## 4. ECARTEE — verdicts et raisons

| # | Titre | Raison |
|---|-------|--------|
| 126 | Tomorrow's Seascape: DoD's Replicator sUSV Element Begins to Take Shape - Defense Security | non-primaire — actualite/presse (blog Defense Security Monitor) |
| 129 | NATO selects Anduril's Lattice platform for next-gen air command and control - The Jerusal | non-primaire — actualite (Jerusalem Post) |
| 131 | Thales UAS100 Long-Range Drone System Meets EASA Design Verification Report Milestone - UA | non-primaire — actualite produit (UAS Vision) |
| 132 | Exail, RTsys and ABYSSA join forces for ocean floor mapping with AUVs | non-primaire — communique d entreprise (Exail) |
| 137 | Strengthening UAS Security with Lessons from the Paris Olympics - IDGA | non-primaire — actualite (IDGA) |
| 154 | A Survey on UAV Control with Multi-Agent Reinforcement Learning - OUCI (10.3390/drones9070 | non-primaire — survey MARL, pas une source primaire |
| 158 | AI-enabled control system helps autonomous drones stay on target in uncertain environments | non-primaire — actualite (MIT news) |
| 166 | CARTEL: Consensus Adapting Real-Time and Efficient Logging (10.1109/RTSS66672.2025.00044) | pas-algorithme-canonique — consensus pour journalisation temps reel (RTSS), hors essaim de drones |
| 167 | Drones & Swarms - NOKOV Motion Capture | non-primaire — page produit (motion capture) |
| 169 | Installing Gazebo with ROS — Gazebo jetty documentation | non-primaire — documentation logicielle (Gazebo) |
| 170 | NATO advances maritime innovation and readiness through Exercise Dynamic Messenger 2025 | non-primaire — actualite (NATO) |
| 171 | Nemyx - Auterion | non-primaire — page produit (Auterion) |
| 173 | AI Drone Swarm Coordination: 20 Advances (2026) - Yenra | non-primaire — blog de veille (Yenra) |
| 174 | Dynamic Modeling and Analysis on the Cable Effect of USV-UUV System Under High-Speed (10.3 | pas-algorithme-canonique — modelisation hydrodynamique du cable USV-UUV, pas un algorithme |
| 175 | A Comprehensive Review of Next-Gen UAV Swarm Robotics: Optimisation Techniques (10.32604/i | non-primaire — revue, pas une source primaire |
| 178 | A machine-learning enabled digital-twin framework for tactical drone-swarm design (10.1016 | pas-algorithme-canonique — jumeau numerique de conception (dynamique multicorps + ML) |
| 179 | American USV Builders Anticipate Mass Demand from U.S. Navy - Defense Security Monitor | non-primaire — actualite (Defense Security Monitor) |
| 180 | FANET and MANET, a Support and Composition Relationship (10.32604/cmc.2025.056400) | pas-algorithme-canonique — architecture reseau FANET/MANET, pas un des 15 algorithmes |
| 181 | AttentionSwarm: Reinforcement Learning with Attention Control Barrier Function for Crazyfl | paradigme-exclu — politique MARL apprise + CBF attention |
| 182 | gym-pybullet-drones download - SourceForge.net | non-primaire — page de telechargement logiciel (gym-pybullet-drones) |
| 184 | Rise of U-space: Revolutionizing Drone Management in Europe - VisionSpace | non-primaire — article de veille (VisionSpace) |
| 185 | US Navy receives first Dive LD drone submarine - CT.gov | non-primaire — actualite (CT.gov) |
| 186 | Anduril unveils new torpedo that can be launched by underwater drones - DefenseScoop | non-primaire — actualite (DefenseScoop) |
| 188 | Un Bouclier de Securite Dynamique pour un Apprentissage par Renforcement (arXiv 2412.04153 | paradigme-exclu — safe RL, politique apprise |
| 189 | Deadlock-free, safe, and decentralized multi-robot navigation in social mini-games via dis | hors-perimetre — robots terrestres en environnement social (portes/intersections), hors flotte aerien+surface |
| 190 | Depth Transfer: Learning to See Like a Simulator for Real-World Drone Navigation (arXiv 25 | paradigme-exclu — politique RL apprise pour evitement (sim-to-real) |
| 191 | Wireless Communication for Low-Altitude Economy with UAV Swarm Enabled Two-Level Movable A | pas-algorithme-canonique — optimisation reseau/antennes mobiles (PHY) |
| 192 | FPV Drone Swarms in Asymmetric Warfare: Tactical Innovations and Ethical Challenges | pas-algorithme-canonique — analyse tactique/ethique de guerre FPV, pas un algorithme |
| 195 | Cryptography-Based Secure Underwater Acoustic Communication for UUVs: A Review (10.3390/el | non-primaire — revue de cryptographie pour UUV |
| 196 | Swarm Intelligence Archives - Andres Andreu | non-primaire — blog (archive de tags) |
| 197 | Multi-agent Reinforcement Learning for Robotized Coral Reef Sample Collection (arXiv 2507. | hors-perimetre — UUV de collecte de coraux (sous-marin), politique MARL |
| 199 | Advancing UAV swarm autonomy with ARCog-NET for task allocation, path planning, and format | pas-algorithme-canonique — architecture cognitive Edge-Fog-Cloud (ARCog-NET), pas un algorithme |
| 201 | Collaborative Target Tracking Algorithm for Multi-Agent Based on MAPPO and BCTD (10.3390/d | paradigme-exclu — MAPPO (politique MARL apprise) |
| 202 | Reinforcement Learning for Decision-Level Interception Prioritization in Drone Swarm Defen | paradigme-exclu — politique RL apprise pour priorisation d interception |
| 203 | A Taxonomy of Hierarchical Multi-Agent Systems: Design Patterns, Coordination Mechanisms ( | non-primaire — taxonomie/review de HMAS, pas de source primaire |
| 204 | OM2P: Offline Multi-Agent Mean-Flow Policy (arXiv 2508.06269) | paradigme-exclu — politique MARL hors-ligne (diffusion/mean-flow) |

## 5. Decision attendue de Christophe

1. Valider / corriger les 5 RATTACHEE (SCI-56..60) et la completion SCI-29.
2. Confirmer les 36 ECARTEE et les 3 DEJA_RATTACHEE.
3. Apres validation, inserer les blocs de `pending_lot01_additions.c4` dans `science.c4` (etape separee, hors de cette carte).
4. Autoriser le deploiement de `analyze_impact.py` corrige (`hermes profile update swarmdrone --yes`).

## 6. Preuve de la correction d'IMPACT_TARGETS (etage 1)

Sortie reelle de `tools/pending_promotion/test_impact_targeting.py` : les 15 identifiants d'algorithmes sont verifies contre `algorithms.c4` ; un article de formation control est cible sur `algFormationControl` (et non `onboard.mission`) ; 50 applied / 105 rejected inchanges.
