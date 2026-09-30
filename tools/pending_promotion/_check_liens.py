#!/usr/bin/env python3
"""Verification serveur des 11 liens internes (content-type + taille + sha256)."""
import hashlib
import subprocess
import sys
import urllib.request

SITE = "https://likec4.breizh.ai"
DISK = "/docker/likec4/workspace/public"
FILES = [
    "Spec_ALG_TASK_ALLOCATION_V3.pdf",
    "Spec_ALG_TASK_ALLOCATION_V2.pdf",
    "Spec_ALG_TASK_ALLOCATION_CBBA.pdf",
    "Specification_ALG_CONSENSUS_v1.pdf",
    "Specification_ALG_CONSENSUS_v2.pdf",
    "Specification_ALG_CONSENSUS_v3.pdf",
    "Specification_ALG_CONSENSUS_v4.pdf",
    "Specification_ALG_CONSENSUS_v5.pdf",
    "consensus_rs/README.md",
    "H-Zip_v2.2_Specification_premium.docx",
]


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "architecte-audit/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read()
        return r.status, r.headers.get("Content-Type", ""), body


def origin_fetch(rel: str):
    """docker exec likec4 curl -s http://localhost:5173/<rel> (origine, sans CDN)."""
    try:
        out = subprocess.run(
            ["docker", "exec", "likec4", "curl", "-s",
             f"http://localhost:5173/{rel}"],
            capture_output=True, timeout=60, check=False,
        )
    except (subprocess.SubprocessError, OSError) as exc:
        return None, str(exc)
    if out.returncode != 0:
        return None, f"rc={out.returncode}"
    return out.stdout, None


def main() -> int:
    print(f"{'STATUT':<8} {'CTYPE':<20} {'TAILLE':>9} {'SHA disque':<12} {'SHA servi':<12} {'SHA origine':<12} fichier")
    rc = 0
    for rel in FILES:
        disk_path = f"{DISK}/{rel}"
        disk_hash = sha256_file(disk_path)
        disk_size = 0
        with open(disk_path, "rb") as f:
            data = f.read()
            disk_size = len(data)
            disk_hash = sha256_bytes(data)
        try:
            status, ctype, body = fetch(f"{SITE}/{rel}")
            served_hash = sha256_bytes(body)
            served_size = len(body)
        except Exception as exc:  # noqa: BLE001
            print(f"ERREUR  fetch public {rel}: {exc}")
            rc = 1
            continue
        origin_body, origin_err = origin_fetch(rel)
        origin_hash = sha256_bytes(origin_body) if origin_body else "-"
        coherent = (status == 200 and disk_hash == served_hash == origin_hash)
        if not coherent:
            rc = 1
        print(f"{status:<8} {ctype:<20} {served_size:>9} {disk_hash[:10]:<12} "
              f"{served_hash[:10]:<12} {origin_hash[:10]:<12} {rel} "
              f"{'OK' if coherent else 'ECART'}")
        if origin_err:
            print(f"        origine: {origin_err}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
