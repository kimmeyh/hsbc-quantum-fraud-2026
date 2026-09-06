"""Tests for the comparison guards (Sprint 7 retro improvement 1).

Each test reconstructs a comparison that actually shipped or was nearly shipped,
and asserts the guard would have refused it.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comparators import ArmSpec, ComparisonError, assert_comparable, reported_difference

TUNED_K6 = ArmSpec(label="tuned four-family", k=6, protocol="stratified", split="test")
FROZEN_K13 = ArmSpec(label="frozen single-family", k=13, protocol="stratified", split="test")
FROZEN_K6 = ArmSpec(label="frozen single-family k=6", k=6, protocol="stratified", split="test")


def test_refuses_the_sprint7_feature_count_mismatch():
    """The real case: the tuned pool is k=6 and the comparator quoted against it
    was k=13. The Sprint 7 plan named that k=13 figure as an acceptance
    criterion, so the guard has to fire at computation time."""
    with pytest.raises(ComparisonError, match="k: 6 vs 13"):
        assert_comparable(TUNED_K6, FROZEN_K13)


def test_allows_the_matched_comparison_that_replaced_it():
    """Rebuilding the comparator at k=6 is what made the +0.0198 legitimate."""
    assert_comparable(TUNED_K6, FROZEN_K6)
    out = reported_difference(TUNED_K6, 0.7827, FROZEN_K6, 0.7629, mde=0.0268)
    assert out["difference"] == pytest.approx(0.0198, abs=1e-4)
    assert out["matched_on"]["k"] == 6


def test_refuses_validation_against_test():
    """The mid-run prediction that went wrong: sweep VALIDATION AP compared
    against TEST AP comparators. Validation runs ~0.005 below test on this
    design, a quarter of the MDE."""
    sweep = ArmSpec(label="sweep selection", k=6, protocol="stratified", split="validation")
    with pytest.raises(ComparisonError, match="different quantities"):
        assert_comparable(sweep, FROZEN_K6)


def test_refuses_a_protocol_mismatch():
    """Stratified against temporal is the same class of error: the split design
    would be reported as if it were the treatment."""
    temporal = ArmSpec(label="temporal arm", k=6, protocol="temporal", split="test")
    with pytest.raises(ComparisonError, match="protocol"):
        assert_comparable(TUNED_K6, temporal)


def test_sub_mde_difference_is_flagged_as_directional():
    """F31 and F33 were both held to this: below the MDE is a direction with a
    mechanism, never a win. The guidance travels with the number."""
    out = reported_difference(TUNED_K6, 0.7827, FROZEN_K6, 0.7629, mde=0.0268)
    assert out["exceeds_mde"] is False
    assert "never as a win" in out["reporting_guidance"]


def test_supra_mde_difference_is_reportable():
    out = reported_difference(TUNED_K6, 0.8200, FROZEN_K6, 0.7629, mde=0.0268)
    assert out["exceeds_mde"] is True
    assert "measured effect" in out["reporting_guidance"]


def test_difference_carries_its_provenance():
    """A bare float can be quoted in a document without its terms; this cannot."""
    out = reported_difference(TUNED_K6, 0.7827, FROZEN_K6, 0.7629)
    for key in ("arm", "comparator", "arm_value", "comparator_value", "matched_on", "split"):
        assert key in out, f"a reported difference must carry {key}"
