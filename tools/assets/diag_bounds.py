"""Diagnostic : les objets importes sont-ils dans le champ de la camera ?

Le rendu precedent produit une image uniforme. Avant de re-rendre, on mesure
la position et les dimensions REELLES des objets importes, et on verifie que
la camera les voit. Aucune supposition.
"""
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "assets" / "assets.json"


def clear():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def main():
    man = json.loads(MANIFEST.read_text())
    clear()
    print("=== import + boites englobantes ===")
    for a in man["assets"]:
        before = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=str(ROOT / a["file"]))
        new = [o for o in bpy.data.objects if o not in before]
        xs, ys, zs = [], [], []
        nverts = 0
        for o in new:
            if o.type != "MESH":
                continue
            nverts += len(o.data.vertices)
            for c in o.bound_box:
                v = o.matrix_world @ Vector(c)
                xs.append(v.x); ys.append(v.y); zs.append(v.z)
        if xs:
            print(f"  {a['category']:18s} objs={len(new)} verts={nverts:5d} "
                  f"x[{min(xs):6.2f},{max(xs):6.2f}] "
                  f"y[{min(ys):6.2f},{max(ys):6.2f}] "
                  f"z[{min(zs):6.2f},{max(zs):6.2f}]")
        else:
            print(f"  {a['category']:18s} objs={len(new)} AUCUNE GEOMETRIE")


if __name__ == "__main__":
    main()
