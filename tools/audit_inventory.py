#!/usr/bin/env python3
"""
SWARM-3D-ARCHITECTURE / E00 — Inventaire automatise du modele LikeC4.
Source de verite : modele compile par LikeC4 (export json), pas le source .c4.
Sortie : docs/audit-inventory.json (machine) + resume console.
"""
import json, subprocess, collections, sys, os, datetime

JSON_IN_CONTAINER = "/data/out/audit.json"

def load():
    raw = subprocess.run(["docker", "exec", "likec4", "cat", JSON_IN_CONTAINER],
                         capture_output=True, text=True)
    if raw.returncode != 0:
        print("ERREUR docker exec:", raw.stderr[:500]); sys.exit(1)
    d = json.loads(raw.stdout)
    if isinstance(d, list):
        proj = [p for p in d if p.get("projectId") and p.get("elements")][0]
    else:
        proj = d
    return proj

def rid(x):
    return x["model"] if isinstance(x, dict) else x

def main():
    proj = load()
    els = proj["elements"]
    rels = proj["relations"]
    rl = list(rels.values()) if isinstance(rels, dict) else rels
    views = proj["views"]
    vl = list(views.values()) if isinstance(views, dict) else views

    # --- parente ---
    parent = {}
    for eid, e in els.items():
        for c in (e.get("children") or []):
            parent[c] = eid

    def path(eid):
        p = [eid]
        while eid in parent:
            eid = parent[eid]; p.append(eid)
        return ".".join(reversed(p))

    inv = {
        "generatedAt": datetime.datetime.now(datetime.UTC).isoformat(),
        "projectId": proj.get("projectId"),
        "counts": {
            "elements": len(els),
            "relations": len(rl),
            "views": len(vl),
            "tags": len(proj["specification"].get("tags", {})),
            "elementKinds": len(proj["specification"].get("elements", {})),
            "relationshipKinds": len(proj["specification"].get("relationships", {})),
        },
        "elementKindsUsed": dict(collections.Counter(e["kind"] for e in els.values())),
        "elementsByKind": {},
        "relations": {"byKind": {}, "untyped": [], "total": len(rl)},
        "views": [],
        "issues": {
            "noDescription": [], "noMetadata": [], "noTags": [],
            "orphan": [], "noTechnology": [], "brokenRef": [],
        },
        "metadataKeys": {},
    }

    for eid, e in sorted(els.items(), key=lambda kv: kv[1]["kind"]):
        inv["elementsByKind"].setdefault(e["kind"], []).append({
            "id": eid, "title": e.get("title"), "path": path(eid),
            "parent": parent.get(eid), "tags": e.get("tags") or [],
            "metadataKeys": sorted((e.get("metadata") or {}).keys()),
            "hasDescription": bool(e.get("description")),
            "notation": e.get("notation"),
        })

    for r in rl:
        inv["relations"]["byKind"][r.get("kind") or "NONE"] = \
            inv["relations"]["byKind"].get(r.get("kind") or "NONE", 0) + 1

    for v in vl:
        try:
            n = len(v.get("nodes") or [])
            e = len(v.get("edges") or [])
        except Exception:
            n = e = -1
        inv["views"].append({
            "id": v.get("id"), "title": v.get("title"),
            "type": ("deployment" if str(v.get("id", "")).startswith("deploiement") or v.get("_type") == "deployment"
                     else "dynamic" if "dynamic" in json.dumps(v.get("_type") or "") else "element"),
            "nodes": n, "edges": e,
            "hasDescription": bool(v.get("description")),
        })

    connected = set()
    for r in rl:
        connected.add(rid(r["source"])); connected.add(rid(r["target"]))

    for eid, e in els.items():
        md = e.get("metadata") or {}
        inv["issues"]["noDescription"] += [] if e.get("description") else [eid]
        inv["issues"]["noMetadata"] += [] if md else [eid]
        inv["issues"]["noTags"] += [] if e.get("tags") else [eid]
        inv["issues"]["orphan"] += [] if eid in connected else [eid]
        inv["issues"]["noTechnology"] += [] if (e.get("technology") or True) else [eid]
        for k in md:
            inv["metadataKeys"][k] = inv["metadataKeys"].get(k, 0) + 1

    # backend du graphe de relations : le modele compile ne porte pas 'kind'
    outdir = os.path.join(os.path.dirname(__file__), "..", "docs")
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "audit-inventory.json"), "w", encoding="utf-8") as f:
        json.dump(inv, f, ensure_ascii=False, indent=1)

    print("=== INVENTAIRE ===")
    print("compteurs:", json.dumps(inv["counts"], ensure_ascii=False))
    print("kinds elements:", json.dumps(inv["elementKindsUsed"], ensure_ascii=False))
    print("kinds relations:", json.dumps(inv["relations"]["byKind"], ensure_ascii=False))
    print("\n--- PROBLEMES DETECTES ---")
    for k, v in inv["issues"].items():
        if v:
            print(f"{k}: {len(v)}")
            for x in v[:12]: print("   ", x)
            if len(v) > 12: print(f"    ... +{len(v)-12}")
    print("\n--- VUES ---")
    for v in inv["views"]:
        print(f"  {v['id']:32s} nodes={v['nodes']:4d} edges={v['edges']:4d} {v['title'][:52]}")

if __name__ == "__main__":
    main()
