"""Verifie que le rendu de preview CONTIENT reellement les assets.

Un fichier PNG qui existe ne prouve rien : le premier rendu produit une image
uniforme (6 couleurs). Ce test ECHOUE si l'image est plate, ce qui rend la
verification falsifiable.

Critere : au moins N couleurs distinctes et une part significative de pixels
non-fond. Un rendu vide echoue ; un rendu correct passe.
"""
import struct
import sys
import zlib
from collections import Counter
from pathlib import Path

MIN_COULEURS = 200
MIN_NONFOND_PCT = 8.0


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
    # le fond = couleur la plus frequente
    bg, bgn = hist.most_common(1)[0]
    nonfond = total - bgn
    pct = 100 * nonfond / total
    ncols = len([c for c, _ in hist.items() if c != bg])

    print(f"PNG {w}x{h}  fond={bg} ({100*bgn/total:.1f}%)  "
          f"non-fond={pct:.1f}%  couleurs_hors_fond={ncols}")

    ok = True
    if ncols < MIN_COULEURS:
        print(f"FAIL: rendu quasi uniforme — {ncols} couleurs < {MIN_COULEURS} attendues")
        ok = False
    if pct < MIN_NONFOND_PCT:
        print(f"FAIL: les assets n'occupent pas l'image — non-fond {pct:.1f}% < {MIN_NONFOND_PCT}%")
        ok = False

    print(f"{'OK' if ok else 'FAIL'} — rendu de preview contient les assets")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "assets/preview.png"))
