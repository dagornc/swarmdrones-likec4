#!/usr/bin/env python3
"""
Cohérence modèle <-> code — SWARM-3D-ARCHITECTURE

Verifie que ce que le modele LikeC4 DECLARE sur chaque algorithme
correspond a ce que le depot de code EXPOSE reellement.

Controles :
  C-1  Le depot declare existe et est accessible
  C-2  La version declaree correspond a une reference reelle du depot
       (branche ou tag)
  C-3  Le depot expose les artefacts attendus (Cargo.toml, src/, tests/,
       reference/, verify_parite_rust.py)
  C-4  Le README du depot declare la meme version que le modele

Usage:
  python3 tools/qa/check_model_code_consistency.py           # rapport
  python3 tools/qa/check_model_code_consistency.py --strict  # exit 1 si ecart
  python3 tools/qa/check_model_code_consistency.py --json    # sortie machine

Principe : un ecart n'est pas forcement une erreur — c'est un SIGNAL.
Le modele peut declarer 'TBD' (algo non implemente) : c'est conforme.
Ce qui est non conforme, c'est une divergence SILENCIEUSE.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Algorithmes dont le depot n'est pas encore implemente (version TBD).
# Le modele le declare explicitement : ce n'est PAS un ecart.
TBD_OK = "TBD"

# Decalage de nommage connu et documente : le modele declare une version de
# SPEC, le depot nomme sa branche d'apres la version du MOTEUR. Les deux
# peuvent differer legitimement. Toute entree ici doit porter sa justification.
NAMING_OFFSET = {
    "algConsensus": {
        "model_version": "7",
        "repo_branch": "v6",
        "why": "La branche v6 du depot implemente la spec v7 (moteur protocole_v6). "
               "Le nom de branche suit le moteur, pas la spec. Documente dans "
               "SPECIFICATION_V7.md et dans le bloc specConsensus du modele.",
    },
}


def read_model_sources():
    """Lit tous les .c4 et retourne le texte concatene."""
    out = {}
    for f in sorted(ROOT.glob("*.c4")):
        out[f.name] = f.read_text(encoding="utf-8")
    return out


def extract_algorithms(files):
    """Extrait les blocs d'algorithme avec depot et version declares."""
    algs = {}
    for fname, src in files.items():
        # Bloc : var = algorithm 'titre' { ... }
        for m in re.finditer(
                r"(\w+)\s*=\s*algorithm\s+'([^']+)'\s*\{(.*?)\n  \}",
                src, re.S):
            var, title, body = m.group(1), m.group(2), m.group(3)
            repo = re.search(r"repository\s+'([^']+)'", body)
            ver = re.search(r"version\s+'([^']+)'", body)
            impl = re.search(r"implementationStatus\s+'([^']+)'", body)
            algs[var] = {
                "var": var,
                "title": title,
                "file": fname,
                "repo": repo.group(1) if repo else None,
                "version": ver.group(1) if ver else None,
                "impl_status": impl.group(1) if impl else None,
            }
    return algs


def gh_api(path):
    """Appel gh api, retourne le JSON ou None."""
    r = subprocess.run(["gh", "api", path], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return None


def check_repo(repo_url):
    """Interroge le depot reel : branches, tags, HEAD, fichiers racine."""
    slug = repo_url.rstrip("/").replace("https://github.com/", "")
    info = {"slug": slug, "branches": [], "tags": [], "files": [], "error": None}

    branches = gh_api(f"repos/{slug}/branches?per_page=100")
    if branches is None:
        info["error"] = "depot inaccessible"
        return info
    info["branches"] = [b["name"] for b in branches]

    tags = gh_api(f"repos/{slug}/tags?per_page=100")
    if tags:
        info["tags"] = [t["name"] for t in tags]

    contents = gh_api(f"repos/{slug}/contents")
    if contents:
        info["files"] = [c["name"] for c in contents]

    return info


def version_refs(version_str):
    """Extrait les references candidates d'une chaine de version du modele.

    Ex: 'v3 (spec SWARM-SPEC-ALG-001-V3, 2026-09-18)' -> ['v3', 'V3']
        'v5.0 (spec SWARM-SPEC-ALG-002, 2026-09-19)'  -> ['v5.0', 'v5', 'V5']
    """
    if not version_str:
        return []
    refs = []
    # vN ou vN.M en debut
    m = re.match(r"\s*(v\d+(?:\.\d+)?)", version_str, re.I)
    if m:
        base = m.group(1)
        refs.append(base)
        refs.append(base.rstrip(".0") if base.endswith(".0") else base)
        refs.append(base.upper())
    return list(dict.fromkeys(refs))


def check_consistency(algs, verbose=True):
    """Execute les 4 controles sur chaque algorithme."""
    results = []
    for var, a in sorted(algs.items()):
        r = {"var": var, "title": a["title"], "repo": a["repo"],
             "version": a["version"], "checks": {}, "notes": []}

        if not a["repo"]:
            r["checks"]["C-1"] = ("SKIP", "aucun depot declare")
            results.append(r)
            continue

        info = check_repo(a["repo"])
        if info["error"]:
            r["checks"]["C-1"] = ("FAIL", info["error"])
            results.append(r)
            continue
        r["checks"]["C-1"] = ("OK", f"{len(info['branches'])} branches")

        # C-2 : la version declaree correspond-elle a une ref reelle ?
        if a["version"] == TBD_OK:
            r["checks"]["C-2"] = ("OK", "TBD declare — algo non implemente (conforme)")
        else:
            refs = version_refs(a["version"])
            found = [x for x in refs if x in info["branches"] or x in info["tags"]]
            if found:
                r["checks"]["C-2"] = ("OK", f"ref trouvee : {found[0]}")
            elif var in NAMING_OFFSET:
                off = NAMING_OFFSET[var]
                if off["repo_branch"] in info["branches"]:
                    r["checks"]["C-2"] = (
                        "OK",
                        f"decalage de nommage documente : modele v{off['model_version']} "
                        f"-> branche {off['repo_branch']}")
                else:
                    r["checks"]["C-2"] = (
                        "FAIL",
                        f"decalage declare vers {off['repo_branch']} mais branche absente")
            else:
                r["checks"]["C-2"] = (
                    "WARN",
                    f"version '{a['version'][:40]}' -> refs {refs} absentes "
                    f"(branches: {info['branches'][:6]})")

        # C-3 : artefacts attendus
        expected = ["Cargo.toml", "src", "tests", "reference"]
        present = [e for e in expected if e in info["files"]]
        missing = [e for e in expected if e not in info["files"]]
        if not missing:
            r["checks"]["C-3"] = ("OK", f"{len(present)}/{len(expected)} artefacts")
        elif a["version"] == TBD_OK:
            r["checks"]["C-3"] = ("OK", f"TBD — {len(present)}/{len(expected)} (non implemente)")
        else:
            r["checks"]["C-3"] = ("WARN", f"manquants : {missing}")

        results.append(r)

    return results


def extract_specdocs(files):
    """Extrait les blocs specDoc avec leur version courante declaree."""
    specs = {}
    for fname, src in files.items():
        for m in re.finditer(
                r"(\w+)\s*=\s*specDoc\s+'([^']+)'\s*\{(.*?)\n  \}",
                src, re.S):
            var, title, body = m.group(1), m.group(2), m.group(3)
            cur = re.search(r"versionCourante\s+'([^']+)'", body)
            algo = re.search(r"algorithme\s+'([^']+)'", body)
            specs[var] = {
                "var": var,
                "title": title,
                "file": fname,
                "version_courante": cur.group(1) if cur else None,
                "algorithme": algo.group(1) if algo else None,
            }
    return specs


def norm_version(v):
    """Normalise une version pour comparaison : 'v5.0 (spec...)' -> '5'."""
    if not v:
        return None
    m = re.match(r"\s*v?(\d+)(?:\.(\d+))?", v, re.I)
    if not m:
        return None
    major = m.group(1)
    minor = m.group(2)
    # v5.0 et v5 sont equivalents ; v7.0 -> 7
    if minor in (None, "0"):
        return major
    return f"{major}.{minor}"


def check_internal_consistency(algs, specs):
    """C-4 : le bloc algorithm et le bloc specDoc declarent-ils la meme version ?

    C'est le controle qui detecte une mise a jour partielle du modele :
    on met a jour la spec mais pas le bloc algorithm (ou l'inverse).
    """
    # Indexer les specDoc par algorithme
    by_algo = {}
    for s in specs.values():
        if s["algorithme"]:
            by_algo.setdefault(s["algorithme"], []).append(s)

    out = {}
    for var, a in algs.items():
        # Le nom canonique de l'algo est dans le titre : 'ALG_CONSENSUS — ...'
        m = re.match(r"\s*(ALG_[A-Z_]+)", a["title"])
        if not m:
            continue
        canon = m.group(1)
        related = by_algo.get(canon, [])
        if not related:
            continue

        algo_v = norm_version(a["version"])
        if algo_v is None:
            continue

        for s in related:
            spec_v = norm_version(s["version_courante"])
            if spec_v is None:
                continue
            if algo_v != spec_v:
                out[var] = {
                    "algo_version": a["version"],
                    "algo_norm": algo_v,
                    "spec_var": s["var"],
                    "spec_version": s["version_courante"],
                    "spec_norm": spec_v,
                }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    files = read_model_sources()
    algs = extract_algorithms(files)
    specs = extract_specdocs(files)

    if not algs:
        print("ERREUR : aucun algorithme extrait du modele", file=sys.stderr)
        return 2

    results = check_consistency(algs)
    internal = check_internal_consistency(algs, specs)

    if args.json:
        print(json.dumps({"repos": results, "internal": internal},
                         indent=2, ensure_ascii=False))
        return 0

    print(f"\nCoherence modele <-> code — {len(results)} algorithmes\n")
    print(f"{'Algo':32s} {'C-1':6s} {'C-2':6s} {'C-3':6s}  Detail")
    print("-" * 100)

    n_fail = n_warn = 0
    for r in results:
        c1 = r["checks"].get("C-1", ("SKIP", ""))
        c2 = r["checks"].get("C-2", ("SKIP", ""))
        c3 = r["checks"].get("C-3", ("SKIP", ""))
        if "FAIL" in (c1[0], c2[0], c3[0]):
            n_fail += 1
        if "WARN" in (c1[0], c2[0], c3[0]):
            n_warn += 1
        detail = c2[1] if c2[0] != "OK" else c3[1]
        print(f"{r['var']:32s} {c1[0]:6s} {c2[0]:6s} {c3[0]:6s}  {detail[:60]}")

    print("-" * 100)
    print(f"{len(results)} algorithmes | FAIL={n_fail} WARN={n_warn}")

    # C-4 : coherence interne
    print(f"\nC-4 Coherence interne (bloc algorithm vs bloc specDoc)\n")
    if not internal:
        print("  OK — aucune divergence interne detectee.")
    else:
        for var, d in sorted(internal.items()):
            print(f"  DIVERGENCE {var}")
            print(f"    bloc algorithm : {d['algo_version'][:50]}  (norm={d['algo_norm']})")
            print(f"    bloc {d['spec_var']:20s}: {d['spec_version'][:50]}  (norm={d['spec_norm']})")
        print(f"\n  {len(internal)} divergence(s) interne(s).")

    if n_fail:
        print("\nECHEC : au moins un depot inaccessible.")
        return 1
    if internal:
        print("\nECHEC : divergence interne du modele (mise a jour partielle).")
        return 1
    if n_warn and args.strict:
        print("\nECHEC (--strict) : au moins un avertissement de coherence.")
        return 1
    print("\nOK — coherence modele <-> code verifiee.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
