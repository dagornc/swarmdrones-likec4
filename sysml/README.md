# Spécifications SysML v2 — Catalogue SWARM-3D

Carte kanban : SYSML-15 (t_d671a500) — profil architecte.

## Contenu

- `ALG_*.sysml` (15 fichiers) — une spécification SysML v2 par algorithme du
  catalogue (notation textuelle OMG / KerML).
- `generate_sysml.py` — générateur (table de traçabilité machine-readable +
  émission des 15 fichiers `.sysml` et du fichier LikeC4 `../sysml.c4`).
- `validate_sysml.py` — parseur structurel maison (voir limites ci-dessous).
- `VALIDATION_REPORT.md` — rapport de validation détaillé (ce qui est vérifié,
  ce qui ne l'est pas).

## Règle d'honnêteté (invariant INV-5 du modèle)

Chaque champ d'une spec SysML v2 est une transcription d'un champ du modèle
LikeC4 (`algorithms.c4` / `e20-audit-completeness.c4` / `messages.c4`). Aucune
valeur numérique n'est inventée : les paramètres sans valeur au modèle sont
déclarés sans initialiseur (TBD). Les expressions `require constraint` sont des
transcriptions qualitatives de `purpose`/`contraintes`/`hypotheses` — elles ne
sont pas exécutables et ne prétendent pas l'être.

## Validation de la syntaxe SysML v2 — statut réel

**Aucun validateur SysML v2 conforme OMG n'est disponible dans cet
environnement.** Vérifié de première main :

- `which syside sysml java` → absent (`java: command not found`, pas de
  `syside` ni `sysml`) ;
- `pip index versions sysml2` → `No matching distribution found` ;
- `npm view sysml2` / `sysml` / `@omg/sysml` → `404 Not Found`.

La seule validation appliquée est donc un **contrôle structurel maison**
(`validate_sysml.py`) : délimiteurs équilibrés `{}` `[]` `()`, ouverture du
package, présence des constructeurs attendus (`part def`, `action def`,
`requirement def`, `interface def`/`item def`/`port def`, `import`), nommage
des déclarations, terminaison des instructions.

**Cela ne valide NI la grammaire OMG, NI la sémantique, NI la résolvabilité des
types.** La conformité OMG SysML v2 reste à établir avec un outil réel
(SysIDE / SysML v2 Pilot Implementation, basé Java) — action recommandée en
intégration continue.

## Structure d'une spec (contenu attendu par la carte)

- `part def` — l'algorithme comme partie du système (port d'échange).
- `attribute` — paramètres (repris de `metadata.parameters`, sans valeur) et
  attributs dérivés (transcription qualitative).
- `action def` — comportement (étapes + flot `first`/`then`).
- `state def` — états internes **si la fiche nomme un automate** (6 algorithmes
  concernés : TASK_ALLOCATION, CONSENSUS, LEADER_ELECTION, NAV_GNSS_DEGRADE,
  HEALTH_MONITORING, JAMMING_RESILIENT_MODE). Absent volontairement pour les
  algorithmes à état local sans automate (documenté dans chaque fichier).
- `requirement def` — exigences tracées (sûreté, performance, contraintes).
- `interface def` — messages consommés (in) / produits (out), cf `messages.c4`.
- traçabilité vers le composant d'accueil : `part def Host_*` avec
  `perform action` + `satisfy`.

## Régénérer / re-valider

```sh
cd sysml
python3 generate_sysml.py        # re-émet les 15 .sysml + ../sysml.c4
python3 validate_sysml.py        # contrôle structurel (15/15 attendu)
```

Validation du modèle LikeC4 (côté conteneur, sans redémarrage) :

```sh
cp sysml.c4 /docker/likec4/workspace/sysml.c4
docker exec likec4 likec4 validate /data   # attendu : ✓ Valid (20 files)
```

## Traçabilité (15/15)

| ALG_ID | likec4_id | source LikeC4 | fichier .sysml |
|---|---|---|---|
| ALG_TASK_ALLOCATION | algTaskAllocation | algorithms.c4 | ALG_TASK_ALLOCATION.sysml |
| ALG_CONSENSUS | algConsensus | algorithms.c4 | ALG_CONSENSUS.sysml |
| ALG_FORMATION_CONTROL | algFormationControl | algorithms.c4 | ALG_FORMATION_CONTROL.sysml |
| ALG_LEADER_ELECTION | algLeaderElection | algorithms.c4 | ALG_LEADER_ELECTION.sysml |
| ALG_PERCEPTION_FUSION | algPerceptionFusion | algorithms.c4 | ALG_PERCEPTION_FUSION.sysml |
| ALG_NAV_GNSS_DEGRADE | algNavigationGNSSDegrade | algorithms.c4 | ALG_NAV_GNSS_DEGRADE.sysml |
| ALG_COLLISION_AVOIDANCE | algCollisionAvoidance | algorithms.c4 | ALG_COLLISION_AVOIDANCE.sysml |
| ALG_SAFETY_RULES | algSafetyRules | algorithms.c4 | ALG_SAFETY_RULES.sysml |
| ALG_PATH_PLANNING | algPathPlanning | algorithms.c4 | ALG_PATH_PLANNING.sysml |
| ALG_HEALTH_MONITORING | algHealthMonitoring | algorithms.c4 | ALG_HEALTH_MONITORING.sysml |
| ALG_ENERGY_AWARE | algEnergyAware | algorithms.c4 | ALG_ENERGY_AWARE.sysml |
| ALG_EVENT_TRIGGERED_COMM | algEventTriggeredComm | e20-audit-completeness.c4 | ALG_EVENT_TRIGGERED_COMM.sysml |
| ALG_COOPERATIVE_LOCALIZATION | algCooperativeLocalization | e20-audit-completeness.c4 | ALG_COOPERATIVE_LOCALIZATION.sysml |
| ALG_FAULT_TOLERANT_CONTROL_ALLOC | algFaultTolerantControlAlloc | e20-audit-completeness.c4 | ALG_FAULT_TOLERANT_CONTROL_ALLOC.sysml |
| ALG_JAMMING_RESILIENT_MODE | algJammingResilientMode | e20-audit-completeness.c4 | ALG_JAMMING_RESILIENT_MODE.sysml |

Intégration LikeC4 : `sysml.c4` (racine du dépôt) ajoute 15 éléments `specDoc`
(`sysml*`), 15 relations `algorithm -[documentedBy]-> specDoc`, et la vue
`algorithmSysmlTraceability`. Aucune fiche `algorithm` existante n'est modifiée.
