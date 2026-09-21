#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_related_components.py — coherence entre la metadonnee `relatedComponents`
declaree sur chaque algorithme et les relations component<->algorithm reellement
presentes dans le modele compile.

But : detecter un lien DECLARE mais ABSENT (lien manquant = defaut reel) et un
lien PRESENT mais NON DECLARE (bruit). Les composants cites mais inexistants
sont signales comme FANTOMES (ex. onboard.resilience).
"""
import json

d = json.load(open("/docker/likec4/workspace/likec4.json"))
proj = [p for p in d if p.get("projectId") == "swarmdrones"][0]
el = proj["elements"]
rels = proj["relations"]
comps = {k for k, v in el.items() if v.get("kind") == "component"}
algs = {k for k, v in el.items() if v.get("kind") == "algorithm"}

real = {}
for r in rels.values():
    s = r.get("source", {}).get("model", "")
    t = r.get("target", {}).get("model", "")
    if s in comps and t in algs:
        real.setdefault(t, set()).add(s)
    if s in algs and t in comps:
        real.setdefault(s, set()).add(t)

print("=== ecart entre relatedComponents declare et relations reelles ===")
bad = 0
for aid in sorted(algs):
    m = el[aid].get("metadata", {}) or {}
    rc = m.get("relatedComponents")
    if not rc:
        print("  %s: PAS de relatedComponents" % aid)
        continue
    declared = {x.strip() for x in rc.split(",") if x.strip()}
    actual = real.get(aid, set())
    declared_existing = {x for x in declared if x in comps}
    ghost = declared - comps
    missing = declared_existing - actual
    extra = actual - declared_existing
    flag = ""
    if missing:
        flag += " MANQUANT=%s" % sorted(missing)
        bad += 1
    if extra:
        flag += " EN_PLUS=%s" % sorted(extra)
    if ghost:
        flag += " FANTOME=%s" % sorted(ghost)
    print("  %s:%s" % (aid, flag if flag else " OK"))

print("\n%d algorithme(s) avec lien declare manquant." % bad if bad
      else "\nAucun lien declare manquant.")
