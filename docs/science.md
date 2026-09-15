# Référentiel scientifique

> Epic **E08** · Carte `t_361b3beb` · Fichier : `science.c4`
> Source : audit de fidélité documentaire exécuté par le profil **SwarmDrone**
> (carte `t_81787f59`, livrable `claim-fidelity-audit.md`, 218 lignes)

## 1. Objet

Relier les **algorithmes** du catalogue à des **sources primaires**, et
surtout **porter le verdict réel** de chacune des 4 affirmations décisives.

Le point de départ était brutal : le corpus local comptait **2 sources
primaires vérifiées sur 1011** — inutilisable comme preuve. Une recherche
externe ciblée a donc été confiée au profil SwarmDrone.

## 2. Résultat principal : une affirmation du modèle est CONTREDITE

**(Voir `sciCbf` / SCI-2.)** Le modèle portait implicitement « CBF :
garanties de non-collision à 30 agents ». La source primaire décisive
(*Kim et al. 2026, CA-HCBF, arXiv:2604.13245*) donne :

- **Simulation** : N ∈ {10, 20, 30}
- **Matériel réel** : **5 robots** LIMO Pro
- À N=30 (simulation) : 89,6 % d'arrivée, **5,1 violations de paire par essai** (σ = 9,6), 669,6 infeasibilities QP par essai

Donc : « 30 agents » = simulation. « En expérience réelle » = **faux** pour
N≈30. Et « garanties » n'est **pas absolue** — même en simulation, les
violations ne tombent pas à zéro.

**J'ai corrigé le modèle dans le sens désagréable**, pas dans le sens
arrangeant. `algCollisionAvoidance` porte désormais `evidence: LOW —
CONTREDIT par la source primaire`. C'est exactement ce que le modèle doit
faire : dire où il n'est pas prouvé.

## 3. Les 4 verdicts

- **SCI-1 — CBBA** : `CONDITIONAL`. Convergence prouvée sous communications
  idéales (Choi 2009). Robustesse au retrait d'agents seulement **empirique**.
  **Aucun article ne prouve la convergence sous partition persistante.**
  Au-delà de 30 : `UNSUPPORTED`. Niveau : MEDIUM.

- **SCI-2 — CBF** : `UNSUPPORTED` telle qu'énoncée. Réel = 5, sim = 30.
  Compromis central : la garantie formelle (sRCBF) se paie par un gel
  (<5 % d'arrivée à N=30) ; CA-HCBF échange la garantie absolue contre la
  performance. Niveau : **LOW / contradictoire**.

- **SCI-3 — CRDT LWW** : `SUPPORTED` (théorie) / `CONDITIONAL` (essaim).
  Théoème de semi-treillis solide, indépendant de N. Mais **très peu
  d'évaluations sur essaim de drones**, et rien avec brouillage RF réel.
  **Distinction critique** : convergence CRDT ≠ convergence de tâche. LWW
  garantit le *même* état, pas un état *correct*.

- **SCI-4 — EKF/UKF distribué** : `CONDITIONAL`. Théorie mature, mais
  validation majoritairement en **simulation et sur UUV**. Le « ~30
  plateformes réelles » **n'est pas confirmé** ; beaucoup de démos réelles
  plafonnent à 3-10. Transposer UUV → UAV n'est pas direct.

## 4. Les 4 trous de benchmark

Chacun est un objet dans le modèle, marqué **« AUCUN ARTICLE TROUVÉ »** :

- **GAP-1** — CBBA à 30 sous partition persistante + brouillage
- **GAP-2** — CBF hétérogène au-delà de 30 en matériel réel
- **GAP-3** — CRDT (LWW + OR-Set) sur drones en vol, brouillage RF réel
- **GAP-4** — Fusion EKF/UKF hiérarchique à ≥100 plateformes

Ces trous ne sont pas des échecs : ce sont **les cibles de recherche
futures**, explicitement identifiées.

## 5. Corrections appliquées au modèle

`algorithms.c4`, y compris corrections dans le sens défavorable :

- `algCollisionAvoidance` : `evidence` MEDIUM → **LOW (CONTREDIT)**
- `algTaskAllocation` : `sourcePath` TBD → sources réelles ; `evidence` → MEDIUM CONDITIONAL
- `algConsensus` : `evidence` HIGH → **HIGH théorie / LOW application** ; ADR-2 requalifié
- `algPerceptionFusion` : `references` vide → survey UUV sourcé ; `evidence` → CONDITIONAL

Les 4 `references: aucune source vérifiée dans cette session` ont été
remplacées par des références réelles.

## 6. Ce que le modèle gagne

Avant E08, le modèle affirmait des performances à 30 agents sans source.
Après, il **déclare lui-même où il n'est pas prouvé** — et cette déclaration
est vérifiable dans le graphe (`sciCbf -[evidences]-> algCollisionAvoidance`).

Dans un contexte pédagogique, c'est plus précieux qu'une affirmation forte :
**le système enseigne aussi ses propres limites.**

## 7. Vérification

- `likec4 validate` → **Valid (13 files)**
- 252 éléments, 495 relations
- **15 éléments #science** (7 sources, 8 findings), **0 orphelin**
- Les 4 algorithmes critiques sont adossés à une source : vérifié sur le modèle compilé
