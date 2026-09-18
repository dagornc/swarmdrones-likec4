#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_algorithm_views.py — SWARM-3D-ARCHITECTURE / LikeC4

Trois corrections sur les vues du dossier 04 (Algorithmique & Capacites) :

  1. algorithmCatalog : 11 -> 15 algorithmes.
     Les 4 algorithmes ajoutes par E20 (e20-audit-completeness.c4) etaient
     absents du catalogue. Titre corrige.

  2. specTaskAllocation rendu VISIBLE : inclus dans algorithmCatalog avec la
     relation documentedBy. Sans inclusion dans une vue, un element du modele
     n'apparait JAMAIS dans l'interface LikeC4.

  3. Rattachement des 4 algorithmes E20 a leurs chaines :
     - chaine de surete (algorithmSafety) : algCooperativeLocalization,
       algFaultTolerantControlAlloc
     - chaine de coordination (algorithmCoordination) : algEventTriggeredComm,
       algJammingResilientMode

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
VIEWS = os.path.join(BASE, 'views.c4')

MARKER = '// === E27 — CORRECTION DES VUES ALGORITHMIQUES ==='


def log(msg):
    print(msg, flush=True)


def main():
    if not os.path.isfile(VIEWS):
        log(f'ERREUR : {VIEWS} introuvable')
        return 1

    src = open(VIEWS, encoding='utf-8').read()

    if MARKER in src:
        log('Deja applique (marqueur present) — rien a faire.')
        return 0

    ts = datetime.now().strftime('%Y%m%d-%H%M%S')
    bak = f'{VIEWS}.bak-e27-{ts}'
    shutil.copy2(VIEWS, bak)
    log(f'  sauvegarde : {bak}')

    original = src
    changes = 0

    # --- Correction 1 : titre du catalogue 11 -> 15 -------------------------
    old_title = "title '04 - Algorithmique & Capacités (Components) \\\\/ Catalogue algorithmique — 11 algorithmes'"
    new_title = "title '04 - Algorithmique & Capacités (Components) \\\\/ Catalogue algorithmique — 15 algorithmes'"
    if old_title in src:
        src = src.replace(old_title, new_title, 1)
        changes += 1
        log('  [1] titre catalogue : 11 -> 15 algorithmes')
    else:
        log('  [1] titre catalogue : motif introuvable (deja corrige ?)')

    # --- Correction 1+2 : includes du catalogue -----------------------------
    # On remplace le bloc d'includes par un bloc complet (15 alg + specDoc).
    old_cat_includes = (
        "    include algTaskAllocation, algConsensus, algFormationControl, algLeaderElection\n"
        "    include algPerceptionFusion, algNavigationGNSSDegrade\n"
        "    include algCollisionAvoidance, algSafetyRules, algPathPlanning\n"
        "    include algHealthMonitoring, algEnergyAware\n"
    )
    new_cat_includes = (
        "    include algTaskAllocation, algConsensus, algFormationControl, algLeaderElection\n"
        "    include algPerceptionFusion, algNavigationGNSSDegrade\n"
        "    include algCollisionAvoidance, algSafetyRules, algPathPlanning\n"
        "    include algHealthMonitoring, algEnergyAware\n"
        "    // E27 : les 4 algorithmes ajoutes par E20 etaient absents du catalogue.\n"
        "    include algEventTriggeredComm, algCooperativeLocalization\n"
        "    include algFaultTolerantControlAlloc, algJammingResilientMode\n"
        "    // E27 : element de specification detaillee (sinon invisible dans l UI).\n"
        "    include specTaskAllocation\n"
    )
    if old_cat_includes in src:
        src = src.replace(old_cat_includes, new_cat_includes, 1)
        changes += 1
        log('  [1+2] catalogue : +4 algorithmes E20, +specTaskAllocation')
    else:
        log('  [1+2] catalogue : bloc includes introuvable')

    # --- Correction 3a : chaine de surete -----------------------------------
    old_safety = (
        "    include onboard.perception, algPerceptionFusion, algNavigationGNSSDegrade\n"
        "    include onboard.safety, algCollisionAvoidance, algSafetyRules\n"
        "    include onboard.autopilot\n"
        "    include onboard.health, algHealthMonitoring\n"
    )
    new_safety = (
        "    include onboard.perception, algPerceptionFusion, algNavigationGNSSDegrade\n"
        "    include onboard.safety, algCollisionAvoidance, algSafetyRules\n"
        "    include onboard.autopilot, algFaultTolerantControlAlloc\n"
        "    include onboard.health, algHealthMonitoring\n"
        "    // E27 : localisation relative inter-agents (sans lien) et commande\n"
        "    // tolerante aux fautes appartiennent a la chaine de surete.\n"
        "    include algCooperativeLocalization\n"
    )
    if old_safety in src:
        src = src.replace(old_safety, new_safety, 1)
        changes += 1
        log('  [3a] chaine de surete : +algCooperativeLocalization, +algFaultTolerantControlAlloc')
    else:
        log('  [3a] chaine de surete : bloc introuvable')

    # --- Correction 3b : chaine de coordination -----------------------------
    old_coord = (
        "    include onboard.taskAuction, algTaskAllocation, algConsensus\n"
        "    include onboard.mission, algPathPlanning, algFormationControl\n"
        "    include algLeaderElection, algEnergyAware\n"
        "    include edge.coordinator\n"
    )
    new_coord = (
        "    include onboard.taskAuction, algTaskAllocation, algConsensus\n"
        "    include onboard.mission, algPathPlanning, algFormationControl\n"
        "    include algLeaderElection, algEnergyAware\n"
        "    include edge.coordinator\n"
        "    // E27 : communication declenchee par evenement et mode resilient au\n"
        "    // brouillage dependent du lien -> chaine de coordination.\n"
        "    include algEventTriggeredComm, algJammingResilientMode\n"
    )
    if old_coord in src:
        src = src.replace(old_coord, new_coord, 1)
        changes += 1
        log('  [3b] chaine de coordination : +algEventTriggeredComm, +algJammingResilientMode')
    else:
        log('  [3b] chaine de coordination : bloc introuvable')

    if changes == 0:
        log('Aucune modification appliquee.')
        return 1

    # marqueur en tete de fichier (commentaire de tracabilite)
    src = MARKER + '\n' + src

    open(VIEWS, 'w', encoding='utf-8').write(src)
    log(f'  ecrit : {VIEWS} ({len(src)} octets, delta {len(src)-len(original):+d})')

    # --- Validation ---------------------------------------------------------
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
