"""The +0.0319 decomposition, read from the shipped artifact.

F42 finding F12: the published gain changed three things at once (learner
families, fit-time class weighting, distance-weighted kNN) and offered only a
Gram-ratio decomposition, not an AUPRC one. It was also selected on seed 42 and
evaluated on ten seeds including 42.

The runner rebuilds every pool from the splits, so reproducing the published
figure is itself evidence the original code path was sound.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ART = Path(__file__).resolve().parents[1] / "results" / "gain_decomposition.json"
PUBLISHED = 0.031905605807983406
MDE = 0.0268


@pytest.fixture(scope="module")
def d():
    if not ART.exists():
        pytest.skip("gain_decomposition.json not generated yet")
    return json.loads(ART.read_text(encoding="utf-8"))


def test_reproduces_the_published_gain(d):
    """The whole decomposition is worthless if the total does not land."""
    total = d["decomposition"]["total"]
    assert abs(total["mean"] - PUBLISHED) < 5e-4, (
        f"decomposition total {total['mean']:.6f} vs published {PUBLISHED:.6f}. "
        f"A drift here means the arms or the comparator no longer match the "
        f"published comparison and the reported figure needs re-deriving.")
    assert total["n_positive"] == total["n"], "published figure is 10 of 10 seeds"


def test_the_gain_is_class_weighting_not_family_diversity(d):
    """The finding the paper now states."""
    dec = d["decomposition"]
    assert dec["weighting"]["mean"] > MDE, (
        "class weighting no longer carries the gain; the paper says it does")
    # ABSOLUTE value: the claim is "buys nothing measurable", a magnitude. A
    # signed comparison passed a large NEGATIVE effect (say -0.05 < 0.0268)
    # while the paper's claim became false, and the failure message would have
    # read "above the MDE" -- the opposite of what happened.
    assert abs(dec["families"]["mean"]) < MDE, (
        f"family diversity alone now measures {dec['families']['mean']:+.4f}, "
        f"a magnitude above the {MDE} MDE. The paper states it buys nothing "
        f"measurable, in either direction.")


def test_selection_bias_is_small(d):
    """Excluding the selection seed must not move the conclusion."""
    total = d["decomposition"]["total"]["mean"]
    loo = d["decomposition"]["leave_out_selection_seed"]
    assert abs(total - loo["mean"]) < 0.005, (
        f"dropping the selection seed moves the gain by "
        f"{abs(total - loo['mean']):.4f}; the paper reports 0.0006")
    assert loo["mean"] > MDE, (
        "the gain no longer clears the MDE without its selection seed, which "
        "would change what the paper can claim")


def test_uses_the_selected_configuration(d):
    """Decomposing an arm the campaign did not choose answers nothing.

    The first version of this runner decomposed `balanced` while the campaign
    selected `balanced_shallow_knn`, and differenced against a pooled mean
    instead of the per-seed comparator. Both defects are why the total did not
    reproduce; this pins the fix.
    """
    assert "knn" in d["decomposition"], (
        "no kNN step: the runner is decomposing a two-arm ladder, so it is not "
        "measuring the selected configuration")
    assert "frozen_k6_comparator_per_seed" in d, (
        "comparator is not per-seed; a pooled mean discards the pairing the "
        "published comparison relies on")
