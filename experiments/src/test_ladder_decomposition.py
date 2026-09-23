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
    """No restated number may drift from its artifact.

    Checks BOTH main effects at the precision the write-up quotes them. The
    first version checked only the k effect at 5dp, which the BLUF now states
    at 4dp -- so it would have failed on a correct document.
    """
    import metrics
    if not WRITEUP.exists():
        pytest.skip("write-up not present")
    rows = json.loads(RESULTS.read_text(encoding="utf-8"))["rows"]

    def cell(cfg):
        return {r["seed"]: r["metrics"]["auprc"] for r in rows
                if r.get("arm") == "cvqboost_proxy" and r.get("config") == cfg
                and r.get("pair_build") == "full"
                and r.get("protocol") == "stratified"}

    free, mid, deep = cell("free"), cell("mid"), cell("deep")
    s = sorted(set(free) & set(mid) & set(deep))
    text = WRITEUP.read_text(encoding="utf-8")

    for label, d in (("k", [mid[x] - free[x] for x in s]),
                     ("order", [deep[x] - free[x] for x in s])):
        r = metrics.seed_mean_t_interval(d)
        assert f"{r['mean']:+.4f}" in text, (
            f"the write-up does not state the computed {label} effect "
            f"{r['mean']:+.4f}")
        lo, hi = r["ci95"]
        assert f"{lo:+.4f}" in text and f"{hi:+.4f}" in text, (
            f"the write-up does not state the {label} effect's interval")


def test_the_fourth_corner_exists_on_all_ten_seeds():
    """F91. Without it the interaction term is unidentified."""
    rows = json.loads(RESULTS.read_text(encoding="utf-8"))["rows"]
    deep = {r["seed"] for r in rows
            if r.get("arm") == "cvqboost_proxy" and r.get("config") == "deep"
            and r.get("pair_build") == "full"
            and r.get("protocol") == "stratified"}
    assert sorted(deep) == list(range(42, 52)), (
        f"expected 10 deep-config seeds, found {len(deep)}")


def test_the_deep_pool_is_377_variables_on_every_seed():
    """k + C(k,2) + C(k,3) for k=13. A different size is a different cell."""
    rows = json.loads(RESULTS.read_text(encoding="utf-8"))["rows"]
    sizes = {r.get("n_weak_classifiers") for r in rows
             if r.get("config") == "deep"}
    assert sizes == {377}, f"deep pool sizes are {sizes}, expected {{377}}"


def test_the_order_effect_is_real_and_the_k_effect_is_not():
    """THE ATTRIBUTION, which F64 alone could not make.

    Subset order carries the gain; feature count does not. Both halves are
    asserted, because either alone would pass on a coincidence.
    """
    import metrics
    rows = json.loads(RESULTS.read_text(encoding="utf-8"))["rows"]

    def cell(cfg):
        return {r["seed"]: r["metrics"]["auprc"] for r in rows
                if r.get("arm") == "cvqboost_proxy" and r.get("config") == cfg
                and r.get("pair_build") == "full"
                and r.get("protocol") == "stratified"}

    free, mid, deep = cell("free"), cell("mid"), cell("deep")
    s = sorted(set(free) & set(mid) & set(deep))
    assert len(s) == 10

    order = metrics.seed_mean_t_interval([deep[x] - free[x] for x in s])
    kfx = metrics.seed_mean_t_interval([mid[x] - free[x] for x in s])

    assert order["excludes_zero"], (
        "the order-3 effect no longer excludes zero; the BLUF's central claim "
        "has changed")
    assert order["mean"] > 0.015, f"order effect fell to {order['mean']:+.4f}"
    assert not kfx["excludes_zero"], (
        "the k effect now excludes zero; the BLUF says it contributes nothing "
        "measurable")


def test_the_writeup_leads_with_a_bluf():
    """Team lead, 2026-09-23: the document must state the overall conclusion
    up front rather than making the reader assemble it."""
    if not WRITEUP.exists():
        pytest.skip("write-up not present")
    text = WRITEUP.read_text(encoding="utf-8")
    assert "## BLUF" in text
    head = text[:text.index("## The four corners")]
    assert "three-feature learners" in head
    assert "+0.0245" in head and "+0.0001" in head


def test_the_writeup_still_states_what_it_does_not_support():
    """The fourth corner is [HW] while the others are proxy, so the
    interaction is implied ACROSS arms rather than measured within one. That
    limit must survive the upgrade from bound to attribution.

    "license" as a verb was reworded to "support" on 2026-09-23: it is legal
    register rather than plain English, and this is a results document.
    """
    if not WRITEUP.exists():
        pytest.skip("write-up not present")
    text = WRITEUP.read_text(encoding="utf-8")
    assert "does NOT support" in text
    assert "implied" in text and "within one" in text


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


HISTORICAL_ROW_COUNT = 168   # rows written before amendment A33


def test_the_historical_rows_are_still_not_retrofitted():
    """A33 says the 168 pre-amendment rows stay as they are.

    Pinned to the ROW BOUNDARY, not to a config name. The first version
    excluded `config == "mid"` as shorthand for "written this sprint", which
    broke the moment F91 added `deep` rows that legitimately carry the stamp.
    A guard that fails on correct behaviour gets deleted rather than fixed.
    """
    rows = json.loads(RESULTS.read_text(encoding="utf-8"))["rows"]
    stamped_old = [i for i, r in enumerate(rows[:HISTORICAL_ROW_COUNT])
                   if "environment" in r]
    assert not stamped_old, (
        f"{len(stamped_old)} of the first {HISTORICAL_ROW_COUNT} row(s) gained "
        "an environment field they could not have observed")
