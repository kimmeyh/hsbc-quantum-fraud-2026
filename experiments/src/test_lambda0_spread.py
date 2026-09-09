"""The lambda=0 minimiser set is a face, not a point.

Reads the shipped artifact rather than recomputing, per the Sprint 9 rule: a
test of the CODE passed while the experiment was wrong, and the test that caught
it read the results file.

The claim this evidence corrects: "the optimum stays uniform even at zero
penalty, so the penalty term is not the cause either". At lambda = 0 the Gram
matrix is rank-one to numerical precision, so a solver started at uniform
returns uniform BY CONSTRUCTION -- the observation could not have come out any
other way, which is the same defect F36 was closed for.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ART = Path(__file__).resolve().parents[1] / "results" / "lambda0_spread.json"


@pytest.fixture(scope="module")
def data():
    if not ART.exists():
        pytest.skip("lambda0_spread.json not generated yet")
    return json.loads(ART.read_text(encoding="utf-8"))


def test_covers_every_committed_pool(data):
    assert len(data["per_seed"]) == 10, (
        f"{len(data['per_seed'])} pools, expected the ten committed seeds")
    assert data["lambda"] == 0.0, "this evidence is only meaningful at lambda = 0"
    assert data["evidence_tag"] == "SIM", "classical solve, must not be tagged [HW]"


def test_solutions_are_far_apart(data):
    """The finding: random starts do NOT converge to one point."""
    s = data["summary"]
    assert s["l1_pairwise_mean"] > 0.3, (
        f"random-start solutions sit a mean L1 of {s['l1_pairwise_mean']:.4f} "
        f"apart. If this collapses toward 0 the minimiser is effectively unique "
        f"and the corrected proposal text overstates in the other direction.")


def test_the_objective_cannot_distinguish_them(data):
    """Why it is a FACE and not just a wide basin: the objective is flat."""
    s = data["summary"]
    assert s["obj_relative_spread_max"] < 1e-6, (
        f"worst-pool relative objective spread {s['obj_relative_spread_max']:.3e}. "
        f"The claim is that these solutions are indistinguishable to the "
        f"objective; a large spread would mean the solver is simply failing.")


def test_every_pool_shows_it_not_just_one(data):
    """One seed could be a fluke; ten make it a property of the formulation."""
    bad = [r["pool"] for r in data["per_seed"] if r["l1_pairwise_mean"] <= 0.3]
    assert not bad, f"pools that did NOT show a spread: {bad}"


def test_the_proposal_no_longer_claims_a_unique_zero_penalty_optimum():
    """Guard the document against the retracted wording."""
    root = Path(__file__).resolve().parents[2]
    text = (root / "docs" / "paper" / "proposal.md").read_text(encoding="utf-8")
    retracted = "the optimum stays uniform even at zero penalty, so the penalty term is not the cause either"
    assert retracted not in text, (
        "the proposal still asserts a unique uniform optimum at zero penalty; "
        "the measured spread disproves it")
