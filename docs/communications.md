# Modèle des messages

> Epic **E06** · Carte `t_f7a97194` · Fichier : `messages.c4`

## 1. Objet

Rendre les communications **explicitement observables**. Avant E06, aucune communication n'était modélisée : les 239 relations parlaient de composants, jamais de ce qui circule entre eux. Or l'étape 6 de la mission exige de pouvoir *animer* ces flux dans la scène 3D.

## 2. Canaux de transport

Quatre canaux logiques, correspondant à des régimes de disponibilité distincts :

- **`CH_MESH`** — canal inter-agents (Zenoh + repli MQTT store-and-forward). *Intermittent par construction.*
- **`CH_CMD`** — canal de commandement (MAVLink/MAVSDK + ordres signés). Ordres soumis à autorisation.
- **`CH_LOCAL`** — bus interne du drone (MAVLink interne / UART-CAN). **Ne dépend d'aucune communication externe** : c'est le support de l'autonomie nominale.
- **`CH_CLOUD`** — canal montant différé. Hors boucle de contrôle.

La séparation `CH_LOCAL` / `CH_MESH` est structurante : elle matérialise dans le modèle l'exigence « le drone doit terminer sa mission nominale sans C2 ni cloud ».

## 3. Les 13 messages

Les 12 messages demandés par la mission, plus `MSG_FAILURE_NOTIFICATION` qui était déjà impliqué par le modèle (blindspot AM12).

- **`MSG_DRONE_STATE`** — état complet d'un agent. 1-10 Hz, mission-critical.
- **`MSG_HEARTBEAT`** — battement de vivacité. 1 Hz, safety-critical. Base de la détection de perte (SCN-06).
- **`MSG_POSITION_UPDATE`** — position relative/absolue. 10-20 Hz, safety-critical.
- **`MSG_NEIGHBOR_STATE`** — vue synthétique du voisinage. 5-10 Hz.
- **`MSG_TASK_BID`** — enchère de tâche. Cœur de CBBA (SCN-04, SCN-07).
- **`MSG_TASK_ASSIGNMENT`** — attribution décidée. Résultat du consensus d'enchères.
- **`MSG_TRAJECTORY_PROPOSAL`** — proposition négociée avant exécution.
- **`MSG_TRAJECTORY_UPDATE`** — trajectoire retenue et exécutée. safety-critical.
- **`MSG_FORMATION_STATE`** — état global de la formation (SCN-03).
- **`MSG_COLLISION_ALERT`** — **le message le plus critique**. Déclenche une action *locale*, sans attendre le réseau.
- **`MSG_MISSION_COMMAND`** — ordre de la GCS, signé et audité.
- **`MSG_CONSENSUS_VOTE`** — vote dans une décision collective.
- **`MSG_FAILURE_NOTIFICATION`** — auto-signalement ou signalement d'un pair.

Chaque message porte, dans ses métadonnées : producteur, consommateurs, canal, fréquence, criticité, schéma, algorithme associé et **comportement en cas de perte**.

## 4. Contrôle qualité — exécuté, pas déclaré

Requête sur le modèle compilé : chaque message a-t-il un producteur (`publishes`) et au moins un consommateur (`subscribes`) ?

```
message                 prod  cons
msgCollisionAlert         1     2
msgConsensusVote          1     1
msgDroneState             1     2
msgFailureNotification    1     2
msgFormationState         1     1
msgHeartbeat              1     2
msgMissionCommand         1     2
msgNeighborState          1     2
msgPositionUpdate         1     2
msgTaskAssignment         1     2
msgTaskBid                1     2
msgTrajectoryProposal     1     1
msgTrajectoryUpdate       1     2

Messages orphelins: 0
```

Le critère « message sans producteur / sans consommateur » de l'étape 18 est **satisfait à 100 %**.

## 5. Preuve d'effet et non-régression

| Mesure | Avant E06 | Après E06 |
|---|---|---|
| Éléments | 111 | **128** (+17) |
| Relations | 254 | **303** (+49) |
| Vues | 24 | **24** (inchangé) |
| Messages | 0 | **13** |
| Canaux | 0 | **4** |
| `likec4 validate` | Valid (4 files) | **Valid (5 files)** |
| Messages orphelins | n/a | **0** |

Nouveaux kinds effectivement utilisés : `publishes` (13), `subscribes` (23), `uses` porté à 15.

## 6. Ce qui reste ouvert

- **Tous les schémas de payload sont `TBD`.** Aucun n'est inventé. Ils seront formalisés quand la simulation exigera des formats précis.
- **Les fréquences marquées `[EXTRAP]`** (1-10 Hz, 10-20 Hz, etc.) sont des ordres de grandeur déduits, non confirmés par une source. Ils sont étiquetés comme tels et ne doivent pas être présentés comme établis.
- **La latence cible de `MSG_COLLISION_ALERT` (≤ 100 ms)** provient du budget §8 du document source. C'est une valeur `[EXTRAP]` — le profil SwarmDrone doit la valider ou la corriger contre une source primaire.
- **Le budget radio total** (blindspot AM3) reste un angle mort : impossible de dimensionner sérieusement les fréquences ci-dessus tant qu'il n'est pas établi.

## 7. Ce que cela débloque

Le graphe `producteur -[publishes]-> message -[subscribes]-> consommateur` est directement consommable par un moteur de rendu : chaque message a un émetteur, un ou plusieurs récepteurs, une criticité et une fréquence. La vue 3D pourra animer un flux par message, coloré par criticité, à la fréquence déclarée.
