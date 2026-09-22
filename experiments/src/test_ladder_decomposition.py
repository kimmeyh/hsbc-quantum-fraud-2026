"""The F64 ladder decomposition must match its rows (Sprint 18 Task C).

The write-up in docs/F64_LADDER_DECOMPOSITION.md states a delta, an interval
and a pool size. Every one of them is recomputed here from results.json, so a
figure in prose cannot drift from the evidence it claims to summarise -- the
F44 defect class, a number in a document that nothing checks.

It also pins the CLAIM SHAPE. The result is a BOUND, not an attribution: the
design cannot separate "order 3 matters" from "order 3 matters given k=17",
because no k=13 order-3 cell exists. A future edit that upgrades the wording to
an attribution fails here.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "experiments" / "results" / "results.json"
WRITEUP = ROOT / "docs" / "F64_LADDER_DECOMPOSITION.md"

sys.path.insert(0, str(ROOT / "experiments" / "src"))


def _cells():
    if not RESULTS.exists():
        pytest.skip("results.json not present")
    rows = json.loads(RESULTS.read_text(encoding="utf-8"))["rows"]

    def cell(cfg):
        return {r["seed"]: r["metrics"]["auprc"] for r in rows
                if r.get("arm") == "cvqboost_proxy" and r.get("config") == cfg
                and r.get("pair_build") == "full"
                and r.get("protocol") == "stratified"}

    return cell("mid"), cell("free")


def test_the_mid_cell_exists_on_all_ten_seeds():
    mid, _ = _cells()
    assert len(mid) == 10, f"expected 10 mid-config seeds, found {len(mid)}"
    assert sorted(mid) == list(range(42, 52))


def test_the_mid_pool_is_153_variables_on_every_seed():
    """k + C(k,2) for k=17. A different pool size means a different cell, and
    the whole comparison would be to the wrong thing."""
    rows = json.loads(RESULTS.read_text(encoding="utf-8"))["rows"]
    sizes = {r.get("n_weak_classifiers") for r in rows
             if r.get("config") == "mid"}
    assert sizes == {153}, f"mid pool sizes are {sizes}, expected {{153}}"


def test_the_delta_is_below_the_mde_and_spans_zero():
    """THE RESULT. Feature count alone does not move the outcome."""
    import metrics
    mid, free = _cells()
    common = sorted(set(mid) & set(free))
    assert len(common) == 10, f"only {len(common)} paired seeds"

    r = metrics.seed_mean_t_interval([mid[s] - free[s] for s in common])
    assert abs(r["mean"]) < 0.0268, (
        f"delta {r['mean']:+.5f} is at or above the A5 MDE; the write-up says "
        "it is below")
    assert not r["excludes_zero"], (
        "the interval no longer spans zero; the write-up's central claim has "
        "changed and the prose must be rewritten")


def test_the_writeup_figures_match_the_rows():
    """No restated number may drift from its artifact."""
    import metrics
    if not WRITEUP.exists():
        pytest.skip("write-up not present")
    mid, free = _cells()
    common = sorted(set(mid) & set(free))
    r = metrics.seed_mean_t_interval([mid[s] - free[s] for s in common])
    text = WRITEUP.read_text(encoding="utf-8")

    assert f"{r['mean']:+.5f}" in text, (
        f"the write-up does not state the computed mean {r['mean']:+.5f}")
    lo, hi = r["ci95"]
    assert f"{lo:+.4f}" in text and f"{hi:+.4f}" in text, (
        "the write-up does not state the computed 95% interval")


def test_the_claim_is_a_bound_not_an_attribution():
    """The Sprint 13 withdrawal objection, pinned.

    A one-factor probe is silent about interaction. The write-up must keep
    saying so, and must keep naming the missing fourth corner that would
    settle it.
    """
    if not WRITEUP.exists():
        pytest.skip("write-up not present")
    text = WRITEUP.read_text(encoding="utf-8")
    assert "BOUND, not an attribution" in text
    assert "does NOT license" in text
    assert "k=13 at order 3" in text, (
        "the write-up no longer names the fourth corner that would identify "
        "the interaction term")


def test_the_new_rows_carry_the_a33_environment_stamp():
    """These are the first rows written since A33. If they lack the stamp,
    the amendment is not doing anything."""
    rows = json.loads(RESULTS.read_text(encoding="utf-8"))["rows"]
    mid = [r for r in rows if r.get("config") == "mid"]
    assert mid, "no mid rows"
    for r in mid:
        env = r.get("environment")
        assert env, f"seed {r.get('seed')} has no environment stamp"
        for field in ("os", "python", "threads"):
            assert field in env, f"environment is missing {field}"


def test_the_historical_rows_are_still_not_retrofitted():
    """A33 says the 168 pre-amendment rows stay as they are."""
    rows = json.loads(RESULTS.read_text(encoding="utf-8"))["rows"]
    stamped_old = [r for r in rows
                   if r.get("config") != "mid" and "environment" in r]
    assert not stamped_old, (
        f"{len(stamped_old)} historical row(s) gained an environment field "
        "they could not have observed")
