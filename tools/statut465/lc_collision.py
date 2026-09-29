import re, json, glob, os

BASE = '/home/hermesagent/workspace/swarmdrones_likec4'
files = glob.glob(BASE + '/*.c4')

# Parse all specDoc declarations: id + block text
specdocs = []  # (file, id, block)
for fp in files:
    txt = open(fp, encoding='utf-8').read()
    for m in re.finditer(r'^\s{2}(\w+) = specDoc (.*?)(?=\n\s{2}\w+ = |\n\Z)', txt, re.S | re.M):
        specdocs.append((os.path.basename(fp), m.group(1), m.group(0)))

print('TOTAL specDocs in all files:', len(specdocs))

# Extract identifiers from each block: doi, arxiv, corpus
def ids_of(block):
    dois = re.findall(r'(?:https://doi\.org/|doi\s+\')(10\.\d{4,9}/[^\s\'"\)]+)', block)
    arx = re.findall(r'(?:arxiv\.org/(?:abs|pdf)/|arxiv\s+\')(\d{4}\.\d{4,5})', block)
    corp = re.findall(r"corpus\s+'#?(\d+)'", block)
    return set(dois), set(arx), set(corp)

catalog = json.load(open('/home/hermesagent/swarmdrone-research/catalog.json'))
by_num = {a['number']: a for a in catalog}
da = json.load(open('/tmp/direct_A_465.json'))

# Build index: identifier -> list of (file, specdoc_id)
doi_idx = {}
arx_idx = {}
corp_idx = {}
for f, sid, block in specdocs:
    dois, arxs, corps = ids_of(block)
    for d in dois: doi_idx.setdefault(d.lower(), []).append((f, sid))
    for a in arxs: arx_idx.setdefault(a.lower(), []).append((f, sid))
    for c in corps: corp_idx.setdefault(c, []).append((f, sid))

# For each of the 465, find existing specDocs
hits = {}
for rec in da:
    n = rec['number']
    match = []
    for d in (rec.get('dois') or []):
        match += doi_idx.get(d.lower(), [])
    for a in (rec.get('arxiv_ids') or []):
        match += arx_idx.get(a.lower(), [])
    match += corp_idx.get(str(n), [])
    # dedupe
    uniq = sorted(set(match))
    if uniq:
        hits[n] = uniq

print('Articles des 465 avec specDoc deja present:', len(hits))
for n in sorted(hits):
    rec = by_num[n]
    print(f"  #{n} {rec['title'][:60]}")
    for f, sid in hits[n]:
        print(f"       -> {f} :: {sid}")
