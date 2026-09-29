import json
from collections import defaultdict

catalog = json.load(open('/home/hermesagent/swarmdrone-research/catalog.json'))
da = json.load(open('/tmp/direct_A_465.json'))
buckets = json.load(open('/tmp/da_buckets.json'))  # number(str) -> [alg...]

ALG_ORDER = [
 'algLeaderElection','algHealthMonitoring','algCooperativeLocalization',
 'algFaultTolerantControlAlloc','algJammingResilientMode','algSafetyRules',
 'algEventTriggeredComm','algEnergyAware','algCollisionAvoidance',
 'algFormationControl','algConsensus','algTaskAllocation','algPathPlanning',
 'algNavigationGNSSDegrade','algPerceptionFusion',
]

by_bucket = defaultdict(list)
for num, algs in buckets.items():
    for a in algs:
        by_bucket[a].append(int(num))
# sort each bucket by number
for a in by_bucket:
    by_bucket[a].sort()

ordered = []
seen = set()
for a in ALG_ORDER:
    for n in by_bucket.get(a, []):
        if n not in seen:
            ordered.append(n); seen.add(n)
# remainder: no bucket
for r in da:
    n = r['number']
    if n not in seen:
        ordered.append(n); seen.add(n)

print('ordered unique:', len(ordered))
json.dump(ordered, open('/tmp/da_order_unique.json','w'))

# split into lots of 25
LOT = 25
lots = [ordered[i:i+LOT] for i in range(0, len(ordered), LOT)]
print('lots:', len(lots), 'sizes:', [len(l) for l in lots])
for i, l in enumerate(lots):
    json.dump(l, open(f'/tmp/lot_{i+1:02d}.json','w'))
print('wrote /tmp/lot_*.json')
