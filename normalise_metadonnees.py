#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
normalise_metadonnees.py — SWARM-3D-ARCHITECTURE / LikeC4  (P4)

Ajoute des metadonnees ENUMERABLES a cote des champs texte libre existants,
pour rendre le modele requetable (filtrage, comptage, coloration).

NE SUPPRIME RIEN : les champs `evidence`, `maturity` restent intacts.
On AJOUTE :
    evidenceLevel   HIGH | MEDIUM | LOW | SUPPORTED | NONE
    maturityLevel   MATURE | EMERGENTE | TBD

Regle de derivation (deterministe, documentee) :
  evidenceLevel :
    - commence par 'HIGH'      -> HIGH
    - commence par 'MEDIUM'    -> MEDIUM
    - commence par 'LOW'       -> LOW
    - commence par 'SUPPORTED' -> SUPPORTED
    - 'aucun article...' / 'aucune source...' -> NONE
    - absent                   -> NONE
  maturityLevel :
    - commence par 'mature'    -> MATURE
    - commence par 'emergente' -> EMERGENTE
    - 'TBD' ou absent          -> TBD

Idempotent : si le champ existe deja, il est remplace (pas duplique).
"""

import os
import re
import subprocess
import sys

BASE = os.environ.get('LIKEC4_BASE', '/docker/likec4/workspace')
TARGETS = ['algorithms.c4', 'e20-audit-completeness.c4']


def derive_evidence(val):
    if val is None:
        return 'NONE'
    v = val.strip()
    for lvl in ('HIGH', 'MEDIUM', 'LOW', 'SUPPORTED'):
        if v.upper().startswith(lvl):
            return lvl
    if v.lower().startswith('aucun') or v.lower().startswith('aucune'):
        return 'NONE'
    return 'NONE'


def derive_maturity(val):
    if val is None:
        return 'TBD'
    v = val.strip()
    if v.lower().startswith('mature'):
        return 'MATURE'
    if v.lower().startswith('emergente'):
        return 'EMERGENTE'
    return 'TBD'


def process_file(path):
    src = open(path, encoding='utf-8').read()
    lines = src.split('\n')
    out = []
    n_ev = n_ma = 0
    cur_ev = cur_ma = None
    in_meta = False
    depth = 0

    for ln in lines:
        # entree/sortie de bloc metadata
        if re.match(r'^\s*metadata\s*\{', ln):
            in_meta = True
            depth = 1
            out.append(ln)
            continue
        if in_meta:
            depth += ln.count('{') - ln.count('}')
            if depth <= 0:
                # fermeture : injecter les champs derives avant l'accolade
                if cur_ev is not None:
                    out.append(f"      evidenceLevel '{derive_evidence(cur_ev)}'")
                    n_ev += 1
                if cur_ma is not None:
                    out.append(f"      maturityLevel '{derive_maturity(cur_ma)}'")
                    n_ma += 1
                cur_ev = cur_ma = None
                in_meta = False
                out.append(ln)
                continue

            m = re.match(r"^\s*evidence\s+'(.*)'\s*$", ln)
            if m:
                cur_ev = m.group(1)
                out.append(ln)
                continue
            m = re.match(r"^\s*maturity\s+'(.*)'\s*$", ln)
            if m:
                cur_ma = m.group(1)
                out.append(ln)
                continue
            # supprimer un eventuel champ derive deja present (idempotence)
            if re.match(r"^\s*evidenceLevel\s+'", ln) or re.match(r"^\s*maturityLevel\s+'", ln):
                continue
        out.append(ln)

    new = '\n'.join(out)
    if new == src:
        print(f'  {os.path.basename(path)}: aucun changement')
        return 0, 0
    open(path, 'w', encoding='utf-8').write(new)
    print(f'  {os.path.basename(path)}: {n_ev} evidenceLevel + {n_ma} maturityLevel')
    return n_ev, n_ma


def main():
    tot_ev = tot_ma = 0
    for t in TARGETS:
        p = os.path.join(BASE, t)
        if not os.path.exists(p):
            print(f'  {t}: absent, ignore')
            continue
        ev, ma = process_file(p)
        tot_ev += ev
        tot_ma += ma

    if tot_ev == 0 and tot_ma == 0:
        print('  aucun changement')
        return 0

    print(f'  total : {tot_ev} evidenceLevel + {tot_ma} maturityLevel')

    print('  validation likec4...')
    r = subprocess.run(['likec4', 'validate'], cwd=BASE,
                       capture_output=True, text=True)
    tail = (r.stdout + r.stderr).strip().split('\n')[-1]
    print(f'  {tail}')
    return 0 if r.returncode == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
