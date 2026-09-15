# Annexe v1 — Architecture SwarmDrones (30 plateformes hétérogènes UAV-R / UAV-F / USV)

**Complément au document `swarm30_arch.md` (v1.0) — volets ① logiciels du marché, ② algorithmes, ③ angles morts, ④ risques, ⑤ impacts LikeC4.**
Version : annexe v1.0. Date : 2026-09-14 (UTC). Posture : revue contradictoire, pas validation.

## Résumé exécutif

- Le document de référence est **solide comme architecture logique** mais **pauvre en ancrage produit et en algorithmes nommés**. Cette annexe comble l'écart avec des briques réelles, nommées, licenciées et vérifiées en source primaire (docs/éditeurs), plus une cartographie d'angles morts et de risques.
- **Constat corpus** : `/home/hermesagent/swarmdrone-research/catalog.json` contient 1011 entrées, mais **seulement 2 atteignent `PRIMARY_SOURCE_VERIFIED`** (420 `unverified`, 48 `D-discovery`, ~508 en `B-*`/`A-primary-candidate`). Le corpus est donc un **gisement de pistes de recherche**, pas une preuve au niveau revendication. Toute affirmation produit de §A a été **re-vérifiée sur source primaire web** (docs officielles, LICENSE, éditeur).
- **Recommandation PRIMAIRE transversale** : socle **open-source, permissif quand possible** — PX4 (BSD-3) et/ou ArduPilot (GPLv3) selon contrainte de distribution propriétaire, ROS 2 (Apache-2.0) comme middleware de composition onboard/edge, uXRCE-DDS (Apache-2.0) comme pont MCU↔DDS, MAVLink (MIT/LGPLv3) comme protocole filaire de fait. **Evidence level: HIGH** (licences et capacités documentées par les projets eux-mêmes).
- **Point dur non résolu par l'architecture** : le **choix ArduPilot (GPLv3) vs PX4 (BSD-3)** est un arbitrage *juridique* avant d'être technique ; il conditionne la capacité à fermer ou non les composants embarqués. Ce conflit n'apparaît **pas** dans §10 du document de référence (→ angle mort AM-1).
- **Trou algorithmique principal** : l'allocation de tâches est mentionnée (« enchères ») mais **aucune famille, aucun critère, aucun benchmark** n'est fixé ; l'évitement de collision multi-agents et la **sûreté formelle sous partition** sont quasi absents (→ §B, §C).

**Verdict global : MEDIUM.** Brique logicielle = faisable avec du COTS/OSS mature ; algorithmique = connu en laboratoire mais **non prouvé à 30 agents hétérogènes sous partition + GNSS dégradé simultanés** (extrapolation assumée).

---

## Rappel de la convention d'étiquetage (héritée du doc de référence)

- `[FAIT]` : fait démontré / capacité publique documentée par la source primaire.
- `[SIM]` : relèverait de la simulation (non exécutée ici).
- `[HYP]` : hypothèse de conception.
- `[EXTRAP]` : extrapolation depuis d'autres échelles/domaines.
- `Non vérifié` : je n'ai pas pu établir existence/licence/version en source primaire.
- Échelle d'evidence retenue : **HIGH** = documenté par la source primaire du projet/éditeur ou ≥2 publications convergentes ; **MEDIUM** = source unique primaire crédible ou contexte limité ; **LOW** = preprint unique, extrapolation ou indice indirect.

---

## §A — Logiciels du marché

Règle de lecture : chaque brique est mappée sur les **composants `onboard.*` / `edge.*` / `c2.*` / `cloud.*`** du §13 du document de référence. Les licences et maturités ci-dessous proviennent des **fichiers LICENSE / docs officielles** listés en fin de document. Les versions sont **omises** sauf mention exacte vérifiée, pour éviter tout chiffre inventé.

### A.1 — Socle de vol (onboard.autopilot, onboard.mission, onboard.safety)

**Composant(s) :** `onboard.autopilot` (Safety-Critical), interface `onboard.mission`, `onboard.safety` (geofence, RTL/atterrissage).

- **Choix PRIMAIRE : PX4 Autopilot.**
  - Éditeur/projet : PX4 Development Team, hébergé par la **Dronecode Foundation** (Linux Foundation). `[FAIT]`
  - Licence : **BSD 3-Clause** (permissive). `[FAIT — LICENSE PX4-Autopilot]`
  - Maturité : mature, multi-plateformes (multirotor, fixed-wing, VTOL, rover, submersibles). `[FAIT — docs PX4]`
  - Raison du choix : licence permissive (pas d'obligation de divulgation), architecture modulaire uORB/DDS-compatible, support ROS 2 de première classe via uXRCE-DDS, écosystème Pixhawk large. Adapté à un essaim hétérogène (UAV-R/UAV-F, et Rover pour USV).
  - Zone : **Onboard** (autopilote embarqué) ; paramétrage/replanif via Edge/C2.
  - Evidence level : **HIGH** (licence et capacités documentées par la source primaire).
- **Choix SECONDAIRES :**
  1. **ArduPilot** (Copter/Plane/Rover/Sub) — **GPLv3** `[FAIT — ardupilot.org/dev/docs/license-gplv3]`. *Préférable si* : on privilégie la richesse des modes autonomes éprouvés (Rover pour USV, Plane pour UAV-F), l'écosystème Mission Planner, et qu'on accepte la contrainte copyleft (code embarqué distribué → obligation de fournir le source ; usage interne non distribué = pas de déclenchement). Le projet documente l'usage d'un **computeur compagnon closed-source** pour ségréguer la valeur. `[FAIT]`
  2. **Autopilotes commerciaux certifiables** (ex. plateformes orientées sécurité industrielle) — *préférable si* : exigence de dossier de conformité/qualification formelle et SLA fournisseur. **Non vérifié** : je n'ai pas établi ici d'entité, licence ni version précises ; à documenter avant toute décision.
  3. **PyPilot / solutions légères USV** — **Non vérifié** dans cette session (existence/version/licence non confirmées) ; piste à investiguer pour les 4 USV.

> **Conflit juridique explicite (absent du §10 du doc de référence) :** BSD-3 (PX4) vs GPLv3 (ArduPilot) n'est pas un détail. Si le livrable doit rester fermable, **PX4 est le défaut** ; si la priorité est la maturité des modes autonomes et l'usage interne, **ArduPilot est défendable**. Décision à figer au niveau programme, pas ingénieur.

### A.2 — Middleware & bus de données (onboard/edge/C2/cloud)

**Composant(s) :** trait transverse — `onboard.*` (bus interne), `edge.*` (fusion/coordination), passerelles `edge.gateway`.

- **Choix PRIMAIRE : ROS 2.**
  - Projet : Open Robotics / ROS 2 community. `[FAIT]`
  - Licence : **Apache-2.0** (recommandation officielle ROS 2). `[FAIT — docs.ros.org]`
  - Maturité : mature, distributions LTS (ex. Jazzy Jalisco), intégration PX4 documentée. `[FAIT]`
  - Raison : composition onboard/edge hétérogène, outillage (colcon, rqt, rosbag pour rejeu), écosystème capteurs/planification. DDS sous-jacent tolérant au découplage temporel.
  - Zone : **Onboard (compagnon)** + **Edge**.
  - Evidence level : **HIGH**.
- **Composants/sous-choix SECONDAIRES :**
  1. **eProsima Fast DDS** — **Apache-2.0**, implémentation DDS par défaut de ROS 2, support commercial disponible ; **Safe DDS** commercial certifiable (claim éditeur, **Non vérifié** indépendamment). *Préférable si* : besoin DDS hors ROS 2 ou montée vers un profil certifiable. `[FAIT — eProsima]`
  2. **Eclipse Zenoh** — **Apache-2.0 OR EPL-2.0**, pub/sub + query + storage, pensé edge→cloud, transports variés (TCP/UDP/TLS/QUIC/série). *Préférable si* : lien faible/intermittent et topologies mesh/route ; publication comparative (voir §B) le place favorable en débit/latence, mais **résultat d'un preprint unique (2023)** → à re-vérifier. `[FAIT existence/licence ; MEDIUM sur perf]`
  3. **MQTT (Eclipse Mosquitto)** — **EPL-2.0 OR BSD-3-Clause**. *Préférable pour* C2/cloud best-effort et liens très contraints (LoRa/satellite via passerelle) ; **moins adapté** onboard temps-réel (broker central, QoS ≠ temps réel).

### A.3 — Pont MCU / autopilote ↔ ordinateur compagnon (onboard.sensors-hal, onboard.perception)

**Composant(s) :** `onboard.sensors-hal`, alimentation de `onboard.perception`/`onboard.mission` par l'autopilote.

- **Choix PRIMAIRE : eProsima Micro XRCE-DDS (+ micro-ROS Agent).**
  - Projet : eProsima / micro-ROS. `[FAIT]`
  - Licence : **Apache-2.0** (client, agent, rmw_microxrcedds). `[FAIT — LICENSE repo]`
  - Maturité : largement déployé dans l'écosystème ROS 2 embarqué ; PX4 embarque `uxrce_dds_client` par défaut. `[FAIT — docs PX4]`
  - Raison : pont standard autopilote↔ROS 2 (uORB ↔ topics ROS 2), sans repasser par MAVLink là où DDS est voulu.
  - **Réserve honnête** : les dépôts micro-ROS signalent « *not ready for production use… not tested for a specific use case* » et rappellent l'attention aux normes de sûreté. `[FAIT — README micro-ROS]` → à traiter en SIL/HIL renforcé.
  - Zone : **Onboard**.
  - Evidence level : **HIGH** (licence/existence), **MEDIUM** (adéquation sûreté).
- **SECONDAIRES :**
  1. **MAVLink / MAVSDK** — MAVLink : XML + C header-only **MIT**, générateur **LGPLv3**. MAVSDK : **BSD-3-Clause**. *Préférable si* : on veut un découplage plus simple, multi-langage, et une compatibilité maximale GCS/radios. `[FAIT]`
  2. **MAVROS** (legacy ROS 1/2 MAVLink bridge) — **BSD-3-Clause** via ROS. *Préférable* pour compatibilité anciens stacks ; **moins recommandé** que uXRCE-DDS pour du neuf.

### A.4 — Relais / mesh / messagerie de flotte (edge.relay, onboard.link)

**Composant(s) :** `onboard.link`, `edge.relay`, `edge.gateway`.

- **Choix PRIMAIRE : Zenoh (peer/mesh, transports hétérogènes).**
  - Licence **Apache-2.0 OR EPL-2.0**, architecture **décentralisée** par conception (pas de broker central), stockage/query distribués — cohérent avec le principe « lien = bonus ». `[FAIT — NOTICE/LICENSE Zenoh]`
  - Evidence level : **MEDIUM** (licence/existence = HIGH ; adéquation essaim radio faible = `[EXTRAP]`, non prouvée à 30 agents).
- **SECONDAIRES :**
  1. **DDS (RTPS) sobre (Fast DDS)** directement en radio mesh — *préférable* si le lien offre un UDP exploitable et qu'on veut rester DDS natif de bout en bout.
  2. **MQTT + broker embarqué/edge** — *préférable* sur liens *store-and-forward* à très faible débit (LoRa/SatCom), via `edge.gateway`.
  3. **Protocoles/implémentations radio dédiées (ex. solutions mesh propriétaires)** — **Non vérifié** : existence/licence non établies ici ; à instruire par radio cible (LoRa, 802.11s, lien dédié).

### A.5 — Perception, fusion, Sense-and-Avoid (onboard.perception, edge.fusion)

**Composant(s) :** `onboard.perception`, `edge.fusion`.

- **Choix PRIMAIRE : ROS 2 perception stack + filtres d'état (EKF/UKF) + bibliothèques de fusion open-source.**
  - Licence : **Apache-2.0** (paquets ROS 2). `[FAIT]`
  - Raison : briques de base disponibles (filtres, repères, tf2), déportables en grande partie sur Edge.
  - Evidence level : **MEDIUM** (composants existent ; **chaîne fusion multi-agents hétérogènes complète = à construire, pas un produit sur étagère**).
- **SECONDAIRES :**
  1. **Cadres SLAM/VIO open-source** (ex. familles factor-graph / VIO) — *préférable* en GNSS-dégradé fort ; disponibilité/licences à vérifier au cas par cas. **Non vérifié** au niveau entité/licence exacte dans cette session.
  2. **Framework de fusion multi-pistes** dédié — pas de produit COTS univoque identifié ; **à spécifier/vérifier**.
- ⚠️ **Point clé :** il n'existe **pas** de produit « perception d'essaim hétérogène 30 plateformes » sur étagère. Cette brique est **intégratrice**, à assembler et valider — voir §C AM-4.

### A.6 — GCS / supervision & planification C2 (c2.gcs, c2.planner, c2.alerting)

**Composant(s) :** `c2.gcs`, `c2.planner`, `c2.alerting`.

- **Choix PRIMAIRE : QGroundControl (QGC) pour la supervision/planification MAVLink.**
  - Projet : Dronecode / communauté MAVLink. `[FAIT]`
  - Licence : **dual Apache-2.0 / GPLv3**. `[FAIT — docs QGC]`
  - Maturité : mature, multi-véhicules, planification de mission, compatible PX4 et ArduPilot.
  - Raison : supervision temps réel, gestion multi-véhicules, base pour l'autorité humaine (§9 du doc).
  - Zone : **C2**.
  - Evidence level : **HIGH**.
- **SECONDAIRES :**
  1. **Mission Planner (ArduPilot)** — **GPLv3**. *Préférable* si socle ArduPilot (écosystème de suivi de plusieurs véhicules, « swarming » leader/followers documenté). `[FAIT — ardupilot.org/planner/docs/swarming]`
  2. **APM Planner 2** — **GPLv3** (ArduPilot). *Préférable* pour environnements multiplateformes ArduPilot.
  3. **Solution C2 intégrée commerciale** (ex. offres de gestion de flotte drone de défense/sécurité) — **Non vérifié** (entités/licences/SLA non établis ici). À évaluer sur critères : multi-véhicules hétérogènes, API ouverte, journal d'audit, export de traces.

### A.7 — Sécurité / identité / audit (c2.auth, transverse)

**Composant(s) :** `c2.auth`, signatures d'ordres critiques, journal d'audit.

- **Choix PRIMAIRE : primitives standard (signature Ed25519/ECDSA, mTLS) sur socle de bibliothèques libres.**
  - Raison : le doc exige « 100 % des ordres critiques signés » + registre d'audit. On ne dépend pas d'un produit unique mais de primitives éprouvées.
  - Evidence level : **HIGH** (primitives), **MEDIUM** (intégration PKI embarquée à dimensionner).
- **SECONDAIRES :**
  1. **PKI interne / serveur de clés** (ex. briques open-source type step-ca, cf. **Non vérifié** pour version/licence précises ici). *Préférable* pour rotation de clés et révocation embarquée.
  2. **Coffre de secrets / HSM** pour la clé d'émission de plans — commercial ou open-source selon criticité. **Non vérifié**.

### A.8 — Cloud : jumeau numérique, replay, stockage, observabilité (cloud.twin, cloud.analytics, cloud.replay-store, cloud.model-registry)

**Composant(s) :** `cloud.twin`, `cloud.analytics`, `cloud.replay-store`, `cloud.model-registry`.

- **Choix PRIMAIRE : Gazebo Sim (gz-sim) + rosbag2/stockage objet (MinIO) + observabilité Prometheus/Grafana.**
  - **Gazebo Sim** : **Apache-2.0** ; simulateur, modèles de capteurs/bruit, transport TCP/IP, SDF. `[FAIT — gz-sim LICENSE]`
  - **MinIO** (stockage objet compatible S3) : **AGPLv3**. `[FAIT]` → ⚠️ **AGPL impose des obligations si exposition réseau de versions modifiées** ; en usage interne non modifié = OK, mais **à valider juridiquement**. Alternative si contrainte : stockage S3 commercial ou **Ceph** (licence à vérifier).
  - **Prometheus** : **Apache-2.0** ; **Grafana** : **AGPL-3.0-only** (cœur), avec sous-composants Apache-2.0. `[FAIT]` → même remarque AGPL que MinIO.
  - Raison : jumeau numérique + rejeu (rosbag2) + métriques = cœur du volet VALIDATION.
  - Zone : **Cloud** (hors boucle de contrôle).
  - Evidence level : **HIGH** (licences/existence), **MEDIUM** (montage jumeau multi-plateformes à 30 agents = à construire).
- **SECONDAIRES :**
  1. **Apache Kafka** — **Apache-2.0** (Kafka cœur) ; attention : certains composants Confluent = *Confluent Community License* (source-available, **pas OSI**). `[FAIT]` *Préférable* si pipeline d'événements massif et rejouabilité par flux.
  2. **PostgreSQL + PostGIS** — **PostgreSQL License** / PostGIS **GPLv2+** ; *préférable* pour registre de missions, géométries, requêtes spatiales. `[FAIT]`
  3. **Système de gestion de versions de modèles (model registry)** dédié — **Non vérifié** (existence/licence) ; à trancher entre solution cloud native et simple registre Git+LFS.

### A.9 — Cartographie / navigation marine (USV) & géodonnées

**Composant(s) :** `onboard.mission` (USV), `edge.fusion` (carte locale), `c2.gcs` (affichage).

- **Choix PRIMAIRE : OpenCPN (plotter marine) + données OSM/OpenSeaMap.**
  - OpenCPN : **GPLv2+** (composants LGPLv2+/v3). `[FAIT — LICENSING OpenCPN]` ; supporte S-57 ENC, raster BSB, AIS, NMEA 0183/2000. `[FAIT]`
  - Raison : visualisation/navigation marine pour les 4 USV et pour l'affichage C2 ; format standard ENC.
  - Zone : **Onboard USV / C2**.
  - Evidence level : **HIGH** (licence/capacités), **MEDIUM** (intégration dans le C2 unifié à faire).
- **SECONDAIRES :**
  1. **Signal K** — **Apache-2.0** (hub de données marines) ; *préférable* pour normaliser un flux NMEA hétérogène côté USV. Source : `[FAIT — pistack comparison]` (source secondaire, à reconfirmer éditeur).
  2. **Outil de géocodage open-source (Nominatim/OSM)** — **GPL** ; *préférable* pour adressage/géodonnées non critiques hors boucle. `[FAIT — OSM Wiki]`

### A.10 — Tableau récapitulatif §A

| Composant (LikeC4 id) | Primaire | Secondaires | Evidence level |
|---|---|---|---|
| onboard.autopilot / mission / safety | **PX4** (BSD-3) | ArduPilot (GPLv3) ; autopilotes certifiables (**Non vérifié**) | HIGH |
| onboard.sensors-hal / pont autopilote | **Micro XRCE-DDS / micro-ROS** (Apache-2.0) | MAVLink+MAVSDK (MIT/BSD-3) ; MAVROS (BSD-3) | HIGH (licence) / MEDIUM (sûreté) |
| onboard.link / edge.relay | **Zenoh** (Apache-2.0/EPL-2.0) | DDS sobre ; MQTT edge ; mesh radio (**Non vérifié**) | MEDIUM |
| onboard.perception / edge.fusion | **ROS 2 + filtres d'état** (Apache-2.0) | SLAM/VIO OSS (à vérifier) ; framework fusion dédié (à spécifier) | MEDIUM |
| Middleware transverse | **ROS 2** (Apache-2.0) + **Fast DDS** (Apache-2.0) | Zenoh ; Mosquitto MQTT (EPL-2.0/BSD-3) | HIGH |
| c2.gcs / planner / alerting | **QGroundControl** (Apache-2.0/GPLv3) | Mission Planner (GPLv3) ; APM Planner 2 ; C2 commercial (**Non vérifié**) | HIGH |
| c2.auth / audit | **primitives Ed25519/ECDSA + mTLS** | PKI interne ; HSM (**Non vérifié**) | HIGH primitives / MEDIUM intégration |
| cloud.twin | **Gazebo Sim** (Apache-2.0) | scénarios d'essaim (à vérifier) | HIGH (licence) / MEDIUM (échelle) |
| cloud.replay-store / storage | **MinIO** (AGPLv3) | S3 commercial ; Ceph (licence à vérifier) | HIGH (licence), ⚠️ AGPL |
| cloud.analytics / observabilité | **Prometheus (Apache-2.0) + Grafana (AGPL-3.0)** | Kafka (Apache-2.0, cf. caveat Confluent) | HIGH (licence), ⚠️ AGPL |
| Données/registre missions | **PostgreSQL + PostGIS** (PostgreSQL License / GPLv2+) | registre Git+LFS | HIGH |
| USV navigation/carte | **OpenCPN** (GPLv2+) | Signal K (Apache-2.0) ; Nominatim/OSM (GPL) | HIGH (licence) |

⚠️ **Alerte licences à traiter en revue juridique (angle mort AM-2) :** présence d'**AGPLv3** (MinIO, Grafana) et de la **Confluent Community License** (source-available ≠ OSI) dans la pile Cloud. Si le système est un service exposé, ces licences créent des obligations fortes. **Décision explicite requise**, pas implicite.

---

## §B — Algorithmes

Méthode : pour chaque fonction, on liste les **familles candidates**, on les compare sur **critères identiques** (complexité, données requises, robustesse à la perte de lien, puissance de calcul, maturité, evidence level), puis on donne **une recommandation nette + une alternative**, et ce qui doit être validé en simulation et à quelle échelle. Les familles nommées sont classiques et documentées dans la littérature ; **les performances chiffrées à 30 agents hétérogènes ne sont PAS prouvées** (sauf mention contraire) → toute perf annoncée serait `[EXTRAP]`/`[HYP]`.

### B.1 — Perception / fusion multi-capteurs et multi-agents

**Fonction :** estimer l'état (pose/attitude/vitesse) par plateforme + consolider une image tactique (pistes) au niveau Edge. Mappe `onboard.perception`, `edge.fusion`.

| Famille | Complexité | Données requises | Robuste perte de lien | Calcul | Maturité | Evidence |
|---|---|---|---|---|---|---|
| Filtre complémentaire / EKF/UKF local | Faible–moyenne | IMU, GNSS, odométrie, baro | **Oui** (local) | Faible | Mature | HIGH |
| Fusion de pistes multi-agents (association + covariance) | Moyenne–élevée | pistes des pairs, horodatage | Partielle (dégrade en isolé) | Moyen | Moyenne | MEDIUM |
| SLAM / VIO par facteur-graphe (coopératif) | Élevée | caméra/LiDAR, boucles, échanges | Faible en isolé fort | Élevé | Émergente | MEDIUM/LOW |
| Apprentissage profond (détection/fusion) | Élevée | jeu de données étiqueté, GPU | Variable | Élevé | Émergente | LOW (transfert essaim) |

- **Recommandation :** fusion **hiérarchique** — EKF/UKF local par plateforme (socle safety) + fusion de pistes au niveau **Edge** (association + covariance, pas de consensus dur). Déport de tout traitement lourd hors plateforme (conforme §2.5 du doc).
- **Alternative :** SLAM/VIO coopératif **uniquement** en zone GNSS-dégradée critique, en brique optionnelle non-safety.
- **À valider en simulation :** cohérence des covariances sous désynchronisation d'horloge (t_publish/t_valid), taux de fausses associations sous partition, à **30 agents** et en scénario dense.
- Evidence level : **MEDIUM** (le socle local est HIGH ; la fusion multi-agents hétérogènes à cette échelle n'est pas un résultat établi).

### B.2 — Navigation GNSS-dégradé

**Fonction :** maintenir une estimation de position exploitable sous GNSS brouillé/dégradé. Mappe `onboard.perception`, `onboard.autopilot`, `onboard.safety`.

| Famille | Complexité | Données requises | Robuste perte de lien | Calcul | Maturité | Evidence |
|---|---|---|---|---|---|---|
| INS / odométrie morte (dead-reckoning) | Faible | IMU, roue/air | **Oui** | Faible | Mature | HIGH |
| Fusion IMU+odom+GNSS (EKF, ex. logique EKF2) | Moyenne | multicapteur | **Oui** | Faible–moyen | Mature | HIGH |
| VIO / odométrie visuelle | Moyenne–élevée | caméra + IMU | Oui (local) | Moyen–élevé | Mature hors essaim | MEDIUM |
| Estimation relative inter-agents (ranging UWB/vision) | Moyenne–élevée | lien de mesure inter-agents | Partielle | Moyen | Émergente | LOW/MEDIUM |
| SLAM coopératif GNSS-denied | Élevée | capteurs riches + échanges | Faible en isolé | Élevé | Émergente | LOW |

- **Recommandation :** défaut = **fusion IMU+odom+GNSS par EKF, avec bascule automatique VIO** quand GNSS perdu, et **réduction de zone + RTL si dérive > seuil** (conforme §7 du doc). C'est la pratique standard des autopilotes (`[FAIT]` capacité générale ; paramétrage réel = à valider).
- **Alternative :** estimation relative inter-agents (ranging) pour maintenir la cohésion du groupe en GNSS-denied, à n'activer qu'en mode DEGRADED.
- **À valider :** scénario de brouillage progressif vs brutal, sur **toutes** les classes (UAV-R, UAV-F, USV avec dynamique marine différente), à 5 puis 30 plateformes ; métrique = erreur de position vs temps sans GNSS, taux de RTL déclenchés à tort (faux positifs).
- Evidence level : **MEDIUM** (socle standard HIGH ; robustesse essaim hétérogène sous brouillage = non démontrée ici).

### B.3 — Allocation de tâches (task allocation)

**Fonction :** attribuer des tâches aux 30 plateformes, de façon robuste au lien. Mappe `onboard.task-auction`, `edge.coordinator`, `c2.planner`.

| Famille | Complexité | Données requises | Robuste perte de lien | Calcul | Maturité | Evidence |
|---|---|---|---|---|---|---|
| Centralisée (MILP/métaheuristique au C2) | Élevée (résolution) | vue globale | **Faible** | Élevé central | Mature | HIGH (en central) |
| Enchères décentralisées (type CBBA, marché) | Moyenne | tâches + capacité locale | **Élevée** | Moyen onboard | Mature en labo | HIGH (publication) |
| Consensus / consensus éventuel (états partagés) | Moyenne | voisinage | Élevée | Faible–moyen | Mature | HIGH |
| RL multi-agents (MARL) | Élevée | entraînement massif | Variable | Élevé | Émergente | LOW |

- **Recommandation :** **hybride** conforme au §2.2 du doc — **enchères embarquées par défaut** (robuste sous partition), **replanification C2** quand le lien est disponible. La famille CBBA (Consensus-Based Bundle Algorithm) est l'ancrage académique de référence (source primaire MIT ACL, cf. Sources).
- **Alternative :** allocation centralisée pure si l'on peut garantir le lien (non le cas ici).
- **À valider :** convergence des enchères sous partition et sous agents perdus (tâches orphelines par lease_expiry), qualité vs optimum central, à 30 agents ; métrique = makespan, % tâches orphelines ré-attribuées, temps de convergence.
- Evidence level : **HIGH** pour l'existence/maturité de la famille (publications primaires) ; **LOW** pour le gain quantitatif à 30 agents hétérogènes (aucune mesure propre).

### B.4 — Coordination sous partition (split-brain, reconvergence)

**Fonction :** maintenir une vue partagée cohérente malgré partitions, sans consensus global dur. Mappe `onboard.link`, `edge.coordinator`, `edge.cache`.

| Famille | Complexité | Données requises | Partition-tolérante | Calcul | Maturité | Evidence |
|---|---|---|---|---|---|---|
| Consensus dur (Raft/Paxos) | Moyenne | quorum, lien stable | **Non** | Moyen | Mature mais inadapté | HIGH (existence) / inadapté |
| CRDT / LWW + horloges logiques | Moyenne | métadonnées version | **Oui** | Faible | Mature | HIGH |
| Consensus éventuel versionné (inspiré log répliqué) | Moyenne–élevée | log + versions | Oui | Moyen | Émergente | MEDIUM |
| Mémoire partagée de flotte (swarm blackboard) | Moyenne | stockage distribué | Oui | Moyen | Émergente | LOW |

- **Recommandation :** **CRDT simple / LWW + horloges logiques** (déjà au §5.3 du doc) + règle de résolution **par rôle (C2 > Edge > Onboard)**. Ne **jamais** exiger de quorum global : un Raft/Paxos sur l'essaim serait un anti-pattern (voir la piste de recherche « SwarmRaft » au corpus, qui **cherche** précisément à rendre un consensus exploitable en essaim — statut recherche, pas produit).
- **Alternative :** consensus éventuel versionné si l'on veut une convergence plus forte sans quorum (à valider).
- **À valider :** convergence après reconnexion ≤ T_reconv (ex. 30 s) dans ≥ 95 % des cas sur **1000 graines** ; scénario split-brain à 2 et 3 partitions simultanées, à 30 agents.
- Evidence level : **HIGH** (CRDT/LWW), **MEDIUM** (règles de résolution par rôle à 30 agents).

### B.5 — Planification (mission, trajectoire, couverture)

**Fonction :** générer plans embarquables + trajectoires sous contraintes (énergie, zone, dynamique). Mappe `c2.planner`, `onboard.mission`, optionnellement `onboard.perception`.

| Famille | Complexité | Données requises | Robustesse dégradée | Calcul | Maturité | Evidence |
|---|---|---|---|---|---|---|
| Planification par grille (A*/D*), waypoints | Faible–moyenne | carte, occupancie | Élevée (embarquée) | Faible | Mature | HIGH |
| Optimisation par échantillonnage (RRT*, PRM) | Moyenne–élevée | espace d'état, collisions | Élevée (embarquée possible) | Moyen–élevé | Mature | HIGH |
| Optimisation par modèle (MPC) | Élevée | modèle dynamique, horizon | Moyenne (calcul) | Élevé | Mature en littérature | MEDIUM |
| RL / apprentissage (planification) | Élevée | entraînement, sim | Variable | Élevé | Émergente | LOW |
| Allocation-production combinée (plan+affectation) | Élevée | vue globale | Faible (C2) | Élevé | Moyenne | MEDIUM |

- **Recommandation :** **plan embarqué figé/versionné** (waypoints + règles) par défaut, **MPC court-horizon** au niveau Edge pour la coordination de proximité si ressource le permet, **Ré-optimisation C2** en différé. Aligné §2.5 (traitement lourd hors plateforme).
- **Alternative :** RRT*/MPC onboard pour UAV-R riches en calcul ; planification purement grille pour UAV-F/USV contraints.
- **À valider :** temps de recalcul en scénario dynamique, dégradation quand le calcul est déporté mais le lien coupé ; à 30 agents, métrique = temps de (re)planification p95, faisabilité énergie.
- Evidence level : **HIGH** (familles classiques) ; **MEDIUM/LOW** sur l'application hétérogène 30 agents.

### B.6 — Évitement de collision / déconfliction spatiale

**Fonction :** garantir la séparation inter-agents et vs obstacles, localement et sans C2. Mappe `onboard.safety`, `onboard.perception`, `edge.coordinator`.

| Famille | Complexité | Données requises | Sans lien | Calcul | Maturité | Evidence |
|---|---|---|---|---|---|---|
| Champs de potentiel / forces répulsives (inspiré Boids) | Faible | positions voisines | **Oui** | Faible | Mature | MEDIUM |
| Règles de géométrie (collision cone) | Moyenne | positions/vitesses | Oui | Faible–moyen | Mature | MEDIUM |
| **Control Barrier Functions (CBF)** | Moyenne–élevée | modèle + contraintes | Oui (réactif) | Moyen | Émergente (preuves de sûreté) | MEDIUM |
| Planification déconflictée (espacetemps, priorisée) | Élevée | trajectoires + priorité | Partielle | Élevé | Mature en ATM | MEDIUM |
| RL sûr (safety-shielded) | Élevée | entraînement + bouclier | Variable | Élevé | Émergente | LOW |

- **Recommandation :** **couche sûreté embarquée non négociable** = géofence + séparation de proximité par **règles géométriques/CBF**, indépendante du lien et des algorithmes d'allocation (conforme §4.1 `onboard.safety` Safety-Critical). CBF est la famille la plus prometteuse pour donner une **garantie formelle locale** ; plusieurs preprints/prépublications récentes l'explorent pour multi-UAV (cf. corpus, `Non vérifié` au niveau revue).
- **Alternative :** champs de potentiel/Boids (socle simple, robuste) + déconfliction globale au C2/Edge quand le lien existe.
- **À valider :** taux de violations d'espace ≤ 1 % des pas de temps en scénario dense (critère §9.2 du doc) ; scénarios d'urgence (perte de lien + obstacle dynamique + agent défaillant), à **30 agents** ; vérifier l'absence de minima locaux et de « deadlocks » d'évitement.
- Evidence level : **MEDIUM** (CBF documentée ; preuve à 30 agents hétérogènes sous décision distribuée = non établie).

### B.7 — Sûreté (safety) : garanties et comportement dégradé

**Fonction :** garantir que la plateforme reste sûre indépendamment du lien, du cloud et des autres agents. Mappe `onboard.safety`, `onboard.energy`.

| Famille | Complexité | Données requises | Sans lien | Calcul | Maturité | Evidence |
|---|---|---|---|---|---|---|
| Règles/réflexes embarqués (geofence, RTL, seuils) | Faible | état local | **Oui** | Faible | Mature | HIGH |
| Barrières de sûreté (CBF) locales | Moyenne | modèle + contraintes | Oui | Moyen | Émergente | MEDIUM |
| Surveillance/commutateurs (watchdog, monitor) | Faible | télémétrie interne | Oui | Faible | Mature | HIGH |
| Vérification formelle / atteignabilité | Élevée | modèle formel | Oui (offline) | Élevé (offline) | Émergente | LOW |
| Monte-Carlo adversarial multi-graines | Moyenne | sim + injection pannes | n/a | Élevé (offline) | Mature (pratique) | MEDIUM |

- **Recommandation :** socle = **règles embarquées pré-approuvées** (H5 du doc) + **watchdog indépendant** ; CBF en renfort pour la séparation ; **validation par Monte-Carlo adversarial** (§9.1 du doc, N≥1000 graines) avec injection **simultanée** de pannes (lien + GNSS + agent) et non pas séquentielle.
- **Alternative :** approche formelle par atteignabilité sur un modèle réduit (par plateforme), utile pour argumenter la sûreté, mais **coûteuse** et limitée à des modèles simplifiés.
- **À valider :** le critère le plus dur du doc — « mission nominale complétée sans lien C2 ≥ 80 % de la durée » — **et** le non-déclenchement de RTL intempestifs ; à 30 agents, sur 1000 graines.
- Evidence level : **MEDIUM** (règles embarquées = HIGH ; garantie globale essaim = non démontrée).

---

## §C — Angles morts

Revue **volontairement agressive**. Gravité : **critique** = compromet la faisabilité ou la sécurité du système ; **majeur** = dégrade fortement ou surprend en cours de route ; **mineur** = à surveiller.

### AM-1 — Arbitrage de licence non tranché (PX4 BSD-3 vs ArduPilot GPLv3) — **critique**
- **Énoncé :** le doc de référence ne fige aucun socle logiciel, donc laisse ouverte une décision *juridique* structurante (copyleft vs permissif) qui contraint tout le reste.
- **Pourquoi angle mort :** le §10 traite des conflits techniques inter-vues, jamais du droit logiciel. Or « distribuer un firmware GPLv3 modifié » déclenche des obligations.
- **Conséquence :** refonte coûteuse si l'on part sur ArduPilot puis découvre une exigence de fermeture, ou l'inverse.
- **Recommandation :** **couvrir** — décision programme explicite, écrite, avant tout développement.

### AM-2 — Exposition AGPLv3 / licences source-available dans le Cloud — **majeur**
- **Énoncé :** le stack Cloud primaire proposé (MinIO AGPLv3, Grafana AGPL-3.0) et l'écosystème Kafka (caveat Confluent) introduisent des obligations fortes dès exposition réseau de versions modifiées.
- **Pourquoi angle mort :** l'architecture « cloud hors boucle » a été pensée fonctionnellement, pas juridiquement.
- **Conséquence :** obligation de publier des modifications, blocage d'un modèle SaaS ou commercial.
- **Recommandation :** **couvrir** — revue licences + alternance de briques si nécessaire (S3 commercial, stockage à licence permissive).

### AM-3 — Télémétrie/consommation radio à 30 agents non dimensionnée physiquement — **critique**
- **Énoncé :** le §8 du doc donne 1–10 Hz/agent « delta-compressée » mais **le budget radio total n'est pas calculé**, ni la contention de créneaux à 30 agents.
- **Pourquoi angle mort :** à 30 agents + Edge, la densité et la contention sont non linéaires (§2.1 du doc le reconnaît sans le traiter).
- **Conséquence :** saturation, perte de messages critiques de sûreté, dégradation en cascade.
- **Recommandation :** **couvrir** — modèle de budget radio et simulation de contention (`[SIM]` obligatoire) ; c'est un prérequis, pas un raffinement.

### AM-4 — Perception/fusion « d'essaim » sans brique ni métrique — **majeur**
- **Énoncé :** `onboard.perception`/`edge.fusion` sont décrits fonctionnellement mais **aucun algorithme, aucun critère, aucun jeu de données** n'est associé (voir §A.5 et §B.1).
- **Pourquoi angle mort :** la fusion multi-agents hétérogènes est **le** cœur de valeur et aussi le plus dur.
- **Conséquence :** sous-estimation de l'effort ; impossibilité de mesurer la qualité de l'image tactique.
- **Recommandation :** **couvrir** — spécifier métriques (P_d, taux fausses pistes, latence de fusion) et données de test.

### AM-5 — Validation d'échelle : 2→5→12→30 en vol réel est irréaliste à budget constant — **critique**
- **Énoncé :** le §9.1 propose un vol réel progressif 2 → 5 → 12 → 30 avec coupe-lien forcée à chaque palier.
- **Pourquoi angle mort :** 30 plateformes hétérogènes en vol simultané = coût, logistique, réglementation (BVLOS, zones) **énormes** ; la faisabilité programmatique n'est pas évaluée.
- **Conséquence :** le critère d'acceptation « à 30 agents » risque de **n'être jamais mesuré en réel** — validation uniquement simulée, donc evidence plafonnée.
- **Recommandation :** **couvrir + accepter** — définir explicitement quels critères sont prouvés en SIL/HIL/digital twin et lesquels exigent le réel ; plafond d'échelle réelle réaliste (ex. 5–12).

### AM-6 — Désynchronisation d'horloge / cohérence temps distribué — **majeur**
- **Énoncé :** le doc repose sur `t_publish`/`t_valid` mais **ne spécifie pas** la synchronisation d'horloge inter-plateformes (PTP/GNSS-time) ni son comportement en GNSS-dégradé.
- **Pourquoi angle mort :** sans temps cohérent, la fraîcheur déclarée et les versions (LWW) deviennent fausses → décisions basées sur données périmées.
- **Conséquence :** fusion incohérente, conflits de version mal résolus, régressions silencieuses.
- **Recommandation :** **couvrir** — spécifier source de temps, garde-fous en perte de GNSS, et tester la dérive d'horloge.

### AM-7 — Cybersécurité du lien montant et de l'autopilote — **critique**
- **Énoncé :** le doc mentionne chiffrement/signature et quarantaine, mais **pas** de modèle de menaces, ni de surface d'attaque autopilote (MAVLink/DDS non authentifiés par défaut), ni de gestion de clés embarquée.
- **Pourquoi angle mort :** un essaim est une cible à fort effet de levier (une clé compromise = flotte compromise) ; le conflit sûreté/sécurité (§10.3) est reconnu mais non résolu en conception.
- **Conséquence :** prise de contrôle, injection d'ordres, ou déni de service provoquant des chutes.
- **Recommandation :** **couvrir** — modèle de menaces STRIDE, authentification des liens (mTLS/DDS-Security), rotation de clés, red-teaming.

### AM-8 — Cadre réglementaire & conformité (BVLOS, COLREGs, espace aérien) — **majeur**
- **Énoncé :** aucune section du doc ne traite la réglementation du vol BVLOS d'essaim ni la navigation maritime (COLREGs pour les 4 USV, qui imposent des règles d'évitement normatives).
- **Pourquoi angle mort :** un USV autonome doit respecter COLREGs ; un essaim d'UAV BVLOS doit obtenir autorisations. Ce sont des **contraintes de conception**, pas des formalités.
- **Conséquence :** impossibilité légale d'exploiter, ou refonte des comportements d'évitement pour conformité.
- **Recommandation :** **couvrir** — cartographier les obligations par domaine et les intégrer comme exigences.

### AM-9 — Gestion énergétique hétérogène & effet « mission impossible » — **majeur**
- **Énoncé :** `onboard.energy` existe pour chaque plateforme, mais **aucune allocation globale d'énergie** : un UAV-F (longue portée, faible manœuvrabilité) et un UAV-R (courte autonomie) n'ont pas les mêmes budgets.
- **Pourquoi angle mort :** l'allocation de tâches (§B.3) doit être **contrainte par l'énergie**, sinon on attribue une tâche à un agent qui ne peut pas la terminer.
- **Conséquence :** tâches orphelines, RTL en série, mission non complétée.
- **Recommandation :** **couvrir** — intégrer la contrainte énergie dans le coût d'enchère (CBBA pondéré énergie).

### AM-10 — Handover inter-domaines (UAV↔USV) : définitions et responsabilités floues — **majeur**
- **Énoncé :** le doc mentionne les rôles de passerelle et les « handoffs », mais **ne définit pas** qui détient l'autorité lors d'un transfert de tâche d'un UAV à un USV (frames, unités, carte, niveau de confiance).
- **Pourquoi angle mort :** le cross-domain est justement la complexité revendiquée de l'architecture hétérogène.
- **Conséquence :** double exécution d'une tâche (UAV et USV croient tous deux en être responsables) ou abandon de tâche.
- **Recommandation :** **couvrir** — protocole de handoff explicite (lease + acquittement + bascule de frame) et tests dédiés.

### AM-11 — Modèle de données / ontologie commun non spécifié — **mineur**
- **Énoncé :** aucun schéma commun (unités, frames, sémantique des tâches) n'est fixé pour `cloud.twin` et `edge.fusion`.
- **Pourquoi angle mort :** trois classes de plateformes avec capteurs et dynamiques différents doivent échanger un vocabulaire commun.
- **Conséquence :** intégrations ad hoc, dette technique, jumeau numérique divergent du réel.
- **Recommandation :** **surveiller** — définir tôt un schéma minimal versionné (sinon dette difficile à résorber).

### AM-12 — Comportement en cas d'agent défaillant / perdu (pas seulement lien) — **majeur**
- **Énoncé :** le doc traite la perte de lien, mais **pas** la perte d'un agent (panne moteur, chute, échouage USV) ni la réintégration d'un agent revenu.
- **Pourquoi angle mort :** un agent défaillant crée une tâche orpheline ET potentiellement un danger (chute sur une trajectoire).
- **Conséquence :** collision avec l'agent défaillant, tâche perdue, faux positif de partition.
- **Recommandation :** **couvrir** — heartbeat + détection de défaillance + diffusion de zone d'exclusion temporaire.

### AM-13 — Observabilité et rejeu : que rejoue-t-on exactement ? — **mineur**
- **Énoncé :** `cloud.replay-store` existe sans spécifier **quoi** enregistrer (décisions, entrées/capteurs, horodatages, versions de plan).
- **Pourquoi angle mort :** « rejouer une décision » exige d'enregistrer aussi les entrées et l'aléa (graine).
- **Conséquence :** rejeu non déterministe → impossible de reproduire un incident.
- **Recommandation :** **couvrir** — spécifier le contrat de trace (déterminisme, graines, versions).

### AM-14 — Bruit/fausses détections non quantifiés (P_d, P_fa) — **majeur**
- **Énoncé :** les critères §9 mentionnent P_d et P_fa mais **aucune valeur cible n'est fixée** ni les conditions de mesure.
- **Pourquoi angle mort :** ces probabilités conditionnent toute la fusion et le sense-and-avoid.
- **Conséquence :** critères d'acceptation non testables.
- **Recommandation :** **couvrir** — fixer P_d/P_fa cibles par capteur et par scénario.

### AM-15 — Sûreté épistémique du jumeau numérique (fidélité) — **majeur**
- **Énoncé :** le doc s'appuie sur un jumeau numérique pour valider, mais **aucune procédure de synchronisation/fidélité** (évaluation d'écart sim↔réel) n'est prévue.
- **Pourquoi angle mort :** valider en sim n'a de valeur que si la sim est fidèle ; or celle-ci dérive.
- **Conséquence :** critères « validés » en sim qui échouent au réel.
- **Recommandation :** **couvrir** — métrique de fidélité (écart de trajectoire, d'énergie, de timing de lien), campagne de recalibration.

### AM-16 — Facteur humain et charge du C2 — **mineur**
- **Énoncé :** l'autorité humaine est posée (§9) mais la **charge cognitive** d'un opérateur supervisant 30 agents n'est pas évaluée.
- **Pourquoi angle mort :** le C2 devient un goulot humain sous incertitude.
- **Conséquence :** décisions tardives, non-respect des garde-fous de temps.
- **Recommandation :** **surveiller** — mesures de charge (temps de décision, taux d'escalades).

---

## §D — Risques

Catégories : technique / science / sécurité / opérationnel / réglementaire / programme.
Probabilité et impact : faible / moyen / élevé. **Criticité** = P×I (faible/moyenne/élevée) — sert au tri.

### R-1 — Contention/saturation radio à 30 agents — technique — P élevée / I élevé — **critique**
- **Mitigation :** budget radio modélisé, CSF/QoS par criticité, delta-compression, priorisation des messages de sûreté, repli en mode dégradé autonome.
- **Alerte précoce :** taux de perte de messages critiques > 1 % ; latence p95 > budget §8.

### R-2 — Prise de contrôle / injection via lien ou autopilote non authentifié — sécurité — P moyenne / I élevé — **critique**
- **Mitigation :** mTLS/DDS-Security, signature des ordres critiques, PKI embarquée + rotation, red-team, quarantaine (déjà prévue §7).
- **Alerte précoce :** ordres non signés détectés ; tentatives d'authentification échouées.

### R-3 — Validation réelle à 30 agents non réalisable (coût/réglementation) — programme — P élevée / I élevé — **critique**
- **Mitigation :** plafonner l'échelle réelle, pousser SIL/HIL/digital twin, définir explicitement ce qui est prouvé par modalité et l'exposer comme tel.
- **Alerte précoce :** glissement du calendrier de campagne ; refus d'autorisation BVLOS.

### R-4 — Perte de cohérence sous partition / split-brain — technique — P moyenne / I élevé — **critique**
- **Mitigation :** CRDT/LWW + résolution par rôle, pas de quorum global, lease expiry, tests de reconvergence multi-partitions.
- **Alerte précoce :** divergence de versions détectée ; reconvergence > T_reconv.

### R-5 — Dérive en GNSS-dégradé (position) — technique/science — P moyenne / I élevé — **critique**
- **Mitigation :** EKF + bascule VIO, réduction de zone, RTL sur seuil de dérive, validation brouillage progressif/brutal.
- **Alerte précoce :** croissance de l'incertitude de position ; RTL multiples.

### R-6 — Non-conformité réglementaire (BVLOS, COLREGs, espace) — réglementaire — P moyenne / I élevé — **élevée**
- **Mitigation :** cartographie réglementaire par domaine, intégration des règles d'évitement maritimes en conception, dossier d'autorisation précoce.
- **Alerte précoce :** exigences nouvelles d'une autorité ; refus de zone.

### R-7 — Conflit de licence bloquant la distribution (GPLv3/AGPL/Confluent) — programme — P moyenne / I moyen — **moyenne**
- **Mitigation :** décision écrite du socle, revue juridique des briques AGPL, alternatives permissives.
- **Alerte précoce :** découverte d'une obligation d'ouverture non anticipée.

### R-8 — Fusion/perception dégradée en scénario dense (fausses pistes) — science — P moyenne / I moyen — **moyenne**
- **Mitigation :** métriques P_d/P_fa cibles, fusion Edge avec covariance, tests denses à 30 agents.
- **Alerte précoce :** taux de fausses pistes au-delà de la cible ; latence de fusion hors budget.

### R-9 — Collision en scénario d'urgence (lien coupé + agent défaillant) — opérationnel — P faible-moyenne / I élevé — **élevée**
- **Mitigation :** couche sûreté embarquée (CBF/geométrie) indépendante du lien, zone d'exclusion de l'agent défaillant, Monte-Carlo adversarial.
- **Alerte précoce :** violations d'espace > 1 % des pas ; minima locaux d'évitement.

### R-10 — Désynchronisation d'horloge (données périmées prises pour fraîches) — technique — P moyenne / I moyen — **moyenne**
- **Mitigation :** source de temps spécifiée, garde-fous en perte de GNSS, tests de dérive.
- **Alerte précoce :** écart d'horloge inter-plateformes > seuil ; cohérence t_publish/t_valid invalidée.

### R-11 — Fidélité du jumeau numérique insuffisante (critères validés à tort) — science — P moyenne / I moyen — **élevée**
- **Mitigation :** métriques de fidélité sim↔réel, recalibration, campagnes de vérification croisée.
- **Alerte précoce :** écart de trajectoire/énergie/timing au-delà du seuil.

### R-12 — Tâches orphelines par non-prise en compte de l'énergie — opérationnel — P moyenne / I moyen — **moyenne**
- **Mitigation :** coût d'enchère pondéré énergie, seuils de repli, suivi énergie par plateforme.
- **Alerte précoce :** RTL en série ; taux de tâches non terminées.

### R-13 — Effort de R&D sous-estimé sur la fusion multi-agents hétérogènes — programme/science — P élevée / I moyen — **élevée**
- **Mitigation :** découper la brique, définir métriques et données de test précoces, prévoir une phase d'intégration dédiée.
- **Alerte précoce :** dérive du planning sur `edge.fusion`.

### R-14 — Charge C2 humaine excessive sous incertitude — opérationnel — P moyenne / I moyen — **moyenne**
- **Mitigation :** automatiser les bascules pré-approuvées, escalades graduées, mesures de charge.
- **Alerte précoce :** temps de décision croissant ; escalades en rafale.

### R-15 — Handoff inter-domaines ambigu (double exécution / abandon) — technique/opérationnel — P moyenne / I faible-moyen — **moyenne**
- **Mitigation :** protocole lease+acquittement, tests de handoff, journalisation.
- **Alerte précoce :** tâches exécutées deux fois ; tâches abandonnées sans trace.

### Tableau récapitulatif §D (trié par criticité décroissante)

| ID | Catégorie | P | I | Criticité | Mitigation-clé |
|---|---|---|---|---|---|
| R-1 | Technique | élevée | élevé | **critique** | Budget radio + QoS par criticité |
| R-2 | Sécurité | moyenne | élevé | **critique** | mTLS/DDS-Security + signature + PKI |
| R-3 | Programme | élevée | élevé | **critique** | Plafond échelle réelle + SIL/HIL |
| R-4 | Technique | moyenne | élevé | **critique** | CRDT/LWW + pas de quorum global |
| R-5 | Technique/science | moyenne | élevé | **critique** | EKF+VIO + RTL sur dérive |
| R-6 | Réglementaire | moyenne | élevé | élevée | Cartographie réglementaire précoce |
| R-9 | Opérationnel | faible-moy. | élevé | élevée | Sûreté embarquée indépendante du lien |
| R-11 | Science | moyenne | moyen | élevée | Métriques de fidélité sim↔réel |
| R-13 | Programme/science | élevée | moyen | élevée | Découpage + métriques précoces |
| R-7 | Programme | moyenne | moyen | moyenne | Décision licence écrite |
| R-8 | Science | moyenne | moyen | moyenne | P_d/P_fa cibles + fusion Edge |
| R-10 | Technique | moyenne | moyen | moyenne | Source de temps + tests dérive |
| R-12 | Opérationnel | moyenne | moyen | moyenne | Enchère pondérée énergie |
| R-14 | Opérationnel | moyenne | moyen | moyenne | Bascules auto + escalades graduées |
| R-15 | Technique/opérat. | moyenne | faible-moy. | moyenne | Protocole lease+acquittement |

---

## §E — Impacts sur le modèle LikeC4

### E.1 — Éléments à AJOUTER (nouvelles entités)

- `tech.software.*` — une entité par brique §A, avec attributs : `licence`, `maturite`, `version`, `role` (PRIMARY/SECONDARY), `zone`.
  Ex. : `tech.software.OsAutopilot.PX4`, `tech.software.Middleware.Zenoh`, `tech.software.Gcs.QGroundControl`, `tech.software.Cloud.GazeboSim`, `tech.software.Cloud.MinIO`.
- `tech.algo.*` — une entité par famille candidate §B, attributs : `famille`, `complexite`, `robustesse_lien`, `calcul`, `maturite`, `evidence`.
  Ex. : `tech.algo.TaskAllocation.CBBA`, `tech.algo.Safety.CBF`, `tech.algo.Coordination.CRDT`.
- `risk.*` — une entité par risque §D, attributs : `categorie`, `probabilite`, `impact`, `criticite`, `mitigation`, `alerte_precoce`.
- `blindspot.*` — une entité par angle mort §C, attributs : `gravite`, `statut` (couvrir/accepter/surveiller), `consequence`.

### E.2 — Relations à AJOUTER

- `onboard.* | edge.* | c2.* | cloud.* -> tech.software.*` : relation **« est implémenté par »** (avec `role = PRIMAIRE/SECONDAIRE`).
- `onboard.* | edge.* | c2.* -> tech.algo.*` : relation **« s'appuie sur »**.
- `tech.software.* -> risk.*` : relation **« est exposé à »** (traçabilité brique→risque).
- `tech.algo.* -> blindspot.*` : relation **« ne couvre pas »** (ce qu'un algorithme choisi laisse ouvert).
- `tech.software.* -> tech.software.*` : relation **« substitue / alternative à »** (primaire ↔ secondaires).

### E.3 — Attributs / tags utiles (transverses)

- Tags : `#safety-critical`, `#licence-copyleft`, `#licence-permissive`, `#source-available`, `#non-verifie`, `#extrapolation`, `#evidence-high|medium|low`, `#zone-onboard|edge|c2|cloud`.
- Attribut `evidence_level` obligatoire sur tout élément matériel (§A et §B) — sinon `Non vérifié`.

### E.4 — Vues nouvelles à produire (2–3)

1. **Vue « Choix technologiques » (`view technoChoices`)** : diagramme composants `onboard/edge/c2/cloud` → briques primaires ; les secondaires en note/tag. Permet de voir d'un coup d'œil le socle retenu.
2. **Vue « Matrice de risques » (`view riskMatrix`)** : les `risk.*` positionnés par `probabilite`×`impact`, colorés par `criticite`, reliés aux composants qu'ils affectent.
3. **Vue « Angles morts par gravité » (`view blindspotBySeverity`)** : les `blindspot.*` groupés par gravité, reliés aux fonctions candidat non couvertes (perception, handoff, énergie…).

> Note d'illustration : le document de référence `SwarmOS` cité par le projet n'est utilisé ici que comme **exemple de structure** (éléments/relations/vues), jamais comme preuve scientifique.

---

## Conclusion opérationnelle (synthèse exécutive)

- **§A :** aucune brique « perception d'essaim hétérogène » n'existe sur étagère ; le socle (autopilote, middleware, GCS, simulation) est mûr et sous licences connues. **Décision juridique de licence non tranchée** = premier verrou.
- **§B :** les familles sont classiques et bien ancrées ; **les performances à 30 agents hétérogènes ne sont PAS établies** — tout chiffre serait une extrapolation. Priorité de validation : radio, GNSS-dégradé, reconvergence, sûreté.
- **§C :** 16 angles morts dont **4 critiques** (AM-1 licence, AM-3 radio, AM-5 échelle réelle, AM-7 cybersécurité).
- **§D :** 15 risques dont **5 critiques** (R-1, R-2, R-3, R-4, R-5).
- **§E :** le modèle LikeC4 doit gagner 4 familles d'entités (`tech.software`, `tech.algo`, `risk`, `blindspot`), des relations de traçabilité, et 3 vues.

**Prochaine étape recommandée (discriminante) :** un benchmark reproductible de **budget radio + reconvergence + sûreté** à 5 puis 30 agents en SIL, multi-graines (N ≥ 1000), avant tout engagement matériel — car c'est le point où l'architecture est la plus faible et la plus facile à trancher par l'expérience.

---

## Sources

Sources primaires réelles consultées lors de cette session (existence/licence/capacités) :

- PX4 Autopilot — dépôt & documentation : https://github.com/PX4/PX4-Autopilot ; https://px4.io/
- ArduPilot — documentation « Swarming » (leader/followers) : https://ardupilot.org/planner/docs/swarming.html ; https://ardupilot.org/
- MAVLink — protocole et génération : https://mavlink.io/ ; https://github.com/mavlink/mavlink
- MAVSDK — https://github.com/mavlink/MAVSDK
- QGroundControl — https://github.com/mavlink/qgroundcontrol ; https://qgroundcontrol.com/
- ROS 2 — https://docs.ros.org/ ; https://github.com/ros2
- eProsima Fast DDS — https://github.com/eProsima/Fast-DDS ; https://www.eprosima.com/
- eProsima Micro XRCE-DDS — https://github.com/eProsima/Micro-XRCE-DDS ; micro-ROS : https://micro.ros.org/
- Eclipse Zenoh — https://github.com/eclipse-zenoh/zenoh ; https://zenoh.io/
- Eclipse Mosquitto (MQTT) — https://github.com/eclipse/mosquitto ; https://mosquitto.org/
- Gazebo Sim (gz-sim) — https://github.com/gazebosim/gz-sim ; https://gazebosim.org/
- Apache Kafka — https://kafka.apache.org/ ; https://github.com/apache/kafka
- Prometheus — https://github.com/prometheus/prometheus ; Grafana — https://github.com/grafana/grafana
- MinIO — https://github.com/minio/minio ; https://min.io/
- PostgreSQL — https://www.postgresql.org/ ; PostGIS — https://postgis.net/
- OpenCPN — https://opencpn.org/ ; https://github.com/OpenCPN/OpenCPN
- Signal K — https://signalk.org/ ; OpenStreetMap/Nominatim — https://www.openstreetmap.org/ ; https://nominatim.org/
- Piste comparative débit/latence Zenoh/MQTT/Kafka (preprint) — arXiv:2303.09419 : https://arxiv.org/abs/2303.09419
- CBBA (Consensus-Based Bundle Algorithm) — trace académique MIT ACL, p. ex. https://acl.mit.edu/ (source primaire de la famille, à reciter précisément au niveau de l'AIA4J/AIAA)

**Corpus local consulté (pistes, non preuve de revendication) :** `/home/hermesagent/swarmdrone-research/catalog.json` (1011 entrées ; quasi exclusivement `DISCOVERED`/`METADATA_VERIFIED`, 2 seuls `PRIMARY_SOURCE_VERIFIED`) et `quality-ledger.json`.

**Statuts épistémiques utilisés :** `[FAIT]` = existence/licence/capacité vérifiée à la source ; `[SIM]` = à établir par simulation ; `[HYP]` = hypothèse ; `[EXTRAP]` = extrapolation au-delà des preuves ; `Non vérifié` = non établi dans cette session.






