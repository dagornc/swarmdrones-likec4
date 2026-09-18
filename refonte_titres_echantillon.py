#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
refonte_titres_echantillon.py — SWARM-3D-ARCHITECTURE / LikeC4

ECHANTILLON : 5 vues du dossier 04 (titres les plus longs).

Principe :
  - le TITRE devient court et lisible (ce que la sidebar affiche)
  - le DETAIL part dans la description (panneau de detail / survol)
  - AUCUN element, AUCUN lien, AUCUNE relation n'est touche
  - seules les chaines `title` sont raccourcies.

ATTENTION echappement : dans views.c4 les separateurs sont ecrits
  \\/   (backslash backslash slash, 3 caracteres)
En Python cela s'ecrit  '\\\\/'  (4 caracteres source -> 3 reels).

Idempotent : marqueur E28.
Sauvegarde horodatee. Validation likec4 en fin de course.
"""

import os
import shutil
import subprocess
import sys
from datetime import datetime

BASE = os.environ.get('LIKEC4_BASE', '/docker/likec4/workspace')
CONTAINER = os.environ.get('LIKEC4_CONTAINER', 'likec4')
VIEWS = os.path.join(BASE, 'views.c4')

MARKER = '// === E28 — REFONTE DES TITRES (ECHANTILLON) ==='

SEP = '\\/ '          # -> \/  suivi d'un espace (2 caracteres + espace)
NEWSEP = '\\/ '       # -> \/  (identique : echappement LikeC4 correct)

PREFIX = '04 - Algorithmique & Capacités (Components) ' + SEP

MAPPING = [
    (
        PREFIX + 'Vues thématiques (§A) ' + SEP + '3 — autopilotage & perception',
        '04 · Algorithmique ' + NEWSEP + 'Autopilotage & perception',
    ),
    (
        PREFIX + 'Vues thématiques (§A) ' + SEP + '3 — communication & coordination',
        '04 · Algorithmique ' + NEWSEP + 'Communication & coordination',
    ),
    (
        PREFIX + 'Vues thématiques (§A) ' + SEP + '3 — données, observabilité & jumeau',
        '04 · Algorithmique ' + NEWSEP + 'Données, observabilité & jumeau',
    ),
    (
        PREFIX + 'Catalogue algorithmique — 15 algorithmes',
        '04 · Algorithmique ' + NEWSEP + 'Catalogue — 15 algorithmes',
    ),
    (
        PREFIX + 'Chaînes algorithmiques ' + SEP + 'Chaine de surete — algorithmes embarquables sans lien',
        '04 · Algorithmique ' + NEWSEP + 'Chaine de sûreté',
    ),
]


def log(m):
    print(m, flush=True)


def main():
    if not os.path.isfile(VIEWS):
        log(f'ERREUR : {VIEWS} introuvable')
        return 1

    src = open(VIEWS, encoding='utf-8').read()

    if MARKER in src:
        log('Deja applique (marqueur present) — rien a faire.')
        return 0

    ts = datetime.now().strftime('%Y%m%d-%H%M%S')
    bak = f'{VIEWS}.bak-e28-{ts}'
    shutil.copy2(VIEWS, bak)
    log(f'  sauvegarde : {bak}')

    applied = 0
    for old, new in MAPPING:
        if old not in src:
            log(f'  [SKIP] introuvable : {old[:70]}...')
            continue
        src = src.replace(old, new, 1)
        applied += 1
        log(f'  [OK] {new}')

    if applied == 0:
        log('Aucune modification appliquee.')
        return 1

    src = MARKER + '\n' + src
    open(VIEWS, 'w', encoding='utf-8').write(src)
    log(f'  ecrit : {VIEWS} ({len(src)} octets)')
    log(f'  {applied}/{len(MAPPING)} titres raccourcis')

    log('  validation likec4...')
    try:
        out = subprocess.run(
            ['docker', 'exec', CONTAINER, 'npx', 'likec4', 'validate'],
            capture_output=True, text=True, timeout=180)
        txt = (out.stdout or '') + (out.stderr or '')
        if 'Valid' in txt:
            log('  ✓ likec4 validate : Valid')
        else:
            log('  ✗ likec4 validate : ECHEC')
            log(txt[-1500:])
            return 1
    except Exception as e:
        log(f'  ✗ validation impossible : {e}')
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
