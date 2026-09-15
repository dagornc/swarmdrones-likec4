#!/usr/bin/env python3
"""
E03 — Application du typage des relations (carte t_5f46d5aa)

Transforme, pour chaque arc, sa forme :
    a -> b 'libelle' { options }
en :
    a -[kind]-> b 'libelle' { options }

Regles :
  - le libelle, les options et l'indentation sont PRESERVES a l'identique ;
  - aucun arc n'est supprime ni ajoute ;
  - idempotent : un arc deja type est laisse tel quel.

Usage :
  python3 tools/arc_apply.py --dry-run   # montre ce qui serait fait
  python3 tools/arc_apply.py            # applique (ecrit architecture.c4)
"""
import re, json, sys, collections

SRC = 'architecture.c4'
TY = '/tmp/typage.json'


def main(dry):
    d = json.load(open(TY))
    ty = {a['ln']: a['kind'] for a in d['arcs']}
    lines = open(SRC).read().split('\n')
    out = []
    changed = 0
    skipped = 0
    for i, ln in enumerate(lines):
        n = i + 1
        if n not in ty:
            out.append(ln)
            continue
        # deja type ? ('-[kind]->') : on le REMPLACE si le kind change
        mk = re.match(r"^(\s*)([\w.]+)\s*-\s*\[([\w-]+)\]\s*->(.*)$", ln)
        if mk:
            ind, src, oldkind, rest = mk.groups()
            newkind = ty[n]
            if oldkind == newkind:
                skipped += 1
                out.append(ln)
                continue
            changed += 1
            out.append(f"{ind}{src} -[{newkind}]->{rest}")
            continue
        m = re.match(r"^(\s*)([\w.]+)(\s*)->(\s*)([\w.]+)(.*)$", ln)
        if not m:
            out.append(ln)
            continue
        ind, src, sp1, sp2, dst, rest = m.groups()
        kind = ty[n]
        new = f"{ind}{src}{sp1}-[{kind}]->{sp2}{dst}{rest}"
        changed += 1
        out.append(new)
    if dry:
        print(f"[dry-run] arcs a typer : {changed} | deja types : {skipped}")
        for i, ln in enumerate(lines):
            n = i + 1
            if n in ty:
                m = re.match(r"^(\s*)([\w.]+)(\s*)->(\s*)([\w.]+)(.*)$", ln)
                if m:
                    print(f"  L{n}: {m.group(2)} -[{ty[n]}]-> {m.group(5)}")
        return
    open(SRC, 'w').write('\n'.join(out))
    print(f"[applique] arcs types : {changed} | deja types : {skipped}")


if __name__ == '__main__':
    main('--dry-run' in sys.argv)
