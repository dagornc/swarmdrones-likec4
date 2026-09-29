# Rapport — Traitement des 3 sources A CONSULTER (COLLISION & FORMATION)

**Tâche** : t_5514113a
**Date** : 2026-09-29
**Profil** : architecte
**Modèle** : `~/workspace/swarmdrones_likec4/` (repo `dagornc/swarmdrones-likec4`, HEAD de travail 2b184f7 → commit 3cf27bc)

---

## 1. Conclusion

Les 3 sources du domaine COLLISION & FORMATION ont été **lues** (abstract + métadonnées primaires) et **rattachées** : aucune n'a été écartée. Trois constats-verdicts ont été créés dans `science.c4` (SCI-16, SCI-17, SCI-18), chacun selon le patron 2 sauts exigé :

    srcXXX -[uses]<- sciXXX -[evidences]-> algYYY

Les 3 sources passent du statut `A CONSULTER` au statut `CONSULTEE`.

| Source | Verdict | Rattachement | Preuve de lecture |
|---|---|---|---|
| srcCBFMultiFixed (10.3390/drones8080415) | SUPPORTED (HOCBF/QP voilure fixe) / CONDITIONAL (sim 2D, N non reporté) | sciCbfFixedWing (SCI-16) → algCollisionAvoidance | Crossref API + abstract MDPI |
| srcAPFWall (arXiv:2409.10332) | SUPPORTED (mécanique APF+WF) / CONDITIONAL (transposition UAV 2D→3D) | sciApfWallFollower (SCI-17) → algCollisionAvoidance | page abs arXiv |
| srcFormationRL (arXiv:2410.18495) | SUPPORTED (sim + réel) / CONDITIONAL (échelle N=30) | sciFormationRL (SCI-18) → algFormationControl | page abs arXiv (v2 2025-03-01) |

---

## 2. Détail par source

### 2.1 srcCBFMultiFixed — rattachée à algCollisionAvoidance (SCI-16)

- **DOI** : `10.3390/drones8080415` — vérifié via Crossref (`api.crossref.org/works/10.3390/drones8080415`, HTTP 200).
- **Titre réel (Crossref)** : « Control Barrier Function-Based Collision Avoidance Guidance Strategy for Multi-Fixed-Wing UAV Pursuit-Evasion Environment ». Le titre du lien dans le modèle était tronqué (« …UAV Pursuit ») ; il a été **corrigé au titre Crossref exact**.
- **Auteurs** : Xinyuan Lv, Chi Peng, Jianjun Ma — National University of Defence Technology, Changsha. **Drones 8(8):415**, MDPI, 2024.
- **Contenu lu (abstract)** : CBF d'ordre supérieur (HOCBF) sur modèle 2D multi-UAV à voilure fixe en poursuite-évasion n-sur-n / n-sur-1 ; contraintes HOCBF multiples fusionnées en UNE contrainte linéaire ; résolution par QP avec solution en forme fermée (guidage nominal + terme d'évitement) ; maintien au-dessus de la distance minimale de sécurité tout en atteignant la cible. **SIMULATION uniquement, aucun matériel réel, N non reporté dans l'abstract.**
- **Verdict** : SUPPORTED pour la mécanique HOCBF/QP voilure fixe ; CONDITIONAL pour l'échelle SWARM-3D (sim 2D, N non reporté). Complémentaire de srcCAHCBF (multirotors) : le modèle couvre désormais les deux variantes CBF (voilure tournante + voilure fixe).

### 2.2 srcAPFWall — rattachée à algCollisionAvoidance (SCI-17)

- **arXiv** : `2409.10332` — page abs lue (`arxiv.org/abs/2409.10332`, HTTP 200).
- **Titre réel** : « Escaping Local Minima: Hybrid Artificial Potential Field with Wall-Follower for Decentralized Multi-Robot Navigation ». Kim et al., soumis 2024-09-16.
- **Contenu lu (abstract)** : APF hybride + comportement de suivi de mur (wall-follower) pour échapper aux minima locaux en navigation décentralisée multi-robots, SANS carte et SANS communication (capteurs/état locaux) ; deux commutations APF↔WF (à base de règles, ou encodeur entraîné sur démonstrations d'experts) ; obstacles non convexes ET dynamiques (dont les autres robots) ; taux de succès nettement supérieur à l'état de l'art.
- **Verdict** : SUPPORTED pour la mécanique (variante « champs de potentiel » de algCollisionAvoidance, réactive et sans lien) ; CONDITIONAL pour la transposition UAV — source multi-robots **générique 2D** (suivi de mur orienté sol), pas de voilure fixe.

### 2.3 srcFormationRL — rattachée à algFormationControl (SCI-18)

- **arXiv** : `2410.18495` — page abs lue (`arxiv.org/abs/2410.18495`, HTTP 200), version v2 (2025-03-01).
- **Titre réel** : « Multi-UAV Formation Control with Static and Dynamic Obstacle Avoidance via Reinforcement Learning ». Xie et al.
- **Contenu lu (abstract)** : pipeline RL deux étapes — (1) recherche de fonction de récompense équilibrant vol dirigé, évitement d'obstacles, maintien de formation et déploiement zero-shot ; (2) curriculum learning + encodeur d'observation par attention ; validation en **SIMULATION ET en environnement RÉEL**, surpasse les baselines planification et RL (taux sans collision, maintien de formation).
- **Verdict** : SUPPORTED (sim + réel) ; CONDITIONAL pour l'échelle SWARM-3D (nombre d'UAV et voilure fixe non reportés dans l'abstract). C'est l'une des rares sources du référentiel à disposer d'une **validation réelle** pour la formation.

---

## 3. Modifications du modèle

### science.c4
- 3 sources : `statut 'A CONSULTER'` → `statut 'CONSULTEE (…)'`, `description` enrichie du contenu réel lu.
- Correction du titre du lien de srcCBFMultiFixed au titre Crossref exact.
- 3 nouveaux findings : `sciCbfFixedWing` (SCI-16), `sciApfWallFollower` (SCI-17), `sciFormationRL` (SCI-18).
- 6 relations : 3 `-[uses]->` (finding → source) + 3 `-[evidences]->` (finding → algorithme).

### algorithms.c4
- `algCollisionAvoidance` : `evidence`/`references` enrichies (SCI-2 + SCI-16 + SCI-17).
- `algFormationControl` : `evidence`/`references`/`evidenceLevel` corrigées (SCI-11 + SCI-18 ; `evidenceLevel NONE → MEDIUM`). Corrige une incohérence préexistante (la carte disait encore « aucune source verifiée » alors que SCI-11 la rattachait déjà).

---

## 4. Validation

Exécutée sur **clone propre** (`git clone . /tmp/lc_*`), jamais sur la copie active :

```
npx -y likec4@1.59.2 validate            → ✓ Valid (20 files)
integrity_check (export JSON du clone)    → 7/7 OK
  I-1  784 relations, 0 arcs cassés
  I-2  0 orphelins (7 sources sans verdict exemptées — conforme)
  I-7  27 constats = 18 verdicts + 9 gaps ; 18 verdicts sourcés
```

Résultats reproduits après commit contre le conteneur de production :
`docker exec likec4 likec4 validate` → ✓ Valid (20 files) ; `python3 tools/qa/integrity_check.py` → 7/7 OK.

## 5. Limites et renoncements

1. **Aucune source écartée** : les 3 sources apportent chacune un apport spécifique (variante HOCBF voilure fixe, APF anti-minima locaux, formation RL validée en réel). Aucun rattachement de complaisance n'a été nécessaire.
2. **`check_model_code_consistency.py` → FAIL=15**, non du fait de cette carte : `gh` n'est pas authentifié dans cette session (aucun GH_TOKEN), donc C-1 « dépôt inaccessible » échoue pour les 15 algorithmes. État **préexistant** vérifié avant modifications (FAIL=15 à HEAD), inchangé après (les champs `repository`/`version` ne sont pas touchés). Les dépôts `dagornc/alg-*` sont publics (HTTP 200 via API non authentifiée) : FAIL=0 exige une session `gh` authentifiée (orchestrateur/Christophe).
3. **Verdicts volontairement CONDITIONAL** sur l'échelle SWARM-3D (N=30) : aucune des 3 sources ne valide N=30 en vol réel.
