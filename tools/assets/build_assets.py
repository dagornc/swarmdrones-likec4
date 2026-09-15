#!/usr/bin/env python3
"""
Generateur d'assets 3D — Piste B : Blender.

PROBLEME RESOLU
    Le modele LikeC4 decrit des CATEGORIES ("multirotor", "voilure fixe",
    "plateforme de surface") mais AUCUNE dimension (INV-4). La 3D, elle, a
    besoin de geometrie chiffree.

REGLE TENUE
    Ce generateur n'invente AUCUNE caracteristique du systeme. Il produit une
    forme PAR CATEGORIE declaree par le modele, et l'echelle est une simple
    CONVENTION DE SCENE (unite = 1), jamais une dimension revendiquee.
    Aucune valeur physique (metres, kilogrammes) n'est ecrite dans les assets
    ni dans les metadonnees. C'est la meme discipline que REG-2/REG-3 cote
    viewer : on ne publie pas de chiffre non prouve.

TRAcABILITE
    Chaque asset porte en metadonnee la categorie visuelle et la classe
    d'origine telles qu'elles viennent de export/scene.json. Aucun asset
    n'existe si le modele ne l'a pas declare.

Usage:
    blender --background --python tools/assets/build_assets.py
    blender --background --python tools/assets/build_assets.py -- --check
"""
import json
import sys
from pathlib import Path

import bpy  # fourni par Blender

ROOT = Path(__file__).resolve().parents[2]
SCENE = ROOT / "export" / "scene.json"
OUTDIR = ROOT / "assets" / "glb"
MANIFEST = ROOT / "assets" / "assets.json"

# --- Formes : construction geometrique par categorie visuelle.
# L'echelle est arbitraire et non revendiquee : "1" n'est pas "1 metre".
# On ne code QUE la topologie (combien de corps, quelle disposition),
# jamais une dimension presentee comme celle du vrai systeme.


def clear():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def mat(name, rgb, rough=0.45, metal=0.3):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    return m


def obj_from_mesh(name, verts, faces, material, col=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate()
    o = bpy.data.objects.new(name, me)
    o.data.materials.append(material)
    if col:
        o.color = (*col, 1.0)
    bpy.context.collection.objects.link(o)
    return o


def box(name, material, sx, sy, sz, loc=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = (sx, sy, sz)
    o.data.materials.append(material)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return o


def cyl(name, material, r, h, loc=(0, 0, 0), rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    o.data.materials.append(material)
    return o


def sphere(name, material, r, loc=(0, 0, 0)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.data.materials.append(material)
    return o


# --- une fonction par categorie visuelle DECLAREE PAR LE MODELE ---------------

def build_fixed_wing():
    """UAV-R : 18 exemplaires. Corps allonge + ailes etroites (voilure fixe)."""
    m = mat("fixed-wing", (0.29, 0.64, 1.0), rough=0.40, metal=0.35)
    parts = []
    parts.append(box("fuselage", m, 0.30, 2.60, 0.24))          # corps
    parts.append(box("wing", m, 4.20, 0.55, 0.10))              # voilure
    parts.append(box("tailplane", m, 1.10, 0.35, 0.08, loc=(0, -1.15, 0.06)))
    parts.append(box("fin", m, 0.08, 0.42, 0.52, loc=(0, -1.15, 0.20)))
    return parts


def build_multirotor():
    """UAV-F : 8 exemplaires. Vol stationnaire, manoeuvre fine (multirotor)."""
    m = mat("multirotor", (0.29, 0.83, 0.78), rough=0.45, metal=0.25)
    parts = []
    parts.append(box("fuselage", m, 0.70, 0.70, 0.22))
    for i, (dx, dy) in enumerate([(0.62, 0.62), (-0.62, 0.62), (0.62, -0.62), (-0.62, -0.62)]):
        parts.append(box(f"arm{i}", m, 0.62, 0.10, 0.07, loc=(dx * 0.5, dy * 0.5, 0.0)))
        parts.append(cyl(f"rotor{i}", m, 0.30, 0.04, loc=(dx, dy, 0.10)))
    return parts


def build_surface_vessel():
    """USV : 4 exemplaires. Plateforme de surface maritime."""
    m = mat("surface-vessel", (0.18, 0.83, 0.78), rough=0.35, metal=0.25)
    parts = []
    parts.append(box("hull", m, 1.30, 3.40, 0.42))
    parts.append(box("bow", m, 0.90, 0.90, 0.34, loc=(0, 1.75, 0.02)))
    parts.append(box("cabin", m, 0.80, 0.90, 0.55, loc=(0, -0.35, 0.45)))
    parts.append(cyl("mast", m, 0.05, 1.10, loc=(0, -0.60, 1.00)))
    return parts


def build_reference_mockup():
    """Maquette de reference : 1 seul. DOIT etre visuellement distincte (REG-5).

    On la rend volontairement ABSTRAITE : structure filaire cubique violette,
    non confondable avec une plateforme operationnelle.
    """
    m = mat("reference-mockup", (0.71, 0.48, 1.0), rough=0.30, metal=0.50)
    parts = [box("mockup_core", m, 2.20, 2.20, 2.20)]
    # montants d'angle : marqueur visuel d'abstraction
    for dx in (-1, 1):
        for dy in (-1, 1):
            parts.append(box(f"strut_{dx}_{dy}", m, 0.10, 0.10, 2.60,
                             loc=(dx * 1.05, dy * 1.05, 0)))
    return parts


def build_ground_station():
    """Poste C2 : 1. Infrastructure sol."""
    m = mat("ground-station", (1.0, 0.69, 0.13), rough=0.60, metal=0.15)
    parts = []
    parts.append(box("shelter", m, 1.60, 1.00, 0.70, loc=(0, 0, 0.35)))
    parts.append(cyl("antenna", m, 0.08, 1.60, loc=(0, 0, 1.30)))
    parts.append(cyl("dish", m, 0.55, 0.06, loc=(0, 0, 2.00), rot=(0.5, 0, 0)))
    return parts


def build_edge_node():
    """Noeud Edge : 1. Coordination et fusion."""
    m = mat("edge-node", (1.0, 0.69, 0.13), rough=0.50, metal=0.30)
    parts = []
    parts.append(box("rack", m, 0.60, 0.60, 1.50))
    parts.append(cyl("link", m, 0.06, 0.90, loc=(0, 0, 1.10)))
    return parts


def build_digital_twin():
    """Jumeau numerique : 1. Reflet, consommateur d'observation."""
    m = mat("digital-twin", (1.0, 0.69, 0.13), rough=0.35, metal=0.45)
    parts = []
    parts.append(box("core", m, 0.90, 0.90, 0.90))
    parts.append(sphere("halo", m, 1.05))
    return parts


BUILDERS = {
    "fixed-wing": build_fixed_wing,
    "multirotor": build_multirotor,
    "surface-vessel": build_surface_vessel,
    "reference-mockup": build_reference_mockup,
    "ground-station": build_ground_station,
    "edge-node": build_edge_node,
    "digital-twin": build_digital_twin,
}


def provenance(scene):
    """Associe chaque categorie visuelle a sa classe d'origine dans le modele."""
    prov = {}
    for inst in scene["instances"]:
        cat = inst.get("visual_category")
        if not cat:
            continue
        d = prov.setdefault(cat, {"class_ids": set(), "nature": set(),
                                  "population": 0, "zone": set()})
        d["class_ids"].add(inst["class_id"])
        d["nature"].add(inst.get("nature"))
        d["zone"].add(inst.get("zone"))
        d["population"] += 1
    return prov


def build_all():
    scene = json.loads(SCENE.read_text())
    prov = provenance(scene)

    declared = set(prov)
    handled = set(BUILDERS)
    missing = declared - handled
    extra = handled - declared
    if missing:
        print(f"FAIL: categories declarees sans generateur : {sorted(missing)}")
        return None, 1
    if extra:
        # un generateur pour une categorie que le modele ne declare plus :
        # on le signale (le modele est la source de verite).
        print(f"AVERTISSEMENT: generateurs sans categorie declaree : {sorted(extra)}")

    OUTDIR.mkdir(parents=True, exist_ok=True)
    assets = []
    for cat in sorted(declared):
        clear()
        parts = BUILDERS[cat]()
        # metadonnees de tracabilite sur chaque objet de l'asset
        info = prov[cat]
        for p in parts:
            p["source_category"] = cat
            p["source_class"] = sorted(info["class_ids"])[0]

        bpy.ops.object.select_all(action="SELECT")
        out = OUTDIR / f"{cat}.glb"
        bpy.ops.export_scene.gltf(
            filepath=str(out), export_format="GLB",
            use_selection=True, export_apply=True,
            # export_extras : sans cette option, les proprietes personnalisees
            # (source_category, source_class) ne sont PAS ecrites dans le GLB.
            # L'asset deviendrait intraçable : impossible de remonter au modele.
            export_extras=True,
        )
        assets.append({
            "category": cat,
            "file": f"assets/glb/{cat}.glb",
            "source_class_ids": sorted(info["class_ids"]),
            "nature": sorted(x for x in info["nature"] if x),
            "zone": sorted(x for x in info["zone"] if x),
            "instances_in_model": info["population"],
            "parts": [p.name for p in parts],
            "scale_convention": "unite de scene arbitraire — AUCUNE dimension physique revendiquee",
        })

    manifest = {
        "$schema": "swarm3d-assets/v1",
        "generated_from": "export/scene.json (categories visuelles declarees par le modele)",
        "note": "Aucune dimension physique n'est inventee : seule la topologie "
                "par categorie est decrite. Les assets sont des CONVENTIONS "
                "VISUELLES, pas des specifications.",
        "assets": assets,
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"OK — {len(assets)} assets produits")
    for a in assets:
        print(f"  {a['category']:18s} <- {','.join(a['source_class_ids'])}  ({a['instances_in_model']} instances)")
    return manifest, 0


def check():
    if not MANIFEST.exists():
        print("FAIL: assets/assets.json absent — lancer la generation")
        return 1
    man = json.loads(MANIFEST.read_text())
    scene = json.loads(SCENE.read_text())
    ok = True

    declared = {i["visual_category"] for i in scene["instances"] if i.get("visual_category")}
    produced = {a["category"] for a in man["assets"]}
    if declared != produced:
        print(f"FAIL: ecart modele/assets — manquants={sorted(declared-produced)} "
              f"en_trop={sorted(produced-declared)}")
        ok = False

    for a in man["assets"]:
        f = ROOT / a["file"]
        if not f.exists():
            print(f"FAIL: fichier absent {a['file']}")
            ok = False
            continue
        if f.stat().st_size < 200:
            print(f"FAIL: fichier suspicieusement petit {a['file']} ({f.stat().st_size} o)")
            ok = False
            continue
        # tracabilite REELLEMENT embarquee dans le binaire, pas seulement
        # declaree dans le manifeste : un asset intraçable ne peut pas etre
        # rattache au modele, donc il ne vaut rien.
        blob = f.read_bytes()
        if a["category"].encode() not in blob:
            print(f"FAIL: {a['file']} ne porte pas sa categorie d'origine (tracabilite absente)")
            ok = False

    # aucun chiffre presentant une dimension physique : on refuse qu'un asset
    # publie une caracteristique non prouvee (meme discipline que REG-2/REG-3).
    blob = json.dumps(man, ensure_ascii=False).lower()
    for banned in [" met", "meter", "kilogram", " kg", " cm", " mm", "watt", "wh"]:
        if banned in blob:
            print(f"FAIL: le manifeste contient une unite physique interdite : '{banned.strip()}'")
            ok = False

    print(f"{'OK' if ok else 'FAIL'} — {len(man['assets'])} assets, "
          f"categories alignees sur le modele ({len(declared)}), "
          f"tracabilite embarquee, aucune dimension physique revendiquee")
    return 0 if ok else 1


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--check" in argv:
        code = check()
        print(f"__EXIT__{code}")
        return
    _, code = build_all()
    print(f"__EXIT__{code}")


if __name__ == "__main__":
    main()
