"""Artifact tests for the IEEE CVQBoost and H3 evidence files.

Sprint 9 improvement 1: every runner writing evidence needs a test that READS
that evidence. These two files were unguarded until test_artifact_guards.py
flagged them on its first run.

Each assertion below is a property the PREREGISTRATION requires, checked
against the committed artifact rather than against the code that wrote it.
That distinction is the whole point: in Sprint 9 the code was fine and the
experiment was wrong, and only the artifact showed it.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

RESULTS = Path(__file__).resolve().parents[1] / "results"


def _load(name: str):
    p = RESULTS / name
    if not p.exists():
        pytest.skip(f"{name} not present")
    return json.loads(p.read_text(encoding="utf-8"))


# --- ieee_cvqboost.json ----------------------------------------------------

def test_ieee_cvqboost_evidence_is_a_full_run_not_a_smoke_run():
    """A smoke result must never be reported as evidence.

    Sprint 8 lost a full IEEE results file to a test that called
    run(smoke=True) while the runner wrote to one destination.
    """
    d = _load("ieee_cvqboost.json")
    assert d.get("smoke") is False, (
        "ieee_cvqboost.json is a SMOKE run; it must not stand as evidence")


def test_ieee_cvqboost_records_dedup_as_section_4_requires():
    """Section 4 removes exact duplicates BEFORE splitting, count reported.

    Amendment A17 records what happens when a fold builder skips this: three
    exploratory arms trained on a superset of the preregistered dataset,
    invisible for two sprints.
    """
    d = _load("ieee_cvqboost.json")
    assert "exact_duplicates_removed" in d, "the dedup count must be reported"
    assert d["rows_after_dedupe"] > 0
    assert d["exact_duplicates_removed"] >= 0


def test_ieee_cvqboost_prediction_was_recorded_before_the_result():
    """The runner commits to a prediction in advance, which is the point.

    A prediction recorded after seeing the number is not a prediction, and the
    field exists so a reader can check the order rather than trust it.
    """
    d = _load("ieee_cvqboost.json")
    assert d.get("prediction_recorded_in_advance"), (
        "no advance prediction recorded; the arm loses its main honesty claim")


def test_ieee_cvqboost_pool_subsampling_is_disclosed():
    """Pool construction is subsampled on IEEE-CIS -- a COST decision with a
    protocol consequence, so it must be stated in the artifact, not hidden."""
    d = _load("ieee_cvqboost.json")
    assert "pool_subsample" in d and "scope_decision" in d, (
        "subsampling and its scope consequence must both be recorded")


# --- ieee_h3_ladder.json ---------------------------------------------------

def test_h3_ladder_is_scoreable_only_with_enough_cells():
    """Prereg: H3 is scored only if at least 3 ladder cells per dataset run.

    A ladder marked scoreable on fewer cells would be claiming more than the
    preregistration permits.
    """
    d = _load("ieee_h3_ladder.json")
    if d.get("scoreable"):
        assert len(d["cells"]) >= 3, (
            f"marked scoreable with only {len(d['cells'])} cells; the prereg "
            f"requires at least 3")


def test_h3_ladder_cells_cover_the_preregistered_k_values():
    """k in {5, 9, 13, 17}, named in the preregistration and in A18."""
    d = _load("ieee_h3_ladder.json")
    ks = {int(k) for k in d["delta_by_k"]}
    assert ks == {5, 9, 13, 17}, f"ladder covers {sorted(ks)}, expected 5/9/13/17"


def test_h3_ladder_records_free_tier_fit_per_cell():
    """Each cell states whether it would fit the A12 free-tier ceiling.

    That is what turns the ceiling from a constraint into a measurement: the
    ladder shows what the ceiling costs.
    """
    d = _load("ieee_h3_ladder.json")
    missing = [c for c in d["cells"] if "fits_free_tier" not in c]
    assert not missing, f"{len(missing)} cells do not record fits_free_tier"


def test_h3_ladder_cells_carry_evidence_tags():
    """Every reported number carries an evidence tag. No metered time was
    spent here, so every cell must be [SIM]."""
    d = _load("ieee_h3_ladder.json")
    tags = {c.get("evidence_tag") for c in d["cells"]}
    assert tags == {"SIM"}, f"unexpected evidence tags in the ladder: {tags}"
