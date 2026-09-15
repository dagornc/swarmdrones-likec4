"""Mesure objective d'une image PNG : preuve qu'elle contient du contenu.

Ne suppose pas que le rendu est correct : le mesure. Decodeur PNG minimal
(sans dependance externe) puis statistiques de pixels.
"""
import struct
import sys
import zlib
from pathlib import Path

BG = (11, 15, 20)


def decode(path):
    d = Path(path).read_bytes()
    if d[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit("pas un PNG")
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
    out = []
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
        out.append(bytes(line))
        prev = line
    return w, h, ch, out


def main(path, bands=2):
    w, h, ch, rows = decode(path)
    print(f"PNG {w}x{h} canaux={ch}")
    total_nonbg = 0
    for band in range(bands):
        y0, y1 = band * h // bands, (band + 1) * h // bands
        nb = 0
        colors = set()
        for y in range(y0, y1, 3):
            line = rows[y]
            for x in range(0, w, 3):
                r, g, b = line[x * ch], line[x * ch + 1], line[x * ch + 2]
                if abs(r - BG[0]) + abs(g - BG[1]) + abs(b - BG[2]) > 24:
                    nb += 1
                    colors.add((r // 24, g // 24, b // 24))
        tot = max(((y1 - y0) // 3) * (w // 3), 1)
        print(f"  bande {band+1}: non-fond={100*nb/tot:5.1f}%  couleurs={len(colors)}")
        total_nonbg += nb
    verdict = "CONTENU PRESENT" if total_nonbg > 2000 else "IMAGE QUASI VIDE"
    print(f"TOTAL non-fond echantillonne={total_nonbg} -> {verdict}")
    return 0 if total_nonbg > 2000 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "assets/preview.png"))
