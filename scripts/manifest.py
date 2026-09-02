"""Data provenance manifest generator and verifier (ADR-0003; disposition item 9).

Lives in scripts/ (process tooling), NOT experiments/src/ (frozen at prereg-freeze).
Dataset locations come from the frozen loader module experiments/src/data.py, the
single source of truth, so the manifest always attests the exact files the loaders
read. Manifest entries are keyed by portable logical names (e.g. "ulb/creditcard.csv"),
never machine paths, so the committed MANIFEST.json is valid on any clone.

Known failure modes: a staged file changed legitimately (re-download) -> regenerate
after confirming provenance; ULB lives OUTSIDE this repo (XGBvHQXGB checkout) by
ADR-0003 -- on another machine set ULB_CSV to its creditcard.csv path.

Usage:
  python scripts/manifest.py generate   # writes experiments/data/MANIFEST.json
  python scripts/manifest.py verify     # exits 1 on any missing/extra/changed file
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "experiments" / "src"))
import data  # noqa: E402  (frozen module; read-only import)

DATA = REPO / "experiments" / "data"
MANIFEST = DATA / "MANIFEST.json"
ULB_CSV = Path(os.environ.get("ULB_CSV", str(data.ULB_CSV)))


def required() -> dict[str, Path]:
    """Logical key -> path for every file the frozen loaders read. Missing any
    of these is a hard failure in both generate and verify."""
    req = {"ulb/creditcard.csv": ULB_CSV}
    for name in data.SPECTRA_NAMES:
        req[f"spectra/spectra_{name}.csv"] = data.SPECTRA_DIR / f"spectra_{name}.csv"
    for f in ("train_transaction.csv", "train_identity.csv"):
        req[f"ieee-cis/{f}"] = data.IEEE_CIS_DIR / f
    return req


def staged() -> dict[str, Path]:
    """required() plus every other CSV staged in the data dirs (e.g. IEEE-CIS
    test files, ULB variants). All of it gets checksummed."""
    files = dict(required())
    for sub in ("spectra", "ieee-cis"):
        d = DATA / sub
        if d.is_dir():
            for p in sorted(d.glob("*.csv")):
                files.setdefault(f"{sub}/{p.name}", p)
    if ULB_CSV.parent.is_dir():
        for p in sorted(ULB_CSV.parent.glob("creditcard*.csv")):
            files.setdefault(f"ulb/{p.name}", p)
    return files


def _entry(p: Path) -> dict:
    h = hashlib.sha256()
    lines = 0
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
            lines += chunk.count(b"\n")
    return {"sha256": h.hexdigest(), "bytes": p.stat().st_size, "lines": lines}


def generate() -> int:
    files = staged()
    missing = [k for k, p in required().items() if not p.exists()]
    if missing:
        print(f"FAIL: required dataset files missing, no manifest written: {missing}")
        return 1
    entries = {k: _entry(p) for k, p in sorted(files.items()) if p.exists()}
    MANIFEST.write_text(json.dumps(
        {"generated": time.strftime("%Y-%m-%dT%H:%M:%S"), "files": entries}, indent=1))
    for k, e in entries.items():
        print(f"{k}: {e['bytes']:>11,} B  {e['lines']:>9,} lines  {e['sha256'][:12]}")
    print(f"MANIFEST written: {len(entries)} files")
    return 0


def verify() -> int:
    if not MANIFEST.exists():
        print("FAIL: no MANIFEST.json; run generate first")
        return 1
    recorded = json.loads(MANIFEST.read_text())["files"]
    files = staged()
    ok = True
    for k in required():
        if k not in recorded:
            print(f"FAIL required file absent from manifest: {k}")
            ok = False
    for k, rec in recorded.items():
        p = files.get(k)
        if p is None or not p.exists():
            print(f"FAIL missing on disk: {k}")
            ok = False
            continue
        if _entry(p)["sha256"] != rec["sha256"]:
            print(f"FAIL checksum: {k}")
            ok = False
    for k in files:
        if k not in recorded and files[k].exists():
            print(f"FAIL staged file not in manifest (regenerate + re-audit): {k}")
            ok = False
    print("VERIFY OK" if ok else "VERIFY FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "verify"
    sys.exit({"generate": generate, "verify": verify}[mode]())
