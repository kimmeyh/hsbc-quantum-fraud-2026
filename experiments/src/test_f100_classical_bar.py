"""The F100 classical bar reports a paired comparison and names its limits.

Sprint 21 Task D. The result -- two classical lanes beating the CVQBoost proxy
on every cell and seed -- is the kind that gets quoted out of context, so these
guards pin the three things that keep it honest:

  1. the comparison is PAIRED per seed, because A24 records that B2's +0.0256
     gain was invisible unpaired (inside a 0.030 seed-to-seed sd);
  2. the comparator's evidence tag is PROJ, not HW, and the document says so;
  3. the metrics are OVERALL, not in-segment, so they cannot be read as H5.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parent
ROOT = SRC.parents[1]
sys.path.insert(0, str(SRC))

RESULT = ROOT / "experiments" / "results" / "f100_classical_bar.json"
DOC = ROOT / "docs" / "F100_CLASSICAL_BAR.md"

LANES = {"logreg", "gam_additive", "ga2m", "hgb", "joint_twin"}


def _result():
    if not RESULT.exists():
        pytest.skip(f"{RESULT.name} not present; run run_f100_classical_bar.py")
    return json.loads(RESULT.read_text(encoding="utf-8"))


def test_all_three_cells_and_five_seeds_ran():
    r = _result()
    assert r["n_cells"] == 15, (
        f"expected 3 cells x 5 seeds = 15, got {r['n_cells']}")
    assert len(r["summary"]) == 3


def test_every_lane_f100_promises_is_present_in_every_cell():
    """A bar missing a lane is not a complete bar. The JOINT twin especially:
    omitting it is how the Fourier Wall paper shows a fake quantum win."""
    r = _result()
    for dataset, s in r["summary"].items():
        missing = LANES - set(s["lanes"])
        assert not missing, f"{dataset} is missing lane(s): {sorted(missing)}"


def test_the_comparison_is_paired_per_seed():
    """Not a difference of means. A24: B2's gain sat inside the seed-to-seed
    standard deviation and read as noise until the comparison was paired."""
    r = _result()
    for dataset, s in r["summary"].items():
        for lane, v in s["lanes"].items():
            if v["mean_delta_vs_cvqboost_proxy"] is None:
                continue
            assert v["n_paired"] >= 2, (
                f"{dataset}/{lane} has {v['n_paired']} paired seed(s); a "
                "bootstrap CI over fewer than two is not a CI")
            assert v["seeds_favoring_lane"] is not None, (
                f"{dataset}/{lane} reports no per-seed direction count, so a "
                "reader cannot tell a consistent effect from one seed "
                "carrying the mean")
            assert v["delta_ci95"] is not None


def test_the_comparator_is_tagged_as_the_proxy_not_the_device():
    """The whole result is relative to the CVQBoost CLASSICAL PROXY. Tagging
    or describing it as a device comparison would promote a claim past its
    evidence tag."""
    r = _result()
    assert r["evidence_tag"] == "SIM"
    assert r["metered_seconds"] == 0
    assert "PROJ" in r["comparator"].upper(), (
        "the comparator must carry its evidence tag in its own name")
    assert "NOT a Dirac-3" in r["note"] or "not a dirac" in r["note"].lower()


def test_the_result_file_says_these_are_overall_not_in_segment_metrics():
    """H5 is an in-segment claim. These are full-test-fold metrics, and a
    method can lose overall while winning on a slice -- which is the entire
    premise of segment transfer."""
    r = _result()
    low = r["note"].lower()
    assert "in-segment" in low and "overall" in low, (
        "the note must distinguish these overall metrics from H5's "
        "in-segment claim")


def test_the_document_carries_both_disclaimers():
    if not DOC.exists():
        pytest.skip("F100_CLASSICAL_BAR.md not present")
    low = DOC.read_text(encoding="utf-8").lower()
    assert "does not say anything about dirac-3" in low, (
        "the document must state that no figure in it is a device result")
    assert "does not say anything about h5" in low, (
        "the document must state that these are not the in-segment claim")
    assert "proj" in low, "the proxy's evidence tag must appear"


def test_the_documented_winners_match_the_recorded_ones():
    """The document interprets the result file. If they disagree, one is stale
    and a reader cannot tell which."""
    r = _result()
    if not DOC.exists():
        pytest.skip("F100_CLASSICAL_BAR.md not present")
    text = DOC.read_text(encoding="utf-8")
    for dataset, s in r["summary"].items():
        for lane in s["lanes_beating_proxy"]:
            assert lane in text, (
                f"{lane} beats the proxy on {dataset} in the data but is not "
                "named in the document")


def test_a_lane_that_beats_the_proxy_has_a_ci_excluding_zero():
    """A positive mean delta whose CI straddles zero is not a win, and must
    not be listed as one."""
    r = _result()
    for dataset, s in r["summary"].items():
        for lane in s["lanes_beating_proxy"]:
            v = s["lanes"][lane]
            lo, _hi = v["delta_ci95"]
            assert lo > 0, (
                f"{dataset}/{lane} is listed as beating the proxy but its "
                f"95% CI lower bound is {lo}, which does not exclude zero")
