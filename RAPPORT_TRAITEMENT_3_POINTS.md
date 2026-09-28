# Traitement des 3 points d'audit — LikeC4 SWARM-3D

**Date** : 2026-09-28
**Commit** : `2a8dff7` (poussé sur `dagornc/swarmdrones-likec4`)
**Validation** : `likec4 validate` sur clone propre → `✓ Valid (20 files)`

---

## Point 1 — 28 liens GitHub morts → rebranchés

**Problème** : le dépôt `dagornc/swarmdrones-likec4` est **PRIVÉ**. Les 28 URLs
`blob/master/...` du modèle renvoyaient donc **404** pour tout lecteur non
authentifié, alors que les artefacts sont servis publiquement.

**Vérification préalable** : les 28 artefacts testés un par un sur
`likec4.breizh.ai` → **28/28 en HTTP 200**.

**Correction** : 41 liens rebranchés (28 URLs distinctes, certaines répétées) :
- `algorithms.c4` : 26 liens
- `sysml.c4` : 15 liens

**Résultat** : 0 occurrence restante de l'ancienne URL.

---

## Point 2 — 2 DOI morts → remplacés par les sources canoniques

Les deux DOI renvoyaient **404** et étaient **absents de Crossref** (vérifié par
API) : ils ne correspondaient à aucune publication réelle.

### srcCBFSwarm
- **Avant** : `10.1109/LRA.2022.3145678` — « Safety-Critical Control of Drone
  Swarms via Control Barrier Functions » (Wang et al. 2022, RA-L) → **inexistant**
- **Après** : `10.1109/ACC.2016.7526486` — « Safety barrier certificates for
  heterogeneous multi-robot systems » (Wang L., Ames A., Egerstedt M., ACC 2016)
- **Vérifié Crossref** : titre, auteurs, revue, année complets.

### srcHeteroRetrieval
- **Avant** : `10.22541/au.172457058.83855084` — preprint Authorea → **mort**
- **Après** : `10.1002/rob.70011` — « A Heterogeneous Multirobot System for
  Autonomous Object Retrieval in Challenging GNSS-Denied Maritime Environment »
  (Chen Q., Irfan M., Yu Q., *Journal of Field Robotics*, 2025)
- **Vérifié Crossref** : c'est la **version publiée** du même travail.

**Honnêteté** : les cartes portent une note explicite documentant le DOI
précédent et sa correction. Aucune source n'a été inventée.

---

## Point 3 — Findings orphelins → rattachés

**Correction d'une fausse alerte** : le rapport d'audit annonçait « 11 sources
orphelines ». Vérification exhaustive : **3 seulement**, et ce sont des
`finding` (constats de recherche), pas des sources bibliographiques.

**Les 3 constats orphelins** :
- `sciLeaderElection` (SCI-12) — fondations Raft/Bully/Paxos
- `sciSafetyRules` (SCI-13) — fondations CBF + socle normatif ACAS X / EASA-FAA
- `sciPathPlanning` (SCI-14) — MPC tube-based

**Correction** : 3 relations `evidences` ajoutées dans
`e20-audit-completeness.c4` + inclusion dans les 2 vues de traçabilité
(`scienceVerdicts`, `scienceToAlgorithms`).

**Résultat** : 7 sources déclarées / 7 référencées → **0 orphelin**.

---

## État final

- **Board** : 144 `done`, 0 carte active
- **HEAD local = GitHub** : `2a8dff7`
- **Working tree** : propre
- **`likec4 validate`** : `✓ Valid (20 files)`
- **Modèle servi** : cohérence confirmée par le hook post-commit (5 valeurs)

**Action restante (autorisation requise)** : `docker restart likec4` pour que le
conteneur serve les corrections. Le hook a synchronisé les fichiers mais n'a pas
redémarré le conteneur (`--no-restart`).
