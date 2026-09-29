import re, sys
inp = sys.argv[1] if len(sys.argv) > 1 else '/tmp/lot01_additions.c4'
prefix = inp.rsplit('/',1)[-1].replace('_additions.c4','')
txt = open(inp).read()

rel_marker = "  // --- Relations du lot ---"
idx_rel = txt.find(rel_marker)
part_sf = txt[:idx_rel]
part_rel = txt[idx_rel:]

m = re.search(r'^  \w+ = finding ', part_sf, re.M)
if m:
    idx_f = m.start()
    part_spec = part_sf[:idx_f]
    part_find = part_sf[idx_f:]
else:
    part_spec, part_find = part_sf, ''

open(f'/tmp/{prefix}_specdocs.c4','w').write(part_spec)
open(f'/tmp/{prefix}_findings.c4','w').write(part_find)
open(f'/tmp/{prefix}_relations.c4','w').write(part_rel)
print(f'{prefix}: specdocs={part_spec.count("= specDoc")} findings={part_find.count("= finding")} rels={part_rel.count("-(")}')
