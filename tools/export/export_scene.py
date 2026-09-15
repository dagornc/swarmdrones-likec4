#!/usr/bin/env python3
"""
Export vers le consommateur 3D — pont LikeC4 -> Blender / moteur Web 3D.

Ce script est la SEULE porte de sortie du modele vers la 3D. Il produit un
artefact derive, jamais une seconde source de verite.

Regle structurante (INV-4) :
    le modele semantique ne contient AUCUNE coordonnee. Ce script n'en
    invente pas non plus. Il produit une scene NON SPATIALISEE : c'est la
    couche consommateur (Blender) qui place les objets, dans SON espace.

Usage:
    python3 tools/export/export_scene.py            # ecrit export/scene.json
    python3 tools/export/export_scene.py --check    # verifie l'artefact existant
"""
import json
import subprocess
import sys
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "export" / "scene.json"
# Copie servie au viewer (fetch "scene.json" est relatif au dossier viewer/).
# Elle est produite par l'export : plus aucune copie manuelle, donc plus de
# risque de servir une scene perimee. Le SHA256 est publie dans les deux
# fichiers et verifie a chaque controle.
VIEWER_OUT = ROOT / "viewer" / "scene.json"
CONTAINER = "likec4"


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_model():
    subprocess.run(["docker", "exec", CONTAINER, "likec4", "export", "json", "/data", "-o", "/data/out/export.json"],
                   capture_output=True, text=True, check=True)
    raw = subprocess.run(["docker", "exec", CONTAINER, "cat", "/data/out/export.json"],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(raw)[0]


def build(model):
    els, rels = model["elements"], model["relations"]
    world = {k: v for k, v in els.items() if "world" in (v.get("tags") or [])}

    # --- instanciation : une entree de scene par PLATEFORME, pas par classe ---
    instances, sid = [], 0
    for k, v in els.items():
        if v["kind"] != "worldEntity":
            continue
        md = v.get("metadata") or {}
        try:
            n = int(md.get("population", 0))
        except (TypeError, ValueError):
            n = 0
        label = (v.get("title") or "").split(" — ")[0].strip()
        nature = md.get("nature")
        for i in range(n):
            sid += 1
            instances.append({
                "instance_id": f"{k}#{i + 1:02d}",
                "class_id": k,
                "label": f"{label}-{i + 1:02d}",
                "kind": "platform" if nature == "plateforme_essaim" else nature or "unknown",
                "nature": nature,
                "id_likec4": md.get("id_likec4"),
                "visual_category": md.get("categorie_visuelle"),
                "zone": md.get("domaine"),
                "scene_role": md.get("role_scene"),
                "is_reference_mockup": nature == "maquette_reference",
                "is_swarm_platform": nature == "plateforme_essaim",
                "transform": None,  # INV-4 : rempli par le consommateur
            })

    # --- zones et etats (classes, pas instances) ---
    zones = [{"id": k, "title": v.get("title")} for k, v in world.items() if v["kind"] == "zoneSemantic"]
    categories = [{"id": k, "title": v.get("title")} for k, v in world.items() if v["kind"] == "sceneCategory"]
    states = []
    for k, v in world.items():
        if v["kind"] != "worldState":
            continue
        md = v.get("metadata") or {}
        states.append({"id": k, "title": v.get("title"), "scenario": md.get("scenario"),
                       "rendering": md.get("rendu"), "limit": md.get("limite") or md.get("statut")})

    # --- garde-fous : le consommateur DOIT les appliquer ---
    rules = []
    for k, v in world.items():
        if v["kind"] != "renderRule":
            continue
        md = v.get("metadata") or {}
        rules.append({"id": k, "title": v.get("title"), "test": md.get("test"),
                      "source": md.get("source"), "verifiable": md.get("verifiable") == "oui"})

    # --- liens de derivation, pour que le consommateur trace ses propres objets ---
    links = [{"from": r["source"]["model"], "to": r["target"]["model"], "kind": r["kind"]}
             for r in rels.values()
             if r["source"]["model"] in world or r["target"]["model"] in world]

    operational = [i for i in instances if i["is_swarm_platform"]]
    scene = {
        "$schema": "swarm3d-scene/v1",
        "generated_from": "modele LikeC4 compile (14 fichiers)",
        "invariants_applied": {
            "INV-4": "aucune coordonnee dans cet artefact ; transform=null partout",
            "REG-5": "30 plateformes operationnelles + 1 maquette de reference distincte",
        },
        "counts": {
            "instances": len(instances),
            "operational_platforms": len(operational),
            "reference_mockups": sum(1 for i in instances if i["is_reference_mockup"]),
            "infrastructure": sum(1 for i in instances if i["nature"] == "infrastructure"),
            "zones": len(zones), "categories": len(categories),
            "states": len(states), "render_rules": len(rules),
        },
        "instances": instances,
        "zones": zones,
        "categories": categories,
        "states": states,
        "render_rules": rules,
        "derivation_links": links,
        "consumer_obligations": [
            "Ne jamais inventer d identifiant : tout instance_id/class_id vient d ici.",
            "Ne PAS afficher de valeur d energie (DE-07 non determinee).",
            "Ne PAS afficher de portee radio chiffree (annonces non verifiees).",
            "Toute scene a 30 doit porter la mention « N=30 NON PROUVE ».",
            "Distinguer visuellement la maquette de reference des 30 plateformes.",
            "Fournir les transform : le modele ne spatialise jamais.",
        ],
    }
    return scene


def write_artifact(scene):
    """Ecrit la scene ET sa copie servie au viewer, en une seule operation.

    Le viewer charge `scene.json` relativement a son propre dossier. Sans cette
    etape, il fallait copier le fichier a la main — source de divergence
    silencieuse : le viewer pouvait afficher et VALIDER une scene perimee alors
    que le modele avait change. Les deux copies sont donc produites ici, et
    leur empreinte est publiee pour rendre toute divergence detectable.
    """
    payload = json.dumps(scene, ensure_ascii=False, indent=1)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(payload, encoding="utf-8")
    VIEWER_OUT.parent.mkdir(exist_ok=True)
    VIEWER_OUT.write_text(payload, encoding="utf-8")

    h = _sha256(OUT)
    # fichiers compagnons : ils rendent la divergence visible sans ouvrir
    # les artefacts (et sans dependre d'un depot git, absent ici).
    (OUT.parent / "scene.sha256").write_text(h + "  export/scene.json\n", encoding="utf-8")
    (VIEWER_OUT.parent / "scene.sha256").write_text(h + "  viewer/scene.json\n", encoding="utf-8")
    return h


def check():
    if not OUT.exists():
        print("FAIL: export/scene.json absent — lancer l export")
        return 1
    s = json.loads(OUT.read_text())
    c = s["counts"]
    ok = True
    # aucune coordonnee
    bad = [i for i in s["instances"] if i.get("transform") is not None]
    if bad:
        print(f"FAIL INV-4: {len(bad)} instances portent un transform"); ok = False
    # population exacte
    if c["operational_platforms"] != 30:
        print(f"FAIL: {c['operational_platforms']} operationnels (attendu 30)"); ok = False
    if c["reference_mockups"] != 1:
        print(f"FAIL: {c['reference_mockups']} maquette (attendu 1)"); ok = False
    if c["render_rules"] < 6:
        print(f"FAIL: {c['render_rules']} regles (attendu >=6)"); ok = False
    # coherence avec la copie servie au viewer : la scene servie doit etre
    # IDENTIQUE a la scene exportee, sinon le viewer valide du perime.
    if not VIEWER_OUT.exists():
        print("FAIL: viewer/scene.json absent — copie servie au viewer manquante")
        ok = False
    elif _sha256(VIEWER_OUT) != _sha256(OUT):
        print("FAIL: viewer/scene.json DIVERGE de export/scene.json "
              "(relancer l export : python3 tools/export/export_scene.py)")
        ok = False
    print(f"{'OK' if ok else 'FAIL'} — {c['instances']} instances, "
          f"{c['operational_platforms']} operationnels + {c['reference_mockups']} maquette, "
          f"{c['zones']} zones, {c['states']} etats, {c['render_rules']} regles, "
          f"coords={sum(1 for i in s['instances'] if i.get('transform'))}")
    return 0 if ok else 1


def main():
    if "--check" in sys.argv:
        sys.exit(check())
    scene = build(load_model())
    h = write_artifact(scene)
    print(json.dumps(scene["counts"], ensure_ascii=False))
    print(f"ecrit: export/scene.json + viewer/scene.json  sha256={h[:16]}")
    sys.exit(check())


if __name__ == "__main__":
    main()
