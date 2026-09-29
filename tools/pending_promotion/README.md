# Outillage — circuit de promotion pending -> LikeC4 (carte t_1ce6f331)

Pipeline en 3 etages pour promouvoir les propositions `pending` de
`impact-proposals.json` vers le modele LikeC4, avec validation humaine.

## Etage 1 — le cron produit les propositions (corrige)
`analyze_impact.py` (depot `swarmdrone-profile/scripts/`, commit 8df91ad) cible
desormais les 15 algorithmes canoniques (alg*) en priorite, avant les
composants (onboard.*/edge.*). Test : `test_impact_targeting.py`.
Deploiement : `hermes profile update swarmdrone --yes` (autorisation Christophe).

## Etage 2 — l'agent lit et statue
1. `python3 lc_pending_cards.py` — cartes des propositions pending
   (titre/DOI/arXiv/abstract extrait de articles/).
2. Adjudication manuelle : rediger un ledger JSON (modele :
   `ledger_pending_lot01.json`), reutilisant le schema de la campagne 465
   (`rattachees` / `specdoc_only` / `deja` / `ecartees`).
3. `python3 report_verdicts.py ledger_pending_lot01.json` — genere
   `RAPPORT_VERDICTS_<lot>.md` (rapport decidable) ET `<lot>_additions.c4`
   (blocs LikeC4, NON inseres).

Verdicts :
- `RATTACHEE` -> patron 2 sauts : `srcXXX -[uses]<- sciFinding -[evidences]-> algYYY`
- `ECARTEE`  -> hors-perimetre | pas-algorithme-canonique | paradigme-exclu |
                non-primaire | deja-couvert | non-verifiable | doublon

## Etage 3 — validation humaine (OBLIGATOIRE)
Aucune ecriture automatique dans `science.c4`. Christophe valide le rapport ;
l'insertion des blocs `<lot>_additions.c4` a lieu dans une etape separee,
hors de cette carte.

## Garde-fous
- Anti-doublon par DOI/arXiv ET par titre (le DOI du specDoc peut differer de
  l'arXiv) : voir `tools/statut465/README.md`.
- Ne jamais inventer un DOI, un composant, un finding ou un lien.
- Verifier les identifiants d'algorithmes dans `algorithms.c4`.
- SCI suivant au 2026-09-29 : SCI-61 (SCI-60 max apres ce lot).
- `gen_science_additions.py` est reutilise depuis `tools/statut465/`.

## Etat au 2026-09-29
- 45 propositions pending statuees en un lot (ledger_pending_lot01.json) :
  5 RATTACHEE (SCI-56..60), 1 completion SCI-29, 3 DEJA_RATTACHEE, 36 ECARTEE.
- science.c4 : 66 specDocs + 55 findings + ce lot en attente de validation.
