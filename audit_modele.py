#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_modele.py — SWARM-3D-ARCHITECTURE / LikeC4

Audit automatique du modele LikeC4. Detecte les regressions
structurelles SANS bloquer (avertissements uniquement).

CONTROLES :
  A1. Elements declares mais absents de toute vue (invisibles)
  A2. Doublons de nomenclature (meme concept, deux ids)
  A3. Metadonnees collisionnant avec un mot-cle reserve LikeC4
  A4. Relations pointant vers un element inexistant (dangling)
  A5. Elements sans description
  A6. Vues sans titre ou sans description

USAGE :
  python3 audit_modele.py            # rapport complet
  python3 audit_modele.py --strict   # exit 1 si anomalie critique
  python3 audit_modele.py --quiet    # resume seulement

Concu pour etre appele par le hook post-commit (mode --quiet).
"""

import argparse
import glob
import os
import re
import sys
from collections import defaultdict

BASE = os.environ.get('LIKEC4_BASE', '/docker/likec4/workspace')

# Mots-cles reserves LikeC4 : une metadonnee portant ce nom est
# interpretee par l'outil (bug sourcePath du 2026-09-18).
RESERVED = {
    'sourcePath', 'title', 'description', 'id', 'kind', 'view',
    'metadata', 'style', 'link', 'tags', 'technology', 'icon',
    'navigateTo', 'notes', 'summary', 'group', 'color', 'shape',
}

# Kinds qui ne sont PAS des elements d'architecture (pas de vue attendue)
NON_ARCH_KINDS = {
    'view', 'specification', 'model', 'deployment', 'relationship',
    'tag', 'color', 'kind', 'specDoc', 'factSheet', 'state', 'finding',
    'hypothesis', 'decision', 'risk', 'blindspot', 'invariant',
}


def read_all():
    files = {}
    for f in sorted(glob.glob(os.path.join(BASE, '*.c4'))):
        files[os.path.basename(f)] = open(f, encoding='utf-8').read()
    return files


def parse_elements(files):
    """Retourne {fqn: (kind, file, has_description)}."""
    decl = {}
    for fname, src in files.items():
        stack = []
        for ln in src.split('\n'):
            m = re.match(r"^(\s*)([a-zA-Z][A-Za-z0-9_]*)\s*=\s*([a-z][A-Za-z0-9_]*)\s*'", ln)
            if m:
                indent = len(m.group(1))
                eid, kind = m.group(2), m.group(3)
                while stack and stack[-1][0] >= indent:
                    stack.pop()
                fqn = '.'.join([s[1] for s in stack] + [eid])
                if kind not in ('view', 'specification', 'model', 'deployment',
                                'relationship', 'tag', 'color', 'kind'):
                    decl[fqn] = [kind, fname, False]
                if ln.rstrip().endswith('{'):
                    stack.append((indent, eid))
            else:
                m2 = re.match(r"^(\s*)\}", ln)
                if m2:
                    indent = len(m2.group(1))
                    while stack and stack[-1][0] >= indent:
                        stack.pop()
    # detection de description (approximative : bloc ''' dans les 40 lignes suivantes)
    for fname, src in files.items():
        lines = src.split('\n')
        for i, ln in enumerate(lines):
            m = re.match(r"^\s*([a-zA-Z][A-Za-z0-9_]*)\s*=\s*([a-z][A-Za-z0-9_]*)\s*'", ln)
            if m and m.group(2) not in ('view', 'specification', 'model', 'deployment',
                                        'relationship', 'tag', 'color', 'kind'):
                window = '\n'.join(lines[i:i + 40])
                if "description" in window or "'''" in window:
                    # marquer tous les fqn dont le dernier segment == id
                    for fqn in decl:
                        if fqn.split('.')[-1] == m.group(1):
                            decl[fqn][2] = True
    return decl


def parse_views(files):
    """Retourne [(view_id, file, body, has_title, has_description)]."""
    views = []
    for fname, src in files.items():
        for vm in re.finditer(
                r"^\s*view\s+([A-Za-z0-9_]+)\s*(?:of\s+[A-Za-z0-9_.]+\s*)?\{(.*?)^\s*\}",
                src, re.M | re.S):
            body = vm.group(2)
            views.append((vm.group(1), fname, body,
                          "title" in body, "description" in body))
    return views


def check_a1_invisible(decl, views):
    inview = set()
    for _, _, body, _, _ in views:
        for tok in re.findall(r"[a-zA-Z][A-Za-z0-9_.]*", body):
            inview.add(tok)
    out = []
    for fqn, (kind, fname, _) in sorted(decl.items()):
        if kind in NON_ARCH_KINDS:
            continue
        if fqn not in inview and fqn.split('.')[-1] not in inview:
            out.append((fqn, kind, fname))
    return out


def check_a2_doublons(decl, files):
    """Detecte les doublons de nomenclature.

    Deux cas :
      (a) meme id declare deux fois (meme fichier ou non) -> critique
      (b) meme nom court normalise, meme kind, dans deux fichiers -> suspect
    """
    out = []

    # (a) double declaration du meme id
    counts = defaultdict(list)
    for fname, src in files.items():
        for m in re.finditer(
                r"^\s*([a-zA-Z][A-Za-z0-9_]*)\s*=\s*([a-z][A-Za-z0-9_]*)\s*'", src, re.M):
            eid, kind = m.group(1), m.group(2)
            if kind in ('view', 'specification', 'model', 'deployment',
                        'relationship', 'tag', 'color', 'kind'):
                continue
            line = src[:m.start()].count('\n') + 1
            counts[eid].append((kind, fname, line))
    for eid, items in sorted(counts.items()):
        if len(items) > 1:
            out.append((eid, items, 'double-declaration'))

    # (b) meme nom court, meme kind, fichiers differents
    by_short = defaultdict(list)
    for fqn, (kind, fname, _) in decl.items():
        by_short[fqn.split('.')[-1].lower()].append((fqn, kind, fname))
    for short, items in sorted(by_short.items()):
        if len(items) > 1:
            kinds = {k for _, k, _ in items}
            files_ = {f for _, _, f in items}
            if len(kinds) == 1 and len(files_) > 1:
                out.append((short, items, 'nomenclature-parallele'))
    return out


def check_a3_reserved(files):
    """Metadonnees portant un nom reserve LikeC4, DANS un bloc metadata { }.

    Hors bloc metadata, `title`/`description`/`technology` sont des
    proprietes legitimes de l'element : ne pas les signaler.
    """
    out = []
    for fname, src in files.items():
        # localiser les blocs metadata { ... }
        for mm in re.finditer(r"metadata\s*\{(.*?)\}", src, re.S):
            body = mm.group(1)
            base = src[:mm.start(1)].count('\n')
            for m in re.finditer(r"^\s*([a-zA-Z][A-Za-z0-9_]*)\s+'", body, re.M):
                name = m.group(1)
                if name in RESERVED:
                    line = base + body[:m.start()].count('\n') + 1
                    out.append((fname, line, name))
    return out


def check_a4_dangling(files, decl):
    """Relations pointant vers un id inexistant."""
    known = set(decl.keys())
    shorts = {fqn.split('.')[-1] for fqn in known}
    out = []
    for fname, src in files.items():
        for m in re.finditer(
                r"^\s*([a-zA-Z][A-Za-z0-9_.]*)\s*-\[[a-zA-Z]+\]->\s*([a-zA-Z][A-Za-z0-9_.]*)",
                src, re.M):
            src_id, dst_id = m.group(1), m.group(2)
            for eid in (src_id, dst_id):
                if eid not in known and eid.split('.')[-1] not in shorts:
                    line = src[:m.start()].count('\n') + 1
                    out.append((fname, line, eid))
    return out


def check_a5_sans_description(decl):
    return [(fqn, kind, fname) for fqn, (kind, fname, has) in sorted(decl.items())
            if not has and kind not in NON_ARCH_KINDS]


def check_a6_vues(views):
    return [(vid, fname) for vid, fname, _, has_t, has_d in views
            if not has_t or not has_d]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--strict', action='store_true')
    ap.add_argument('--quiet', action='store_true')
    args = ap.parse_args()

    files = read_all()
    decl = parse_elements(files)
    views = parse_views(files)

    a1 = check_a1_invisible(decl, views)
    a2 = check_a2_doublons(decl, files)
    a3 = check_a3_reserved(files)
    a4 = check_a4_dangling(files, decl)
    a5 = check_a5_sans_description(decl)
    a6 = check_a6_vues(views)

    crit = len(a2) + len(a3) + len(a4)   # anomalies critiques

    if args.quiet:
        print(f"[audit] {len(decl)} elements, {len(views)} vues | "
              f"critiques={crit} (doublons={len(a2)}, reserves={len(a3)}, "
              f"dangling={len(a4)}) | invisibles={len(a1)} "
              f"sans-desc={len(a5)} vues-incompletes={len(a6)}")
        return 1 if (args.strict and crit) else 0

    print("=" * 72)
    print("  AUDIT DU MODELE LIKEC4 — SWARM-3D-ARCHITECTURE")
    print("=" * 72)
    print(f"  {len(files)} fichiers · {len(decl)} elements · {len(views)} vues")
    print()

    print(f"--- A2. DOUBLONS DE NOMENCLATURE : {len(a2)} ---")
    for short, items, why in a2:
        print(f"  [{why}] {short}")
        for it in items:
            if len(it) == 3 and isinstance(it[2], int):
                kind, fname, line = it
                print(f"      {kind:14} {fname}:{line}")
            else:
                fqn, kind, fname = it
                print(f"      {kind:14} {fqn:34} ({fname})")
    print()

    print(f"--- A3. METADONNEES RESERVEES (collision LikeC4) : {len(a3)} ---")
    for fname, line, name in a3:
        print(f"  {fname}:{line}  '{name}'")
    print()

    print(f"--- A4. RELATIONS DANGLING : {len(a4)} ---")
    for fname, line, eid in a4:
        print(f"  {fname}:{line}  -> {eid}")
    print()

    print(f"--- A1. ELEMENTS INVISIBLES (aucune vue) : {len(a1)} ---")
    for fqn, kind, fname in a1:
        print(f"  {kind:16} {fqn:40} ({fname})")
    print()

    print(f"--- A5. ELEMENTS SANS DESCRIPTION : {len(a5)} ---")
    for fqn, kind, fname in a5[:30]:
        print(f"  {kind:16} {fqn:40} ({fname})")
    if len(a5) > 30:
        print(f"  ... et {len(a5) - 30} autres")
    print()

    print(f"--- A6. VUES SANS TITRE OU DESCRIPTION : {len(a6)} ---")
    for vid, fname in a6:
        print(f"  {vid:34} ({fname})")
    print()

    print("=" * 72)
    print(f"  SYNTHESE : critiques={crit} | invisibles={len(a1)} | "
          f"sans-desc={len(a5)} | vues-incompletes={len(a6)}")
    print("=" * 72)

    return 1 if (args.strict and crit) else 0


if __name__ == '__main__':
    sys.exit(main())
