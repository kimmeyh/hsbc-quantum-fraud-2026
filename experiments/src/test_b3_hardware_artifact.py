"""The shipped B3 artifact must satisfy what the preregistration requires of it.

Required by the F35 artifact guard, and for the reason that guard exists: in
Sprint 9 a test of the CODE passed while the EXPERIMENT was wrong. These
assertions open the file that ships and check properties the protocol demands,
not properties the runner happens to produce.

The specific failure this would have caught: an early draft of the runner chose
features by mutual information over raw columns, skipping IEEEFeaturePipeline
and the item-4 leakage controls. Every unit test still passed. The artifact
would have carried a [HW] arm not comparable to the [SIM] arm it is quoted
against, which is the whole claim of A22.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ART = Path(__file__).resolve().parents[1] / "results" / "b3_hardware.json"

pytestmark = pytest.mark.skipif(not ART.exists(), reason="B3 has not been run")


@pytest.fixture(scope="module")
def art() -> dict:
    return json.loads(ART.read_text(encoding="utf-8"))


def test_is_hardware_evidence_not_a_dry_run(art):
    """A dry run must never be mistaken for hardware evidence."""
    assert art["evidence_tag"] == "HW"
    assert art["dry_run"] is False
    assert art["fits"] > 0


def test_every_row_carries_a_measured_cost(art):
    """Section 11 requires metered_seconds on every hardware row.

    A default is not a measurement: the A21 probe recorded 5.0s from a default
    while the true cost was 10s. Costs here are balance deltas, so they must be
    present and positive on every fit that ran.
    """
    for r in art["rows"]:
        if r["status"] != "ok":
            continue
        assert isinstance(r["metered_seconds"], (int, float))
        assert r["metered_seconds"] > 0, f"k={r['k']} fold={r['fold']} has no cost"


def test_total_cost_equals_the_sum_of_its_rows(art):
    """The headline spend must reconcile against the rows it summarizes."""
    assert art["total_metered_seconds"] == pytest.approx(
        sum(float(r.get("metered_seconds") or 0) for r in art["rows"]))


def test_the_ladder_covers_the_preregistered_k_values(art):
    """H3's ladder is k in {5, 9, 13, 17}; a partial run must not read as whole."""
    assert sorted({r["k"] for r in art["rows"]}) == [5, 9, 13, 17]


def test_k17_runs_above_the_retired_free_tier_ceiling(art):
    """The point of A22: k=17 exceeds A12's 100-variable ceiling.

    If this cell ever came back at or below 100 variables, the claim that the
    ladder was re-run above the ceiling would be false.
    """
    k17 = [r for r in art["rows"] if r["k"] == 17]
    assert k17, "no k=17 cell"
    for r in k17:
        assert r["n_variables"] == 136
        assert r["n_variables"] > 100


def test_variable_counts_match_the_ieee_arms_sequential_build(art):
    """B3 must use the SAME pool build as the [SIM] arm it is quoted against.

    This is the assertion that makes the A22 comparison meaningful, and it is
    easy to get backwards. A3 selected the FULL pair build and applied it to the
    ULB cells, where vars = n + C(n,2). The IEEE-CIS arm is different:
    `run_ieee_cvqboost.py` builds its pools with `pair_build="seq"`, and has
    since it was written, so vars = C(n,2) -- 10, 36, 78, 136 at k = 5, 9, 13,
    17.

    B3 matches that, which is what the claim requires: only the SOLVER differs
    between the [HW] and [SIM] ladders. A B3 run switched to the full build
    would silently add k learners per cell and stop being comparable to the
    published arm, so the count is pinned to the sequential arithmetic here.
    """
    for r in art["rows"]:
        k = r["k"]
        assert r["n_variables"] == k * (k - 1) // 2, (
            f"k={k} has {r['n_variables']} variables; the IEEE arm's sequential "
            f"build gives {k * (k - 1) // 2}. If this changed to the full build "
            f"the [HW] ladder is no longer comparable to the [SIM] one.")


def test_stored_means_back_every_figure_quoted_in_the_papers(art):
    """The ladder is quoted as fold means, so the means must be STORED.

    F44: a number that lives only in prose is unchecked by construction.
    """
    by_k = {r["k"]: r for r in art["by_k"]}
    assert sorted(by_k) == [5, 9, 13, 17]
    for k, r in by_k.items():
        assert r["folds"] == 3, f"k={k} summarizes {r['folds']} folds, not 3"
        rows = [x for x in art["rows"] if x["k"] == k and x["status"] == "ok"]
        assert r["auprc_mean"] == pytest.approx(
            sum(x["auprc"] for x in rows) / len(rows), abs=1e-4)


def test_the_ladder_is_monotonic_in_k(art):
    """A22 reports a monotonic ladder. If that ever breaks, the claim is wrong."""
    means = [r["auprc_mean"] for r in sorted(art["by_k"], key=lambda x: x["k"])]
    assert means == sorted(means), f"ladder is not monotonic: {means}"


def test_hardware_stays_below_the_classical_arms(art):
    """The null A22 rests on: the best [HW] cell trails the classical [SIM] bar.

    Hard-coded deliberately. If a future run overturns this, the test SHOULD
    fail and force the claim to be rewritten rather than quietly pass.
    """
    best_hw = max(r["auprc_mean"] for r in art["by_k"])
    assert best_hw < 0.5739, (
        f"best hardware cell {best_hw} now meets or beats LightGBM's 0.5739; "
        f"the null reported in A22 and section A.5 must be revisited")

def test_pools_were_built_on_the_same_rows_as_the_sim_arm(art):
    """The assertion whose absence let a false claim reach the documents.

    A22's central claim is that the [HW] and [SIM] ladders differ ONLY in the
    solver. The first B3 run built its pools on the entire training fold while
    `run_ieee_h3.py` subsamples pool construction to POOL_SUBSAMPLE_N = 100,000
    -- 4.1x to 5.8x more rows, and a different lambda_coef, since that scales
    with len(y). The published [HW] ladder was inflated by up to +0.0699 AUPRC
    and the comparison was invalid.

    Every other test in this file passed throughout. This one is the difference
    between testing that the numbers are consistent and testing that they mean
    what the paper says they mean.
    """
    import run_ieee_h3

    for r in art["rows"]:
        assert "n_pool_rows" in r, (
            "row does not record its pool-row count, so comparability with the "
            "[SIM] arm cannot be verified from the artifact")
        expected = min(r["n_train_rows"], run_ieee_h3.POOL_SUBSAMPLE_N)
        assert r["n_pool_rows"] == expected, (
            f"k={r['k']} fold={r['fold']} built its pool on {r['n_pool_rows']:,} "
            f"rows; the [SIM] arm uses {expected:,}. The two ladders are no "
            f"longer comparable and no [HW]-vs-[SIM] claim may be made.")
