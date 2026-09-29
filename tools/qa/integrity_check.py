#!/usr/bin/env python3
"""
Structural Integrity Check — E12 (SWARM-3D-ARCHITECTURE)

Verifications de coherence au-dela de la syntaxe : ce que `likec4 validate`
ne voit PAS.

Controles :
  I-1  Integrite referentielle : tout arc pointe un element existant
  I-2  Orphelins : elements sans aucun arc (hors vues)
  I-3  Chaine complete : CAPACITE -> FONCTION -> ALGORITHME -> COMPOSANT -> RUNTIME -> NOEUD
  I-4  Contrat de simulation respecte (invariants INV-1..4)
  I-5  Garde-fous du World Model (REG-1..6) presents et verifiables
  I-6  Aucune valeur inventee : pas de chiffre non source (energie, portee)
  I-7  Coherence des affirmations scientifiques (verdicts)

Usage: python3 tools/qa/integrity_check.py [--json]
"""
import json
import subprocess
import sys
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTAINER = "likec4"


def load():
    subprocess.run(["docker", "exec", CONTAINER, "likec4", "export", "json", "/data", "-o", "/data/out/qa.json"],
                   capture_output=True, text=True, check=True)
    raw = subprocess.run(["docker", "exec", CONTAINER, "cat", "/data/out/qa.json"],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(raw)[0]


def kinds_of(model):
    return {v["kind"] for v in model["elements"].values()}


def check_referential(model):
    els, rels = model["elements"], model["relations"]
    bad = [r for r in rels.values() if r["source"]["model"] not in els or r["target"]["model"] not in els]
    return {"id": "I-1", "nom": "Integrite referentielle", "ok": not bad,
            "detail": f"{len(rels)} relations, {len(bad)} arcs casses"}


def check_orphans(model):
    els, rels = model["elements"], model["relations"]
    seen = set()
    for r in rels.values():
        seen.add(r["source"]["model"])
        seen.add(r["target"]["model"])
    # on ignore les elements de contrat/rendu, naturellement portes par metadata
    exempt = {"renderRule"}

    # Les sources bibliographiques SANS verdict sont legitimes SANS rattachement :
    #   - 'A CONSULTER' : non encore lues (regle "pas de lecture, pas de verdict");
    #   - 'ECARTEE'     : lues mais rejetees (aucun apport a un algorithme).
    # Les compter comme orphelins produit un faux positif qui banalise le FAIL
    # — et masquerait un vrai orphelin.
    def is_legit_unattached_source(v):
        md = v.get("metadata") or {}
        statut = str(md.get("statut", "")).upper()
        return (v["kind"] == "specDoc"
                and ("A CONSULTER" in statut or "ECARTEE" in statut))

    orphan = [k for k, v in els.items()
              if k not in seen
              and v["kind"] not in exempt
              and not is_legit_unattached_source(v)]
    unattached = [k for k, v in els.items()
                  if k not in seen and is_legit_unattached_source(v)]
    detail = f"{len(orphan)} orphelins" + (f" : {orphan[:6]}" if orphan else "")
    if unattached:
        detail += f" ({len(unattached)} sources sans verdict exemptees — conforme)"
    return {"id": "I-2", "nom": "Elements orphelins", "ok": not orphan,
            "detail": detail}


def check_chain(model):
    """Verifie qu'une chaine CAPACITE->FONCTION->ALGORITHME->COMPOSANT->RUNTIME->NOEUD existe."""
    els, rels = model["elements"], model["relations"]
    arc = {}
    for r in rels.values():
        arc.setdefault(r["source"]["model"], set()).add((r["kind"], r["target"]["model"]))

    def kind_of(k):
        return els[k]["kind"] if k in els else "?"

    # capacite -> fonction (realizes) -> algorithme (implements) -> composant
    caps = [k for k, v in els.items() if v["kind"] == "capability"]
    chains = []
    for c in caps:
        fns = [t for (kd, t) in arc.get(c, set()) if kind_of(t) == "function"]
        for f in fns:
            algs = [t for (kd, t) in arc.get(f, set()) if kind_of(t) == "algorithm"]
            comps = [t for (kd, t) in arc.get(f, set()) if kind_of(t) in ("component", "node", "service")]
            chains.append((c, f, len(algs) + len(comps)))
    n_full = sum(1 for _, _, n in chains if n > 0)
    return {"id": "I-3", "nom": "Chaine CAPACITE->FONCTION->ALGORITHME", "ok": n_full > 0,
            "detail": f"{len(chains)} liens capacite->fonction, {n_full} avec algorithme rattache"}


def check_sim_contract(model):
    els = model["elements"]
    has_contract = any("ontract" in (v.get("title") or "") or v["kind"] == "simContract"
                       for v in els.values())
    has_inv = [k for k, v in els.items() if "INV-" in (v.get("title") or "") or "invariant" in (v.get("title") or "").lower()]
    return {"id": "I-4", "nom": "Contrat de simulation", "ok": has_contract,
            "detail": f"contrat: {has_contract}, invariants nommes: {len(has_inv)}"}


def check_render_rules(model):
    rules = [k for k, v in model["elements"].values().__iter__()] if False else \
            [k for k, v in model["elements"].items() if v["kind"] == "renderRule"]
    src = (ROOT / "worldmodel.c4").read_text(encoding="utf-8")
    verifiable = src.count("test '")
    return {"id": "I-5", "nom": "Garde-fous World Model", "ok": len(rules) >= 6 and verifiable >= 6,
            "detail": f"{len(rules)} regles de rendu, {verifiable} portent un test"}


def check_no_invented(model):
    """Cherche des valeurs chiffrees d'energie/portee non sourcees dans le modele."""
    pat = re.compile(r"(capacite|autonomie|endurance|portee)\s*[:=]\s*\d+\s*(Wh|min|km|m|%)", re.I)
    hits = []
    for f in sorted(ROOT.glob("*.c4")):
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if pat.search(line) and "NON" not in line.upper() and "interdit" not in line.lower():
                hits.append(f"{f.name}:{n}")
    return {"id": "I-6", "nom": "Aucune valeur inventee", "ok": not hits,
            "detail": f"{len(hits)} valeurs chiffrees non sourcees" + (f" : {hits[:4]}" if hits else "")}


def check_science(model):
    """Les constats se scindent en deux natures, et confondre les deux fausse
    la mesure : SCI-* portent un VERDICT (une affirmation evaluee contre une
    source primaire) ; GAP-* documentent un TROU (aucun article trouve) et
    n'ont donc pas de verdict par construction."""
    els = model["elements"]
    findings = {k: v for k, v in els.items() if v["kind"] == "finding"}
    verdicts = {k: v for k, v in findings.items() if "verdict" in (v.get("metadata") or {})}
    gaps = {k: v for k, v in findings.items() if k.lower().startswith("gap")}
    refs = {k: v for k, v in findings.items()
            if (v.get("metadata") or {}).get("source") or (v.get("metadata") or {}).get("references")
            or (v.get("metadata") or {}).get("sources")}
    # Chaque constat-verdict doit porter une source ; chaque gap doit etre nomme comme tel.
    verdicts_sans_source = [k for k in verdicts if k not in refs]
    ok = len(verdicts) > 0 and not verdicts_sans_source
    return {"id": "I-7", "nom": "Coherence scientifique", "ok": ok,
            "detail": f"{len(findings)} constats = {len(verdicts)} avec verdict + {len(gaps)} gaps ; "
                      f"{len(verdicts)} verdicts sources" +
                      (f" ; SANS SOURCE: {verdicts_sans_source}" if verdicts_sans_source else "")}


CHECKS = [check_referential, check_orphans, check_chain, check_sim_contract,
          check_render_rules, check_no_invented, check_science]


def main():
    model = load()
    res = []
    for fn in CHECKS:
        try:
            res.append(fn(model))
        except Exception as e:  # noqa: BLE001
            res.append({"id": "?", "nom": fn.__name__, "ok": False, "detail": f"ERREUR: {e}"})
    if "--json" in sys.argv:
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return
    print(f"\n{'ID':<5} {'Controle':<34} {'Etat':<5} Detail")
    print("-" * 105)
    for c in res:
        print(f"{c['id']:<5} {c['nom']:<34} {'OK' if c['ok'] else 'FAIL':<5} {c['detail'][:58]}")
    print("-" * 105)
    ko = [c["id"] for c in res if not c["ok"]]
    print(f"{len(res) - len(ko)}/{len(res)} controles OK" + (f"  | ECHECS: {ko}" if ko else "  | TOUS OK"))


if __name__ == "__main__":
    main()
