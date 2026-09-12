"""Collect QCi job identifiers into the tracked manifest.

WHY. `experiments/results/pools/` is gitignored, so the raw hardware responses
do NOT ship. Job ids recoverable only from those files are recoverable only on
the machine that ran them -- which is not what "retained for audit" means to a
reviewer with a fresh clone. This lifts every id we hold into
`hw_job_ids.json`, which IS tracked.

Found by internal review: three documents claimed B2's eleven ids were retained
while the shipped artifacts carried none of them.

    python experiments/src/collect_job_ids.py [--check]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import store  # noqa: E402

RESULTS = Path(__file__).resolve().parents[1] / "results"
OUT = RESULTS / "hw_job_ids.json"
RESP = RESULTS / "pools" / "hw_responses"
ID_RE = re.compile(r"['\"]job_id['\"]:\s*['\"]([0-9a-f]{24})['\"]")


def _from_responses() -> dict[str, str]:
    """Cell label -> job id, for every retained response file."""
    found: dict[str, str] = {}
    if not RESP.exists():
        return found
    for f in sorted(RESP.glob("*.json")):
        try:
            text = json.loads(f.read_text(encoding="utf-8"))
        except Exception:                              # noqa: BLE001
            continue
        if not isinstance(text, str):
            text = json.dumps(text)
        m = ID_RE.search(text)
        if m:
            found[f.stem] = m.group(1)
    return found


def build() -> dict:
    prior = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    ids = list(prior.get("job_ids", []))

    by_cell = dict(prior.get("by_cell") or {})
    by_cell.update(_from_responses())

    b3 = RESULTS / "b3_hardware.json"
    if b3.exists():
        for r in json.loads(b3.read_text(encoding="utf-8"))["rows"]:
            if r.get("job_id"):
                by_cell[f"b3_k{r['k']}_fold{r['fold']}"] = r["job_id"]

    for v in by_cell.values():
        if v not in ids:
            ids.append(v)

    return {
        "note": ("QCi job identifiers retained for audit. `by_cell` maps each cell "
                 "to its id; `job_ids` is the flat list. The raw responses live "
                 "under experiments/results/pools/, which is NOT tracked, so ids "
                 "recoverable only from those files would not reach a reviewer -- "
                 "they are lifted here instead."),
        "generator": "experiments/src/collect_job_ids.py",
        "n": len(ids),
        "by_cell": dict(sorted(by_cell.items())),
        "job_ids": ids,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    built = build()
    if args.check:
        shipped = json.loads(OUT.read_text(encoding="utf-8"))
        if shipped.get("n") != built["n"]:
            print(f"MISMATCH: shipped n={shipped.get('n')}, rebuilt n={built['n']}")
            return 1
        print(f"hw_job_ids.json current: {built['n']} identifiers")
        return 0
    store.atomic_write_json(OUT, built)
    print(f"hw_job_ids.json: {built['n']} identifiers, "
          f"{len(built['by_cell'])} mapped to cells")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
