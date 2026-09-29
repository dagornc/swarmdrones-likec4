import json
model = json.load(open('/tmp/lc_v7/likec4.json'))
proj = model[0] if isinstance(model, list) else model
els = proj['elements']; rels = proj['relations']

# I-1 referential
bad = [r['id'] for r in rels.values() if r['source']['model'] not in els or r['target']['model'] not in els]
print('I-1 referentiel:', 'OK' if not bad else f'{len(bad)} broken')

# I-2 orphans
seen = set()
for r in rels.values():
    seen.add(r['source']['model']); seen.add(r['target']['model'])
def legit(v):
    md = v.get('metadata') or {}
    st = str(md.get('statut','')).upper()
    return v['kind']=='specDoc' and ('A CONSULTER' in st or 'ECARTEE' in st)
orphans = [k for k,v in els.items() if k not in seen and v['kind']!='renderRule' and not legit(v)]
print('I-2 orphelins:', 'OK' if not orphans else f'{len(orphans)} {orphans[:6]}')

# I-7 scientific coherence: findings (kind finding) must have verdict + at least one uses source
finds = [k for k,v in els.items() if v['kind']=='finding']
no_verdict = [k for k in finds if not ((els[k].get('metadata') or {}).get('verdict') or (els[k].get('metadata') or {}).get('statut'))]
print(f'I-7 coherence scientifique: {len(finds)} findings, {len(no_verdict)} sans verdict/statut', no_verdict[:5])

# counts
print('elements:', len(els), '| relations:', len(rels))
specs = [k for k,v in els.items() if v['kind']=='specDoc']
print('specDoc:', len(specs), '| finding:', len(finds))
