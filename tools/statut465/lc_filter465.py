import json
from collections import Counter

c = json.load(open('/home/hermesagent/swarmdrone-research/catalog.json'))

# Inspect scope structure
scope_sample = c[0]['scope']
print('SCOPE SAMPLE:', json.dumps(scope_sample, ensure_ascii=False)[:300])

trusts = Counter()
scope_levels = Counter()
scope_reason_sample = {}

direct_A = []
for a in c:
    trusts[a.get('trust')] += 1
    sc = a.get('scope') or {}
    lvl = sc.get('level')
    scope_levels[lvl] += 1
    if lvl == 'direct' and a.get('trust') == 'A-primary-candidate':
        direct_A.append(a)

print()
print('TRUST COUNTS:', dict(trusts))
print('SCOPE LEVEL COUNTS:', dict(scope_levels))
print('DIRECT + A-PRIMARY:', len(direct_A))

# Year distribution
years = Counter()
for a in direct_A:
    dates = a.get('claimed_publication_dates') or []
    if dates:
        years[dates[0][:4]] += 1
    else:
        years['NODATE'] += 1
print('YEAR DIST:', dict(sorted(years.items())))

# scope.reason samples
print()
print('SCOPE.REASON values (top):')
rc = Counter()
for a in direct_A:
    rc[(a.get('scope') or {}).get('reason','')] += 1
for r, n in rc.most_common(30):
    print(f'  {n:4d}  {r[:100]}')

# Save the 465 to a working file
with open('/tmp/direct_A_465.json','w') as f:
    json.dump(direct_A, f, ensure_ascii=False, indent=1)
print()
print('Saved /tmp/direct_A_465.json with', len(direct_A), 'records')
