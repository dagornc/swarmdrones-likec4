#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Affiche l'arborescence de navigation LikeC4 reconstruite depuis les titres."""
import re, os
BASE = '/home/hermesagent/workspace/swarmdrones_likec4'
tree = {}
for f in ['views.c4', 'ux-parcours.c4', 'e19-system-context.c4']:
    txt = open(os.path.join(BASE, f), encoding='utf-8').read()
    for m in re.finditer(r"title '((?:[^'\\]|\\.)*)'", txt):
        t = m.group(1).replace("\\'", "'")
        # un '/' échappé (\/) reste dans le libellé ; sinon c'est un séparateur
        segs = re.split(r'(?<!\\) / ', t)
        segs = [s.replace('\\/', '/') for s in segs]
        node = tree
        for s in segs:
            node = node.setdefault(s, {})

def show(node, depth=0):
    for k in sorted(node.keys()):
        print('  ' * depth + ('📁 ' if node[k] else '• ') + k)
        show(node[k], depth + 1)

show(tree)
