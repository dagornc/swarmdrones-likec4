#!/usr/bin/env python3
"""report_verdicts.py — genere le rapport de verdicts ET les blocs LikeC4
(specDoc + finding + relations) pour un ledger de propositions pending.

Les blocs LikeC4 ne sont JAMAIS inseres dans science.c4 : ils sont ecrits dans
un fichier separe, a appliquer uniquement apres validation humaine (Christophe).

Usage :
    python3 tools/pending_promotion/report_verdicts.py \
        tools/pending_promotion/ledger_pending_lot01.json \
        [--out-dir /tmp]

Sorties :
    RAPPORT_VERDICTS_<lot>.md   rapport lisible et decidable
    <lot>_additions.c4          blocs LikeC4 a valider (non inseres)
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATUT465 = HERE.parent / 'statut465' / 'gen_science_additions.py'


def load_gen():
    spec = importlib.util.spec_from_file_location('gen_science_additions', STATUT465)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def gen_additions(gen, ledger) -> str:
    parts = []
    for d in ledger.get('rattachees', []):
        parts.append(gen.specdoc(d))
        parts.append(gen.finding(d))
        parts.append(gen.relations(d))
    for d in ledger.get('specdoc_only', []):
        parts.append(gen.specdoc(d))
        parts.append(f"  {d['target_finding']} -[uses]-> {d['src']} '{d['note']}'")
    banner = (
        "// =============================================================================\n"
        f"//  {ledger.get('lot_label','LOT')} — BLOCS A VALIDER (non inseres dans science.c4)\n"
        "//  Validation humaine OBLIGATOIRE avant insertion (carte t_1ce6f331).\n"
        "// =============================================================================\n\n"
    )
    return banner + "\n\n".join(parts) + "\n"


def report(ledger, additions_path: str) -> str:
    L = []
    A = lambda s='': L.append(s)

    n_ratt = len(ledger.get('rattachees', []))
    n_sd = len(ledger.get('specdoc_only', []))
    n_deja = len(ledger.get('deja', []))
    n_ec = len(ledger.get('ecartees', []))
    total = n_ratt + n_sd + n_deja + n_ec

    A("# RAPPORT — Verdicts du circuit pending -> LikeC4 (carte t_1ce6f331)")
    A()
    A(f"Lot : {ledger.get('lot_label','')}")
    A(f"Date : 2026-09-29 — architecte")
    A()
    A("## Objet")
    A()
    A("Ce rapport statue chacune des 45 propositions `pending` de "
      "`impact-proposals.json` (etage 2 du circuit de promotion). "
      "AUCUNE ecriture n'a ete faite dans `science.c4` : les blocs LikeC4 "
      "correspondants aux rattachements sont fournis separement, a inserer "
      "uniquement apres validation de Christophe (etage 3).")
    A()
    A("## Synthese")
    A()
    A(f"| Verdict | Nombre |")
    A(f"|---------|--------|")
    A(f"| RATTACHEE (nouveau finding) | {n_ratt} |")
    A(f"| RATTACHEE (completion d'un finding existant) | {n_sd} |")
    A(f"| DEJA_RATTACHEE (source deja presente) | {n_deja} |")
    A(f"| ECARTEE | {n_ec} |")
    A(f"| **Total** | **{total}** |")
    A()

    if n_ratt:
        A("## 1. RATTACHEE — nouveaux findings proposes (SCI-56..SCI-60)")
        A()
        A("Patron 2 sauts : `srcXXX <-[uses]- sciFinding -[evidences]-> algYYY`.")
        A()
        for d in ledger['rattachees']:
            f = d['finding']
            algs = ", ".join(a for a, _ in d['algs'])
            A(f"### {f['title']}")
            A()
            A(f"- Source : {d['title']}")
            A(f"- specDoc : `{d['src']}` | finding : `{f['id']}`")
            A(f"- Algorithme(s) cible(s) : {algs}")
            A(f"- Lien : {_links(d)}")
            A(f"- Justification : {f['description']}")
            A()

    if n_sd:
        A("## 2. RATTACHEE — completion d'un finding existant (specdoc only)")
        A()
        for d in ledger['specdoc_only']:
            A(f"- {d['title']}")
            A(f"  - specDoc : `{d['src']}` -> complete `{d['target_finding']}`")
            A(f"  - note : {d['note']}")
            A()

    if n_deja:
        A("## 3. DEJA_RATTACHEE — deja sources, aucun doublon a creer")
        A()
        for d in ledger['deja']:
            A(f"- #{d['number']} {d['title'][:80]}")
            A(f"  - specDoc existant : `{d.get('existing_src','?')}` | finding : `{d.get('existing_finding','?')}`")
            A()

    if n_ec:
        A("## 4. ECARTEE — verdicts et raisons")
        A()
        A("| # | Titre | Raison |")
        A("|---|-------|--------|")
        for d in ledger['ecartees']:
            t = d['title'].replace('|', '\\|')[:90]
            A(f"| {d['number']} | {t} | {d['reason']} |")
        A()

    A("## 5. Decision attendue de Christophe")
    A()
    A("1. Valider / corriger les 5 RATTACHEE (SCI-56..60) et la completion SCI-29.")
    A("2. Confirmer les 36 ECARTEE et les 3 DEJA_RATTACHEE.")
    A(f"3. Apres validation, inserer les blocs de `{additions_path}` dans "
      "`science.c4` (etape separee, hors de cette carte).")
    A("4. Autoriser le deploiement de `analyze_impact.py` corrige "
      "(`hermes profile update swarmdrone --yes`).")
    A()
    A("## 6. Preuve de la correction d'IMPACT_TARGETS (etage 1)")
    A()
    A("Sortie reelle de `tools/pending_promotion/test_impact_targeting.py` : "
      "les 15 identifiants d'algorithmes sont verifies contre `algorithms.c4` ; "
      "un article de formation control est cible sur `algFormationControl` "
      "(et non `onboard.mission`) ; 50 applied / 105 rejected inchanges.")
    A()
    return "\n".join(L)


def _links(d: dict) -> str:
    if d.get('link_doi'):
        return f"https://doi.org/{d['link_doi']}"
    if d.get('link_arxiv'):
        return f"https://arxiv.org/abs/{d['link_arxiv']}"
    return d.get('link_url', '(lien dans le ledger)')


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('ledger', type=Path)
    ap.add_argument('--out-dir', type=Path, default=HERE)
    args = ap.parse_args()

    ledger = json.loads(args.ledger.read_text(encoding='utf-8'))
    gen = load_gen()

    lot_slug = args.ledger.stem.replace('ledger_', '')
    additions_path = args.out_dir / f"{lot_slug}_additions.c4"
    report_path = args.out_dir / f"RAPPORT_VERDICTS_{lot_slug}.md"

    additions = gen_additions(gen, ledger)
    additions_path.write_text(additions, encoding='utf-8')

    md = report(ledger, additions_path.name)
    report_path.write_text(md, encoding='utf-8')

    n_ratt = len(ledger.get('rattachees', []))
    n_sd = len(ledger.get('specdoc_only', []))
    n_deja = len(ledger.get('deja', []))
    n_ec = len(ledger.get('ecartees', []))
    print(f"ledger charge : {args.ledger}")
    print(f"RATTACHEE={n_ratt} specdoc_only={n_sd} DEJA={n_deja} ECARTEE={n_ec} "
          f"(total {n_ratt+n_sd+n_deja+n_ec})")
    print(f"rapport  : {report_path}")
    print(f"additions: {additions_path} (NON inseres — a valider)")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
