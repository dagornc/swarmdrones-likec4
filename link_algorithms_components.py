#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
link_algorithms_components.py — SWARM-3D-ARCHITECTURE / LikeC4

Deux modifications ADDITIVES sur le modele LikeC4 :

  1. Lier chaque element `algorithm` aux elements `component` associes.
     - Les relations composant -> algorithme existent deja (implements/uses).
     - On ajoute le sens manquant algorithme -> composant (`runsOn`) pour les
       4 algorithmes qui n'en avaient aucun, en s'appuyant sur les relations
       inverses deja presentes dans le modele (aucune invention).

  2. Ajouter a l'algorithme qui dispose d'une specification detaillee
     (algTaskAllocation, 3 versions successives) un element de type `specDoc`
     qui stocke les liens vers les differentes versions du document.
     - Les liens PDF de spec sont DEPLACES de l'element `algorithm` vers
       l'element `specDoc` (les liens bibliographiques DOI/arXiv restent).
     - Relation `algorithm -[documentedBy]-> specDoc`.

Idempotent : relancer le script ne duplique rien.
Sauvegarde horodatee avant ecriture. Validation likec4 en fin de course.
"""

import os
import re
import shutil
import subprocess
import sys
from datetime import datetime

BASE = os.environ.get('LIKEC4_BASE', '/docker/likec4/workspace')
CONTAINER = os.environ.get('LIKEC4_CONTAINER', 'likec4')
ALGO_FILE = os.path.join(BASE, 'algorithms.c4')

# ---------------------------------------------------------------------------
# 1. Relations algorithme -> composant manquantes (sens `runsOn`)
#    Justification : deduites des relations inverses composant -> algorithme
#    deja presentes dans le modele (aucune invention).
# ---------------------------------------------------------------------------
RUNS_ON_MISSING = [
    ('algEventTriggeredComm', 'onboard.linkRadio',
     'politique d emission evenementielle (cf onboard.linkRadio -[implements]->)'),
    ('algCooperativeLocalization', 'onboard.perception',
     'localisation relative (cf onboard.perception -[implements]->)'),
    ('algFaultTolerantControlAlloc', 'onboard.autopilot',
     'commande tolerante (cf onboard.autopilot -[implements]->)'),
    ('algJammingResilientMode', 'onboard.mission',
     'superviseur de mode (cf onboard.mission -[implements]->)'),
]

# ---------------------------------------------------------------------------
# 2. Element specDoc pour l'algorithme documente
# ---------------------------------------------------------------------------
SPEC_ELEMENT_ID = 'specTaskAllocation'
SPEC_ELEMENT_TITLE = 'Specification detaillee — ALG_TASK_ALLOCATION (3 versions)'
SPEC_LINKS = [
    ('https://likec4.breizh.ai/Spec_ALG_TASK_ALLOCATION_V3.pdf',
     'Specification detaillee Task Allocation v3 (PDF) — version courante'),
    ('https://likec4.breizh.ai/Spec_ALG_TASK_ALLOCATION_V2.pdf',
     'Specification detaillee Task Allocation v2 (PDF) — version anterieure'),
    ('https://likec4.breizh.ai/Spec_ALG_TASK_ALLOCATION_CBBA.pdf',
     'Specification detaillee CBBA (PDF, v1.1) — version initiale'),
]
SPEC_OWNER = 'algTaskAllocation'

MARKER = '// === E26 — LIENS ALGORITHMES <-> COMPOSANTS + SPECIFICATIONS DETAILLEES ==='


def log(msg):
    print(msg, flush=True)


def backup(path):
    ts = datetime.now().strftime('%Y%m%d-%H%M%S')
    bak = f'{path}.bak-e26-{ts}'
    shutil.copy2(path, bak)
    log(f'  sauvegarde : {bak}')
    return bak


def main():
    if not os.path.isfile(ALGO_FILE):
        log(f'ERREUR : {ALGO_FILE} introuvable')
        return 1

    src = open(ALGO_FILE, encoding='utf-8').read()

    if MARKER in src:
        log('Deja applique (marqueur present) — rien a faire.')
        return 0

    backup(ALGO_FILE)
    original = src

    # --- 2a. Retirer les 3 liens PDF de spec de l'element algorithm ---------
    removed = 0
    for url, _label in SPEC_LINKS:
        pat = re.compile(r'^\s*link\s+' + re.escape(url) + r'\s+.*\n', re.MULTILINE)
        src, n = pat.subn('', src)
        removed += n
    log(f'  liens PDF de spec retires de {SPEC_OWNER} : {removed}/3')

    # --- 2b. Inserer l'element specDoc + la relation documentedBy -----------
    spec_block = []
    spec_block.append('')
    spec_block.append('  ' + MARKER)
    spec_block.append('  // 1. Element de type specDoc : stocke les liens vers les')
    spec_block.append('  //    differentes versions du document de specification detaillee.')
    spec_block.append('  // 2. Relations algorithm -> component (sens `runsOn` manquant).')
    spec_block.append('  // =========================================================================')
    spec_block.append('')
    spec_block.append(f"  {SPEC_ELEMENT_ID} = specDoc '{SPEC_ELEMENT_TITLE}' {{")
    spec_block.append('    #source-doc')
    for url, label in SPEC_LINKS:
        spec_block.append(f'    link {url} "{label}"')
    spec_block.append("    description 'Document de specification detaillee de l algorithme d allocation de taches. Trois versions successives conservees : CBBA v1.1 (initiale), v2, v3 (courante).'")
    spec_block.append('    metadata {')
    spec_block.append("      algorithme 'ALG_TASK_ALLOCATION'")
    spec_block.append("      versions '3 (CBBA v1.1, v2, v3)'")
    spec_block.append("      versionCourante 'v3 (2026-09-18)'")
    spec_block.append("      nature 'specification genie logiciel interne'")
    spec_block.append("      statut 'DISPONIBLE'")
    spec_block.append('    }')
    spec_block.append('  }')
    spec_block.append('')
    spec_block.append(f"  {SPEC_OWNER} -[documentedBy]-> {SPEC_ELEMENT_ID} 'specification detaillee (3 versions)'")
    spec_block.append('')
    spec_block.append('  // --- Relations algorithm -> component (sens `runsOn` manquant) ---')
    for alg, comp, why in RUNS_ON_MISSING:
        spec_block.append(f"  {alg} -[runsOn]-> {comp} '{why}'")
    spec_block.append('')

    # inserer avant la derniere accolade fermante du fichier
    idx = src.rstrip().rfind('}')
    if idx == -1:
        log('ERREUR : accolade fermante introuvable')
        return 1
    src = src[:idx] + '\n'.join(spec_block) + '\n' + src[idx:]

    open(ALGO_FILE, 'w', encoding='utf-8').write(src)
    log(f'  ecrit : {ALGO_FILE} ({len(src)} octets, delta {len(src)-len(original):+d})')

    # --- 3. Validation ------------------------------------------------------
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
            log(txt[-2000:])
            return 1
    except Exception as e:
        log(f'  ✗ validation impossible : {e}')
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
