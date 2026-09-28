#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPEC-13-LIKE (t_06cd10ec) — generateur de liaison LikeC4.

Relie, de facon purement ADDITIVE, les artefacts des 3 taches soeurs :
  - SPEC-13-PUBLISH (t_79a5637b + complement e137723) : 13 PDF v1 dans
    specification/ (7 valides + 6 REJETES publies malgre rejet) ;
  - SYSML-15 (t_d671a500) : 15 .sysml (deja lies dans sysml.c4) ;
  - RUST-13 (t_8ed8aa02) : 13 portages Rust dagornc/alg-<slug>.

Sortie : section G ajoutee a algorithms.c4 (13 specDoc PDF + 13 sourceCode
+ relations). Les relations vers les .sysml NE SONT PAS re-creees (deja dans
sysml.c4).

HONNETETE : les 6 PDF REJETES par leur rapport de validation (2-6/20,
defauts BLOQUANTS) ont ete pousses sur le depot par le commit e137723
« 6 specifications complementaires publiees », CONTRE la decision
d'exclusion de SPEC-13-PUBLISH (t_79a5637b). Le lien est reel (le PDF
existe), mais la carte specDoc porte statut 'REJETEE (publiee malgre rejet)'
et le rapport de validation associe. Aucun rejet n'est masque.
"""

import io
import os
import sys

REPO = os.path.dirname(os.path.abspath(__file__))
ALG_C4 = os.path.join(REPO, "algorithms.c4")

PDF_BASE = "https://github.com/dagornc/swarmdrones-likec4/blob/master/specification"
SYSML_BASE = "https://github.com/dagornc/swarmdrones-likec4/blob/master/sysml"
GH_MAIN = "https://github.com/dagornc/SwarmDrones"

# ---------------------------------------------------------------------------
# Les 13 algorithmes manquants : un enregistrement par algorithme, portant
# a la fois la spec PDF (specDoc) et le portage Rust (sourceCode).
# `statut_spec` : PUBLIE (valide) ou REJETEE (publiee malgre rejet).
# ---------------------------------------------------------------------------
ALGOS = [
    {
        "alg_id": "ALG_FORMATION_CONTROL", "alg": "algFormationControl",
        "elem": "specFormationControl", "src": "srcFormationControl",
        "title": "Controle de formation", "slug": "alg-formation-control",
        "crate": "formation_control_rs",
        "tests": "10/10 (5 unitaires + 5 integration)",
        "parite": "bit-a-bit Rust/Python — 200/200 comparaisons, 0 ecart (50 graines x 4 scenarios)",
        "limites": "modele cinematique 2D sans dynamique de vol ; algorithme source idea/conceptual (evidenceLevel NONE) — implementation de reference simplifiee, pas de validation operationnelle",
        "statut_spec": "PUBLIE",
        "validation": "PUBLIEE — conforme (SPEC-13-PUBLISH, t_79a5637b)",
    },
    {
        "alg_id": "ALG_LEADER_ELECTION", "alg": "algLeaderElection",
        "elem": "specLeaderElection", "src": "srcLeaderElection",
        "title": "Election de leader", "slug": "alg-leader-election",
        "crate": "leader_election_rs",
        "tests": "9/9 (4 unitaires RNG + 5 integration)",
        "parite": "bit-a-bit — 300/300 comparaisons, 0 ecart (50 graines x 6 scenarios)",
        "limites": "reference simplifiee : aucune preuve de surete/vivacite asynchrone, detecteur de perte suppose fiable, une partition peut produire plusieurs leaders (expose par la metrique double_leader)",
        "statut_spec": "REJETEE",
        "validation": "REJETEE — 5/20, 3 defauts BLOQUANTS (validation_leader_election_v1.md) ; publiee malgre rejet par le commit e137723",
    },
    {
        "alg_id": "ALG_PERCEPTION_FUSION", "alg": "algPerceptionFusion",
        "elem": "specPerceptionFusion", "src": "srcPerceptionFusion",
        "title": "Fusion multi-capteurs (EKF/UKF)", "slug": "alg-perception-fusion",
        "crate": "perception_fusion_rs",
        "tests": "12/12 (6 unitaires + 6 integration)",
        "parite": "bit-a-bit — 200 comparaisons, 0 ecart (50 graines x 4 scenarios x 80 pas)",
        "limites": "EKF reduit (equivaut a un filtre de Kalman) ; pas d UKF/filtre particulaire/attitude 3D ; GAP-4 ouvert (fusion hierarchique a 100+ plateformes)",
        "statut_spec": "PUBLIE",
        "validation": "PUBLIEE — conforme (SPEC-13-PUBLISH, t_79a5637b)",
    },
    {
        "alg_id": "ALG_NAV_GNSS_DEGRADE", "alg": "algNavigationGNSSDegrade",
        "elem": "specNavigationGNSSDegrade", "src": "srcNavigationGNSSDegrade",
        "title": "Navigation sous GNSS degrade", "slug": "alg-nav-gnss-degrade",
        "crate": "nav_gnss_degrade_rs",
        "tests": "13/13",
        "parite": "bit-a-bit — 250 comparaisons, 0 ecart (50 graines x 5 scenarios)",
        "limites": "pas de matrices de covariance, d attitude 3D ni de biais estimes ; CSV arrondi a 9 decimales ; pas de commande physique de retour (RTL)",
        "statut_spec": "PUBLIE",
        "validation": "PUBLIEE — conforme (SPEC-13-PUBLISH, t_79a5637b)",
    },
    {
        "alg_id": "ALG_COLLISION_AVOIDANCE", "alg": "algCollisionAvoidance",
        "elem": "specCollisionAvoidance", "src": "srcCollisionAvoidance",
        "title": "Evitement de collision (CBF)", "slug": "alg-collision-avoidance",
        "crate": "collision_avoidance_rs",
        "tests": "10/10 (4 unitaires RNG + 6 integration/invariants)",
        "parite": "bit-a-bit — 150/150 comparaisons, 0 ecart (50 graines x 3 scenarios)",
        "limites": "pas de dynamique quadrirotor, de retard, d incertitude ni d obstacles statiques ; projections sequentielles (pas de QP CBF global) ; absence de collision verifiee sur 50 graines nominales seulement",
        "statut_spec": "PUBLIE",
        "validation": "PUBLIEE — conforme (SPEC-13-PUBLISH, t_79a5637b)",
    },
    {
        "alg_id": "ALG_SAFETY_RULES", "alg": "algSafetyRules",
        "elem": "specSafetyRules", "src": "srcSafetyRules",
        "title": "Surete par regles pre-approuvees", "slug": "alg-safety-rules",
        "crate": "safety_rules_rs",
        "tests": "13/13 (4 unitaires RNG + 9 integration)",
        "parite": "bit-a-bit — 900 comparaisons, 0 ecart (100 graines x 9 scenarios)",
        "limites": "validation Monte-Carlo adversarial N>=1000 NON faite ; pas d essai HIL/SIL ; garde CBF scalaire conservatrice (pas de QP complet) ; colonne fausse_alerte a 0 (meme verite terrain que les seuils)",
        "statut_spec": "REJETEE",
        "validation": "REJETEE — 5/20, 2 defauts BLOQUANTS (validation_safety_rules_v1.md) ; publiee malgre rejet par le commit e137723",
    },
    {
        "alg_id": "ALG_PATH_PLANNING", "alg": "algPathPlanning",
        "elem": "specPathPlanning", "src": "srcPathPlanning",
        "title": "Planification de trajectoire (waypoints + MPC)", "slug": "alg-path-planning",
        "crate": "path_planning_rs",
        "tests": "13/13 Rust + 3/3 reference Python",
        "parite": "bit-a-bit — 250 comparaisons, 0 ecart (50 graines x 5 scenarios)",
        "limites": "variante A* grille 4-connexe uniquement ; pas de MPC/RRT*/CBS ni de dynamique continue ; temps de calcul mesure par proxy (noeuds developpes)",
        "statut_spec": "PUBLIE",
        "validation": "PUBLIEE — conforme (SPEC-13-PUBLISH, t_79a5637b)",
    },
    {
        "alg_id": "ALG_HEALTH_MONITORING", "alg": "algHealthMonitoring",
        "elem": "specHealthMonitoring", "src": "srcHealthMonitoring",
        "title": "Surveillance d etat et detection de faute", "slug": "alg-health-monitoring",
        "crate": "health_monitoring_rs",
        "tests": "13/13 (6 unitaires + 7 integration)",
        "parite": "bit-a-bit — 250 comparaisons, 0 ecart (50 graines x 5 scenarios)",
        "limites": "modele de reference simplifie, non calibre sur journaux de vol ni capteur reel ; faux negatifs non caracterises ; statut experimental (non validated)",
        "statut_spec": "REJETEE",
        "validation": "REJETEE — 4/20, 3 defauts BLOQUANTS (validation_health_monitoring_v1.md) ; publiee malgre rejet par le commit e137723",
    },
    {
        "alg_id": "ALG_ENERGY_AWARE", "alg": "algEnergyAware",
        "elem": "specEnergyAware", "src": "srcEnergyAware",
        "title": "Planification sensible a l energie", "slug": "alg-energy-aware",
        "crate": "energy_aware_rs",
        "tests": "7/7 (4 RNG + 3 integration/CLI)",
        "parite": "bit-a-bit — 300/300 comparaisons, 0 ecart (50 graines x 6 scenarios)",
        "limites": "cout energetique lineaire non calibre sur vehicule reel ; pas d aerodynamique/vent/vieillissement batterie ; pas d optimisation combinatoire multi-taches",
        "statut_spec": "REJETEE",
        "validation": "REJETEE — 4/20, 2 defauts BLOQUANTS (validation_energy_aware_v1.md) ; publiee malgre rejet par le commit e137723",
    },
    {
        "alg_id": "ALG_EVENT_TRIGGERED_COMM", "alg": "algEventTriggeredComm",
        "elem": "specEventTriggeredComm", "src": "srcEventTriggeredComm",
        "title": "Communication declenchee par evenement", "slug": "alg-event-triggered-comm",
        "crate": "event_triggered_comm_rs",
        "tests": "13/13 (4 RNG + 2 CLI + 7 integration)",
        "parite": "bit-a-bit — 200/200, 0 ecart (50 graines x 4 scenarios)",
        "limites": "implementation conceptuelle : pas de radio/SITL/HITL ; zones scalaires (pas 2D/3D) ; latence = modele discret de service, pas un modem reel",
        "statut_spec": "REJETEE",
        "validation": "REJETEE — 3/20, 3 defauts BLOQUANTS (validation_event_triggered_comm_v1.md) ; publiee malgre rejet par le commit e137723",
    },
    {
        "alg_id": "ALG_COOPERATIVE_LOCALIZATION", "alg": "algCooperativeLocalization",
        "elem": "specCooperativeLocalization", "src": "srcCooperativeLocalization",
        "title": "Localisation cooperative inter-agents", "slug": "alg-cooperative-localization",
        "crate": "cooperative_localization_rs",
        "tests": "15/15",
        "parite": "bit-a-bit — 200 comparaisons, 0 ecart (50 graines x 4 scenarios)",
        "limites": "pas de ST-DCL complet ni d EKF/UKF distribue ; repere commun suppose (ambiguite TOF/TDOA non modelisee) ; graphe deterministe de 8 agents ; GAP-6 ouvert",
        "statut_spec": "PUBLIE",
        "validation": "PUBLIEE — conforme (SPEC-13-PUBLISH, t_79a5637b)",
    },
    {
        "alg_id": "ALG_FAULT_TOLERANT_CONTROL_ALLOC", "alg": "algFaultTolerantControlAlloc",
        "elem": "specFaultTolerantControlAlloc", "src": "srcFaultTolerantControlAlloc",
        "title": "Allocation de commande tolerante aux fautes", "slug": "alg-fault-tolerant-control-alloc",
        "crate": "fault_tolerant_control_alloc_rs",
        "tests": "12/12 (4 RNG + 8 integration) + clippy -D warnings OK",
        "parite": "bit-a-bit — 250/250, 0 ecart (5 scenarios x 50 graines)",
        "limites": "variante pseudo-inverse ponderee + projection de saturation ; pas d allocation hybride ni saturation azimuth ; pas de HITL ; la faute est supposee detectee en amont (ALG_HEALTH_MONITORING)",
        "statut_spec": "PUBLIE",
        "validation": "PUBLIEE — conforme (SPEC-13-PUBLISH, t_79a5637b)",
    },
    {
        "alg_id": "ALG_JAMMING_RESILIENT_MODE", "alg": "algJammingResilientMode",
        "elem": "specJammingResilientMode", "src": "srcJammingResilientMode",
        "title": "Mode double cooperatif/autonome sous brouillage", "slug": "alg-jamming-resilient-mode",
        "crate": "jamming_resilient_mode_rs",
        "tests": "14/14",
        "parite": "bit-a-bit — 250/250, 0 ecart (50 graines x 5 scenarios)",
        "limites": "modele conceptuel discret de supervision : pas de RF, reseau, dynamique de vol ni HOCBF ; profils de brouillage synthetiques ; GAP-5 ouvert ; pas d attestation TPM",
        "statut_spec": "REJETEE",
        "validation": "REJETEE — 6/20, 3 defauts BLOQUANTS (validation_jamming_resilient_mode_v1.md) ; publiee malgre rejet par le commit e137723",
    },
]


def specdoc_block(a):
    pdf_url = "{}/Spec_{}_v1.pdf".format(PDF_BASE, a["alg_id"])
    sysml_url = "{}/{}.sysml".format(SYSML_BASE, a["alg_id"])
    if a["statut_spec"] == "REJETEE":
        title = "Specification detaillee — {} (v1 — REJETEE par validation)".format(a["alg_id"])
        statut = "REJETEE (publiee malgre rejet)"
    else:
        title = "Specification detaillee — {} (v1)".format(a["alg_id"])
        statut = "PUBLIE"
    return """  {elem} = specDoc '{title}' {{
    #source-doc
    link {pdf_url} "Specification detaillee {t} v1 (PDF) — depot PRIVE dagornc/swarmdrones-likec4 (specification/)"
    link {sysml_url} "Specification SysML v2 ({alg_id}.sysml) — relation documentedBy portee par sysml.c4"
    description 'Document de specification detaillee de l algorithme {alg_id} ({t}), version v1, dans le depot PRIVE dagornc/swarmdrones-likec4 (specification/). Validation : {val}. La specification SysML v2 associee vit dans sysml/{alg_id}.sysml et est referencee par l element specDoc sysml* de sysml.c4 (relation documentedBy deja presente — non dupliquee ici).'
    metadata {{
      algorithme '{alg_id}'
      versions '1 (v1)'
      versionCourante 'v1 (2026-09-28)'
      nature 'specification genie logiciel interne'
      statut '{statut}'
      validation '{val}'
      sysml 'sysml/{alg_id}.sysml — porte par sysml.c4'
    }}
  }}
""".format(elem=a["elem"], title=title, alg_id=a["alg_id"], t=a["title"],
           pdf_url=pdf_url, sysml_url=sysml_url, val=a["validation"], statut=statut)


def sourcecode_block(a):
    if a["statut_spec"] == "REJETEE":
        specpdf = "Spec_{}_v1.pdf — REJETEE par validation (cf specDoc {}) ; publiee malgre rejet".format(
            a["alg_id"], a["elem"])
    else:
        specpdf = "Spec_{}_v1.pdf (PUBLIE)".format(a["alg_id"])
    desc = ("Portage Rust de l algorithme {} (crate/binaire {}). Le code vit dans le "
            "depot public https://github.com/dagornc/{}, reference depuis le depot principal "
            "https://github.com/dagornc/SwarmDrones. Parite bit-a-bit verifiee avec la reference "
            "Python normative reference/sim_{}.py (socle RUST-13, RNG MT19937 compatible CPython). "
            "Ce depot est une IMPLEMENTATION DE REFERENCE SIMPLIFIEE : la parite Rust/Python prouve "
            "que les deux simulateurs calculent la meme chose, elle ne valide pas scientifiquement "
            "l algorithme, sa stabilite formelle ni son aptitude au vol reel. Structure : "
            "Cargo.toml, src/{{rng,sim,lib,main}}.rs, tests/parite.rs, reference/*.py, "
            "verify_parite_rust.py, LICENSE (MIT).").format(
            a["alg_id"], a["crate"], a["slug"], a["slug"].replace("alg-", "").replace("-", "_"))
    lines = [
        "  {} = sourceCode '{} — portage Rust de {}' {{".format(a["src"], a["slug"], a["alg_id"]),
        "    #source-code",
        "    link https://github.com/dagornc/{} \"Depot GitHub {} — code source du portage Rust ({})\"".format(
            a["slug"], a["slug"], a["crate"]),
        "    link {} \"Depot principal SwarmDrones — agregateur de la solution A\"".format(GH_MAIN),
        "    description '{}'".format(desc),
        "    metadata {",
    ]
    meta = [
        ("algorithme", a["alg_id"]),
        ("langage", "Rust (edition 2024, zero dependance externe)"),
        ("depot", "https://github.com/dagornc/{}".format(a["slug"])),
        ("depotPrincipal", "https://github.com/dagornc/SwarmDrones"),
        ("integration", "depot dedie public autonome — NON rattache en submodule de SwarmDrones (constate 2026-09-28)"),
        ("parite", a["parite"]),
        ("tests", a["tests"]),
        ("limites", a["limites"]),
        ("licence", "MIT — Copyright (c) 2026 Christophe Dagorn"),
        ("nature", "portage de reference (implementation simplifiee)"),
        ("statut", "PUBLIE"),
        ("specPdf", specpdf),
    ]
    for k, v in meta:
        lines.append("      {} '{}'".format(k, v))
    lines.append("    }")
    lines.append("  }")
    return "\n".join(lines)


def main():
    with io.open(ALG_C4, "r", encoding="utf-8") as fh:
        text = fh.read()

    if "specFormationControl = specDoc" in text:
        print("SKIP: section SPEC-13-LIKE deja presente dans algorithms.c4", file=sys.stderr)
        return 0

    out = []
    out.append("  // ===========================================================================")
    out.append("  //  G. SPEC-13-LIKE (carte t_06cd10ec) — LIAISON DES ARTEFACTS SOEURS")
    out.append("  //")
    out.append("  //  Specs PDF : 13 PDF v1 dans specification/ (SPEC-13-PUBLISH t_79a5637b +")
    out.append("  //    complement e137723). 7 VALIDEES ; 6 REJETEES par leur rapport de")
    out.append("  //    validation (2-6/20, defauts BLOQUANTS) mais poussees quand meme par le")
    out.append("  //    commit e137723, CONTRE l exclusion decidee par SPEC-13-PUBLISH.")
    out.append("  //    Le lien est reel, la carte specDoc porte le statut REJETEE : aucun")
    out.append("  //    rejet n est masque (cf specDoc.*.validation).")
    out.append("  //")
    out.append("  //  SysML v2 (SYSML-15, t_d671a500) : relations algX -[documentedBy]-> sysmlX")
    out.append("  //    deja portees par sysml.c4 — NON dupliquees ici (cf note parente).")
    out.append("  //")
    out.append("  //  Portages Rust (RUST-13, t_8ed8aa02) : 13 depots publics dagornc/alg-<slug>.")
    out.append("  //    Metadonnees (parite/tests/limites) lues dans les README reels des depots,")
    out.append("  //    verifiees le 2026-09-28. Aucune valeur inventee.")
    out.append("  // ===========================================================================")
    out.append("")
    for a in ALGOS:
        out.append(specdoc_block(a))
    out.append("")
    for a in ALGOS:
        out.append(sourcecode_block(a))
    out.append("")
    out.append("  // --- Relations SPEC-13-LIKE ---")
    out.append("  // algorithm -[documentedBy]-> specDoc PDF (13) ;")
    out.append("  // sourceCode -[implements]-> algorithm (13) ;")
    out.append("  // sourceCode -[documentedBy]-> specDoc PDF (13).")
    out.append("")
    for a in ALGOS:
        out.append("  {} -[documentedBy]-> {} 'specification detaillee v1 (PDF)'".format(
            a["alg"], a["elem"]))
    out.append("")
    for a in ALGOS:
        out.append("  {} -[implements]-> {} 'portage Rust (parite bit-a-bit)'".format(
            a["src"], a["alg"]))
    out.append("")
    for a in ALGOS:
        out.append("  {} -[documentedBy]-> {} 'specification detaillee v1 (PDF)'".format(
            a["src"], a["elem"]))
    out.append("")

    section = "\n".join(out)

    stripped = text.rstrip("\n")
    if stripped.endswith("}"):
        idx = stripped.rfind("\n}")
        new_text = stripped[:idx] + "\n" + section + stripped[idx + 1:]
    else:
        new_text = stripped + "\n" + section + "\n}"

    with io.open(ALG_C4, "w", encoding="utf-8") as fh:
        fh.write(new_text + "\n")

    print("OK: section SPEC-13-LIKE (13 specDoc + 13 sourceCode) inseree dans algorithms.c4")


if __name__ == "__main__":
    main()
