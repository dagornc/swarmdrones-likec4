# Outillage — campagne de statut des 465 articles (carte t_3f3134cc)

Scripts réutilisables pour poursuivre la campagne (lots restants 7-19).

## Pipeline par lot
1. `python3 lc_cards.py /tmp/lot_NN.json > cards_NN.txt` — cartes (titre/DOI/abstract) à lire
2. Adjudication manuelle : rédiger `/tmp/ledger_lotNN.json` (modèle : voir ledger_lot01..06.json)
3. `python3 gen_science_additions.py /tmp/ledger_lotNN.json > lotNN_additions.c4`
4. `python3 lc_split.py lotNN_additions.c4` (produit lotNN_{specdocs,findings,relations}.c4)
5. `python3 lc_insert.py lotNN` (insère dans science.c4)
6. `cp science.c4 /tmp/lc_v7/ && docker run -v /tmp/lc_v7:/data --entrypoint sh ghcr.io/likec4/likec4:1.59.2 -c "likec4 validate /data"`
7. Mettre à jour RAPPORT_STATUT_465.md + commit

## Garde-fous
- SCI suivant : SCI-48 (SCI-47 max au 2026-09-29).
- Jamais de doublon d'élément : vérifier collisions via `python3 lc_collision.py` (DOI/arXiv/corpus#) ET reconnaissance par TITRE (le DOI publié peut différer de l'arXiv du specDoc).
- 24 articles ont déjà un specDoc (voir lc_already.py) : les réutiliser (DEJA), ne jamais dupliquer.
- Détection automatique insuffisante : toujours confronter au titre (ex. #205 SwarmRaft = srcSwarmRaft malgré DOI différent).
- `RATTACHEE` → specDoc + finding + evidences ; `specdoc_only` → compléter un finding existant (target_finding).
- Verdict ECARTEE : hors-perimetre | pas-algorithme-canonique | paradigme-exclu | non-primaire | deja-couvert | non-verifiable | doublon.
- La validation ne couvre que la syntaxe : vérifier I-1/I-2 via export JSON (lc_final_integrity.py).

## État au 2026-09-29
- 150/465 statués (lots 1-6, commits debd594..66cc2f2).
- 26 RATTACHEE (SCI-24..47 + 2 complétions SCI-6/SCI-8), 17 DEJA_RATTACHEE, 1 DEJA_ECARTEE (#134), 106 ECARTEE.
- Ledger consolidé : ledger_statut_465.json.
- Le push vers GitHub échoue dans la session architecte (gh non authentifié) — passer par l'orchestrateur/Christophe.
