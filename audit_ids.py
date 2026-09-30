#!/usr/bin/env python3
"""
Audit de coherence des identifiants LikeC4 — v2.
Approche : parser l'arbre d'imbrication pour connaitre les noms qualifies reels,
puis verifier les references de relations et d'includes.
"""
import re, os, json, collections

ROOT = "/home/hermesagent/workspace/swarmdrones_likec4"

ACTIVE = [
    "architecture.c4", "algorithms.c4", "hardware.c4", "messages.c4",
    "metamodel.c4", "functional.c4", "deployment.c4", "scenarios.c4",
    "simulation.c4", "worldmodel.c4", "facts.c4", "decisions_hw.c4",
    "science.c4", "sysml.c4", "hzip.c4", "views.c4", "ux-parcours.c4",
    "e19-system-context.c4", "e20-audit-completeness.c4", "proposals-applied.c4",
]

# Kinds extraits de metamodel.c4 (specification) + kinds historiques d'architecture.c4
KINDS = (
    # historiques (architecture.c4)
    "operator|external|platform|edgeStation|c2System|cloudSystem|component|"
    "hypothesis|decision|software|algorithm|risk|blindspot|host|"
    # metamodel.c4
    "actuator|agent|apiContract|application|belongs|calls|capability|channel|"
    "command|commands|companionComputer|computeNode|constrains|consumes|container|"
    "contains|controller|controls|dataset|dependsOn|deployedAs|deployedOn|"
    "deploymentUnit|derivedFrom|documentedBy|drone|evaluates|event|evidences|"
    "experiment|exposes|factSheet|finding|flightController|function|groundStation|"
    "implements|interface|maps|measuredBy|message|middleware|mission|module|network|"
    "networkDevice|observes|optimizer|planner|policy|populates|process|produces|"
    "protocol|publishes|realizes|receives|renderRule|responsibility|runsOn|runtime|"
    "scenario|sceneCategory|scientificPaper|sends|sensor|server|service|sourceCode|"
    "specDoc|standard|state|strategy|subscribes|subsystem|supportedBy|system|"
    "telemetry|test|topic|triggers|unknown|uses|validates|worldEntity|worldState|"
    "zoneSemantic|zone|element|deployment|instance|relationship|kind|tag|"
    "paper|fact|requirement|specification"
)

DECL_RE = re.compile(
    r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(" + KINDS + r")\b(?:\s*'([^']*)')?"
)

# Faux positifs a ignorer dans les includes de vues
VIEW_NOISE = {
    "navigateTo", "with", "include", "exclude", "of", "and", "or", "not",
    "element", "tag", "critical", "amont", "aval", "contexte", "index",
    "droneInternal", "hzipEvidence", "hzipFrames", "hzipLayers", "hzipTests",
    "zone", "onboard", "edge", "c2", "cloud", "refDrone", "simContract",
    "where", "style", "global", "autoLayout", "LeftRight", "TopBottom",
    "rank", "same", "source", "target", "safety", "mission",
}

def strip_comments(text):
    # Neutralise les blocs ''' ... ''' en PRESERVANT les sauts de ligne
    # (sinon la numerotation et l'imbrication par accolades se desynchronisent).
    def _blank(m):
        return "\n" * m.group(0).count("\n")
    text = re.sub(r"'''[\s\S]*?'''", _blank, text)
    # PAS de regle /* */ : LikeC4 n'a pas de commentaires bloc, et les liens
    # GitHub contiennent des globs '/*' qui seraient pris pour des commentaires.
    text = re.sub(r"//[^\n]*", "", text)
    return text

def parse_tree(path):
    """Retourne (qualified_names, decls) en suivant l'imbrication par accolades."""
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    clean = strip_comments(raw)
    lines = clean.split("\n")

    qualified = {}   # nom qualifie -> (kind, label, line, file)
    decls = {}       # identifiant local -> (kind, label, line)
    stack = []       # pile de (identifiant, profondeur)
    depth = 0

    for i, line in enumerate(lines):
        m = DECL_RE.match(line)
        if m:
            ident, kind, label = m.group(1), m.group(2), m.group(3) or ""
            prefix = ".".join(s[0] for s in stack)
            qname = f"{prefix}.{ident}" if prefix else ident
            qualified[qname] = (kind, label, i + 1, os.path.basename(path))
            decls[ident] = (kind, label, i + 1)

        # Compter les accolades HORS chaines de caracteres
        stripped = re.sub(r"'[^']*'", "''", line)
        opens = stripped.count("{")
        closes = stripped.count("}")

        if m and opens > 0:
            stack.append((m.group(1), depth))
            depth += opens - closes
            while stack and depth <= stack[-1][1]:
                stack.pop()
            continue
        depth += opens - closes
        while stack and depth <= stack[-1][1]:
            stack.pop()

    return qualified, decls

def main():
    all_q = {}
    all_local = collections.defaultdict(list)
    per_file = {}

    for fn in ACTIVE:
        p = os.path.join(ROOT, fn)
        if not os.path.exists(p):
            continue
        q, d = parse_tree(p)
        per_file[fn] = q
        for name, (kind, label, ln, f) in q.items():
            all_q.setdefault(name, []).append((kind, label, ln, f))
        for ident, (kind, label, ln) in d.items():
            all_local[ident].append((fn, kind, label, ln))

    print(f"=== NOMS QUALIFIES DECLARES : {len(all_q)} ===")

    # Collisions de noms qualifies
    dups = {k: v for k, v in all_q.items() if len(v) > 1}
    print(f"\n--- COLLISIONS DE NOMS QUALIFIES ({len(dups)}) ---")
    for k, v in sorted(dups.items()):
        print(f"  {k}:")
        for kind, label, ln, f in v:
            print(f"    {f}:{ln}  kind={kind}  label='{label}'")
    if not dups:
        print("  (aucune)")

    # Collisions d'identifiants locaux (meme nom, fichiers differents)
    print(f"\n--- IDENTIFIANTS LOCAUX HOMONYMES (fichiers differents) ---")
    n = 0
    for ident, occs in sorted(all_local.items()):
        files = {o[0] for o in occs}
        if len(files) > 1:
            n += 1
            print(f"  {ident}: {sorted(files)}")
    if n == 0:
        print("  (aucun)")

    # References de relations : "a -> b" et "a -[x]-> b"
    print(f"\n--- REFERENCES DE RELATIONS NON RESOLUES ---")
    rel_re = re.compile(r"^\s*([A-Za-z_][\w.]*)\s*(?:-\[[^\]]*\]->|->)\s*([A-Za-z_][\w.]*)")
    unresolved = collections.defaultdict(list)
    for fn in ACTIVE:
        p = os.path.join(ROOT, fn)
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as f:
            clean = strip_comments(f.read())
        for i, line in enumerate(clean.split("\n")):
            m = rel_re.match(line)
            if not m:
                continue
            for ref in (m.group(1), m.group(2)):
                if ref in all_q:
                    continue
                # tolerance : nom local declare dans le meme fichier
                if ref in per_file[fn]:
                    continue
                # tolerance : nom local declare ailleurs (modele global LikeC4)
                if ref in all_local:
                    continue
                unresolved[ref].append((fn, i + 1, line.strip()[:110]))

    if unresolved:
        for ref in sorted(unresolved):
            occ = unresolved[ref]
            print(f"  {ref}  ({len(occ)} occ.)")
            for fn, ln, ctx in occ[:2]:
                print(f"    {fn}:{ln}  {ctx}")
    else:
        print("  (aucune)")

    # Includes de vues non resolus
    print(f"\n--- INCLUDES DE VUES NON RESOLUS ---")
    inc_re = re.compile(r"^\s*include\s+(.+)$")
    inc_unres = collections.defaultdict(list)
    for fn in ACTIVE:
        p = os.path.join(ROOT, fn)
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as f:
            clean = strip_comments(f.read())
        for i, line in enumerate(clean.split("\n")):
            m = inc_re.match(line)
            if not m:
                continue
            body = m.group(1)
            for tok in re.findall(r"[A-Za-z_][\w.]*", body):
                if tok in VIEW_NOISE:
                    continue
                # predicats de filtre LikeC4 : element.tag, element.kind, element.metadata...
                if tok.split(".")[0] in ("element", "relation", "source", "target"):
                    continue
                if tok.endswith(".") or "**" in body:
                    continue
                if tok in all_q or tok in per_file[fn] or tok in all_local:
                    continue
                inc_unres[tok].append((fn, i + 1, line.strip()[:110]))
    if inc_unres:
        for ref in sorted(inc_unres):
            occ = inc_unres[ref]
            print(f"  {ref}  ({len(occ)} occ.)")
            for fn, ln, ctx in occ[:2]:
                print(f"    {fn}:{ln}  {ctx}")
    else:
        print("  (aucune)")

    # Libelles kebab-case dont l'identifiant est camelCase (piege de nommage)
    print(f"\n--- PIEGE DE NOMMAGE : libelle kebab-case vs identifiant camelCase ---")
    traps = []
    for name, occs in all_q.items():
        local = name.split(".")[-1]
        for kind, label, ln, f in occs:
            if "-" in label and label.replace("-", "").lower() == local.lower():
                traps.append((name, label, f, ln))
    for name, label, f, ln in sorted(traps):
        print(f"  {f}:{ln}  ident='{name}'  label='{label}'")
    if not traps:
        print("  (aucun)")

    out = {
        "qualified_count": len(all_q),
        "collisions": {k: [{"kind": kd, "label": lb, "line": l, "file": f}
                           for kd, lb, l, f in v] for k, v in dups.items()},
        "unresolved_relations": {k: [{"file": f, "line": l, "ctx": c} for f, l, c in v]
                                 for k, v in unresolved.items()},
        "unresolved_includes": {k: [{"file": f, "line": l, "ctx": c} for f, l, c in v]
                                for k, v in inc_unres.items()},
        "naming_traps": [{"ident": i, "label": lb, "file": f, "line": l}
                         for i, lb, f, l in traps],
    }
    with open(os.path.join(ROOT, "audit_ids_report.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] audit_ids_report.json")

if __name__ == "__main__":
    main()
