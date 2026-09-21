#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""audit_comp_alg.py — etat des lieux des relations component <-> algorithm.

Source de verite : le modele compile servi par le conteneur likec4
(/docker/likec4/workspace/likec4.json), pas le texte des .c4.

Trois controles :
  1. Inventaire des relations component <-> algorithm.
  2. Composants sans aucun lien algorithmique (orphelins).
  3. DOUBLONS : meme paire (source, kind, target) declaree dans plusieurs
     fichiers .c4. LikeC4 accepte les doublons (deux arcs superposes dans
     l'UI), mais c'est une dette de modele : le meme fait est affirme deux
     fois, et une correction future peut n'en toucher qu'un.
"""
import json
import sys
from collections import defaultdict

MODEL = sys.argv[1] if len(sys.argv) > 1 else "/docker/likec4/workspace/likec4.json"

d = json.load(open(MODEL))
proj = [p for p in d if p.get("projectId") == "swarmdrones"][0]
el = proj["elements"]
rels = proj["relations"]

comps = {eid: e for eid, e in el.items() if e.get("kind") == "component"}
algs = {eid: e for eid, e in el.items() if e.get("kind") == "algorithm"}
print("components=%d  algorithms=%d" % (len(comps), len(algs)))

ca = []
for rid, r in rels.items():
    s = r.get("source", {}).get("model", "")
    t = r.get("target", {}).get("model", "")
    if (s in comps and t in algs) or (s in algs and t in comps):
        ca.append((s, r.get("kind"), t))

print("\n=== %d relations component<->algorithm ===" % len(ca))
for s, k, t in sorted(ca):
    print("  %-28s -[%s]-> %s" % (s, k, t))

# --- 3. Doublons de paire (source, kind, target) ---------------------------
pairs = defaultdict(list)
for s, k, t in ca:
    pairs[(s, k, t)].append(s)
dups = {p: n for p, n in pairs.items() if len(n) > 1}
print("\n=== DOUBLONS de paire (source, kind, target) : %d ===" % len(dups))
for (s, k, t), n in sorted(dups.items()):
    print("  x%d  %s -[%s]-> %s" % (len(n), s, k, t))

linked = set()
for s, k, t in ca:
    linked.add(s)
    linked.add(t)

orphan_c = sorted(c for c in comps if c not in linked)
orphan_a = sorted(a for a in algs if a not in linked)
print("\n=== components SANS lien algorithme (%d) ===" % len(orphan_c))
for c in orphan_c:
    print("  %-28s %s" % (c, comps[c].get("title")))
print("\n=== algorithms SANS lien composant (%d) ===" % len(orphan_a))
for a in orphan_a:
    print("  %-28s %s" % (a, algs[a].get("title")))
