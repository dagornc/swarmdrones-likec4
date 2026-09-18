#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_dossier04.py — SWARM-3D-ARCHITECTURE / LikeC4  (P5)

Corrige deux defauts du dossier 04 :
  1. `capabilityMap` est une vue FONCTIONNELLE (capacites/fonctions), pas
     algorithmique -> la deplacer vers `03 · Architecture`.
  2. `Catalogue — 15 algorithmes` : preciser le contenu reel (15 alg + 1 spec).

NE MODIFIE QUE les titres. Aucun corps de vue, aucun include, aucun lien.

Idempotent.
"""

import os
import re
import subprocess
import sys

BASE = os.environ.get('LIKEC4_BASE', '/docker/likec4/workspace')
VIEWS = os.path.join(BASE, 'views.c4')

# (motif exact dans le fichier, remplacement)
FIXES = [
    # 1. capabilityMap : vue fonctionnelle mal rangee dans 04
    (
        r"title '04 · Algorithmique \\/ Carte des capacites — 8 capacites, 19 fonctions'",
        r"title '03 · Architecture \\/ Carte des capacites — 8 capacites, 19 fonctions'",
    ),
    # 2. catalogue : preciser le contenu (15 algorithmes + 1 specification)
    (
        r"title '04 · Algorithmique \\/ Catalogue — 15 algorithmes'",
        r"title '04 · Algorithmique \\/ Catalogue — 15 algorithmes et 1 specification'",
    ),
]


def main():
    src = open(VIEWS, encoding='utf-8').read()
    n = 0
    for pat, rep in FIXES:
        new, c = re.subn(pat, rep, src)
        if c:
            src = new
            n += c
            print(f'  {c}x  {rep[:70]}')
        else:
            print(f'  (deja fait) {pat[:60]}')

    if n == 0:
        print('  aucun changement')
        return 0

    open(VIEWS, 'w', encoding='utf-8').write(src)
    print(f'  {n} titre(s) corrige(s)')

    print('  validation likec4...')
    r = subprocess.run(['likec4', 'validate'], cwd=BASE,
                       capture_output=True, text=True)
    tail = (r.stdout + r.stderr).strip().split('\n')[-1]
    print(f'  {tail}')
    return 0 if r.returncode == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
