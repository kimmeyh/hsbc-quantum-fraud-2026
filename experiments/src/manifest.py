"""Data provenance manifest generator and verifier (ADR-0003; disposition item 9).

Known failure modes: a staged file changed legitimately (re-download) -> regenerate
after confirming provenance; ULB lives OUTSIDE this repo (XGBvHQXGB checkout) by
ADR-0003, so a missing ULB path means that checkout moved, not data loss.

Usage:
  python experiments/src/manifest.py generate   # writes experiments/data/MANIFEST.json
  python experiments/src/manifest.py verify     # exits 1 on any mismatch
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

DATA = Path(__file__).parents[1] / "data"
MANIFEST = DATA / "MANIFEST.json"
ULB_DIR = Path(r"D:\Data\Harold\github\XGBvHQXGB\datasets")

TRACKED = sorted(
    [*ULB_DIR.glob("creditcard*.csv"),
     *(DATA / "spectra").glob("*.csv"),
     *(DATA / "ieee-cis").glob("*.csv")]
)


def _entry(p: Path) -> dict:
    h = hashlib.sha256()
    lines = 0
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
            lines += chunk.count(b"\n")
    return {"path": str(p), "sha256": h.hexdigest(), "bytes": p.stat().st_size,
            "lines": lines}


def generate() -> None:
    entries = [_entry(p) for p in TRACKED]
    MANIFEST.write_text(json.dumps(
        {"generated": time.strftime("%Y-%m-%dT%H:%M:%S"), "files": entries}, indent=1))
    for e in entries:
        print(f"{Path(e['path']).name}: {e['bytes']:>11,} B  {e['lines']:>9,} lines  {e['sha256'][:12]}")
    print(f"MANIFEST written: {len(entries)} files")


def verify() -> int:
    if not MANIFEST.exists():
        print("FAIL: no MANIFEST.json; run generate first")
        return 1
    recorded = {e["path"]: e for e in json.loads(MANIFEST.read_text())["files"]}
    ok = True
    for path, rec in recorded.items():
        p = Path(path)
        if not p.exists():
            print(f"FAIL missing: {path}")
            ok = False
            continue
        cur = _entry(p)
        if cur["sha256"] != rec["sha256"]:
            print(f"FAIL checksum: {path}")
            ok = False
    extra = [str(p) for p in TRACKED if str(p) not in recorded]
    if extra:
        print(f"WARN untracked staged files: {extra}")
    print("VERIFY OK" if ok else "VERIFY FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "verify"
    sys.exit({"generate": lambda: generate() or 0, "verify": verify}[mode]())
