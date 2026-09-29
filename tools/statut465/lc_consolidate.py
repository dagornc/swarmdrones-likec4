import json, glob, os

CAT = '/home/hermesagent/swarmdrone-research/catalog.json'
catalog = json.load(open(CAT))
by_num = {a['number']: a for a in catalog}

consolidated = []
for i in range(1, 20):
    lp = f'/tmp/ledger_lot{i:02d}.json'
    if not os.path.exists(lp):
        continue
    d = json.load(open(lp))
    lot = i
    for r in d.get('rattachees', []):
        rec = by_num.get(int(r['metadata']['corpus']))
        consolidated.append({
            'number': int(r['metadata']['corpus']),
            'title': rec['title'] if rec else r['title'],
            'status': 'RATTACHEE',
            'specdoc': r['src'],
            'finding': r['finding']['id'],
            'algs': [a for a,_ in r['algs']],
            'lot': lot
        })
    for r in d.get('specdoc_only', []):
        rec = by_num.get(int(r['metadata']['corpus']))
        consolidated.append({
            'number': int(r['metadata']['corpus']),
            'title': rec['title'] if rec else r['title'],
            'status': 'RATTACHEE',
            'specdoc': r['src'],
            'finding': r['target_finding'] + ' (completion)',
            'algs': [],
            'lot': lot
        })
    for r in d.get('deja', []):
        rec = by_num.get(r['number'])
        consolidated.append({
            'number': r['number'],
            'title': rec['title'] if rec else r['title'],
            'status': 'DEJA_RATTACHEE',
            'specdoc': r['existing_src'],
            'finding': r['existing_finding'],
            'algs': [],
            'lot': lot
        })
    for r in d.get('ecartees', []):
        rec = by_num.get(r['number'])
        consolidated.append({
            'number': r['number'],
            'title': rec['title'] if rec else r['title'],
            'status': 'ECARTEE',
            'reason': r['reason'],
            'specdoc': '',
            'finding': '',
            'algs': [],
            'lot': lot
        })

# de-dup by number (some lots may overlap; shouldn't, but safety)
seen = set()
final = []
for c in consolidated:
    if c['number'] not in seen:
        seen.add(c['number'])
        final.append(c)

final.sort(key=lambda x: x['number'])
print('total statued:', len(final))
from collections import Counter
print(Counter(c['status'] for c in final))

json.dump(final, open('/home/hermesagent/workspace/swarmdrones_likec4/tools/statut465/ledger_statut_465.json','w'),
          ensure_ascii=False, indent=1)
print('written tools/statut465/ledger_statut_465.json')
