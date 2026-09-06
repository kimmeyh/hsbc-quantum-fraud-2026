"""IEEE-CIS loader report: row/column counts, fraud prevalence, and a
checksum-manifest consistency check. Sprint 6 Task B (F3 prep, issue #32):
PREPARATION ONLY -- reports on the already-frozen `data.load_ieee_cis_train`
join; fits no model, writes no results.json row.

Manifest note: checksum GENERATION lives in scripts/manifest.py (process
tooling, outside the experiments/src freeze, per that module's own
docstring). This module does not duplicate the generator; it independently
recomputes the sha256 of the two IEEE-CIS train files it reads and asserts
the value matches the committed experiments/data/MANIFEST.json entry, so a
loader run is self-verifying against the frozen manifest without importing
scripts/ from inside the frozen src/ tree.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import data

MANIFEST_PATH = Path(__file__).resolve().parents[1] / "data" / "MANIFEST.json"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def manifest_entry_for(logical_key: str) -> dict | None:
    """Look up one logical-key entry ('ieee-cis/train_transaction.csv') in
    the committed MANIFEST.json. Returns None if the manifest or the key
    is absent (caller decides whether that is fatal)."""
    if not MANIFEST_PATH.exists():
        return None
    entries = json.loads(MANIFEST_PATH.read_text())["files"]
    return entries.get(logical_key)



def dedupe_ieee(df):
    """Remove exact duplicates before splitting, per section 4 item 7.

    The protocol says "exact duplicates removed before splitting; counts
    reported PER DATASET". The ULB loaders implement it; this path did not, and
    that is the same omission amendment A17 recorded for the exploratory pool
    modules, in code written in the same sprint.

    On IEEE-CIS the effect is nil rather than merely small: 6 rows sit in
    duplicate feature-groups and NONE is a fraud, against ULB's 1,854 rows at a
    tenfold fraud enrichment where removal moved a result across the MDE. We
    still do it, and still report the count, because "it would not have
    mattered" is a conclusion only available after checking.

    TransactionID is excluded from the duplicate key: it is a unique row
    identifier, so including it would make every row unique and the check
    vacuous. Returns (deduplicated_df, n_removed).
    """
    key = [c for c in df.columns if c != "TransactionID"]
    before = len(df)
    out = df.drop_duplicates(subset=key).reset_index(drop=True)
    return out, before - len(out)

def verify_checksums() -> dict:
    """Recompute sha256 for train_transaction.csv and train_identity.csv
    and compare against MANIFEST.json. Returns a dict keyed by logical
    name with {"sha256", "matches_manifest"} -- never raises on mismatch
    (a report function), callers assert as they see fit."""
    report = {}
    for fname in ("train_transaction.csv", "train_identity.csv"):
        key = f"ieee-cis/{fname}"
        path = data.IEEE_CIS_DIR / fname
        if not path.exists():
            # The docstring promises a report, not an exception. _sha256 would
            # raise FileNotFoundError here, so an absent file crashed a function
            # callers are told is safe to call (PR #36 review finding 13).
            report[key] = {"sha256": None, "manifest_sha256": None,
                           "matches_manifest": False, "status": "FILE MISSING",
                           "path": str(path)}
            continue
        digest = _sha256(path)
        recorded = manifest_entry_for(key)
        report[key] = {
            "sha256": digest,
            "manifest_sha256": recorded["sha256"] if recorded else None,
            "matches_manifest": bool(recorded) and digest == recorded["sha256"],
        }
    return report


def load_report() -> dict:
    """The Task B deliverable: join transaction+identity (via the frozen
    data.load_ieee_cis_train), report row/column counts and fraud
    prevalence, and attach the manifest checksum check. Loads the FULL
    600MB+ file -- exercised manually / in the manually-run path, never
    from the automated test suite (see test_ieee_features.py, which uses
    a small sampled fixture instead)."""
    raw = data.load_ieee_cis_train()
    df, n_dupes = dedupe_ieee(raw)
    rows, cols = df.shape
    prevalence = float(df["isFraud"].mean())
    return {
        "rows_raw": len(raw),
        "rows": rows,
        # Section 4 item 7 asks for the count, not just the action, so the
        # report carries it whether or not it is interesting. On IEEE-CIS it is
        # 6 rows and none of them fraud; on ULB the same step removes 1,854 rows
        # at a tenfold fraud enrichment and moved a result across the MDE (A17).
        "exact_duplicates_removed": n_dupes,
        "cols": cols,
        "fraud_count": int(df["isFraud"].sum()),
        "fraud_prevalence": round(prevalence, 6),
        "checksums": verify_checksums(),
    }


if __name__ == "__main__":
    report = load_report()
    print(json.dumps(report, indent=2))
