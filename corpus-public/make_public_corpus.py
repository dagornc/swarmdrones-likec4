#!/usr/bin/env python3
"""
Génère une version PUBLIABLE du corpus SwarmDrone.

Ne publie QUE des métadonnées bibliographiques (faits publics) :
titre, source, DOI, arXiv, type, hôte, niveau de confiance, périmètre.
Aucun PDF, aucun contenu d'article, aucun chemin local.

Sortie : corpus-public/
  - index.md            : index lisible (tableau)
  - corpus.json         : métadonnées structurées
  - statistiques.md     : tableau de bord
"""
import json, collections, os, re

SRC = '/home/hermesagent/swarmdrone-research/catalog.json'
OUT = '/home/hermesagent/workspace/swarmdrones_likec4/corpus-public'
os.makedirs(OUT, exist_ok=True)

d = json.load(open(SRC))

def clean(s):
    if s is None: return ''
    return re.sub(r'\s+', ' ', str(s)).strip()

records = []
for e in d:
    scope = e.get('scope') or {}
    records.append({
        'n': e.get('number'),
        'title': clean(e.get('title')),
        'source_url': clean(e.get('source_url')),
        'host': clean(e.get('source_host')),
        'type': clean(e.get('resource_type')),
        'trust': clean(e.get('trust')),
        'scope': clean(scope.get('level')),
        'themes': scope.get('themes') or [],
        'dois': e.get('dois') or [],
        'arxiv': e.get('arxiv_ids') or [],
        'dates': e.get('claimed_publication_dates') or [],
    })

# --- corpus.json ---
with open(os.path.join(OUT, 'corpus.json'), 'w', encoding='utf-8') as f:
    json.dump(records, f, ensure_ascii=False, indent=1)

# --- statistiques.md ---
trust = collections.Counter(r['trust'] for r in records)
rtype = collections.Counter(r['type'] for r in records)
scope = collections.Counter(r['scope'] for r in records)
hosts = collections.Counter(r['host'] for r in records if r['host'])
ndoi = sum(1 for r in records if r['dois'])
narx = sum(1 for r in records if r['arxiv'])
ndate = sum(1 for r in records if r['dates'])

with open(os.path.join(OUT, 'statistiques.md'), 'w', encoding='utf-8') as f:
    f.write('# Corpus SwarmDrone — statistiques\n\n')
    f.write(f'**{len(records)} entrées** de veille scientifique sur les essaims de drones.\n\n')
    f.write('## Niveau de confiance\n\n')
    for k, v in trust.most_common():
        f.write(f'- `{k}` : {v}\n')
    f.write('\n## Type de ressource\n\n')
    for k, v in rtype.most_common():
        f.write(f'- `{k}` : {v}\n')
    f.write('\n## Périmètre\n\n')
    for k, v in scope.most_common():
        f.write(f'- `{k}` : {v}\n')
    f.write('\n## Identifiants\n\n')
    f.write(f'- entrées avec DOI : {ndoi}\n')
    f.write(f'- entrées avec identifiant arXiv : {narx}\n')
    f.write(f'- entrées avec date de publication revendiquée : {ndate}\n')
    f.write('\n## Sources les plus fréquentes\n\n')
    for k, v in hosts.most_common(15):
        f.write(f'- `{k}` : {v}\n')
    f.write('\n> Les dates revendiquées ne sont pas des preuves. La métadonnée\n')
    f.write('> décisive est résolue contre la source primaire.\n')

# --- index.md ---
with open(os.path.join(OUT, 'index.md'), 'w', encoding='utf-8') as f:
    f.write('# Corpus SwarmDrone — index\n\n')
    f.write(f'{len(records)} entrées. Métadonnées bibliographiques uniquement '
            '(aucun PDF, aucun contenu d\'article).\n\n')
    f.write('| # | Confiance | Périmètre | Titre | Source |\n')
    f.write('|---:|---|---|---|---|\n')
    for r in records:
        title = r['title'].replace('|', '\\|')[:110]
        host = r['host'] or '—'
        f.write(f"| {r['n']} | {r['trust']} | {r['scope']} | {title} | {host} |\n")

print('OK — écrit dans', OUT)
for fn in sorted(os.listdir(OUT)):
    p = os.path.join(OUT, fn)
    print(f'  {fn}: {os.path.getsize(p)} octets')
