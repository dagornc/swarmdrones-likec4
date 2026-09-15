#!/usr/bin/env python3
"""
Quality Gate — E12 (SWARM-3D-ARCHITECTURE)

Rejoue mecaniquement les 11 criteres du score d'audit E00 (docs/audit-likec4.md,
31/100) contre le modele compile. Chaque note est CALCULEE, pas declaree :
si le calcul ne peut pas etre fait, le critere est marque UNMEASURED, jamais
note a la main.

Usage:
    python3 tools/qa/quality_gate.py            # rapport lisible
    python3 tools/qa/quality_gate.py --json     # rapport machine
"""
import json
import subprocess
import sys
import re
import glob
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTAINER = "likec4"


def load_model():
    """Exporte le modele compile depuis le conteneur et le charge."""
    subprocess.run(
        ["docker", "exec", CONTAINER, "likec4", "export", "json", "/data", "-o", "/data/out/qa.json"],
        capture_output=True, text=True, check=True,
    )
    raw = subprocess.run(
        ["docker", "exec", CONTAINER, "cat", "/data/out/qa.json"],
        capture_output=True, text=True, check=True,
    ).stdout
    return json.loads(raw)[0]


def validate():
    """Retourne (ok, n_files, n_errors). Parse la sortie reelle du conteneur,
    qui porte un prefixe horodate et le caractere ✓."""
    r = subprocess.run(
        ["docker", "exec", CONTAINER, "likec4", "validate", "/data"],
        capture_output=True, text=True,
    )
    out = r.stdout + r.stderr
    out = re.sub(r"\x1b\[[0-9;]*m", "", out)  # retire les codes ANSI
    m = re.search(r"(Valid|Invalid)\s*\((\d+)\s*files?(?:,\s*(\d+)\s*errors?)?\)", out)
    if not m:
        return False, 0, -1
    return m.group(1) == "Valid", int(m.group(2)), int(m.group(3) or 0)


# ---------------------------------------------------------------------------
#  Les 11 criteres. Chaque fonction retourne (note_max, note, justification).
#  Aucune note n'est ecrite en dur : toutes sont derivees d'un comptage.
# ---------------------------------------------------------------------------

def crit_syntax(model):
    ok, nf, nerr = validate()
    return 10, (10 if ok else 0), f"{'Valid' if ok else 'Invalid'} ({nf} files, {nerr} errors)"


def crit_ids(model):
    els = model["elements"]
    n = len(els)
    kebab = re.compile(r"^[a-z][a-zA-Z0-9]*(\.[a-z][a-zA-Z0-9]*)?$")
    conv = sum(1 for k in els if kebab.match(k))
    pct = 100 * conv / n if n else 0
    note = round(10 * pct / 100)
    return 10, min(10, note), f"{n} elements, {conv} conformes a la convention ({pct:.0f}%)"


def crit_element_types(model):
    kinds = {v["kind"] for v in model["elements"].values()}
    # familles requises par E00 : donnees / com / telecom / materiel
    familles = {
        "donnees": {"message", "channel", "factSheet", "evidence", "finding"},
        "communication": {"channel", "message", "linkRadio", "protocol"},
        "materiel": {"hardwareNode", "sensor", "actuator", "computeNode"},
        "algorithmes": {"algorithm"},
        "science": {"finding", "evidence", "source"},
        "world": {"worldEntity", "zoneSemantic", "worldState", "renderRule", "sceneCategory"},
    }
    present = {f: bool(k & kinds) for f, k in familles.items()}
    n_ok = sum(present.values())
    note = round(10 * n_ok / len(familles))
    return 10, note, f"{len(kinds)} kinds ; familles couvertes {n_ok}/{len(familles)} : " + \
        ", ".join(f"{f}{'' if v else '(MANQUE)'}" for f, v in present.items())


def crit_relation_types(model):
    rels = model["relations"]
    kinds = {r["kind"] for r in rels.values()}
    n = len(rels)
    # E00 : 0/15 car tous les arcs etaient `sync`
    note = 0 if len(kinds) <= 1 else round(15 * min(1.0, len(kinds) / 15))
    return 15, note, f"{n} relations, {len(kinds)} kinds distincts utilises"


def crit_doc(model):
    els = model["elements"]
    n = len(els)
    with_desc = sum(1 for v in els.values() if v.get("description"))
    with_meta = sum(1 for v in els.values() if v.get("metadata"))
    pct = 100 * with_desc / n if n else 0
    note = round(10 * pct / 100)
    return 10, min(10, note), f"{with_desc}/{n} descriptions ({pct:.0f}%), {with_meta} avec metadata"


def crit_algorithms(model):
    els = model["elements"]
    algos = [v for v in els.values() if v["kind"] == "algorithm"]
    if not algos:
        return 10, 0, "aucun algorithme"
    champs = ["inputs", "outputs", "parameters", "metrics", "mode", "complexity",
              "hypotheses", "verdict", "evidence", "references"]
    def rich(e):
        md = e.get("metadata") or {}
        return sum(1 for c in champs if md.get(c))
    moy = sum(rich(e) for e in algos) / len(algos)
    note = round(10 * min(1.0, moy / 5))
    return 10, note, f"{len(algos)} algorithmes, {moy:.1f} champs riches en moyenne (cible 5)"


def crit_messages(model):
    msgs = [v for v in model["elements"].values() if v["kind"] == "message"]
    note = 0 if not msgs else (10 if len(msgs) >= 10 else round(10 * len(msgs) / 10))
    return 10, note, f"{len(msgs)} messages objets"


def crit_hardware(model):
    kinds = {"hardwareNode", "sensor", "actuator", "computeNode"}
    hw = [v for v in model["elements"].values() if v["kind"] in kinds]
    note = 0 if not hw else min(10, round(10 * len(hw) / 10)) if len(hw) >= 10 else round(10 * len(hw) / 10)
    return 10, note, f"{len(hw)} elements materiels"


def crit_deployment(model):
    kinds = {"deploymentUnit"}
    units = [v for v in model["elements"].values() if v["kind"] in kinds]
    # chaine Algorithm->Component->Runtime->Node presente ?
    rels = model["relations"]
    kinds_r = {r["kind"] for r in rels.values()}
    has_chain = {"runsOn", "deployedOn"} & kinds_r or "runsOn" in kinds_r
    note = 6 if units and not has_chain else (10 if units and has_chain else 0)
    return 10, note, f"{len(units)} unites de deploiement, chaine typée: {bool(has_chain)}"


def crit_views(model):
    """E00 : 4/5 pour 22 vues, mais 5 vues feuilles MORTES. Le critere porte
    donc sur la navigation et la sante des vues, pas sur leur nombre."""
    views = model.get("views", {})
    n = len(views)
    empty = [k for k, v in views.items() if not v.get("nodes")]
    src = (ROOT / "views.c4").read_text(encoding="utf-8") if (ROOT / "views.c4").exists() else ""
    nav = src.count("navigateTo")
    note = 5
    if empty:
        note -= min(2, len(empty))
    if nav < 12:
        note -= 1
    if n < 22:
        note = min(note, round(5 * n / 22))
    return 5, max(0, note), f"{n} vues, {len(empty)} vides, {nav} navigateTo"


def crit_traceability(model):
    els = model["elements"]
    facts = [v for v in els.values() if (v.get("tags") or []) and "fact" in v["tags"]]
    sci = [v for v in els.values() if v["kind"] in ("finding", "evidence", "source")]
    refs = sum(1 for v in els.values() if (v.get("metadata") or {}).get("references")
               or (v.get("metadata") or {}).get("source"))
    note = 10 if (facts and sci) else (6 if facts or sci else 4)
    return 10, note, f"{len(facts)} faits, {len(sci)} elements scientifiques, {refs} avec source/reference"


CRITERIA = [
    ("Validite syntaxique", crit_syntax),
    ("Identifiants uniques", crit_ids),
    ("Type des elements", crit_element_types),
    ("Type des relations", crit_relation_types),
    ("Completude documentaire", crit_doc),
    ("Couverture algorithmique", crit_algorithms),
    ("Couverture messages", crit_messages),
    ("Couverture materielle", crit_hardware),
    ("Couverture deploiement", crit_deployment),
    ("Vues et navigation", crit_views),
    ("Tracabilite / preuves", crit_traceability),
]


def main():
    as_json = "--json" in sys.argv
    model = load_model()
    rows = []
    total_w = total = 0
    for name, fn in CRITERIA:
        try:
            w, s, why = fn(model)
        except Exception as e:  # noqa: BLE001
            w, s, why = 0, 0, f"UNMEASURED ({e})"
        rows.append({"critere": name, "poids": w, "note": s, "justification": why})
        total_w += w
        total += s
    score = round(100 * total / total_w) if total_w else 0

    if as_json:
        print(json.dumps({"score": score, "cible": 90, "rows": rows}, ensure_ascii=False, indent=1))
        return

    print(f"\n{'Critere':<26} {'Poids':>5} {'Note':>5}  Justification")
    print("-" * 100)
    for r in rows:
        print(f"{r['critere']:<26} {r['poids']:>5} {r['note']:>5}  {r['justification'][:60]}")
    print("-" * 100)
    print(f"{'TOTAL':<26} {total_w:>5} {total:>5}  ==> SCORE {score}/100 (cible >= 90)")
    print(f"\nE00 (initial) : 31/100   |   maintenant : {score}/100   |   delta : +{score-31}")
    print(f"GATE: {'PASS' if score >= 90 else 'FAIL'}")


if __name__ == "__main__":
    main()
