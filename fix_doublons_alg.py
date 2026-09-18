#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_doublons_alg.py — SWARM-3D-ARCHITECTURE / LikeC4  (P1)

Supprime les 7 doublons d'algorithmes de la serie `Algorithms*`
(architecture.c4, coquilles de 5 lignes) et REDIRIGE toutes leurs
relations vers la serie canonique `alg*` (algorithms.c4, 30-39 lignes).

Mapping (valide par l'audit : la serie alg* est 6-8x plus riche) :
  AlgorithmsTaskAllocationCBBA          -> algTaskAllocation
  AlgorithmsCoordinationCRDTLWW         -> algConsensus
  AlgorithmsPerceptionFusionEKFUKF      -> algPerceptionFusion
  AlgorithmsNavigationGNSSDegradeEKFVIO -> algNavigationGNSSDegrade
  AlgorithmsPlanificationWaypointsMPC   -> algPathPlanning
  AlgorithmsEvitementCollisionCBF       -> algCollisionAvoidance
  AlgorithmsSureteReglesCBF             -> algSafetyRules

Aucune relation n'est perdue : elles sont toutes redirigees.
Idempotent. Sauvegarde horodatee. Validation likec4 en fin de course.
"""

import os
import re
import shutil
import subprocess
import sys
from datetime import datetime

BASE = os.environ.get('LIKEC4_BASE', '/docker/likec4/workspace')
CONTAINER = os.environ.get('LIKEC4_CONTAINER', 'likec4')

MAPPING = {
    'AlgorithmsTaskAllocationCBBA': 'algTaskAllocation',
    'AlgorithmsCoordinationCRDTLWW': 'algConsensus',
    'AlgorithmsPerceptionFusionEKFUKF': 'algPerceptionFusion',
    'AlgorithmsNavigationGNSSDegradeEKFVIO': 'algNavigationGNSSDegrade',
    'AlgorithmsPlanificationWaypointsMPC': 'algPathPlanning',
    'AlgorithmsEvitementCollisionCBF': 'algCollisionAvoidance',
    'AlgorithmsSureteReglesCBF': 'algSafetyRules',
}


def log(m):
    print(m, flush=True)


def strip_declaration(src, name):
    """Supprime le bloc `name = algorithm '...' { ... }` (accolades equilibrees)."""
    pat = re.compile(r"^[ \t]*" + re.escape(name) + r"\s*=\s*algorithm\s+'", re.M)
    m = pat.search(src)
    if not m:
        return src, False
    start = m.start()
    # trouver la fin : premiere ligne dont l'indentation ferme le bloc
    i = src.find('{', m.end())
    if i == -1:
        return src, False
    depth = 0
    j = i
    while j < len(src):
        if src[j] == '{':
            depth += 1
        elif src[j] == '}':
            depth -= 1
            if depth == 0:
                break
        j += 1
    if j >= len(src):
        return src, False
    # avaler jusqu'a la fin de ligne
    k = src.find('\n', j)
    if k == -1:
        k = len(src)
    else:
        k += 1
    return src[:start] + src[k:], True


def main():
    fname = 'architecture.c4'
    path = os.path.join(BASE, fname)
    src = open(path, encoding='utf-8').read()
    original = src

    # --- 1. supprimer les declarations (avant redirection, sinon elles sont
    #        renommees et deviennent introuvables -> double declaration) ---
    ndecl = 0
    for old in MAPPING:
        src, ok = strip_declaration(src, old)
        if ok:
            ndecl += 1
            log(f'  suppression declaration {old}')

    # --- 2. rediriger toutes les references restantes ---
    nref = 0
    for old, new in MAPPING.items():
        c = len(re.findall(r'\b' + re.escape(old) + r'\b', src))
        if c:
            src = re.sub(r'\b' + re.escape(old) + r'\b', new, src)
            nref += c
            log(f'  redirection {old} -> {new} ({c}x)')

    if src == original:
        log('Aucune modification (deja fait ?).')
        return 1

    ts = datetime.now().strftime('%Y%m%d-%H%M%S')
    shutil.copy2(path, f'{path}.bak-p1-{ts}')
    open(path, 'w', encoding='utf-8').write(src)
    log(f'  ecrit : {nref} references redirigees, {ndecl} declarations supprimees')

    # --- 3. validation ---
    log('  validation likec4...')
    out = subprocess.run(['docker', 'exec', CONTAINER, 'npx', 'likec4', 'validate'],
                         capture_output=True, text=True, timeout=180)
    txt = (out.stdout or '') + (out.stderr or '')
    if 'Valid' in txt:
        log('  ✓ likec4 validate : Valid')
        return 0
    log('  ✗ likec4 validate : ECHEC')
    log(txt[-2000:])
    return 1


if __name__ == '__main__':
    sys.exit(main())
