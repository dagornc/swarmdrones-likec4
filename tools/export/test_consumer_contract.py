#!/usr/bin/env python3
"""
Test du moteur de verification du viewer, porte sur l'artefact REEL.

Ce script reimplemente les 8 controles de viewer/index.html et les applique
a export/scene.json. But : prouver que le consommateur detecte les violations,
pas seulement qu'il sait dire "OK".

On teste les DEUX sens :
  - sur l'artefact reel  -> tout doit passer ;
  - sur des artefacts MUTILES (energie, portee, transform, mauvais compte)
    -> le controle correspondant DOIT echouer. Un test qui ne peut pas
       echouer ne prouve rien.
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCENE = ROOT / "export" / "scene.json"


def obs_text(s):
    """Texte CONSOMME par la scene : etats d'apparence + obligations.

    On exclut volontairement s['render_rules'] : le texte des garde-fous
    cite les unites qu'il interdit ('aucune valeur Wh/min/Pct'), ce qui
    produirait un faux positif si on le scannait.
    """
    return json.dumps({
        "o": s["consumer_obligations"], "st": s["states"],
        "iv": s["invariants_applied"],
    }, ensure_ascii=False)


def run_checks(s):
    c, I = s["counts"], s["instances"]
    ops = [i for i in I if i["is_swarm_platform"]]
    ref = [i for i in I if i["is_reference_mockup"]]
    inf = [i for i in I if i["nature"] == "infrastructure"]
    chk = []

    withT = [i for i in I if i.get("transform") is not None]
    chk.append(("REG-6/INV-4", withT == []))

    chk.append(("REG-5", len(ops) == 30 and len(ref) == 1))

    ids = [i["instance_id"] for i in I]
    cls = {i["class_id"] for i in I}
    # Ancre : tout class_id doit etre source d'un derivation_link = vient du World Model
    from_model = {l["from"] for l in s["derivation_links"]}
    chk.append(("REG-1", len(set(ids)) == len(ids) and cls <= from_model))

    tx = obs_text(s)
    chk.append(("REG-4", bool(re.search(r"N\s*=\s*30\s*NON\s*PROUV", tx, re.I))))
    chk.append(("REG-2", not re.search(r"\b(Wh|mAh|%|autonomie\s*\d)", tx, re.I)))
    chk.append(("REG-3", not re.search(r"\b\d+\s*(km|m)\b", tx, re.I)))

    chk.append(("INTEGRITE",
                c["instances"] == len(I) and c["operational_platforms"] == len(ops)
                and c["reference_mockups"] == len(ref) and c["infrastructure"] == len(inf)))

    ver = [r for r in s["render_rules"] if r["verifiable"]]
    chk.append(("GARDE-FOUS", len(s["render_rules"]) >= 6 and len(ver) == len(s["render_rules"])))
    return chk


def main():
    s = json.loads(SCENE.read_text())
    print("=== A. ARTEFACT REEL — tout doit passer ===")
    res = run_checks(s)
    bad = [k for k, ok in res if not ok]
    for k, ok in res:
        print(f"  {'OK  ' if ok else 'FAIL'} {k}")
    print(f"  -> {len(res)-len(bad)}/{len(res)} controles passes")

    print()
    print("=== B. ARTEFACTS MUTILES — le controle cible DOIT echouer ===")
    muts = []
    # 1. energie inventee
    m = json.loads(json.dumps(s))
    m["states"][0]["rendering"] = "batterie a 42%"
    muts.append(("energie % dans un etat", "REG-2", m))
    # 2. classe inventee (id hors modele)
    m = json.loads(json.dumps(s))
    m["instances"][0]["class_id"] = "entClasseInventee"
    muts.append(("class_id hors modele", "REG-1", m))
    # 3. portee radio chiffree
    m = json.loads(json.dumps(s))
    m["consumer_obligations"].append("portee radio 15 km")
    muts.append(("portee 15 km dans les obligations", "REG-3", m))
    # 3. transform present (violation INV-4)
    m = json.loads(json.dumps(s))
    m["instances"][0]["transform"] = {"x": 1, "y": 2, "z": 3}
    muts.append(("transform non nul", "REG-6/INV-4", m))
    # 4. population cassee
    m = json.loads(json.dumps(s))
    for i in m["instances"][:3]:
        i["is_swarm_platform"] = False
    muts.append(("3 plateformes requalifiees", "REG-5", m))
    # 5. compteur ment
    m = json.loads(json.dumps(s))
    m["counts"]["operational_platforms"] = 33
    muts.append(("compteur declare 33", "INTEGRITE", m))
    # 6. mention de limite retiree de TOUTES ses sources legitimes
    #    (obligations + rendu de l'etat stLeaderLost). La limite vit aux deux.
    m = json.loads(json.dumps(s))
    m["consumer_obligations"] = [
        o for o in m["consumer_obligations"] if "NON PROUVE" not in o.upper()
    ]
    for st in m["states"]:
        if st.get("rendering"):
            st["rendering"] = st["rendering"].replace("N=30 NON PROUVE", "")
        if st.get("limit"):
            st["limit"] = st["limit"].replace("N=30 NON PROUVE", "")
    muts.append(("mention N=30 NON PROUVE retiree de toutes ses sources", "REG-4", m))

    ok_all = len(bad) == 0
    for label, target, mm in muts:
        r = dict(run_checks(mm))
        caught = r.get(target) is False
        print(f"  {'ATTRAPE ' if caught else 'RATE   '} [{target}] <- {label}")
        ok_all = ok_all and caught

    print()
    print("=== RESULTAT ===")
    print(f"  A (artefact reel conforme) : {'PASS' if not bad else 'FAIL: '+str(bad)}")
    print(f"  B (6 mutations attrapees)  : {'PASS' if all(dict(run_checks(m))[t] is False for _,t,m in muts) else 'FAIL'}")
    verdict = "OK — le consommateur verifie reellement le contrat" if (
        not bad and all(dict(run_checks(m))[t] is False for _, t, m in muts)
    ) else "ECHEC"
    print(f"  {verdict}")
    return 0 if verdict.startswith("OK") else 1


if __name__ == "__main__":
    sys.exit(main())
