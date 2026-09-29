# Rapport — Traitement des 2 sources « A CONSULTER » : apprentissage & sûreté

Carte : t_5773661d — profil architecte — 2026-09-29
Commit : 2b184f7 (amended) — `fix(science): ECARTER 2 sources MARL (apprentissage & surete) sans apport specifique`

## Verdict global

| Source | Domaine | Verdict | Statut final |
|---|---|---|---|
| srcHMARLCBF — HMARL-CBF (NeurIPS 2025) | apprentissage & sûreté | **ECARTEE** | `ECARTEE` |
| srcExplainableMARL — MOISE+MARL (AAMAS 2025) | apprentissage & sûreté | **ECARTEE** | `ECARTEE` |

Les deux sources sont des papiers de conférence récents dont le paradigme (sûreté
APPRISE par RL) est explicitement exclu par le modèle, dont la sûreté et la
coordination sont déterministes et non apprises. Aucun rattachement de
complaisance n'a été créé.

## 1. srcHMARLCBF — HMARL-CBF (NeurIPS 2025)

- **Lien lu** : https://proceedings.neurips.cc/paper_files/paper/2025/file/76486c7eb6056f12e7ce3addced61650-Paper-Conference.pdf (HTTP 200, application/pdf, 5,7 Mo — lu intégralement : abstract, méthode, expériences, ablation, conclusion).
- **Ce que dit l'article** : HMARL-CBF = MARL hiérarchique à compétences (niveau
  haut : politique jointe sur des compétences ; niveau bas : exécution sûre des
  compétences via CBF), cadre CTDE. Garantie de sûreté *pointwise-in-time*
  (à chaque pas) pendant l'entraînement ET l'exécution, vs contraintes CMDP en
  espérance. Validé sur METADRIVE (trafic routier : Merging, Intersection,
  Roundabout, Bottleneck, Tollgate), en simulation uniquement ; ~99 % de succès.
- **Verdict : ECARTEE.** Raisons :
  1. Le modèle EXCLUT la sûreté apprise. `algSafetyRules` = règles PRE-APPROUVÉES
     déterministes + watchdog ; `algCollisionAvoidance` = CBF-QP déterministe
     (« couche non négociable »). HMARL-CBF apprend la sûreté — paradigme opposé.
  2. Domaine routier (METADRIVE), pas aérien/maritime. Aucune transposition directe.
  3. Simulation uniquement : ne lève ni GAP-2 (CBF à N=30 en matériel réel)
     ni GAP-8 (vérification formelle de la composition CBF + règles floues).
  4. Apport = confirmation générique « CBF comme filtre sous politique
     hiérarchique apprise » — précisément le type d'apport générique à écarter.

## 2. srcExplainableMARL — MOISE+MARL (AAMAS 2025)

- **Lien lu** : https://www.ifaamas.org/Proceedings/aamas2025/pdfs/p1968.pdf (HTTP 200, application/pdf, 1,2 Mo — lu intégralement : abstract, cadre MOISE+, méthode TEMM, protocole expérimental, résultats, conclusion).
- **Ce que dit l'article** : MOISE+MARL intègre des rôles et missions
  organisationnels (modèle MOISE+) dans un MARL Dec-POMDP, via des guides de
  contrainte (masquage d'actions, shaping de récompense) et la méthode TEMM
  (inférence non supervisée de rôles/missions implicites). Explicabilité et
  contrôle au niveau ORGANISATIONNEL. Benchmarks génériques (Predator-Prey,
  Overcooked, Warehouse, Cyber-Defense), simulation uniquement.
- **Verdict : ECARTEE.** Raisons :
  1. Aucun algorithme du modèle n'est de la coordination MARL apprise :
     la coopération est portée par CBBA, Raft/CRDT, CBF-QP et MPC (déterministes).
  2. L'explicabilité du modèle (CAP_OBSERVE) = télémétrie / jumeau numérique /
     rejeu — pas l'explication de politiques apprises.
  3. Apport organisationnel hors paradigme du modèle ; benchmarks génériques,
     pas d'essaim de drones. Ne vaut pas rattachement.

## Preuves de lecture

- Les deux PDF ont été téléchargés (HTTP 200, application/pdf) et convertis en
  texte (`pdftotext`) : 1959 lignes pour HMARL-CBF, 633 pour MOISE+MARL.
- Les justifications ECARTEE sont ancrées dans le contenu réel : METADRIVE,
  ≥95 %/~99 % de succès, TEMM, MOISE+, Dec-POMDP, benchmarks cités.

## Changements

1. `science.c4` — `srcHMARLCBF` et `srcExplainableMARL` : statut
   `A CONSULTER` → `ECARTEE`, description remplacée par la justification
   explicite. Liens existants conservés (aucun DOI/lien/composant inventé).
2. `tools/qa/integrity_check.py` — contrôle I-2 : les `specDoc` de statut
   `ECARTEE` (sources lues et rejetées) sont désormais exemptées du contrôle
   d'orphelins, au même titre que `A CONSULTER` (sources non lues).

## Vérifications

- `likec4 validate` sur clone propre : **Valid (20 files)**.
- `python3 tools/qa/integrity_check.py` : **7/7 OK**.
- `python3 tools/qa/check_model_code_consistency.py` : FAIL=15 **préexistant**
  (C-1 « dépôt inaccessible » via `gh api` — la session architecte n'a aucune
  credential GitHub). Non causé par ce diff (qui ne touche ni algorithms.c4 ni
  les dépôts). Preuve que le FAIL est un faux négatif d'outillage : les 15 dépôts
  répondent HTTP 200 en appel API anonyme (curl). C-4 (cohérence interne
  modèle↔code) = OK.

## Note sur la concurrence (hotspot)

`science.c4` est édité en parallèle par 4 autres cartes « A CONSULTER » du même
profil architecte (t_5514113a, t_69386d9c, t_ad1cb4de, t_be28af16). Un premier
commit a capté par erreur le travail non commité de t_69386d9c (srcCrossDomainASW) ;
il a été **amendé** (2b184f7) pour ne contenir QUE les 2 ECARTEE + l'exemption
I-2. Les éditions concurrentes des cartes sœurs sont préservées dans
/tmp/src_read/current_worktree_full.patch et /tmp/src_read/sibling_crossdomain_change.patch.
Point de collision à décomposer si récurrence (une carte par fichier).
