"""The resolution argument must keep matching the device documentation.

F57. The submission previously claimed that hardware agreeing with the classical
proxy on the frozen pool confirmed convexity, and that the agreement bounded any
effect of Dirac-3's continuous-variable resolution. The second was backwards:
every coefficient difference in that Hamiltonian sits about two hundred times
below what the device can distinguish, so uniform is the only answer it can
give and the agreement is forced.

These tests pin the measurement, not the prose, so the claim cannot drift back.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ART = Path(__file__).resolve().parents[1] / "results" / "device_resolution.json"

pytestmark = pytest.mark.skipif(not ART.exists(), reason="resolution artifact absent")


@pytest.fixture(scope="module")
def art() -> dict:
    return json.loads(ART.read_text(encoding="utf-8"))


def test_the_documented_dynamic_range_is_what_we_claim(art):
    """200:1 is the vendor's figure. If someone edits it, the whole argument
    changes and that should be a deliberate act, not a silent one."""
    assert art["dynamic_range"] == 200.0
    assert "200:1" in art["source"]


def test_no_coefficient_difference_is_resolvable_on_the_frozen_pool(art):
    """The load-bearing measurement: the device cannot see this problem's
    structure at all, on any pool."""
    fp = art["frozen_pool"]
    assert fp["n_pools"] >= 10
    assert fp["any_coefficient_difference_resolvable"] is False
    assert fp["off_diagonal_spread_max"] < fp["resolvable_difference_min"] / 100, (
        "the off-diagonal spread is no longer far below the resolvable "
        "difference; the forced-agreement argument must be re-checked")


def test_the_device_visible_problem_has_a_uniform_optimum(art):
    """Quantised at the documented resolution, the minimiser IS uniform -- which
    is why hardware returning uniform proves nothing about the true optimum."""
    assert art["frozen_pool"]["quantised_l1_from_uniform_max"] < 1e-9


def test_a_diffuse_833_variable_optimum_is_not_representable(art):
    """The B2 explanation. If this ever became representable, the sparsification
    account of the 0.83 cosine would need rewriting."""
    dw = art["diffuse_weight_limit"]
    assert dw["uniform_weight_below_resolution"] is True
    assert dw["b2_uniform_weight"] < dw["expected_weight_resolution"]


def test_the_observed_b2_weights_match_the_prediction(art):
    """Prediction: exact zeros, and nonzero weights below the resolution.
    Measured against the retained device responses, not asserted."""
    obs = art.get("b2_observed") or {}
    if not obs:
        pytest.skip("B2 responses not retained in this checkout")
    assert obs["fits_showing_exact_zeros"] == obs["n_responses_parsed"], (
        "not every B2 fit returned exact zeros; the sparsification prediction "
        "no longer holds on every fit")
    assert obs["nonzero_weight_max"] < art["diffuse_weight_limit"]["expected_weight_resolution"]


def test_the_withdrawn_claim_does_not_return(art):
    """The prose half. A26/A31 withdrew 'that agreement bounds any effect of
    resolution'; if it reappears, the artifact and the paper disagree."""
    papers = ART.resolve().parents[2] / "docs" / "paper"
    for name in ("proposal.md", "appendix.md"):
        body = (papers / name).read_text(encoding="utf-8").lower()
        i = body.find("bounds any effect of dirac-3")
        if i < 0:
            continue
        # The appendix QUOTES the withdrawn sentence in order to withdraw it,
        # which is the honest way to record a correction. What must not survive
        # is the sentence standing as our own claim -- so look for the
        # withdrawal in the 200 characters immediately BEFORE the quote, not
        # anywhere in the file, or any unrelated correction elsewhere satisfies
        # it and the guard becomes vacuous (verified by injection).
        # Collapse whitespace first: the markdown wraps at ~78 columns, so the
        # phrase "an earlier version said" is split by a newline in the source
        # and a literal substring test silently never matches it.
        window = " ".join(body[max(0, i - 200):i].split())
        assert "earlier version" in window, (
            f"{name} states the withdrawn resolution claim without withdrawing "
            f"it in the same breath")
