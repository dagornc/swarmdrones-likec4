#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_sysml.py — Controle syntaxique STRUCTUREL maison des fichiers .sysml.

Carte SYSML-15 (t_d671a500). Profil : architecte.

PORTEE REELLE (a lire avant toute interpretation) :
  Ce script n'est PAS un validateur SysML v2 conforme OMG. Aucun outil SysML v2
  (SysIDE / SysML v2 Pilot Implementation / CLI sysml) n'est installe dans cet
  environnement (verifie : pas de java, pas de paquet pip/npm `sysml`/`sysml2`).
  Il verifie uniquement la STRUCTURE LEXICALE des fichiers emis :
    1. delimiteurs equilibres  {}  []  ()
    2. ouverture du package `package '...' {` en tete
    3. presence des constructeurs attendus par spec : part def, action def,
       requirement def, interface def (ou item def / port def), import
    4. chaque declaration `* def <Nom>` possede un nom
    5. terminaison des instructions par `;`, `{` ou `}`

  Il ne valide NI la grammaire OMG, NI la semantique, NI la resolvabilite des
  types. C'est le « parseur minimal » exige par la carte quand aucun outil reel
  n'est disponible — et il est documente comme tel.

Usage :
  python3 validate_sysml.py [repertoire]   # defaut : sysml/ (repertoire du script)
  Sortie : rapport par fichier + resume. Exit 0 si 15/15 OK, 1 sinon.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DIR = HERE

REQUIRED_DEFS = ["part def", "action def", "requirement def"]
OPEN = {"{": "}", "[": "]", "(": ")"}
CLOSE = {v: k for k, v in OPEN.items()}


def strip_comments(text):
    """Supprime les commentaires // et /* */ (en preservant les chaines '...')."""
    out = []
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c == "'":
            j = i + 1
            while j < n and text[j] != "'":
                if text[j] == "\\":
                    j += 1
                j += 1
            out.append(text[i:j+1])
            i = j + 1
            continue
        if c == "/" and i + 1 < n:
            if text[i + 1] == "/":
                while i < n and text[i] != "\n":
                    i += 1
                out.append("\n")
                continue
            if text[i + 1] == "*":
                i += 2
                while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                    i += 1
                i += 2
                out.append(" ")
                continue
        out.append(c)
        i += 1
    return "".join(out)


def check_file(path):
    errors = []
    with open(path, encoding="utf-8") as f:
        raw = f.read()

    code = strip_comments(raw)

    # 1. delimiteurs equilibres
    stack = []
    for c in code:
        if c in OPEN:
            stack.append(c)
        elif c in CLOSE:
            if not stack:
                errors.append(f"delimiteur fermant {c!r} sans ouverture")
            else:
                top = stack.pop()
                if OPEN[top] != c:
                    errors.append(f"delimiteur mal apparie : attendait {OPEN[top]!r}, trouve {c!r}")
    if stack:
        errors.append(f"delimiteurs non fermes : {''.join(stack)}")

    # 2. ouverture package
    head = code.lstrip()
    if not head.startswith("package "):
        errors.append("le fichier ne commence pas par 'package'")
    elif head.find("{") < 0:
        errors.append("package sans '{{' d'ouverture")

    # 3. presence des constructeurs attendus
    for req in REQUIRED_DEFS:
        if req not in code:
            errors.append(f"constructeur manquant : {req}")
    if "import ScalarValues::*;" not in code:
        errors.append("import ScalarValues::*; manquant")
    if not any(d in code for d in ["interface def", "item def", "port def"]):
        errors.append("aucun constructeur d'interface/donnee (interface def | item def | port def)")

    # 4. chaque declaration '* def <Nom>' a un nom
    for line in code.splitlines():
        s = line.strip()
        for kw in ("part def", "action def", "state def", "requirement def",
                   "interface def", "item def", "port def"):
            if s.startswith(kw + " "):
                name = s[len(kw):].strip()
                if not name or name == "{":
                    errors.append(f"declaration '{kw}' sans nom : {s!r}")
                break

    # 5. terminaison des instructions
    for idx, line in enumerate(code.splitlines(), 1):
        s = line.strip()
        if not s:
            continue
        if s == "doc":
            # residu d'une annotation `doc /* ... */` (non terminee par ';' en SysML v2)
            continue
        if s.endswith((";", "{", "}")):
            continue
        errors.append(f"ligne {idx} sans terminateur ';'/'{{'/'}}' : {s[:60]!r}")

    return errors


def main():
    d = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DIR
    files = sorted(f for f in os.listdir(d) if f.endswith(".sysml"))
    if not files:
        print(f"Aucun fichier .sysml dans {d}")
        return 1

    ok = 0
    total_errors = 0
    for fn in files:
        errs = check_file(os.path.join(d, fn))
        if errs:
            total_errors += len(errs)
            print(f"✗ {fn}")
            for e in errs:
                print(f"    - {e}")
        else:
            ok += 1
            print(f"✓ {fn}")

    print()
    print(f"RESULTAT : {ok}/{len(files)} fichiers conformes au controle structurel maison.")
    if total_errors:
        print(f"{total_errors} probleme(s) structurel(s) detecte(s).")
        print("RAPPEL : ceci n'est PAS une validation SysML v2 OMG (aucun outil OMG installe).")
        return 1
    print("RAPPEL : validation structurelle maison uniquement — la conformite OMG SysML v2")
    print("        reste a etablir avec SysIDE / SysML v2 Pilot Implementation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
