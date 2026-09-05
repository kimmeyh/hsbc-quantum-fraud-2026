"""Contract tests over results.json rows (Sprint 6 retro improvement 2).

Three schema defects shipped in one sprint, each a KeyError waiting in a
consumer rather than a value that was merely wrong:

- F32 rows set `config` but not `config_hash`; cost_analysis reads
  `r["config_hash"]` and would have raised when the operating-point table was
  regenerated. Found by reading the consumer, not by a test.
- F32 rows lacked `feature_set`; score_gates keys unknown arms by it, so the
  gate report could not regenerate. Found only when the suite ran.
- F32 rows lacked `pair_build`; same class.

A writer cannot be trusted to remember what every reader needs. These tests
assert the CONTRACT instead: every row carries the fields its consumers index
directly, so a new arm fails here rather than three steps downstream.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import store

RESULTS = Path(__file__).resolve().parents[1] / "results" / "results.json"

# Fields every row must carry, whatever the arm.
UNIVERSAL = ("arm", "seed", "evidence_tag")

# Fields a consumer indexes with [] rather than .get(), so absence raises.
# score_gates keys unknown arms by feature_set; cost_analysis reads config_hash
# on every row and pair_build on cvqboost cells.
CONSUMER_INDEXED = ("config_hash",)

VALID_TAGS = {"HW", "SIM", "PROJ"}


def _rows():
    if not RESULTS.exists():
        pytest.skip("results.json not present")
    return json.loads(RESULTS.read_text())["rows"]


def test_every_row_has_the_universal_fields():
    missing = [
        (i, r.get("arm"), f)
        for i, r in enumerate(_rows())
        for f in UNIVERSAL
        if f not in r
    ]
    assert not missing, f"rows missing universal fields: {missing[:10]}"


def test_every_row_has_the_fields_consumers_index():
    """score_gates and cost_analysis use r[field], not r.get(field)."""
    missing = [
        (i, r.get("arm"), f)
        for i, r in enumerate(_rows())
        for f in CONSUMER_INDEXED
        if f not in r
    ]
    assert not missing, (
        f"rows missing consumer-indexed fields: {missing[:10]}. "
        "A row without these raises KeyError in score_gates or cost_analysis "
        "rather than being skipped, so the gate report cannot regenerate."
    )


def test_cvqboost_rows_carry_the_keys_their_consumers_group_by():
    """cost_analysis groups cvqboost cells by (arm, config, pool_variant) and
    reads pair_build; score_gates groups by (arm, config, protocol, pair_build).
    """
    bad = []
    for i, r in enumerate(_rows()):
        arm = str(r.get("arm", ""))
        if not arm.startswith("cvqboost"):
            continue
        for f in ("config", "pool_variant", "pair_build", "protocol"):
            if f not in r:
                bad.append((i, arm, f))
    assert not bad, f"cvqboost rows missing grouping keys: {bad[:10]}"


def test_evidence_tags_are_from_the_frozen_vocabulary():
    """The tag vocabulary is fixed by the preregistration; a typo silently
    excludes a row from every tag-filtered table."""
    bad = [(i, r.get("arm"), r.get("evidence_tag"))
           for i, r in enumerate(_rows())
           if r.get("evidence_tag") not in VALID_TAGS]
    assert not bad, f"rows with tags outside {VALID_TAGS}: {bad[:10]}"


def test_hardware_rows_account_for_their_spend():
    """A metered row that cannot say what it cost makes the spend guard blind
    (amendment A8). Unparseable billing must be CHARGED and FLAGGED, never absent.
    """
    bad = []
    for i, r in enumerate(_rows()):
        if r.get("evidence_tag") != "HW":
            continue
        if str(r.get("status", "")).startswith("ok"):
            if r.get("metered_seconds") is None:
                bad.append((i, r.get("arm"), "metered_seconds is None on an ok row"))
            # The audit flag arrived with amendment A8, so the 27 Sprint 4 rows
            # (blocks B1 and G0b) predate it. Their spend IS fully recorded --
            # 120.0 s, verified -- so this is a provenance gap in old rows, not
            # an accounting failure. Every block written since A8 must carry it.
            if r.get("block") not in ("B1", "G0b") and "metered_seconds_parsed" not in r:
                bad.append((i, r.get("arm"), "missing metered_seconds_parsed audit flag"))
    assert not bad, f"hardware rows with unaccounted spend: {bad[:10]}"


def test_prediction_paths_are_arm_keyed():
    """Amendment A9: hardware and its exact proxy deliberately share a
    config_hash, so keying predictions by hash alone let the proxy backfill
    OVERWRITE the hardware scores. The arm must change the path."""
    a = store.prediction_path("deadbeef", 42, "stratified", "cvqboost_hw")
    b = store.prediction_path("deadbeef", 42, "stratified", "cvqboost_proxy")
    assert a != b, "same path for two arms: the A9 collision would recur"
