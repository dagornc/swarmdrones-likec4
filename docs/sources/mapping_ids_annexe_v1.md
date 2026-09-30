# MAPPING IDs — annexe v1 (kebab-case) → modèle LikeC4 réel (camelCase)

**CORRECTION OBLIGATOIRE** : l'annexe §E emploie des IDs en kebab-case qui
N'EXISTENT PAS dans `architecture.c4`. Voici le mapping exact à utiliser.
Tout ID non listé ici doit être vérifié avant injection.

| Annexe (faux) | Modèle réel (correct) |
|---|---|
| onboard.sensors-hal | onboard.sensorsHAL |
| onboard.link | onboard.linkRadio |
| onboard.task-auction | onboard.taskAuction |
| cloud.replay-store | cloud.replayStore |
| cloud.model-registry | cloud.modelRegistry |
| onboard.mission / autopilot / safety / perception / energy / health / telemetry | (identiques) |
| edge.gateway / relay / fusion / coordinator / cache | (identiques) |
| c2.gcs / planner / alerting / auth | (identiques) |
| cloud.twin / analytics | (identiques) |

## Nouveaux éléments (à créer, noms libres proposés)

- `tech.software.<Domaine>.<Produit>` — ex. `tech.software.Autopilot.PX4`
- `tech.algo.<Fonction>.<Famille>` — ex. `tech.algo.TaskAllocation.CBBA`
- `risk.R1` … `risk.R15`
- `blindspot.AM1` … `blindspot.AM16`

Attention : les kinds `hypothesis` et `decision` existent déjà (lot ①③).
NE PAS les réutiliser pour les risques/angles morts → créer des kinds dédiés.
