"""Tests for ieee_loader.py: checksum-manifest consistency (Sprint 6 Task
B, F3 prep, issue #32). PREPARATION ONLY -- checks provenance plumbing;
does not fit a model arm and does not write a results.json row.

The full `load_report()` reads both 600MB+/25MB IEEE-CIS train CSVs (a
join over 590,540 rows). That full path is exercised MANUALLY only
(`python experiments/src/ieee_loader.py`), per the memory-budget
instruction; this automated suite checks the checksum/manifest plumbing
against the real files on disk (I/O-bound, no join, no dtype parsing) plus
pure-Python manifest-lookup logic, so it stays fast under pytest.

Run: .venv\\Scripts\\python.exe -m pytest experiments/src/test_ieee_loader.py -q
"""
from __future__ import annotations

import json

import pytest

import ieee_loader as L
import data


def test_manifest_file_exists():
    assert L.MANIFEST_PATH.exists(), "experiments/data/MANIFEST.json missing"


def test_ieee_cis_files_present_on_disk():
    for fname in ("train_transaction.csv", "train_identity.csv"):
        assert (data.IEEE_CIS_DIR / fname).exists()


@pytest.mark.parametrize("fname", ["train_transaction.csv", "train_identity.csv"])
def test_manifest_entry_matches_recorded_metadata(fname):
    """Cheap check: file size on disk matches MANIFEST.json's recorded byte
    count (does not rehash the full 600MB file in the automated suite)."""
    key = f"ieee-cis/{fname}"
    entry = L.manifest_entry_for(key)
    assert entry is not None, f"{key} missing from MANIFEST.json"
    on_disk_bytes = (data.IEEE_CIS_DIR / fname).stat().st_size
    assert on_disk_bytes == entry["bytes"], (
        f"{key}: on-disk size {on_disk_bytes} != manifest {entry['bytes']} "
        "-- file changed since manifest was generated, re-run scripts/manifest.py")


def test_manifest_entry_for_missing_key_returns_none():
    assert L.manifest_entry_for("ieee-cis/does_not_exist.csv") is None


def test_verify_checksums_full_hash_matches_manifest():
    """The one full-file hash test: sha256 both IEEE-CIS train files and
    confirm they match the committed manifest. Slower than the other
    tests in this module (reads 600MB+25MB) but still just I/O + hashing,
    no CSV parsing or join, so it stays well under a minute."""
    report = L.verify_checksums()
    for key, r in report.items():
        assert r["manifest_sha256"] is not None, f"{key} not in manifest"
        assert r["matches_manifest"], (
            f"{key}: sha256 {r['sha256']} != manifest {r['manifest_sha256']}")
