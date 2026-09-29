import re, json, glob, os
BASE = '/home/hermesagent/workspace/swarmdrones_likec4'
files = glob.glob(BASE + '/*.c4')
alltxt = {}
for fp in files:
    alltxt[os.path.basename(fp)] = open(fp, encoding='utf-8').read()

# collect specDocs with ids, file, and identifiers
specdocs = []  # (file, id, block)
for fp in files:
    txt = alltxt[os.path.basename(fp)]
    for m in re.finditer(r'^\s{2}(\w+) = specDoc (.*?)(?=\n\s{2}\w+ = |\n\Z)', txt, re.S | re.M):
        specdocs.append((os.path.basename(fp), m.group(1), m.group(0)))

def ids_of(block):
    dois = set(re.findall(r'(?:https://doi\.org/|doi\s+\')(10\.\d{4,9}/[^\s\'"\)]+)', block))
    arx = set(re.findall(r'(?:arxiv\.org/(?:abs|pdf)/|arxiv\s+\')(\d{4}\.\d{4,5})', block))
    corp = set(re.findall(r"corpus\s+'#?(\d+)'", block))
    return dois, arx, corp

# which specDocs are used by a finding via -[uses]->
used_by_finding = set()
for fp in files:
    txt = alltxt[os.path.basename(fp)]
    for m in re.finditer(r'(\w+)\s+-\[uses\]->\s+(\w+)', txt):
        used_by_finding.add((m.group(2), os.path.basename(fp), m.group(1)))

catalog = json.load(open('/home/hermesagent/swarmdrone-research/catalog.json'))
by_num = {a['number']: a for a in catalog}
da = json.load(open('/tmp/direct_A_465.json'))

doi_idx, arx_idx, corp_idx = {}, {}, {}
for f, sid, block in specdocs:
    dois, arxs, corps = ids_of(block)
    for d in dois: doi_idx.setdefault(d.lower(), []).append((f, sid))
    for a in arxs: arx_idx.setdefault(a.lower(), []).append((f, sid))
    for c in corps: corp_idx.setdefault(c, []).append((f, sid))

used = {sid for (sid, f, who) in used_by_finding}

already = {}
for rec in da:
    n = rec['number']
    match = []
    for d in (rec.get('dois') or []): match += doi_idx.get(d.lower(), [])
    for a in (rec.get('arxiv_ids') or []): match += arx_idx.get(a.lower(), [])
    match += corp_idx.get(str(n), [])
    uniq = sorted(set(match))
    if uniq:
        already[n] = uniq

attached = []
declared_only = []
for n in sorted(already):
    for f, sid in already[n]:
        if sid in used:
            attached.append((n, f, sid))
        else:
            declared_only.append((n, f, sid))

print('=== 465 avec specDoc existant: %d ===' % len(already))
print('--- DEJA RATTACHEES (specDoc lie a un finding): %d ---' % len(attached))
for n, f, sid in attached:
    print(f'  #{n} -> {sid} ({f})')
print('--- DECLAREES mais NON liees a un finding (a statuer): %d ---' % len(declared_only))
for n, f, sid in declared_only:
    print(f'  #{n} -> {sid} ({f})')

json.dump({'attached': attached, 'declared_only': declared_only, 'already': {str(k):v for k,v in already.items()}},
          open('/tmp/lc_already.json','w'), ensure_ascii=False, indent=1)
print('saved /tmp/lc_already.json')
