#!/usr/bin/env python3
"""
gen_science_additions.py — génère les blocs LikeC4 (specDoc + finding + relations)
pour les articles RATTACHEE, à partir d'un ledger JSON.

Usage: python3 gen_science_additions.py /tmp/ledger_lot01.json
Ledger: {
  "rattachees": [ {src, title, link_doi/arxiv/url, link_title, description, metadata{...},
                   finding{id,title,link...,description,metadata{...}}, algs[[alg,note],...]} ],
  "specdoc_only": [ {src, title, link..., description, metadata{...}, target_finding, note} ],
  "deja": [...], "ecartees": [...]   # informational only
}
"""
import json, sys

def indent(text, n):
    pad = ' ' * n
    return '\n'.join(pad + line if line.strip() else line for line in text.split('\n')).strip('\n')

def links(d, indent_n):
    out = []
    if d.get('link_doi'):
        out.append(f"    link https://doi.org/{d['link_doi']} \"{d['link_title']}\"")
    if d.get('link_arxiv'):
        out.append(f"    link https://arxiv.org/abs/{d['link_arxiv']} \"{d['link_title']}\"")
    if d.get('link_url'):
        out.append(f"    link {d['link_url']} \"{d['link_title']}\"")
    return out

def specdoc(d):
    lines = [f"  {d['src']} = specDoc '{d['title']}' {{", "    #science"]
    lines += links(d, 4)
    lines.append("    description '''")
    lines.append(indent(d['description'], 6))
    lines.append("    '''")
    md = d['metadata']
    parts = []
    for k in ['doi','arxiv','annee','nature','corpus','statut']:
        if md.get(k): parts.append(f"{k} '{md[k]}'")
    lines.append("    metadata { " + '; '.join(parts) + " }")
    lines.append("  }")
    return '\n'.join(lines)

def finding(d):
    f = d['finding']
    lines = [f"  {f['id']} = finding '{f['title']}' {{", "    #science"]
    lines += links(f, 4)
    lines.append("    description '''")
    lines.append(indent(f['description'], 6))
    lines.append("    '''")
    md = f['metadata']
    parts = []
    for k in ['verdict','niveau_preuve','source','correction_modele']:
        if md.get(k): parts.append(f"{k} '{md[k]}'")
    lines.append("    metadata { " + '; '.join(parts) + " }")
    lines.append("  }")
    return '\n'.join(lines)

def relations(d):
    out = []
    for alg, note in d['algs']:
        out.append(f"  {d['finding']['id']} -[evidences]-> {alg} '{note}'")
    out.append(f"  {d['finding']['id']} -[uses]-> {d['src']} 'source primaire'")
    return '\n'.join(out)

def main():
    data = json.load(open(sys.argv[1]))
    specs, finds, rels = [], [], []
    for d in data.get('rattachees', []):
        specs.append(specdoc(d)); finds.append(finding(d)); rels.append(relations(d))
    for d in data.get('specdoc_only', []):
        specs.append(specdoc(d))
        rels.append(f"  {d['target_finding']} -[uses]-> {d['src']} '{d['note']}'")
    print("// =============================================================================")
    print(f"//  {data.get('lot_label','LOT')} — SOURCES RATTACHEES (statut CONSULTEE)")
    print("// =============================================================================")
    print()
    if specs:
        print('\n\n'.join(specs))
    if finds:
        print()
        print('\n\n'.join(finds))
    if rels:
        print()
        print("  // --- Relations du lot ---")
        print('\n'.join(rels))

if __name__ == '__main__':
    main()
