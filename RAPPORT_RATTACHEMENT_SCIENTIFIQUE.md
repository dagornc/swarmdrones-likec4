# Rapport — Rattachement des articles scientifiques aux cartes d'algorithme LikeC4

**Tâche** : t_4f8a3ca4 (LIKEC4-SCI)
**Date** : 2026-09-28
**Profil** : architecte
**Modèle** : `~/workspace/swarmdrones_likec4/` (repo `dagornc/swarmdrones-likec4`)

---

## 1. Conclusion (synthèse exécutive)

Le diagnostic du ticket (« 11 algorithmes sans rattachement scientifique ») était **périmé**. Entre la rédaction du ticket et son exécution, le fichier `e20-audit-completeness.c4` (findings SCI-5 à SCI-11) avait déjà rattaché 8 de ces 11 algorithmes à des sources primaires.

État réel constaté sur 15 algorithmes :

- **12 algorithmes** étaient déjà rattachés (`sciX -[evidences]-> algY`) via `science.c4` (SCI-1..4) et `e20-audit-completeness.c4` (SCI-5..11).
- **3 algorithmes** n'avaient **aucun** rattachement scientifique : `algLeaderElection`, `algSafetyRules`, `algPathPlanning`.

Ces 3 algorithmes sont désormais rattachés, sur la base du contenu réel de leurs `research_*.md` (profil mathématique, méthode Dream-RSI), avec des verdicts honnêtes (SUPPORTED sur les fondations, CONDITIONAL sur l'échelle N=30 réel).

**13 nouvelles sources primaires (`specDoc #science`)**, **3 nouveaux constats-verdicts (`SCI-12`, `SCI-13`, `SCI-14`)**, **3 nouveaux gaps (`GAP-7..9`)** et leurs relations ont été ajoutés dans `science.c4`. Les métadonnées `evidence`/`references`/`evidenceLevel` des 3 cartes d'algorithme dans `algorithms.c4` ont été mises en cohérence.

**Aucun DOI, arXiv ni titre n'a été inventé** : toutes les sources ajoutées proviennent textuellement des `research_*.md` des specs. Les références non vérifiables (manuscrits « in preparation »/« submitted », références normatives sans DOI, implémentation etcd) ont été écartées du rattachement et documentées comme non rattachables.

---

## 2. Tableau de couverture des 15 algorithmes

| # | Algorithme | Constat(s) rattaché(s) | Sources primaires | Statut |
|---|---|---|---|---|
| 1 | algTaskAllocation | SCI-1 (science.c4), SCI-10 (e20) | srcCBBA, srcCBBA24, srcDegraded30, srcETPBBA | déjà rattaché |
| 2 | algConsensus | SCI-3 (science.c4), SCI-6 (e20) | srcCRDT, srcKilobot, srcEventTrigConsensus, srcQAR, srcETPBBA | déjà rattaché |
| 3 | algFormationControl | SCI-11 (e20) | srcHeteroUAVUSV, srcVisFormGPSDeg | déjà rattaché |
| 4 | **algLeaderElection** | **SCI-12 (ajouté)** | srcRaft, srcBully, srcPaxos | **corrigé ici** |
| 5 | algPerceptionFusion | SCI-4 (science.c4), SCI-7 (e20) | srcUUV, srcSTDCL, srcUSVCoopLoc | déjà rattaché |
| 6 | algNavigationGNSSDegrade | SCI-5 (e20) | srcSwarmRaft, srcSlamSurvey, srcVisFormGPSDeg | déjà rattaché |
| 7 | algCollisionAvoidance | SCI-2 (science.c4) | srcCAHCBF (et srcCBFMultiFixed) | déjà rattaché |
| 8 | **algSafetyRules** | **SCI-13 (ajouté)** | srcCBFTheory, srcCBFSwarm (+ ACAS X, EASA/FAA normatif) | **corrigé ici** |
| 9 | **algPathPlanning** | **SCI-14 (ajouté)** | srcDMPCTube, srcImpedanceDiffusion, srcDiff4D, srcPathMedUAV, srcVAPF, srcHRLMPC, srcSwarmGPT, srcAccelMPC | **corrigé ici** |
| 10 | algHealthMonitoring | SCI-8 (e20) | srcFTCAllocUSV | déjà rattaché |
| 11 | algEnergyAware | SCI-10 (e20) | srcETPBBA | déjà rattaché |
| 12 | algEventTriggeredComm | SCI-6 (e20) | srcEventTrigConsensus, srcQAR, srcETPBBA | déjà rattaché |
| 13 | algCooperativeLocalization | SCI-7 (e20) | srcSTDCL, srcUSVCoopLoc | déjà rattaché |
| 14 | algFaultTolerantControlAlloc | SCI-8 (e20) | srcFTCAllocUSV | déjà rattaché |
| 15 | algJammingResilientMode | SCI-9 (e20) | srcADMOS, srcZeroTrust | déjà rattaché |

---

## 3. Détail des 3 rattachements créés

### 3.1 SCI-12 — ALG_LEADER_ELECTION

- **Avant** : `evidence 'aucune source verifiee'`, `evidenceLevel 'NONE'`.
- **Sources rattachées** (issues de `research_leader_election_v1.md`) :
  - `srcRaft` — Ongaro & Ousterhout 2014, DOI 10.1145/2627470.2627476
  - `srcBully` — Garcia-Molina 1982, DOI 10.1109/TC.1982.1675885
  - `srcPaxos` — Lamport 1998, DOI 10.1145/279227.279229
- **Verdict** : `SUPPORTED (fondations) / CONDITIONAL (essaim mobile 30)`.
- **Non rattachables** :
  - Dagorn « Adaptive Leader Election for Mobile Drone Swarms » (ICRA 2024) — manuscrit *in preparation*, non public.
  - etcd (Raft en production) — implémentation, pas un article scientifique.

### 3.2 SCI-13 — ALG_SAFETY_RULES

- **Avant** : `evidence 'MEDIUM (repris du modele existant)'` sans source.
- **Sources rattachées** (issues de `research_safety_rules_v1.md`) :
  - `srcCBFTheory` — Ames et al. 2019, DOI 10.23919/ECC.2019.8796023
  - `srcCBFSwarm` — Wang et al. 2022, DOI 10.1109/LRA.2022.3145678
- **Socle normatif documenté sans DOI** : ACAS X (MIT Lincoln Lab), EASA AMC/GM Part-UAS, FAA AC 90-117.
- **Verdict** : `SUPPORTED (fondations CBF + normatif) / CONDITIONAL (composition floue)`.
- **Non rattachables** : Dagorn « Distributed Safety Rules… » (AIAA 2024) — manuscrit *submitted*, non public.

### 3.3 SCI-14 — ALG_PATH_PLANNING

- **Avant** : `evidence 'MEDIUM (repris du modele existant)'` sans source.
- **Sources rattachées** (issues de `research_path_planning_v1.md`) :
  - `srcDMPCTube` — Dai et al. 2026, DOI 10.3390/drones10030177 (source fondatrice, lue intégralement)
  - `srcImpedanceDiffusion` — Batool et al. 2026, arXiv:2603.09031
  - `srcDiff4D` — Li et al. 2026, arXiv:2606.31197
  - `srcPathMedUAV` — Scientific Reports 2026, DOI 10.1038/s41598-026-70043-1
  - `srcVAPF` — Machines 2026, DOI 10.3390/machines13070600
  - `srcHRLMPC` — Studt & Schildbach 2025, arXiv:2509.15799
  - `srcSwarmGPT` — Schuck et al. 2024, arXiv:2412.08428
  - `srcAccelMPC` — Grillo & Plancher 2026, arXiv:2609.09380
- **Verdict** : `SUPPORTED (MPC tube-based) / CONDITIONAL (N=30, partition)`.
- **Non rattachable** : S5 « amphibious UAV PSO » (DOI 10.1007/s44443-026-00976-0) — échec de lecture dans la spec, marquée `[NON VÉRIFIÉ]`.

---

## 4. Inventaire des sources scientifiques par rapport aux research_*.md

Méthode : extraction des DOI/arXiv de chaque `research_*.md`, comparaison avec les sources `specDoc #science` du modèle (science.c4 + e20-audit-completeness.c4).

### 4.1 Algorithmes corrigés dans ce ticket — toutes les sources vérifiables sont désormais dans le modèle

| Algorithme | DOI/arXiv cités dans la spec | Présent comme specDoc #science |
|---|---|---|
| leader_election | 10.1145/2627470.2627476, 10.1109/TC.1982.1675885, 10.1145/279227.279229 | **3/3 ajoutés** |
| safety_rules | 10.23919/ECC.2019.8796023, 10.1109/LRA.2022.3145678 | **2/2 ajoutés** |
| path_planning | 8 sources vérifiables (S1-S4, S6-S9) | **8/8 ajoutées** (S5 exclue, non vérifiée) |

### 4.2 Algorithmes déjà rattachés — écarts résiduels constatés (non ajoutés)

Pour les 12 algorithmes déjà couverts, les `research_*.md` citent des articles additionnels qui **ne sont pas** présents en `specDoc #science` (certains sont néanmoins présents en `link` brut dans la carte d'algorithme). Ces écarts sont **documentés, pas corrigés** : ils relèvent d'un enrichissement ultérieur qui nécessiterait de relire chaque article avant de l'ancrer (règle E08 « pas de lecture, pas de verdict »).

- **collision_avoidance** : 4 absents (10.1109/access.2025.3646978, 10.1109/yac66630.2025.11150122, arXiv:2309.13285, arXiv:2401.14554). Présents : 10.3390/drones8080415, arXiv:2604.13245, arXiv:2603.13103.
- **energy_aware** : 3 absents (10.1109/lra.2022.3148765, 10.1109/tcyb.2022.3189234, 10.1109/tvt.2023.3245678).
- **event_triggered_comm** : 3 absents (10.1109/tac.2011.2113456, 10.1109/tac.2015.2398765, 10.1109/tcyb.2022.3198765).
- **formation_control** : 8 absents en specDoc (mais tous présents en `link` dans algFormationControl) ; arXiv:2410.18495 présent via srcFormationRL.
- **health_monitoring** : 3 absents (10.1109/jproc.2006.887293, 10.1109/phm.2018.8449123, 10.1109/tr.2011.2165098).
- **jamming_resilient_mode** : 1 absent (10.1002/net.3230040204) ; 10.1007/s44465-026-00041-0 et 10.1016/j.ins.2026.124096 présents.
- **nav_gnss_degrade** : sources citées sans DOI (Huang 2024 ; ORB-SLAM2 Mur-Artal & Tardós 2017 ; Groves 2013) — le modèle ancre déjà 3 sources (srcSwarmRaft, srcSlamSurvey, srcVisFormGPSDeg).
- **fault_tolerant_control_alloc** : sources citées sans DOI (Zhang 2024 ; Johansen & Fossen 2013 ; Ames 2019) — le modèle ancre srcFTCAllocUSV.
- **perception_fusion** : ~11 DOI absents en specDoc (dont arXiv:2409.17997, arXiv:2502.02687, arXiv:2603.08379, arXiv:2604.02878, arXiv:2608.10921, 10.1002/rnc.5496, 10.1016/j.sigpro.2022.108678…) ; 10.3390/drones9110752 présent via srcUUV.
- **cooperative_localization** : 4/4 présents (10.3390/drones10010069, 10.1109/tie.2026.3672870, 10.1007/978-981-92-4392-1_19, 10.1016/j.measurement.2026.122307).

---

## 5. Éléments ajoutés au modèle

### 5.1 Nouvelles sources primaires (13) — `science.c4`, section 1ter

srcRaft, srcBully, srcPaxos, srcCBFTheory, srcCBFSwarm, srcDMPCTube, srcImpedanceDiffusion, srcDiff4D, srcPathMedUAV, srcVAPF, srcHRLMPC, srcSwarmGPT, srcAccelMPC.

Statut honnête par source : `REPERTORIEE (titre+DOI)` pour leader_election et safety_rules (cités par la spec, non relus par l'architecte) ; `CONSULTEE (spec — research_path_planning_v1.md, …)` pour path_planning (lus par le profil mathématique, consignés dans la spec).

### 5.2 Nouveaux constats-verdicts (3) — `science.c4`, section 2

- `sciLeaderElection` (SCI-12)
- `sciSafetyRules` (SCI-13)
- `sciPathPlanning` (SCI-14)

### 5.3 Nouveaux gaps (3) — `science.c4`, section 3

- `gap7` (élection de leader sur 30 drones mobiles sous partition)
- `gap8` (vérification formelle composition CBF + règles floues)
- `gap9` (planification multi-agent N=30 sous partition/brouillage)

### 5.4 Relations ajoutées — `science.c4`, section 4

- 14 relations `sciX -[uses]-> srcX`
- 3 relations `sciX -[evidences]-> algY` (les rattachements demandés)
- 3 relations `gapN -[exposes]-> sciX`

### 5.5 Métadonnées mises à jour — `algorithms.c4`

`evidence`, `references`, `evidenceLevel` de algLeaderElection, algSafetyRules, algPathPlanning mis en cohérence avec les nouveaux constats.

---

## 6. Validation

Commande (clone propre, comme exigé) :

```
git clone -q . /tmp/lc_sci && cd /tmp/lc_sci && npx likec4 validate
```

Résultat : voir la section dédiée du compte rendu de complétion. Attendu `✓ Valid (20 files)`.

---

## 7. Renoncements et limites assumés

1. **Périmètre limité aux 3 algorithmes réellement non rattachés.** Le ticket listait 11 algorithmes ; 8 avaient déjà été couverts par `e20-audit-completeness.c4`. Aucun rattachement redondant n'a été créé.
2. **Pas d'ajout massif des articles additionnels** des 12 specs déjà couvertes (section 4.2) : les ancrer en `specDoc #science` exigerait de relire chacun d'eux (règle « pas de lecture, pas de verdict »). Ils sont documentés comme écarts à arbitrer.
3. **Références non vérifiables écartées** du rattachement : manuscrits Dagorn (in preparation / submitted), références normatives sans DOI (ACAS X, EASA/FAA), implémentation etcd, S5 de path_planning (échec de lecture).
4. **Aucun DOI/arXiv/titre inventé** : tout identifiant provient textuellement des `research_*.md`.
