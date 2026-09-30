# Rapport de décision — 17 liens non scientifiques non appariés (11 internes + 6 GitHub)

- Carte : `t_74c19381` (Carte B)
- Audit source : `/home/hermesagent/swarmdrone-research/corpus-link-audit.json` (2026-09-28T08:09Z, `global_ok: false`, 39 liens non appariés sur 254)
- Périmètre de cette carte : 17 liens non scientifiques (11 internes + 6 GitHub). Les 22 liens scientifiques sont traités par la carte A `t_7e2b6f14`.
- Vérification réalisée le : 2026-09-30T08:12Z
- Méthode : HTTP réel (pas de supposition), sur l'URL publique `https://likec4.breizh.ai/…` ET sur l'ORIGINE (`docker exec likec4 curl http://localhost:5173/…`, sans Cloudflare). Pour chaque cible interne : statut HTTP, `content-type`, `content-length` (taille servie) et empreinte SHA-256 (disque vs servi vs origine). Pour chaque cible GitHub : interroge l'API GitHub (existence, visibilité, branche par défaut) et, pour `SwarmDrones`, le `.gitmodules` afin de distinguer les 3 submodules.
- Preuve reproductible : `tools/pending_promotion/_check_liens.py` (vérification des 11 liens internes).

Règle de décision appliquée :
- `rattache` — lien valide, cible existante et cohérente, à conserver / apparier.
- `redirige` — lien pointant une cible obsolète alors qu'une version courante existe.
- `retire` — doublon ou lien qui n'a plus lieu d'être.

## 1. Les 11 liens internes

Rappel du piège du projet : un HTTP 200 ne prouve RIEN sur un serveur SPA/Vite ; une route inexistante renvoie le fallback HTML (~555 o). On exige donc `content-type` + taille cohérente, et ici on ajoute la triple égalité SHA-256 (disque = servi = origine) pour exclure le fallback HTML ET un cache Cloudflare périmé (max-age 14400).

Résultat de la vérification : les 11 cibles internes sont RÉELLEMENT servies, avec un `content-type` et une taille conformes, et une empreinte SHA-256 identique entre le disque (`/docker/likec4/workspace/public/…`), le contenu servi publiquement et l'origine. Aucun fallback HTML, aucun écart disque/servi.

| # | URL | HTTP | content-type | Taille (o) | SHA-256 (12 hex) | Décision | Justification |
|---|-----|------|--------------|-----------|------------------|----------|---------------|
| 1 | `Spec_ALG_TASK_ALLOCATION_V3.pdf` | 200 | `application/pdf` | 1 306 101 | `c9f44f87b3…` | **rattache** | Version antérieure v3 du `specDoc specTaskAllocation`, conservée comme historique. PDF réel (`%PDF-1.7`), servi conforme. |
| 2 | `Spec_ALG_TASK_ALLOCATION_V2.pdf` | 200 | `application/pdf` | 1 088 218 | `68b305cd3e…` | **rattache** | Version antérieure v2, historique. PDF réel, servi conforme. |
| 3 | `Spec_ALG_TASK_ALLOCATION_CBBA.pdf` | 200 | `application/pdf` | 992 930 | `1884258947…` | **rattache** | Version initiale CBBA v1.1, historique. PDF réel, servi conforme. |
| 4 | `Specification_ALG_CONSENSUS_v1.pdf` | 200 | `application/pdf` | 1 267 630 | `9b630476df…` | **rattache** | Version antérieure v1 du `specDoc specConsensus`, historique. PDF réel, servi conforme. |
| 5 | `Specification_ALG_CONSENSUS_v2.pdf` | 200 | `application/pdf` | 1 291 670 | `ff9dc22313…` | **rattache** | Version antérieure v2, historique. PDF réel, servi conforme. |
| 6 | `Specification_ALG_CONSENSUS_v3.pdf` | 200 | `application/pdf` | 1 302 120 | `d45bbe25e3…` | **rattache** | Version antérieure v3, historique. PDF réel, servi conforme. |
| 7 | `Specification_ALG_CONSENSUS_v4.pdf` | 200 | `application/pdf` | 1 352 044 | `e8c555b9c4…` | **rattache** | Version **rejetée** (11,7/20, 2 bloquants, 9 majeurs). Conserver comme trace probatoire de la régression documentée, pas comme référence. PDF réel, servi conforme. |
| 8 | `Specification_ALG_CONSENSUS_v5.pdf` | 200 | `application/pdf` | 1 412 852 | `c6cf0cf73f…` | **rattache** | Version antérieure v5 (19,1/20, « PUBLIABLE SANS RESERVE ») mais supplantée par v7. Historique. PDF réel, servi conforme. |
| 9 | `consensus_rs/README.md` | 200 | `text/markdown` | 54 983 | `ca80f66950…` | **rattache** | README du portage Rust, rattaché à `srcConsensusRs`. C'est un artefact de code publié, pas une version de spec. Fichier réel (`# consensus_rs`), servi conforme. |
| 10 | `H-Zip_v2.2_Specification_premium.docx` | 200 | *(vide — usuel pour .docx)* | 509 619 | `abe5742acf…` | **retire** | **Doublon** du #11 : même URL, deux occurrences dans `hzip.c4`. Celle-ci est portée par l'élément `hzip` (protocol, ligne 44). La citation canonique du document normatif est portée par `specHzip` (specDoc, ligne 380) → conserver #11, retirer celle-ci (ou la remplacer par une relation C4 `hzip -> specHzip`). |
| 11 | `H-Zip_v2.2_Specification_premium.docx` | 200 | *(vide — usuel pour .docx)* | 509 619 | `abe5742acf…` | **rattache** | Lien canonique du document normatif H-Zip v2.2, porté par `specHzip` (`#source-doc`, ligne 380). Fichier réel (`PK\x03\x04`, ZIP/docx), servi conforme. |

Notes techniques :
- Le `content-type` du `.docx` est vide côté serveur. C'est documenté dans `sync_likec4.sh` comme un comportement fréquent pour `.docx`/`.bin` : ce n'est PAS un fallback SPA. La preuve est la triple égalité SHA-256 et la signature magique `PK\x03\x04` (conteneur OOXML/ZIP), taille exacte 509 619 o.
- Tous les PDF présentent la signature magique `%PDF-1.7` et une taille réelle (aucun n'a la taille de fallback ~555 o).

## 2. Les 6 liens GitHub

Vérification par API GitHub (`gh api`, authentifié `dagornc`) : chaque dépôt existe, est public, et sa branche par défaut est confirmée. Pour `SwarmDrones`, le `.gitmodules` confirme les 3 submodules cités.

| # | URL | Dépôt | Visibilité | Branche | Submodule (si SwarmDrones) | Décision | Justification |
|---|-----|-------|-----------|---------|----------------------------|----------|---------------|
| 1 | `github.com/dagornc/alg-task-allocation` | alg-task-allocation | public | `master` | — | **rattache** | Dépôt du portage Rust `task_alloc_rs` (CBBA événementiel + résilience partition). Existe et est accessible. |
| 2 | `github.com/dagornc/SwarmDrones` | SwarmDrones | public | `master` | `algorithms/task-allocation` → `alg-task-allocation.git` | **rattache** | Dépôt principal ; submodule `algorithms/task-allocation` confirmé dans `.gitmodules`. |
| 3 | `github.com/dagornc/alg-consensus` | alg-consensus | public | `master` | — | **rattache** | Dépôt du portage Rust `consensus_rs` (CRDT semi-treillis + gossip). Existe et est accessible. |
| 4 | `github.com/dagornc/SwarmDrones` | SwarmDrones | public | `master` | `algorithms/consensus` → `alg-consensus.git` | **rattache** | Dépôt principal ; submodule `algorithms/consensus` confirmé dans `.gitmodules`. |
| 5 | `github.com/dagornc/alg-protocole` | alg-protocole | public | `main` | — | **rattache** | Implémentation de référence du protocole H-Zip v2.2. Existe et est accessible. |
| 6 | `github.com/dagornc/SwarmDrones` | SwarmDrones | public | `master` | `protocols/hzip` → `alg-protocole.git` | **rattache** | Dépôt principal ; submodule `protocols/hzip` confirmé dans `.gitmodules`. |

Les 3 occurrences de `dagornc/SwarmDrones` sont bien 3 liens DISTINCTS, chacun justifié par un submodule différent (critère d'acceptation 4) :
- `algorithms/task-allocation` → `alg-task-allocation`
- `algorithms/consensus` → `alg-consensus`
- `protocols/hzip` → `alg-protocole`

Aucune des 3 n'est à retirer : elles documentent la composition du dépôt agrégateur.

## 3. Synthèse des décisions

| Décision | Nombre | Liens |
|----------|--------|-------|
| `rattache` | 16 | 8 PDF historiques (Task Allocation ×3, Consensus v1–v5) + README consensus_rs + docx H-Zip (canonique, #11) + 6 GitHub |
| `redirige` | 0 | — |
| `retire` | 1 | le doublon H-Zip (#10, occurrence protocol `hzip`) — le #11 (occurrence specDoc `specHzip`) étant conservé |

Aucune version antérieure ne redirige : l'historique de version (y compris la v4 rejetée) a une valeur de traçabilité et est déjà présenté comme « version antérieure » dans le modèle. Pour Consensus, la version courante v7 est portée par un lien distinct (`Spec_ALG_CONSENSUS_v7.pdf`, servie). Pour Task Allocation, la version courante annoncée (v4) n'a en revanche aucun PDF publié — voir le point 1 de la section 4, qui est l'action de correction à trancher, et non une redirection de ces liens historiques.

## 4. Incohérences et points d'attention (à trancher humainement — non modifiés)

1. **`specTaskAllocation` déclare `versionCourante 'v4'` mais aucun PDF v4 n'est publié.** Les seuls artefacts Task Allocation servis sont CBBA, V2, V3 ; aucun `Spec_ALG_TASK_ALLOCATION_v4.pdf` n'existe ni dans le repo ni dans le serveur. Deux options : publier le PDF v4, ou corriger la métadonnée `versionCourante` (v3). C'est une dette documentaire à traiter séparément — hors périmètre de cette carte (garde-fou : pas d'écriture dans le modèle).

2. **Les 8 PDF historiques ne sont PAS versionnés dans le repo `swarmdrones_likec4/public/`.** Ils ne survivent dans `/docker/likec4/workspace/public/` que parce que `sync_likec4.sh` ne supprime jamais de fichier de destination. Ils sont donc servis aujourd'hui, mais non reproductibles : une reconstruction propre de la destination les ferait disparaître. Si l'on souhaite conserver durablement cet historique (décision `rattache` ci-dessus), il faut les réintégrer dans `public/` versionné (archive) ; sinon, les retirer du modèle.

3. **Doublon H-Zip confirmé** : la même URL `H-Zip_v2.2_Specification_premium.docx` est référencée deux fois dans `hzip.c4` (ligne 44, élément `hzip` ; ligne 380, élément `specHzip`). Empreinte identique (`abe5742acf…`). Recommandation : conserver le lien `#source-doc` sur `specHzip` (canonique) et retirer le lien dupliqué sur `hzip`, en le remplaçant éventuellement par une relation C4 (`hzip -> specHzip`, « documenté par ») pour ne pas perdre la traçabilité.

4. **`versionCourante` Consensus = v7** : la cible courante `Spec_ALG_CONSENSUS_v7.pdf` est bien servie (200, `application/pdf`, 156 484 o, aux deux chemins racine et `specification/`). Les liens v1–v5 restent donc légitimes en tant qu'historique.

## 5. Garde-fous respectés

- Aucune écriture dans `science.c4` (ni dans aucun autre `.c4`) : ce rapport est une décision, l'écriture dans le modèle reste une décision humaine.
- `corpus-link-audit.json` non modifié (artefact d'audit daté).
- Vérification exigeante : `content-type` + taille réelle + SHA-256 disque/servi/origine pour chaque cible interne (pas de confiance dans un HTTP 200 nu).
- Aucun secret exposé.
