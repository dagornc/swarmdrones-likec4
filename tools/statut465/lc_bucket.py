import json, os
from collections import Counter, defaultdict

catalog = json.load(open('/home/hermesagent/swarmdrone-research/catalog.json'))
da = json.load(open('/tmp/direct_A_465.json'))

ALG_KEYWORDS = {
 'algTaskAllocation': ['task allocation','task assignment','auction','cbba','market-based','multi-task','coverage control','area coverage','patrol','sweep'],
 'algConsensus': ['consensus','agreement','coordination','rendezvous','distributed averaging','flocking control'],
 'algFormationControl': ['formation','flocking','virtual structure','leader-follower formation','swarm formation','affine formation'],
 'algLeaderElection': ['leader election','leader-follower','virtual leader','leader selection','hierarchical leader'],
 'algPerceptionFusion': ['sensor fusion','data fusion','target tracking','multi-target tracking','detection','perception','object detection','tracking','vision','information fusion','belief'],
 'algNavigationGNSSDegrade': ['gnss-denied','gnss denied','gps-denied','visual-inertial','visual odometry','slam','localization','navigation','state estimation','vio','loop closure'],
 'algCollisionAvoidance': ['collision avoidance','collision-free','obstacle avoidance','cbf','control barrier','potential field','sense-and-avoid','separation'],
 'algSafetyRules': ['safety','safe control','barrier certificate','certification','airworthiness','assurance','safety-critical','fail-safe'],
 'algPathPlanning': ['path planning','trajectory planning','motion planning','rrt','a*','route planning','trajectory generation','waypoint'],
 'algHealthMonitoring': ['fault diagnosis','fault detection','health monitoring','anomaly detection','prognostic','fdd','degradation','fault isolation'],
 'algEnergyAware': ['energy','battery','power-aware','endurance','energy-aware','charging','energy consumption'],
 'algEventTriggeredComm': ['event-triggered','event triggered','communication scheduling','bandwidth','transmission','channel','communication-aware','sampling'],
 'algCooperativeLocalization': ['cooperative localization','relative localization','mutual localization','distributed estimation','cooperative positioning','uav-uav ranging'],
 'algFaultTolerantControlAlloc': ['fault-tolerant','fault tolerant','control allocation','actuator fault','reconfiguration','ftc','fault accommodation'],
 'algJammingResilientMode': ['jamming','anti-jamming','interference','gnss spoofing','gps spoofing','resilient communication','denial of service','adversarial'],
}

def buckets_of(rec):
    title = (rec.get('title') or '').lower()
    reason = ((rec.get('scope') or {}).get('reason') or '').lower()
    themes = [(t or '').lower() for t in (rec.get('scope') or {}).get('themes', [])]
    hay = title + ' ' + reason + ' ' + ' '.join(themes)
    hits = [a for a, kws in ALG_KEYWORDS.items() if any(k in hay for k in kws)]
    return hits

buckets = defaultdict(list)
nobucket = []
for r in da:
    h = buckets_of(r)
    if h:
        for a in h:
            buckets[a].append(r)
    else:
        nobucket.append(r)

print('=== BUCKET COUNTS (articles may hit multiple) ===')
for a in ALG_KEYWORDS:
    print(f'  {a:32s} {len(buckets[a]):4d}')

print()
print('NO-BUCKET (no keyword match):', len(nobucket))

# Save bucket mapping
out = {}
for r in da:
    out[str(r['number'])] = buckets_of(r)
json.dump(out, open('/tmp/da_buckets.json','w'), ensure_ascii=False, indent=1)

# Save sorted order: bucket, then number
order = []
seen = set()
for a in ALG_KEYWORDS:
    for r in buckets[a]:
        if r['number'] not in seen:
            order.append(r['number'])
            seen.add(r['number'])
for r in nobucket:
    if r['number'] not in seen:
        order.append(r['number'])
        seen.add(r['number'])
json.dump(order, open('/tmp/da_order.json','w'))
print('TOTAL ORDERED:', len(order))
