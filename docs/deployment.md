# Modèle de déploiement

> Epic **E07** · Carte `t_de7c0750` · Fichier : `deployment.c4`

## 1. Objet

Rendre explicite la chaîne **Algorithm → Component → Runtime → Node** et
rendre **instanciable** le déploiement à l'échelle de l'essaim.

Avant E07 : aucun déploiement modélisé. On savait *quoi* existait, pas
*ce qui tourne où*.

## 2. Principe : LikeC4 reste sémantique

**Aucune coordonnée n'a été introduite.** Ni latitude, ni longitude, ni
altitude, ni position 3D. Le modèle dit *ce qui est déployé sur quoi*, pas
*où c'est dans l'espace*.

Le placement spatial appartient au **World Model** (E11). C'est la
séparation exigée par la mission : LikeC4 = source de vérité sémantique,
le moteur 3D = consommateur.

## 3. Les 6 runtimes

- `rtFlight` — temps réel, NuttX/PX4, sur `flightCtrl`. **Sans réseau.**
- `rtCompanion` — Linux ARM64, non temps réel, sur `companion`.
- `rtSensorsHAL` — abstraction capteurs, sur la plateforme.
- `rtEdge` — coordination au sol, **partagé**, perte tolérée.
- `rtC2` — poste de commandement, perte tolérée.
- `rtCloud` — jumeau numérique. **Cible du Digital Twin 3D.**

## 4. Échelle N=30

`deplDroneRef` est l'**instance-type** : le simulateur en crée 30 copies.

- **UAV-R ×18** — multirotor, drone de référence (`refDrone`)
- **UAV-F ×8** — variante à voilure fixe (`#tbd`)
- **USV ×4** — variante de surface (`#tbd`)

Aucune coordonnée : seulement la cardinalité et la variante.

## 5. La chaîne, prouvée complète

Deux lectures possibles :
- **descendante** — « où tourne cet algorithme ? »
- **montante** — « qu'est-ce qui tourne sur cette plateforme ? »

**Résultat du contrôle : 11/11 chaînes complètes, 0 orphelin.**

```
algSafetyRules        -> onboard.safety     -> rtFlight     -> refDrone.flightCtrl
algCollisionAvoidance -> onboard.safety     -> rtFlight     -> refDrone.flightCtrl
algPerceptionFusion   -> onboard.perception -> rtSensorsHAL -> refDrone
algNavigationGNSS...  -> onboard.perception -> rtSensorsHAL -> refDrone
algHealthMonitoring   -> onboard.health     -> rtCompanion  -> refDrone.companion
algTaskAllocation     -> onboard.taskAuction-> rtCompanion  -> refDrone.companion
                      -> edge.coordinator   -> rtEdge
algConsensus          -> onboard.taskAuction-> rtCompanion  -> refDrone.companion
                      -> edge.coordinator   -> rtEdge
algPathPlanning       -> onboard.mission    -> rtCompanion  -> refDrone.companion
algFormationControl   -> onboard.mission    -> rtCompanion  -> refDrone.companion
algEnergyAware        -> onboard.mission    -> rtCompanion  -> refDrone.companion
algLeaderElection     -> onboard.mission    -> rtCompanion  -> refDrone.companion
```

## 6. Résultat structurant : la séparation de criticité est *démontrée*

La chaîne de sûreté (`rtFlight`) et la chaîne de coordination
(`rtCompanion`) **ne partagent aucun runtime**. Ce n'est plus une
affirmation d'intention : c'est une propriété du graphe, vérifiable.

C'est ce qui rend défendable le prédicat central de la mission :
*« le drone termine sa mission nominale sans C2 ni cloud »*.

## 7. Ce qui reste TBD

Trois choix de plateforme ne sont pas tranchés et bloquent des détails :

- `rtFlight` / `rtCompanion` — dépend de **DE-05** (partition calcul) ;
- radios et maillage — dépend de **DE-06** (bande) ;
- aucune valeur de ressource (RAM, CPU, TOPS) n'a été inventée.

## 8. Vérification

- `likec4 validate` → **Valid (9 files)**
- 162 éléments, 354 relations
- 6 runtimes, 5 unités de déploiement
- **11/11 chaînes complètes · 0 runtime orphelin · 0 unité orpheline**
