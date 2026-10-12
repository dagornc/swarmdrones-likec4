#!/usr/bin/env python3
"""
=============================================================================
GOVERNANCE DU MODELE SwarmDrones (LikeC4)
=============================================================================
Script de gouvernance continue : validation + non-regression + divergence +
drift du modele servi + coherence modele<->code.

Cinq controles, un seul point d'entree :
  1. VALIDATION      : `likec4 validate` (compilation reelle du modele).
  2. NON-REGRESSION  : comparaison des compteurs (elements/relations/vues par
                       kind) avec une baseline stockee. Toute baisse est un
                       signal d'alerte (regression silencieuse).
  3. DIVERGENCE      : comparaison des fichiers .c4 entre la copie active
                       (montee dans le conteneur) et la copie git de reference.
  4. DRIFT SERVI     : le modele SERVI par le conteneur reflete-t-il le disque ?
                       Comble l'angle mort du dev server Vite (instantane au
                       demarrage, HMR inoperant sur le modele compile).
  5. MODELE <-> CODE : le modele dit-il la verite sur les depots reels ?
                       Depot accessible, version -> ref reelle, coherence
                       interne bloc algorithm vs bloc specDoc.

Usage :
  python3 gouvernance_swarmdrones.py            # controle complet
  python3 gouvernance_swarmdrones.py --init     # (re)etablit la baseline
  python3 gouvernance_swarmdrones.py --validate # validation seule
  python3 gouvernance_swarmdrones.py --baseline # non-regression seule
  python3 gouvernance_swarmdrones.py --divergence # divergence seule
  python3 gouvernance_swarmdrones.py --served   # drift du modele servi seul
  python3 gouvernance_swarmdrones.py --model-code # coherence modele<->code seule

Code de sortie : 0 = OK, 1 = au moins un controle a echoue.
=============================================================================
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------
def _resolve_container():
    """Resout dynamiquement le conteneur LikeC4 servi.

    Le nom a change (likec4 -> likec4-static) et l'ID est recree a chaque
    redeploiement : un nom en dur casse silencieusement la gouvernance.
    On cherche par prefixe de nom, avec repli sur l'ancien nom.
    """
    for pattern in ("likec4-static", "likec4"):
        code, out, _ = run(
            ["docker", "ps", "--filter", f"name={pattern}",
             "--format", "{{.Names}}"]
        )
        names = [n.strip() for n in out.splitlines() if n.strip()]
        if names:
            return names[0]
    return "likec4-static"  # repli : echouera explicitement si absent


DATA_DIR = "/data"                      # chemin DANS le conteneur
ACTIVE_DIR = Path("/docker/likec4/workspace")   # copie active (montee)
GIT_DIR = Path("/home/hermesagent/workspace/swarmdrones_likec4")  # copie git
# Les exports sont ecrits dans un repertoire temporaire possede par
# l'utilisateur courant : /docker/likec4/workspace appartient a root (ecrit
# par l'ancien conteneur), et le CLI hote tourne en hermesagent -> EACCES.
# On evite tout chown (modification de permissions) en exportant ailleurs.
OUT_DIR = Path(os.environ.get("GOV_OUT_DIR", "/tmp/gov_likec4"))
BASELINE_FILE = ACTIVE_DIR / "gov_baseline.json"
MODEL_EXPORT = OUT_DIR / "gov_model.json"

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def run(cmd, **kw):
    """Execute une commande et retourne (code, stdout, stderr)."""
    p = subprocess.run(cmd, capture_output=True, text=True, **kw)
    return p.returncode, p.stdout, p.stderr


def docker_exec(args, **kw):
    return run(["docker", "exec", CONTAINER] + args, **kw)


CONTAINER = _resolve_container()


def likec4_cli(args, **kw):
    """Execute le CLI LikeC4 sur l'HOTE via npx.

    Historique : jusqu'au 2026-10-10, un conteneur `likec4` faisait tourner le
    dev server (Vite) et embarquait le CLI. Le deploiement statique l'a
    remplace par `likec4-static` (nginx pur, SANS CLI). Le CLI est desormais
    fourni par npx sur l'hote (likec4 1.59.4). Toute invocation `docker exec
    likec4 ...` est donc structurellement obsolete.
    """
    return run(["npx", "--yes", "likec4"] + args, cwd=str(ACTIVE_DIR), **kw)


def export_model():
    """Exporte le modele compile en JSON (CLI hote)."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    code, out, err = likec4_cli(
        ["export", "json", ".", "-o", str(MODEL_EXPORT)]
    )
    if code != 0:
        print(f"[ERREUR] export json a echoue : {(err or out).strip()[-300:]}")
        return False
    return True


def export_likec4_json():
    """Regenere le likec4.json (modele compile) dans OUT_DIR.

    Ce fichier est un export manuel qui peut se perimer si on ne le regenere
    pas. Le regenere a chaque gouvernance garantit qu'il reflete toujours le
    modele courant (liens, elements, vues). Ecrit dans OUT_DIR (tmp) car
    ACTIVE_DIR appartient a root.
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    code, out, err = likec4_cli(
        ["export", "json", ".", "-o", str(OUT_DIR / "likec4.json")]
    )
    if code != 0:
        print(f"[ERREUR] regeneration likec4.json a echoue : {(err or out).strip()[-300:]}")
        return False
    print("  likec4.json regenere (modele compile a jour).")
    return True


def load_model():
    """Charge le modele compile exporte."""
    with open(MODEL_EXPORT) as f:
        data = json.load(f)
    proj = data[0]
    return proj


def items(x):
    """Normalise elements/relations (dict id->obj ou list) en liste."""
    if isinstance(x, dict):
        return list(x.values())
    return [v for v in x if isinstance(v, dict)]


def compute_metrics(proj):
    """Calcule les metriques de non-regression depuis le modele compile."""
    elements = items(proj.get("elements", {}))
    relations = items(proj.get("relations", {}))
    views = proj.get("views", {})
    deployments = proj.get("deployments", {})

    kind_count = Counter(e.get("kind", "?") for e in elements)
    rel_kind = Counter(r.get("kind", "?") for r in relations)

    # vues : dict id->obj ou list
    view_ids = list(views.keys()) if isinstance(views, dict) else [
        v.get("id") for v in views if isinstance(v, dict)
    ]

    return {
        "total_elements": len(elements),
        "total_relations": len(relations),
        "total_views": len(view_ids),
        "total_deployments": len(deployments),
        "elements_by_kind": dict(kind_count),
        "relations_by_kind": dict(rel_kind),
        "view_ids": sorted(view_ids),
    }


# ---------------------------------------------------------------------------
# CONTROLE 1 — VALIDATION
# ---------------------------------------------------------------------------
def check_validate():
    print("=== [1/5] VALIDATION (likec4 validate) ===")
    code, out, err = likec4_cli(["validate", "."])
    # Le CLI LikeC4 ecrit son rapport sur stderr (logger), pas stdout.
    combined = (out or "") + (err or "")
    ok = code == 0 and "Valid" in combined
    last = [l for l in combined.strip().splitlines() if l.strip()]
    print(("  OK  " if ok else "  ECHEC ") + (last[-1] if last else "aucune sortie"))
    return ok


# ---------------------------------------------------------------------------
# CONTROLE 2 — NON-REGRESSION
# ---------------------------------------------------------------------------
def check_baseline(init=False):
    print("=== [2/5] NON-REGRESSION (baseline) ===")
    if not export_model():
        return False
    proj = load_model()
    metrics = compute_metrics(proj)

    if init or not BASELINE_FILE.exists():
        BASELINE_FILE.write_text(json.dumps(metrics, indent=2, ensure_ascii=False))
        print(f"  Baseline (re)etablie : {BASELINE_FILE.name}")
        print(f"    elements={metrics['total_elements']} relations={metrics['total_relations']} "
              f"views={metrics['total_views']} deployments={metrics['total_deployments']}")
        return True

    base = json.loads(BASELINE_FILE.read_text())
    problems = []

    # Compteurs globaux : toute BAISSE est une regression.
    for key in ["total_elements", "total_relations", "total_views", "total_deployments"]:
        b, c = base.get(key, 0), metrics[key]
        if c < b:
            problems.append(f"  [REGRESSION] {key} : {b} -> {c} (baisse)")
        elif c > b:
            print(f"  [info] {key} : {b} -> {c} (hausse, a verifier)")

    # Par kind : baisse d'un kind = regression.
    for kind, b in base.get("elements_by_kind", {}).items():
        c = metrics["elements_by_kind"].get(kind, 0)
        if c < b:
            problems.append(f"  [REGRESSION] elements kind '{kind}' : {b} -> {c}")
    for kind, b in base.get("relations_by_kind", {}).items():
        c = metrics["relations_by_kind"].get(kind, 0)
        if c < b:
            problems.append(f"  [REGRESSION] relations kind '{kind}' : {b} -> {c}")

    # Vues : toute vue de la baseline absente = regression.
    base_views = set(base.get("view_ids", []))
    cur_views = set(metrics["view_ids"])
    missing = base_views - cur_views
    for v in sorted(missing):
        problems.append(f"  [REGRESSION] vue absente : '{v}'")

    if problems:
        print("\n".join(problems))
        return False
    print("  OK  aucun ecart de non-regression.")
    return True


# ---------------------------------------------------------------------------
# CONTROLE 3 — DIVERGENCE ENTRE COPIES
# ---------------------------------------------------------------------------
def check_divergence():
    print("=== [3/5] DIVERGENCE (copie active vs copie git) ===")
    if not GIT_DIR.exists():
        print(f"  [info] copie git absente : {GIT_DIR} (controle ignore)")
        return True

    active_files = {p.name: p for p in ACTIVE_DIR.glob("*.c4")}
    git_files = {p.name: p for p in GIT_DIR.glob("*.c4")}

    def sha(p):
        return hashlib.sha256(p.read_bytes()).hexdigest()

    divergences = []

    # Fichiers presents dans la copie active mais absents de la copie git.
    for name in sorted(set(active_files) - set(git_files)):
        divergences.append(f"  [DIVERGENCE] fichier actif absent de git : {name}")

    # Fichiers presents dans git mais absents de la copie active.
    for name in sorted(set(git_files) - set(active_files)):
        divergences.append(f"  [DIVERGENCE] fichier git absent de la copie active : {name}")

    # Fichiers communs : comparaison de contenu.
    for name in sorted(set(active_files) & set(git_files)):
        if sha(active_files[name]) != sha(git_files[name]):
            divergences.append(f"  [DIVERGENCE] contenu different : {name}")

    if divergences:
        print("\n".join(divergences))
        print("  [AVERTISSEMENT] Les deux copies divergent. La copie active")
        print("     (/docker/likec4/workspace) est celle servie par le conteneur ;")
        print("     la copie git est en retard. Ce n'est PAS un echec de non-regression,")
        print("     mais un rappel : resynchroniser la copie git si elle doit etre")
        print("     la reference de versionnement.")
        return True  # divergence = avertissement, pas un echec bloquant
    print("  OK  les deux copies sont identiques.")
    return True


# ---------------------------------------------------------------------------
# CONTROLE 4 — DRIFT DU MODELE SERVI (instantane du conteneur vs disque)
# ---------------------------------------------------------------------------
def check_served_drift():
    """Le modele SERVI par le site statique reflete-t-il le disque ?

    ANGLE MORT COMBLE (2026-09-29), REECRIT (2026-10-12) : jusqu'au 2026-10-10,
    un dev server LikeC4 (Vite) compilait le modele au DEMARRAGE, et un .c4
    modifie apres le demarrage n'etait pas servi. Le deploiement statique
    (nginx + `likec4 build`) a supprime ce risque : le site sert un bundle
    fige, produit par build_static.sh.

    Nouveau controle : le bundle servi (`deploy/site/likec4-views.js`) est-il
    plus recent que les sources .c4 ? Si une source est plus recente que le
    bundle, le site sert un modele perime.
    """
    print("=== [4/5] DRIFT MODELE SERVI (bundle statique vs disque) ===")

    site_dir = ACTIVE_DIR.parent / "deploy" / "site"
    # Repli : emplacement du bind mount du conteneur likec4-static.
    if not site_dir.exists():
        site_dir = Path("/home/hermesagent/workspace/swarmdrones_likec4/deploy/site")
    bundle = site_dir / "likec4-views.js"

    if not bundle.exists():
        print(f"  [info] bundle servi introuvable : {bundle} (controle ignore)")
        return True

    bundle_mtime = bundle.stat().st_mtime
    stale = []
    for src in sorted(ACTIVE_DIR.glob("*.c4")):
        if src.stat().st_mtime > bundle_mtime:
            stale.append(src.name)

    if stale:
        print(f"  [DRIFT] {len(stale)} source(s) .c4 plus recente(s) que le bundle servi :")
        for name in stale[:5]:
            print(f"    - {name}")
        print("  [ACTION] relancer build_static.sh puis redeployer (autorisation Christophe).")
        return False

    print(f"  OK  le bundle servi est a jour (posterieur aux {len(list(ACTIVE_DIR.glob('*.c4')))} sources).")
    return True


# ---------------------------------------------------------------------------
# CONTROLE 5 — COHERENCE MODELE <-> CODE
# ---------------------------------------------------------------------------
def check_model_code():
    """Le modele dit-il la verite sur les depots de code reels ?

    Verifie que chaque algorithme declare pointe un depot accessible, que la
    version declaree correspond a une reference reelle, et que le bloc
    `algorithm` et le bloc `specDoc` declarent la MEME version (detection des
    mises a jour partielles du modele).
    """
    print("=== [5/5] COHERENCE MODELE <-> CODE ===")
    script = GIT_DIR / "tools" / "qa" / "check_model_code_consistency.py"
    if not script.exists():
        print(f"  [info] script absent : {script} (controle ignore)")
        return True

    r = subprocess.run([sys.executable, str(script)],
                       capture_output=True, text=True, cwd=str(GIT_DIR))
    ok = r.returncode == 0
    if ok:
        # Extraire la ligne de synthese.
        for line in r.stdout.splitlines():
            if "algorithmes |" in line:
                print(f"  OK  {line.strip()}")
                break
        else:
            print("  OK  coherence modele <-> code verifiee.")
    else:
        print("  [ECHEC] incoherence modele <-> code :")
        for line in r.stdout.splitlines():
            if "DIVERGENCE" in line or "FAIL" in line or "ECHEC" in line:
                print(f"    {line.strip()}")
    return ok


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Gouvernance du modele SwarmDrones LikeC4")
    ap.add_argument("--init", action="store_true", help="(re)etablir la baseline")
    ap.add_argument("--validate", action="store_true", help="validation seule")
    ap.add_argument("--baseline", action="store_true", help="non-regression seule")
    ap.add_argument("--divergence", action="store_true", help="divergence seule")
    ap.add_argument("--served", action="store_true", help="drift du modele servi seul")
    ap.add_argument("--model-code", action="store_true", help="coherence modele<->code seule")
    args = ap.parse_args()

    # Mode selection : si aucun flag, tout executer.
    if args.validate:
        ok = check_validate()
    elif args.baseline:
        ok = check_baseline(init=args.init)
    elif args.divergence:
        ok = check_divergence()
    elif args.served:
        ok = check_served_drift()
    elif args.model_code:
        ok = check_model_code()
    else:
        ok_v = check_validate()
        # Regenerer le likec4.json (modele compile a jour) a chaque controle complet.
        ok_l = export_likec4_json()
        ok_b = check_baseline(init=args.init)
        ok_d = check_divergence()
        ok_s = check_served_drift()
        ok_m = check_model_code()
        ok = ok_v and ok_l and ok_b and ok_d and ok_s and ok_m

    print()
    print("=== RESULTAT GLOBAL : " + ("OK" if ok else "ECHEC") + " ===")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
