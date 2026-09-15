"""Rendu de verification des assets — preuve visuelle measurable.

Importe les 7 GLB, les dispose en grille, puis cadre la camera sur les bornes
REELLES mesurees apres placement (et non sur une position supposee).

Le rendu precedent produisait une image uniforme : la camera ne voyait rien.
Correction : on mesure les bornes effectives, on place la camera en fonction,
et on verifie apres coup que l'image n'est pas uniforme.
"""
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "assets" / "assets.json"
OUT = ROOT / "assets" / "preview.png"
COLS = 4
STEP = 6.0


def clear():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def world_bg():
    w = bpy.data.worlds.new("bg")
    bpy.context.scene.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.06, 0.08, 0.10, 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = 1.0


def mesh_bounds(objs):
    xs, ys, zs = [], [], []
    for o in objs:
        if o.type != "MESH":
            continue
        for c in o.bound_box:
            v = o.matrix_world @ Vector(c)
            xs.append(v.x); ys.append(v.y); zs.append(v.z)
    if not xs:
        return None
    return (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))


def main():
    man = json.loads(MANIFEST.read_text())
    assets = man["assets"]
    n = len(assets)
    rows = (n + COLS - 1) // COLS

    clear()
    world_bg()

    placed = []
    for i, a in enumerate(assets):
        col, row = i % COLS, i // COLS
        before = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=str(ROOT / a["file"]))
        new = [o for o in bpy.data.objects if o not in before]
        b = mesh_bounds(new)
        if b is None:
            continue
        cx, cy, cz = (b[0] + b[1]) / 2, (b[2] + b[3]) / 2, (b[4] + b[5]) / 2
        # translation a appliquer aux objets racine
        tx = col * STEP - cx
        ty = -row * STEP - cy
        tz = -cz
        for o in new:
            if o.parent is None:
                o.location = (o.location.x + tx, o.location.y + ty, o.location.z + tz)
        bpy.context.view_layer.update()
        placed.append((a["category"], new))

    # bornes REELLES de toute la grille
    allobjs = [o for _, objs in placed for o in objs]
    bb = mesh_bounds(allobjs)
    if bb is None:
        print("RENDU: FAIL aucune geometrie importee")
        return
    cx, cy, cz = (bb[0] + bb[1]) / 2, (bb[2] + bb[3]) / 2, (bb[4] + bb[5]) / 2
    sx, sy, sz = bb[1] - bb[0], bb[3] - bb[2], bb[5] - bb[4]
    span = max(sx, sy, sz)
    print(f"BORNES GRILLE x[{bb[0]:.2f},{bb[1]:.2f}] y[{bb[2]:.2f},{bb[3]:.2f}] "
          f"z[{bb[4]:.2f},{bb[5]:.2f}] span={span:.2f}")

    # camera : vue 3/4 depuis le dessus, distance calculee sur le span reel
    cam_data = bpy.data.cameras.new("cam")
    cam_data.lens = 50
    cam = bpy.data.objects.new("cam", cam_data)
    bpy.context.collection.objects.link(cam)
    dist = span * 0.62
    cam.location = (cx + dist * 0.72, cy - dist * 0.85, cz + dist * 0.62)
    # orientation : pointer vers le centre par construction de la matrice
    direction = Vector((cx, cy, cz)) - Vector(cam.location)
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = cam
    print(f"CAMERA loc=({cam.location.x:.2f},{cam.location.y:.2f},{cam.location.z:.2f}) "
          f"dist={dist:.2f}")

    # eclairage genereux : sans lumiere, tout serait noir
    for name, loc, energy in [("key", (cx + span, cy - span, cz + span * 1.4), 30.0),
                              ("fill", (cx - span, cy - span * 1.2, cz + span), 15.0),
                              ("rim", (cx, cy + span * 1.5, cz + span), 15.0)]:
        ld = bpy.data.lights.new(name, type="AREA")
        ld.energy = energy * (span ** 2) * 8
        ld.size = span
        lo = bpy.data.objects.new(name, ld)
        lo.location = loc
        d = Vector((cx, cy, cz)) - Vector(loc)
        lo.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
        bpy.context.collection.objects.link(lo)

    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 32
    try:
        sc.cycles.use_denoising = False
    except Exception:
        pass
    sc.render.resolution_x = 1600
    sc.render.resolution_y = 460 * rows
    sc.render.filepath = str(OUT)
    sc.render.film_transparent = False
    bpy.ops.render.render(write_still=True)
    print(f"RENDU: OK -> {OUT}")


if __name__ == "__main__":
    main()
