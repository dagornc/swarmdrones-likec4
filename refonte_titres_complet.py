#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
refonte_titres_complet.py — SWARM-3D-ARCHITECTURE / LikeC4

Refonte des 51 titres restants (les 5 du dossier 04 sont deja faits en E28).

Convention :
  'NN · Theme' + ' \\/ ' + 'Sous-niveau'
  ex: '01 · Gouvernance \\/ Matrice de risques'

Regles :
  - le prefixe numerique est conserve (tri alphabetique correct)
  - le libelle de theme est raccourci
  - le detail (compteurs, listes) part dans la description si utile
  - AUCUN element, lien ou relation n'est touche
  - les titres deja en '04 · Algorithmique' sont ignores (idempotence)

Idempotent : marqueur E29.
Sauvegarde horodatee. Validation likec4 en fin de course.
"""

import os
import shutil
import subprocess
import sys
from datetime import datetime

BASE = os.environ.get('LIKEC4_BASE', '/docker/likec4/workspace')
CONTAINER = os.environ.get('LIKEC4_CONTAINER', 'likec4')

SEP = '\\/ '   # separateur reel dans le fichier : backslash + slash + espace

# Themes : ancien libelle long -> nouveau libelle court
THEMES = {
    '01 - Gouvernance & Stratégie (Executive View)': '01 · Gouvernance',
    '02 - Parcours & Opérations (Business & Scenarios)': '02 · Parcours',
    '03 - Architecture Logique & Flux (C4 Containers & Interactions)': '03 · Architecture',
    '04 - Algorithmique & Capacités (Components)': '04 · Algorithmique',
    '05 - Physique & Déploiement (Infrastructure)': '05 · Déploiement',
    '06 - Sûreté, Vérification & Recherche': '06 · Sûreté',
    '99 - Vues complémentaires': '99 · Compléments',
}

# Sous-titres : ancien -> nouveau (pour les niveaux 2/3)
SUBSTITUTIONS = [
    ('Vues thématiques (§A) ' + SEP + '3 — ', ''),
    ('Chaînes algorithmiques ' + SEP, ''),
    ('Détail des Zones (Contexte amont \\\\\\/ aval) ' + SEP, 'Zones ' + SEP),
    ('UX Parcours ' + SEP + 'Chaînes de valeur ' + SEP, 'Chaînes de valeur ' + SEP),
]


def log(m):
    print(m, flush=True)


def main():
    files = ['views.c4', 'ux-parcours.c4', 'e19-system-context.c4']
    total = 0

    for fname in files:
        path = os.path.join(BASE, fname)
        if not os.path.isfile(path):
            log(f'  [SKIP] {fname} introuvable')
            continue

        src = open(path, encoding='utf-8').read()
        original = src
        n = 0

        # 1. remplacer les libelles de theme longs
        for old, new in THEMES.items():
            if old in src:
                c = src.count(old)
                src = src.replace(old, new)
                n += c
                log(f'  [{fname}] theme : {old[:40]}... -> {new} ({c}x)')

        # 2. simplifier les sous-niveaux
        for old, new in SUBSTITUTIONS:
            if old in src:
                c = src.count(old)
                src = src.replace(old, new)
                n += c
                log(f'  [{fname}] sous-niveau : {old[:45]}... -> {new!r} ({c}x)')

        if src != original:
            ts = datetime.now().strftime('%Y%m%d-%H%M%S')
            bak = f'{path}.bak-e29-{ts}'
            shutil.copy2(path, bak)
            open(path, 'w', encoding='utf-8').write(src)
            log(f'  [{fname}] ecrit ({len(src)} octets, {n} remplacements)')
            total += n
        else:
            log(f'  [{fname}] inchange')

    if total == 0:
        log('Aucune modification.')
        return 1

    log(f'  TOTAL : {total} remplacements')

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
