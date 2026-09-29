import json, os, re, sys

CAT = '/home/hermesagent/swarmdrone-research/catalog.json'
ART = '/home/hermesagent/swarmdrone-research/articles'
catalog = json.load(open(CAT))
by_num = {a['number']: a for a in catalog}

def get_abstract(filename):
    p = os.path.join(ART, filename)
    if not os.path.exists(p):
        return None
    txt = open(p, encoding='utf-8', errors='replace').read()
    m = re.search(r'## Abstract\s*\n(.*?)(?=\n## |\Z)', txt, re.S)
    if not m:
        m = re.search(r'(?i)abstract\s*\n+(.{200,})', txt, re.S)
    if m:
        return re.sub(r'\s+', ' ', m.group(1)).strip()
    return None

def card(num, maxabs=900):
    a = by_num.get(num)
    if not a:
        return f'#{num}: MISSING'
    dates = a.get('claimed_publication_dates') or []
    year = dates[0][:4] if dates else '?'
    dois = a.get('dois') or []
    arx = a.get('arxiv_ids') or []
    ident = ''
    if dois: ident += 'DOI:' + ','.join(dois) + ' '
    if arx: ident += 'arXiv:' + ','.join(arx) + ' '
    if not ident: ident = a.get('source_url','')[:70]
    themes = (a.get('scope') or {}).get('themes') or []
    ab = get_abstract(a['filename'])
    if ab:
        ab = ab[:maxabs]
    else:
        ab = '(pas d abstract extrait)'
    return (f"#{num} [{year}] {a['title'][:150]}\n"
            f"    id: {ident.strip()}\n"
            f"    themes: {','.join(themes)}\n"
            f"    abs: {ab}\n")

if __name__ == '__main__':
    order = json.load(open('/tmp/da_order.json'))
    nums = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else order
    out = '\n'.join(card(n) for n in nums)
    print(out)
