#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_served_links.py — verifie que le modele REELLEMENT SERVI par
likec4.breizh.ai contient bien les liens component->algorithm ajoutes.

Le conteneur sert un instantane pris a son demarrage : un fichier .c4 modifie
sur disque n'est PAS forcement servi. Ce script telecharge le modele servi,
l'evalue avec node (le modele est un litteral JS, pas du JSON strict) et
compare les paires (source, target) attendues.

Usage : python3 verify_served_links.py [chemin_modele_servi]
"""
import json
import subprocess
import sys

SERVED = sys.argv[1] if len(sys.argv) > 1 else "/tmp/served_model.js"

# Paires ajoutees (source, target) — sens composant -> algorithme.
PAIRS = [
    ("onboard.perception", "algCollisionAvoidance"),
    ("onboard.autopilot", "algCollisionAvoidance"),
    ("onboard.safety", "algNavigationGNSSDegrade"),
    ("onboard.autopilot", "algNavigationGNSSDegrade"),
    ("onboard.autopilot", "algSafetyRules"),
    ("onboard.autopilot", "algEnergyAware"),
    ("onboard.perception", "algFormationControl"),
    ("onboard.perception", "algJammingResilientMode"),
    ("edge.coordinator", "algHealthMonitoring"),
    ("edge.coordinator", "algLeaderElection"),
    ("edge.coordinator", "algPathPlanning"),
    ("onboard.health", "algFaultTolerantControlAlloc"),
]

raw = open(SERVED, encoding="utf-8", errors="replace").read()
start = raw.find("atom(")
if start < 0:
    print("!! appel atom( introuvable dans le modele servi")
    sys.exit(2)
start += len("atom(")

# On equilibre les accolades en tenant compte des chaines (simples et doubles).
depth = 0
quote = None
esc = False
end = None
for i in range(start, len(raw)):
    c = raw[i]
    if quote:
        if esc:
            esc = False
        elif c == "\\":
            esc = True
        elif c == quote:
            quote = None
        continue
    if c in "\"'":
        quote = c
    elif c == "{":
        depth += 1
    elif c == "}":
        depth -= 1
        if depth == 0:
            end = i + 1
            break
if end is None:
    print("!! objet du modele non termine")
    sys.exit(2)

obj_src = raw[start:end]
# Evaluation JS -> JSON via node (le litteral n'est pas du JSON strict).
node_script = (
    "const fs=require('fs');"
    "const s=fs.readFileSync(0,'utf8');"
    "const o=eval('('+s+')');"
    "process.stdout.write(JSON.stringify(o));"
)
try:
    out = subprocess.run(
        ["node", "-e", node_script],
        input=obj_src, capture_output=True, text=True, timeout=120,
    )
except Exception as e:  # noqa: BLE001
    print("!! echec de l'evaluation node : %s" % e)
    sys.exit(2)
if out.returncode != 0:
    print("!! node a echoue : %s" % out.stderr[:400])
    sys.exit(2)

data = json.loads(out.stdout)
# Le modele servi est un objet projet unique (pas une liste).
proj = data if data.get("projectId") == "swarmdrones" else None
if proj is None:
    print("!! projet 'swarmdrones' absent du modele servi")
    sys.exit(2)
rels = proj["relations"]

present = set()
for r in rels.values():
    s = r.get("source", {}).get("model", "")
    t = r.get("target", {}).get("model", "")
    present.add((s, t))

print("=== verification des %d paires dans le modele SERVI ===" % len(PAIRS))
miss = 0
for s, t in PAIRS:
    ok = (s, t) in present
    print("  %s  %-22s -> %s" % ("OK " if ok else "MANQUE", s, t))
    if not ok:
        miss += 1
print("\n%d paire(s) absente(s) du modele servi." % miss if miss
      else "\nToutes les paires sont presentes dans le modele servi.")
sys.exit(1 if miss else 0)
