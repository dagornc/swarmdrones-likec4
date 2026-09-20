# ADR — H-Zip v2.1 : arbitrage de la cible « Protocole », figement des paramètres et borne de divergence

Date : 2026-09-20
Auteur : Architecte (carte kanban t_53fee5f0, suite du lot H-Zip)
Statut : DECIDE (modèle LikeC4 mis à jour, `likec4 validate` Valid, gouvernance OK)
Prérequis : spécification normative H-Zip v2.1 (`H-Zip_v2.1_Specification_premium.docx`), §23.5 « en cas d'écart, la spécification fait foi ».

---

## 1. Décision 1 — Cible « Protocole »

### 1.1 Question

Demande initiale : « Place cette spécif dans le github SwarmDrones dans un algorithme appelé Protocole ».

Problème : le kind `algorithm` est déjà instancié 15 fois (`ALG_*`, famille ALGORITHMIQUE) et H-Zip est déclaré `protocol` (famille COMMUNICATION, kind distinct). Créer un `algorithm` « Protocole » dupliquerait sémantiquement `hzip`.

### 1.2 Options

| Option | Description | Avantage | Inconvénient |
|---|---|---|---|
| (a) RETENUE | Dépôt `dagornc/alg-protocole` + instance `sourceCode` reliée à `hzip` | Cohérent avec le patron `srcConsensusRs` / `srcAlgTaskAllocation` ; LikeC4 référence le code sans le contenir | Création de dépôt externe (action Christophe) |
| (b) | Renommer/étendre le kind `protocol` | Nomenclature plus riche | Touche le métamodèle, risque de régression sur 44 kinds |
| (c) | Ne rien créer, garder `hzip` seul | Aucun risque | Laisse la demande initiale sans réponse, rompt le patron multi-dépôts |

### 1.3 Décision

Option (a). `hzip` reste un `protocol` (il EST un protocole, pas un algorithme). La demande
initiale est satisfaite par l'instance `sourceCode` `srcAlgProtocole`, dépôt
`https://github.com/dagornc/alg-protocole`, rattaché au dépôt principal
`https://github.com/dagornc/SwarmDrones` en tant que sous-module (chemin `protocols/hzip`).

Relations (mêmes kinds que le patron existant, pas de nouveau kind) :

```
srcAlgProtocole -[implements]->  hzip      'implémentation de référence du protocole'
srcAlgProtocole -[documentedBy]-> specHzip 'spécification normative v2.1'
```

Précision sémantique : la carte source parlait de relier le `sourceCode` à `hzip` par
`-[documentedBy]->`. Le patron `srcConsensusRs` utilise `implements` vers l'élément
abstrait (l'algorithme) et `documentedBy` vers la spécification. Ici l'élément abstrait
est le `protocol` `hzip` : le lien code→protocole est donc `implements`, et
`documentedBy` relie le code à `specHzip`. Le modèle est ainsi homogène avec
`srcConsensusRs` / `srcAlgTaskAllocation` (aucun kind ni arc nouveau).

Renoncements : pas de création d'un 16e `algorithm` « Protocole » (évite la duplication
sémantique) ; pas de modification du métamodèle (option b écartée).

### 1.4 Action externe (autorisation Christophe requise)

La création effective du dépôt GitHub `dagornc/alg-protocole` est une action externe
(création de dépôt au nom de Christophe) : NON exécutée dans cette session. Le modèle
déclare le dépôt comme cible ; le dépôt devra être créé puis référencé en sous-module
avant toute implémentation. Aucun secret n'est manipulé ici.

---

## 2. Décision 2 — Borne de divergence (T_hb, e_max)

### 2.1 Énoncé

Borne du modèle prédictif entre deux heartbeats : `e_max = ½ · a_max · T_hb²`
(§8.4 de la spécification). La valeur indicative `a_max = 2 m/s²`, `T_hb = 10 s` donne
100 m — confirmé TROP permissif pour un essaim dense. Cible retenue : `T_hb ~ 1 s` (UAV).

### 2.2 Valeurs figées (par classe)

`a_max` et la séparation minimale `d_min` sont des bornes physiques de classe
(§8.2) ; elles sont des HYPOTHÈSES À MESURER (décisions matérielles DE-05/DE-06),
explicitement marquées comme telles. La règle de cohérence appliquée :

```
e_max(classe) ≤ min( ½·a_max(classe)·T_hb(classe)² , ε_max , 0,25·d_min(classe) )
```

| Classe | a_max (hyp.) | T_hb FIGÉ | e_max calculé | d_min (hyp.) | e_max/d_min | Verdict |
|---|---|---|---|---|---|---|
| UAV | 2,0 m/s² (donné) | 1,0 s | 1,0 m | 5 m | 20 % | OK |
| USV | 1,0 m/s² | 2,0 s | 2,0 m | 20 m | 10 % | OK |
| UUV | 0,5 m/s² | 5,0 s | 6,25 m | 30 m | 21 % | OK (renforcé par trames D à ε_base=3 m) |

### 2.3 Justification du budget de bande (trame H = 8 octets = 64 bits)

| T_hb | Débit/noeud | Essaim 200 noeuds |
|---|---|---|
| 1 s (UAV) | 64 bit/s | 12,8 kbit/s |
| 2 s (USV) | 32 bit/s | 6,4 kbit/s |
| 5 s (UUV) | 12,8 bit/s | 2,56 kbit/s |

Le heartbeat global à 1 Hz sur 200 noeuds (12,8 kbit/s) excède la capacité d'un canal
acoustique unique (100 bit/s à 10 kbit/s, Akyildiz et al. 2005). Le heartbeat est donc
LOCAL (voisinage) et la hiérarchie par hubs est INDISPENSABLE (chaque hub ne recadre
que son cluster : ≤ 20 terminaux + 1 hub → entrée hub 1,28 kbit/s).

---

## 3. Décision 3 — Les paramètres figés (valeur + justification)

Référence : table §24.1 de la spécification. Chaque valeur est justifiée par un calcul
ou une référence, pas par un choix arbitraire. Sauf mention contraire, « indicatif » de
la spécification = valeur FIGÉE, car déjà cohérente avec les bornes calculées.

| # | Paramètre | Valeur FIGÉE | Justification |
|---|---|---|---|
| 1 | `N_cluster_max` | 20 | Terminal ID 5 bits = 32 valeurs ; 20 ≤ 32 (marge 12). Entrée hub = 20×64 b = 1,28 kbit/s sur W_agg |
| 2 | `N_hub_max` | 25 | Hub ID 5 bits = 32 valeurs ; 25 ≤ 32. 200 noeuds / 25 hubs = 8 terminaux/hub (≤ 20) |
| 3 | `f_hb` / `T_hb` | UAV 1 Hz · USV 0,5 Hz · UUV 0,2 Hz | §8.6 + budget de bande (§2.3). La valeur « 0,1 Hz global » du §24.1 est SUPPRIMÉE (contredite par §8.6) |
| 4 | `e_max` | 1,0 m · 2,0 m · 6,25 m | ½·a_max·T_hb² (§2.2) ; ≤ 25 % de d_min |
| 5 | `epsilon_base` | UAV 1 m · USV 2 m · UUV 3 m | ε_base ≤ e_max pour chaque classe (UAV 1=1 ; USV 2=2 ; UUV 3<6,25) |
| 6 | `epsilon_max` | 5 m | Plafond global ≥ max(ε_base)=3 m ; borne la transmission obligatoire |
| 7 | `sigma_max` | 45° (π/4) | Seuil de conflit directionnel : au-delà d'un quadrant, le barycentre vectoriel n'est plus représentatif (§11.2) |
| 8 | `N_tx_max` | 10 /s | Rate limit trames D : 10×32 b = 320 bit/s au pire, négligeable ; le silence nominal = 0 |
| 9 | `W_agg` | 1 s | Aligné sur T_hb UAV (1 s) : agrégation à la cadence du heartbeat le plus rapide |
| 10 | `T_hb_max` (voisin perdu) | 3 × T_hb : 3 s · 6 s · 15 s | 3 heartbeats consécutifs manqués → signal « perdu ». P(faux positif) = 0,30³ = 2,7 % uniquement au pire taux de perte ; signal SOFT (effacé au heartbeat suivant) |
| 11 | `T_hub_max` (hub perdu) | 10 s (5 × T_hb USV) | P(faux positif) = 0,30⁵ = 0,24 % ; bascule = T_hub_max + T_conf = 15 s, acceptable en mission-critical (terminaux en APF seul pendant l'outage) |
| 12 | `T_conf` | 5 s | 2,5 cycles de heartbeat hub (T_hb USV 2 s) pour l'adoption du hub secondaire |
| 13 | `T_switch_min` | 60 s | Anti-oscillation : ≥ 30 × T_hb UAV ; un re-rattachement de cluster est coûteux |
| 14 | `ΔRSSI_min` | 6 dB | Hystérésis radio standard (facteur 4 en puissance) ; évite le ping-pong de rattachement |
| 15 | `T_recover` | 10 s | 10 × T_hb UAV : temps de re-synchronisation des modèles prédictifs avant réintégration PSO |
| 16 | `N_rep` | 3 | P(3 copies perdues) = 0,30³ = 2,7 % ; le heartbeat (T_hb) est le filet de sûreté ultime. N_rep=2→9 %, N_rep=4→0,81 % (rendement décroissant) |
| 17 | `P_loss_max` | 30 % | Seuil de dégradation : au-delà, la détection par heartbeat devient peu fiable et N_rep=3 ne suffit plus |
| 18 | `w_min` | 0,2 | Gain pondéré minimal accepté pour une mise à jour de gBest. min(gains matrice)=0,3 (UAV→UUV) ; w_min = 0,67 × min = plancher sous le signal le plus faible légitime, coupe le bruit |
| 19 | Matrice `w` / `τ` | §17.1 (9 gains + 9 constantes) | FIGÉE telle que proposée : gain = compatibilité dynamique (même classe 1,0 ; air→eau 0,3 ; eau→air 0,5) ; τ = nombre de cycles pour suivre (même classe 1, cross-classe 2–5) |

### Paramètres de test associés (hzip.c4)

| Test | Paramètre | Valeur FIGÉE | Justification |
|---|---|---|---|
| testHzipCrc | N (tirages) | 10 000 | 0 échec → taux de non-détection ≤ 0,03 % (IC95 unilatéral, Clopper-Pearson). CRC-8 détecte par construction tout bit-flip simple : le test vérifie l'IMPLÉMENTATION (tramage, calcul, contrôle), pas la théorie du CRC |
| testHzipLatence | cible | ≤ 20 ms | Une période de boucle à 50 Hz ; cohérent avec la couche réactive (tolérance nulle) |
| testHzipDivergence | T_hb, e_max | §2.2 | Borne du modèle prédictif |
| testHzipBande | capacité modem | À MESURER (DE-07) | Hypothèse de travail 100 bit/s – 10 kbit/s (Akyildiz 2005) ; ne pas inventer la capacité du modem retenu |

---

## 4. Corrections de cohérence modèle ↔ spécification

Le modèle `hzip.c4` contredisait la spécification normative sur les tailles de trames
(§23.5 : la spécification fait foi). Corrections appliquées :

| Élément | Avant | Après (spécification) |
|---|---|---|
| Trame S | 6-8 octets ; fitness 6 b ; seq 4 b ; CRC-8 | 8 octets ; FITNESS 8 b (1 mode + 1 rés. + 2 classe + 4 score) ; SEQ 8 b ; CRC-16 |
| Trame D | 4-6 octets ; « SYNC+ID+delta+seq+CRC-8 » | 4 octets ; SYNC + TARGET + DELTA + CRC-8 |
| Trame H | 4-6 octets ; « SYNC+ID+position+seq+CRC-8 » | 8 octets ; SYNC + ID + AZIMUT + ELEVATION + FITNESS + SEQ + CRC-16 |

La Trame R (4 octets) était déjà conforme.

---

## 5. Vérification

- `likec4 validate` → Valid (18 fichiers), exit 0.
- Gouvernance (`gouvernance_swarmdrones.py`) → RESULTAT GLOBAL OK ; baseline ré-initialisée
  pour absorber l'ajout de `srcAlgProtocole` (+1 sourceCode) et `decHzipProtocole` (+1 decision).
- `total_deployments` : le compteur vaut 2 = nombre de clés (`elements`, `relations`) de la
  section `deployment` du modèle compilé (artefact de la gouvernance, pas un décompte de
  noeuds). Toute hausse est signalée `[info]` (non bloquant) par `check_baseline` ; la
  baseline actuelle est déjà à 2, donc aucune alerte ne subsiste.

---

## 6. Actions restantes (hors périmètre de cette carte)

1. Création du dépôt GitHub `dagornc/alg-protocole` — action Christophe (autorisation requise).
2. Ré-édition de la spécification normative (v2.2) intégrant les valeurs figées ci-dessus —
   carte de suivi pour le profil swarmdrone.
3. Mesure des bornes physiques réelles (a_max, v_max, d_min, capacité du modem) en banc —
   décisions matérielles DE-05/DE-06/DE-07.
4. Campagne de calibration par simulation multi-agents (200 noeuds, 3 classes, canal bruité)
   pour confirmer les valeurs figées (§24.1 méthode).
