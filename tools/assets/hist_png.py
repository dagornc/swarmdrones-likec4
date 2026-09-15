"""Diagnostic : quelles sont les couleurs REELLES de l'image ?

Le test precedent a trouve 100% de non-fond mais une seule couleur : soit le
fond reel differe de l'hypothese, soit le rendu est uniforme. On mesure
l'histogramme reel au lieu de supposer.
"""
import struct
import sys
import zlib
from collections import Counter
from pathlib import Path


def decode(path):
    d = Path(path).read_bytes()
    w, h, bd, ct = struct.unpack(">IIBB", d[16:26])
    idat = b""
    pos = 8
    while pos < len(d):
        ln = struct.unpack(">I", d[pos:pos + 4])[0]
        typ = d[pos + 4:pos + 8]
        if typ == b"IDAT":
            idat += d[pos + 8:pos + 8 + ln]
        pos += 12 + ln
    raw = zlib.decompress(idat)
    ch = 4 if ct == 6 else 3
    rows = []
    prev = bytearray(w * ch)
    p = 0
    for _ in range(h):
        f = raw[p]; p += 1
        line = bytearray(raw[p:p + w * ch]); p += w * ch
        if f == 1:
            for i in range(ch, len(line)):
                line[i] = (line[i] + line[i - ch]) & 255
        elif f == 2:
            for i in range(len(line)):
                line[i] = (line[i] + prev[i]) & 255
        elif f == 3:
            for i in range(len(line)):
                a = line[i - ch] if i >= ch else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 255
        elif f == 4:
            for i in range(len(line)):
                a = line[i - ch] if i >= ch else 0
                b = prev[i]
                c = prev[i - ch] if i >= ch else 0
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 255
        rows.append(bytes(line))
        prev = line
    return w, h, ch, rows


def main(path):
    w, h, ch, rows = decode(path)
    hist = Counter()
    for y in range(0, h, 2):
        line = rows[y]
        for x in range(0, w, 2):
            hist[(line[x * ch], line[x * ch + 1], line[x * ch + 2])] += 1
    total = sum(hist.values())
    print(f"PNG {w}x{h} canaux={ch}  echantillons={total}")
    print("Top 12 couleurs (RGB : part) :")
    for c, n in hist.most_common(12):
        print(f"  {c}  {100*n/total:5.1f}%")
    print(f"couleurs distinctes (echantillon): {len(hist)}")
    # est-ce uniformement sombre ?
    moy = sum((r + g + b) / 3 * n for (r, g, b), n in hist.items()) / total
    print(f"luminosite moyenne = {moy:.1f}/255")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "assets/preview.png"))
