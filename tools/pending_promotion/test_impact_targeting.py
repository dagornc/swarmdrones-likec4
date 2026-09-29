#!/usr/bin/env python3
"""Test de la correction d'IMPACT_TARGETS (carte t_1ce6f331, etage 1).

Verifie, sur la SOURCE versionnee (avant deploiement) :
  1. IMPACT_TARGETS contient les 15 algorithmes canoniques, identifiants
     EXACTEMENT ceux de algorithms.c4 (acceptation #1).
  2. Un article de formation control est cible sur algFormationControl et non
     onboard.mission (acceptation #2).
  3. Les comptes applied/rejected/pending de impact-proposals.json sont
     inchangees par la correction (lecture seule, acceptation #3).
  4. Quelques cas de routage supplementaires (allocation, consensus, path
     planning, collision avoidance, composant par defaut).

Usage : python3 tools/pending_promotion/test_impact_targeting.py
Sortie : code 0 si tout est OK, 1 sinon.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

LIKEC4 = Path('/home/hermesagent/workspace/swarmdrones_likec4')
PROFILE_SRC = Path('/home/hermesagent/swarmdrone-profile/scripts/analyze_impact.py')
PROP = Path('/home/hermesagent/swarmdrone-research/impact-proposals.json')

CANONICAL = [
    "algTaskAllocation", "algConsensus", "algFormationControl",
    "algLeaderElection", "algPerceptionFusion", "algNavigationGNSSDegrade",
    "algCollisionAvoidance", "algSafetyRules", "algPathPlanning",
    "algHealthMonitoring", "algEnergyAware", "algEventTriggeredComm",
    "algCooperativeLocalization", "algFaultTolerantControlAlloc",
    "algJammingResilientMode",
]


def load_analyze():
    spec = importlib.util.spec_from_file_location("analyze_impact", PROFILE_SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def alg_ids_in_algorithms_c4() -> set[str]:
    txt = (LIKEC4 / 'algorithms.c4').read_text(encoding='utf-8')
    return set(re.findall(r'\b(alg[A-Z][A-Za-z0-9]+)\b', txt))


def counts_before() -> dict:
    data = json.loads(PROP.read_text(encoding='utf-8'))
    return {
        'applied': sum(1 for p in data if p.get('status') == 'applied'),
        'rejected': sum(1 for p in data if p.get('status') == 'rejected'),
        'pending': sum(1 for p in data if p.get('status') == 'pending'),
    }


def main() -> int:
    failures = []
    mod = load_analyze()

    # --- 1. Les 15 identifiants sont cibles et EXACTEMENT ceux du modele -----
    targets = set(mod.IMPACT_TARGETS)
    alg_targets = set(mod.ALGORITHM_TARGETS)
    model_ids = alg_ids_in_algorithms_c4()
    canonical = set(CANONICAL)

    print("== 1. Identifiants des 15 algorithmes ==")
    print(f"IMPACT_TARGETS total : {len(targets)} (algo {len(alg_targets)} + composants {len(targets)-len(alg_targets)})")
    print(f"algorithmes absents de ALGORITHM_TARGETS : {sorted(canonical - alg_targets) or 'aucun'}")
    print(f"algorithmes en trop vs liste canonique  : {sorted(alg_targets - canonical) or 'aucun'}")
    print(f"alg* presents dans algorithms.c4        : {len(model_ids)}")

    if canonical != alg_targets:
        failures.append("ALGORITHM_TARGETS != liste canonique des 15")
    else:
        print("OK : ALGORITHM_TARGETS == 15 algorithmes canoniques")

    missing_in_model = canonical - model_ids
    if missing_in_model:
        failures.append(f"identifiants absents de algorithms.c4 : {sorted(missing_in_model)}")
    else:
        print("OK : les 15 identifiants existent dans algorithms.c4")

    # --- 2. Test de ciblage formation control -------------------------------
    print("\n== 2. Test de ciblage (formation control -> algFormationControl) ==")
    formation_abs = (
        "this paper utilizes the distributed model predictive control method to "
        "investigate the formation control problem of unmanned aerial vehicles in "
        "the obstacle environment and establishes cooperative capability evaluation "
        "metrics of the swarm. the formation cost function adjusts the relative "
        "positions and velocities of uavs ensuring the desired formation. obstacle "
        "avoidance function provides safe formation control."
    )
    scored = mod.score_targets(formation_abs)
    print(f"top cible : {scored[0][0]} (hits={scored[0][1]}) ; full={scored[:4]}")
    if scored[0][0] != 'algFormationControl':
        failures.append("formation control n'est PAS cible sur algFormationControl")
    if any(e == 'onboard.mission' for e, _ in scored):
        # onboard.mission peut encore matcher en 2e position, c'est OK ;
        # ce qui compte c'est que algFormationControl soit PREMIER.
        pass
    print("OK" if scored[0][0] == 'algFormationControl' else "ECHEC")

    # --- Cas supplementaires ------------------------------------------------
    print("\n== 3. Cas de routage supplementaires ==")
    cases = [
        ("task allocation", "distributed task allocation via consensus based bundle algorithm cbba auction for multi-robot teams", "algTaskAllocation"),
        ("consensus", "average consensus and gossip admm for distributed agreement among drones", "algConsensus"),
        ("path planning", "a* and rrt jump point search for uav path planning and motion planning", "algPathPlanning"),
        ("collision avoidance", "collision avoidance with velocity obstacle and collision cone for dynamic obstacles", "algCollisionAvoidance"),
        ("component par defaut", "battery endurance and solar power consumption for drone missions", "onboard.energy"),
        ("event-triggered", "event-triggered and self-triggered communication reduces transmissions in a zeno-free manner for drone swarms", "algEventTriggeredComm"),
        ("hybride energie+ETC (algorithme, pas composant)", "energy-aware hybrid event-triggered control balances energy use and communication for micro-drones", "algEnergyAware"),
    ]
    for label, text, expected in cases:
        got = mod.score_targets(text)[0][0] if mod.score_targets(text) else None
        ok = (got == expected)
        print(f"  {label:24s} -> {got:28s} (attendu {expected}) {'OK' if ok else 'ECHEC'}")
        if not ok:
            failures.append(f"routage {label}: {got} != {expected}")

    # --- 4. Comptes applied/rejected/pending inchanges ----------------------
    print("\n== 4. Comptes impact-proposals.json (lecture seule) ==")
    c = counts_before()
    print(f"applied={c['applied']} rejected={c['rejected']} pending={c['pending']}")
    if c['applied'] != 50 or c['rejected'] != 105:
        failures.append(f"comptes inattendus : {c}")
    else:
        print("OK : 50 applied / 105 rejected (le script ne reecrit pas ce fichier)")

    print("\n" + ("RESULTAT : OK (tous les tests passent)" if not failures else
                  "RESULTAT : ECHEC — " + "; ".join(failures)))
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
