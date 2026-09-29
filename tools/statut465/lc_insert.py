import sys

BASE = '/home/hermesagent/workspace/swarmdrones_likec4/science.c4'
prefix = sys.argv[1] if len(sys.argv) > 1 else 'lot01'
txt = open(BASE, encoding='utf-8').read()

spec = open(f'/tmp/{prefix}_specdocs.c4', encoding='utf-8').read().strip()
find = open(f'/tmp/{prefix}_findings.c4', encoding='utf-8').read().strip()
rels = open(f'/tmp/{prefix}_relations.c4', encoding='utf-8').read().strip()

def insert_before(t, marker, block):
    i = t.find(marker)
    assert i != -1, f'marker not found: {marker!r}'
    return t[:i] + block + '\n\n' + t[i:]

m2 = '  // ===========================================================================\n  //  2. VERDICTS'
banner_spec = (
    "  // ===========================================================================\n"
    f"  //  1quater. SOURCES AJOUTEES — carte t_3f3134cc {prefix.upper()} (2026-09-29)\n"
    "  // ===========================================================================\n\n"
)
txt = insert_before(txt, m2, banner_spec + spec)

m3 = '  // ===========================================================================\n  //  3. TROUS DE BENCHMARK'
banner_find = (
    "  // ===========================================================================\n"
    f"  //  2bis. VERDICTS AJOUTES — carte t_3f3134cc {prefix.upper()} (2026-09-29)\n"
    "  // ===========================================================================\n\n"
)
txt = insert_before(txt, m3, banner_find + find)

last = txt.rstrip()
assert last.endswith('}'), 'file does not end with }'
i = last.rfind('}')
banner_rel = f"  // --- Rattachements carte t_3f3134cc {prefix.upper()} (2026-09-29) ---\n"
txt = last[:i] + banner_rel + rels + '\n' + last[i:]

open(BASE, 'w', encoding='utf-8').write(txt)
print(f'OK — science.c4 updated with {prefix}')
