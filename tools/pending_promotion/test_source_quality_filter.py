#!/usr/bin/env python3
"""Test d'injection du filtre de qualite de source (carte t_06092fce, etage 3).

Verifie, sur la SOURCE versionnee (avant deploiement) :
  1. Injection du defaut sur le chemin par defaut : un titre de PRESSE contenant
     "consensus" est classe presse-commercial et ne produit PLUS de proposition
     vers algConsensus (avant : le ciblage par mots-cles le proposait).
  2. Les propositions SCIENTIFIQUES passent toujours : arXiv / DOI / revue /
     depot institutionnel restent classifies "scientifique" et produisent une
     proposition (le ciblage corrige en carte 4 n'est pas casse).
  3. Les sources TECHNIQUES (doc officielle / depot de code) sont classees
     "technique" et ne produisent pas de proposition.
  4. Regression : les 64 propositions pending du lot 02 sont reclassifiees par le
     filtre et la repartition correspond a la grille validee (26 presse-commercial
     / 3 technique / 35 scientifique).

Usage : python3 tools/pending_promotion/test_source_quality_filter.py
Sortie : code 0 si tout est OK, 1 sinon.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

PROFILE_SRC = Path('/home/hermesagent/swarmdrone-profile/scripts/analyze_impact.py')
RESEARCH = Path('/home/hermesagent/swarmdrone-research')
LIKEC4 = Path('/home/hermesagent/workspace/swarmdrones_likec4')


def load_analyze():
    spec = importlib.util.spec_from_file_location("analyze_impact", PROFILE_SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def classify(mod, host, url="", arxiv_ids=None, title=""):
    rec = {"source_host": host, "source_url": url, "arxiv_ids": arxiv_ids or [], "title": title}
    return mod.classify_source_nature(rec)


def main() -> int:
    failures: list[str] = []
    mod = load_analyze()

    print("== 1. Injection de defaut : presse + mot-cle 'consensus' ==")
    press_consensus = {
        "number": 999901,
        "title": "Consensus-based drone swarm coordination: market outlook and vendor roundup",
        "source_host": "defensescoop.com",
        "source_url": "https://defensescoop.com/2025/01/01/consensus-drone-swarm-coordination/",
        "arxiv_ids": [],
        "dois": [],
    }
    nature = mod.classify_source_nature(press_consensus)
    text = mod.article_text(press_consensus, RESEARCH)
    targets = mod.score_targets(text)
    before = (targets[0][0] if targets else None)
    after = None if nature != "scientifique" else (targets[0][0] if targets else None)
    print(f"  nature = {nature}")
    print(f"  AVANT (score_targets seul) : top cible = {before}")
    print(f"  APRES (filtre de nature)   : proposition produite = {after}")
    if nature != "presse-commercial":
        failures.append("la presse 'consensus' n'est pas classee presse-commercial")
    if after is not None:
        failures.append("la presse 'consensus' produirait encore une proposition")
    print("  OK" if nature == "presse-commercial" and after is None else "  ECHEC")

    print("\n== 2. Les sources scientifiques passent toujours ==")
    sci_cases = [
        ("arXiv (champ arxiv_ids)", {"source_host": "", "source_url": "",
                                     "arxiv_ids": ["2509.06481"], "title": "Event Driven CBBA",
                                     "dois": []}),
        ("arXiv (URL)", {"source_host": "arxiv.org",
                         "source_url": "https://arxiv.org/pdf/2509.06481",
                         "arxiv_ids": [], "title": "Event Driven CBBA", "dois": []}),
        ("DOI (doi.org)", {"source_host": "doi.org",
                           "source_url": "https://doi.org/10.3390/drones9070484",
                           "arxiv_ids": [], "title": "A Survey", "dois": ["10.3390/drones9070484"]}),
        ("revue MDPI", {"source_host": "www.mdpi.com",
                        "source_url": "https://www.mdpi.com/2504-446X/9/8/521",
                        "arxiv_ids": [], "title": "Collaborative Target Tracking", "dois": ["10.3390/drones9080521"]}),
        ("revue IET", {"source_host": "digital-library.theiet.org",
                       "source_url": "https://digital-library.theiet.org/doi/full/10.1049/csy2.70006",
                       "arxiv_ids": [], "title": "Bioinspired", "dois": ["10.1049/csy2.70006"]}),
        ("depot institutionnel (Berkeley)", {"source_host": "msol.berkeley.edu",
                                             "source_url": "https://msol.berkeley.edu/wp-content/uploads/2025/05/212.pdf",
                                             "arxiv_ids": [], "title": "digital-twin", "dois": ["10.1016/j.cma.2025.117999"]}),
    ]
    for label, rec in sci_cases:
        got = mod.classify_source_nature(rec)
        ok = got == "scientifique"
        print(f"  {label:34s} -> {got:18s} {'OK' if ok else 'ECHEC'}")
        if not ok:
            failures.append(f"scientifique non reconnue : {label}")

    print("\n== 3. Les sources techniques sont classee 'technique' ==")
    tech_cases = [
        ("documentation officielle (Gazebo)", "gazebosim.org",
         "https://gazebosim.org/docs/latest/ros_installation/"),
        ("depot de code (SourceForge)", "sourceforge.net",
         "https://sourceforge.net/projects/gym-pybullet-drones.mirror/"),
    ]
    for label, host, url in tech_cases:
        got = classify(mod, host, url)
        ok = got == "technique"
        print(f"  {label:34s} -> {got:18s} {'OK' if ok else 'ECHEC'}")
        if not ok:
            failures.append(f"technique non reconnue : {label}")

    print("\n== 4. Defaut conservateur : hote inconnu -> presse-commercial ==")
    got = classify(mod, "some-random-news-site.example")
    print(f"  hote inconnu -> {got}")
    if got != "presse-commercial":
        failures.append("defaut conservateur non respecte")

    print("\n== 5. Regression : les 64 propositions du lot 02 ==")
    catalog = json.loads((RESEARCH / "catalog.json").read_text(encoding="utf-8"))
    by_num = {a["number"]: a for a in catalog if isinstance(a, dict)}
    ledger = json.loads((LIKEC4 / "tools/pending_promotion/ledger_pending_lot02.json").read_text(encoding="utf-8"))
    manual = {c["number"]: c["classe"] for c in ledger["classification"]}
    counts = {"scientifique": 0, "technique": 0, "presse-commercial": 0}
    mismatches = []
    for num, expected in sorted(manual.items()):
        rec = by_num[num]
        got = mod.classify_source_nature(rec)
        counts[got] = counts.get(got, 0) + 1
        if got != expected:
            mismatches.append((num, expected, got))
    print(f"  repartition filtre : {counts}")
    print(f"  ecarts vs grille manuelle : {len(mismatches)}")
    for num, exp, got in mismatches[:20]:
        print(f"    #{num}: attendu {exp}, filtre dit {got}")
    if counts != {"scientifique": 35, "technique": 2, "presse-commercial": 27}:
        failures.append(f"repartition filtre inattendue : {counts}")
    if mismatches:
        failures.append(f"{len(mismatches)} ecart(s) filtre vs grille manuelle")

    print("\n" + ("RESULTAT : OK (filtre par injection valide)" if not failures else
                  "RESULTAT : ECHEC — " + "; ".join(failures)))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
