# RAPPORT VERIF CARTES ALGOS — LIKEC4-ALGO-LINKS (carte t_f5a50f47)

Date : 2026-09-28
Modele : dagornc/swarmdrones-likec4 (repo prive, clone propre au HEAD 1f5608c)
Methode : analyse du modele compile (`npx likec4 export json`), verification des
URLs via `gh api` (authentifie dagornc) et `curl -sI`, validation sur clone propre.

## 1. Matrice de couverture 15 algorithmes x 4 types de liens

Colonnes :
  spec   = algo -[documentedBy]-> spec<Algo> (specification DOCX/PDF)
  sysml  = algo -[documentedBy]-> sysml<Algo> (specification SysML v2)
  runsOn = algo -[runsOn]-> <composant> (composant d execution)
  uses   = algo -[uses]-> <message|scenario|composant> (dependances)

AVANT correction : 6 cases ❌ (colonne `uses`).
APRES correction : 15/15 en 4 colonnes = 60/60 ✅.

| # | Algorithme                | spec | sysml | runsOn | uses |
|---|---------------------------|------|-------|--------|------|
| 1 | algTaskAllocation         | ✅   | ✅    | ✅     | ✅ (4) |
| 2 | algConsensus              | ✅   | ✅    | ✅     | ✅ (1) |
| 3 | algFormationControl       | ✅   | ✅    | ✅     | ✅ (2) |
| 4 | algLeaderElection         | ✅   | ✅    | ✅     | ✅ (1) |
| 5 | algPerceptionFusion       | ✅   | ✅    | ✅     | ✅ (2) |
| 6 | algNavigationGNSSDegrade  | ✅   | ✅    | ✅     | ✅ (2) |
| 7 | algCollisionAvoidance     | ✅   | ✅    | ✅     | ✅ (2) |
| 8 | algSafetyRules            | ✅   | ✅    | ✅     | ✅ (2) |
| 9 | algPathPlanning           | ✅   | ✅    | ✅     | ✅ (3) |
|10 | algHealthMonitoring       | ✅   | ✅    | ✅     | ✅ (2) |
|11 | algEnergyAware            | ✅   | ✅    | ✅     | ✅ (1) |
|12 | algEventTriggeredComm     | ✅   | ✅    | ✅     | ✅ (1) |
|13 | algCooperativeLocalization| ✅   | ✅    | ✅     | ✅ (2) |
|14 | algFaultTolerantControlAlloc | ✅ | ✅    | ✅     | ✅ (1) |
|15 | algJammingResilientMode   | ✅   | ✅    | ✅     | ✅ (1) |

Detail des cibles :
  runsOn : 17 arcs. 15/15 algos ont >=1 composant hote (13 onboard uniquement ;
           algTaskAllocation et algConsensus en double onboard.taskAuction + edge.coordinator).
  implements : 42 arcs. 15/15 algos implementes par >=1 composant logiciel
           (27 composant + 15 portages Rust sourceCode).
  evidences : 19 arcs (finding -> algorithme). 15/15 algos sourcent >=1 constat scientifique.

## 2. Liens manquants DETECTES et CORRIGES (12 arcs `uses` ajoutes)

Les 6 algorithmes ci-dessous n avaient AUCUN lien `uses` sortant, alors que leur
metadonnee `relatedMessages` declare explicitement ces dependances. Les 12 arcs ont
ete materialises dans algorithms.c4 (section E25), source de verite = `relatedMessages`
de chaque carte (aucun lien invente).

  algTaskAllocation  -> msgTaskBid, msgTaskAssignment, msgConsensusVote, msgHeartbeat (4)
  algConsensus       -> msgConsensusVote (1)
  algFormationControl-> msgFormationState, msgPositionUpdate (2)
  algPerceptionFusion-> msgPositionUpdate, msgNeighborState (2)
  algHealthMonitoring-> msgHeartbeat, msgFailureNotification (2)
  algEnergyAware     -> msgMissionCommand (1)

## 3. Doublons de relations CORRIGES (6 paires, dette de modele)

Meme fait affirme deux fois (source, kind, cible) dans deux fichiers differents.
Copie dupliquee supprimee dans architecture.c4 ; copie canonique conservee.

  1. algPathPlanning  -[uses]-> msgTrajectoryProposal   (conserve algorithms.c4:479)
  2. algPathPlanning  -[uses]-> scn01                   (conserve algorithms.c4:481)
  3. algSafetyRules   -[uses]-> msgCollisionAlert       (conserve algorithms.c4:486)
  4. algSafetyRules   -[exposed-to]-> blindspotAM5      (conserve algorithms.c4:487)
  5. sciCbf           -[evidences]-> algCollisionAvoidance (conserve science.c4:491)
  6. sciGnssDegraded  -[evidences]-> algNavigationGNSSDegrade (conserve e20-audit-completeness.c4:420)

## 4. Liens morts et cibles fantomes

  - Liens morts (relation dont la source ou la cible n est pas un element declare) : 0.
  - Cible fantome dans une relation : 0.
  - FANTOME en METADONNEE (non resolu, voir section 6) : la metadonnee
    `relatedComponents` de algTaskAllocation cite `onboard.resilience`, qui n existe
    pas comme composant du modele (24 composants declares, aucun resilience).

## 5. URLs verifiees (code HTTP)

Total verifie : 55 URLs, toutes HTTP 200.

  - 17 depots GitHub (dagornc/alg-* + dagornc/SwarmDrones) : 17/17 HTTP 200 (curl).
  - 13 PDF de specification (blob master : 11 en _v1 + leader/nav en _v2) : 13/13 HTTP 200 (gh api).
  - 15 fichiers SysML v2 (blob master) : 15/15 HTTP 200 (gh api).
  - 10 fichiers servis par likec4.breizh.ai (PDF TaskAllocation/Consensus + README + H-Zip) : 10/10 HTTP 200 (curl).

Correspondance URL <-> algorithme : verifiee. Chaque spec<Algo> reference son propre
PDF (Spec_ALG_<SLUG>_v*.pdf), chaque sysml<Algo> son propre .sysml, chaque src<Algo>
son propre depot alg-<slug>. Aucun PDF d un algo ne pointe vers un autre algo.

Note d ecart : la carte annoncait « 79 URLs GitHub ». Le modele courant contient
45 URLs GitHub distinctes (+10 likec4.breizh.ai, +~160 DOI/arXiv/divers = 206 URLs
distinctes au total). Les 45 URLs GitHub + 10 likec4 ont toutes ete verifiees 200.
Le chiffre « 79 » ne correspond pas a l etat actuel du modele (probablement un
comptage anterieur ou un comptage d occurrences et non d URLs distinctes).

## 6. Points non resolus (lacunes signalees, non fabriquees)

  - onboard.resilience : cite uniquement en metadonnee `relatedComponents` de
    algTaskAllocation. Non materialise en composant (le commentaire du modele
    algorithms.c4 dit explicitement « lien fantome, NON materialise — a arbitrer
    cote modele »). Corriger necessite une decision d architecture : soit creer un
    composant `onboard.resilience`, soit retirer la mention. NON tranche ici pour ne
    pas inventer de composant.

## 7. Coherence semantique onboard/edge (verification)

  - Aucun algorithme declare `runsOn` sur un composant de calage sol (edge/c2) alors
    que sa spec le dit embarque, ni l inverse.
  - Seuls algTaskAllocation et algConsensus portent un double `runsOn`
    (onboard.taskAuction + edge.coordinator) : c est coherent, leur metadonnee
    `relatedComponents` et leurs `implements`/`uses` Edge confirment la declinaison
    Edge (allocation/consensus au niveau coordination locale).
  - Cas multi-couches verifies : algPathPlanning (hote onboard.mission, implementations
    c2.planner + edge.coordinator + onboard.mission), algLeaderElection (hote
    onboard.mission, implementation edge.coordinator), algHealthMonitoring (hote
    onboard.health, implementations onboard.health + edge.coordinator) — tous conformes
    a leurs `relatedComponents` respectifs et a la validation spec (ex. path_planning :
    « Composants porteurs : onboard.mission, c2.planner, edge.coordinator ✅ »).

## 8. Validation et publication

  - `npx likec4 validate` sur clone propre (HEAD + corrections) : ✓ Valid (20 files), exit 0.
  - Comptages finaux (modele compile) : 405 elements, 771 relations, 70 vues.
    Relations touchant les algorithmes : implements 42, uses 45, documentedBy 30,
    runsOn 17, evidences 19, exposed-to 10.
  - Commit + push : voir historique git (fichiers modifies : algorithms.c4, architecture.c4).

## 9. Fichiers modifies

  - algorithms.c4   : +12 arcs `uses` manquants (section E25).
  - architecture.c4 : -6 lignes de relations dupliquees (deduplication).
  - (science.c4 : modification en cours par un worker parallele au moment de la
    verification — hors perimetre de cette carte, laissee intacte et non commitee ici.)
