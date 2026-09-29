#!/usr/bin/env python3
"""lc_pending_cards.py — liste les propositions `pending` avec leur source
primaire (titre + identifiant + abstract extrait de articles/) pour que
l'agent puisse statuer.

Usage :
    python3 tools/pending_promotion/lc_pending_cards.py
    python3 tools/pending_promotion/lc_pending_cards.py --limit 10

Garde-fous anti-doublon : chaque carte affiche number, title, source_url,
DOIs et arXiv IDs, PLUS l'abstract — l'adjudication doit confronter par
DOI/arXiv ET par titre (cf. tools/statut465/README.md).
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

PROP = Path('/home/hermesagent/swarmdrone-research/impact-proposals.json')
CAT = Path('/home/hermesagent/swarmdrone-research/catalog.json')
ART = Path('/home/hermesagent/swarmdrone-research/articles')


def get_abstract(filename: str) -> str | None:
    if not filename:
        return None
    p = ART / filename
    if not p.exists():
        return None
    txt = p.read_text(encoding='utf-8', errors='replace')
    m = re.search(r'## Abstract\s*\n(.*?)(?=\n## |\Z)', txt, re.S)
    if m:
        return re.sub(r'\s+', ' ', m.group(1)).strip()
    m = re.search(r'(?im)^abstract\s*:?\s*\n+(.{200,})', txt, re.S)
    if m:
        return re.sub(r'\s+', ' ', m.group(1)).strip()
    return None


def card(p: dict, by_num: dict, maxabs: int = 900) -> str:
    art = p.get('article', {})
    num = art.get('number')
    rec = by_num.get(num)
    filename = rec.get('filename') if rec else None
    dois = art.get('dois') or []
    arx = art.get('arxiv_ids') or []
    ident = ('DOI:' + ','.join(dois) + ' ') if dois else ''
    ident += ('arXiv:' + ','.join(arx)) if arx else ''
    if not ident.strip():
        ident = (art.get('source_url') or '')[:70]
    ab = get_abstract(filename)
    ab = (ab[:maxabs] if ab else '(pas d abstract extrait)')
    return (f"#{num} [elem={p.get('element_id')} conf={p.get('confidence')}]\n"
            f"    id: {ident.strip()}\n"
            f"    T: {art.get('title','')[:150]}\n"
            f"    U: {(art.get('source_url') or '')[:120]}\n"
            f"    abs: {ab}\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--limit', type=int, default=None,
                    help='limiter le nombre de cartes (defaut : toutes)')
    args = ap.parse_args()

    proposals = json.loads(PROP.read_text(encoding='utf-8'))
    catalog = json.loads(CAT.read_text(encoding='utf-8'))
    by_num = {a['number']: a for a in catalog}
    pending = [p for p in proposals if p.get('status') == 'pending']
    if args.limit:
        pending = pending[: args.limit]
    print(f"=== {len(pending)} proposition(s) pending ===")
    for p in pending:
        print(card(p, by_num))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
