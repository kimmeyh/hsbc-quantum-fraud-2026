"""The shipped B2 artifact must satisfy what the preregistration requires of it.

B2 is the largest configuration the campaign ran, 833 continuous variables, and
its paired result is the one clean positive CVQBoost has. That makes its
artifact the most load-bearing in the submission, and the F35 guard requires a
test that reads what SHIPS rather than what the code would produce.

The specific failure this file exists to prevent: B2 is also arm cvqboost_hw /
stratified with ten seeds, so when it ran it won score_gates' best-validation-AP
selection and silently displaced the H1b endpoint -- taking the H4
solver-fidelity line with it, because B2 has no proxy twin at 833 variables.
Every unit test still passed. Only a test that asserts what the numbers MEAN
catches that class of defect.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ART = Path(__file__).resolve().parents[1] / "results" / "b2_hardware.json"

pytestmark = pytest.mark.skipif(not ART.exists(), reason="B2 has not been run")


@pytest.fixture(scope="module")
def art() -> dict:
    return json.loads(ART.read_text(encoding="utf-8"))


def test_is_hardware_evidence_at_the_committed_size(art):
    """Section 10 commits B2 at 833 variables; a smaller run is a different cell."""
    assert art["evidence_tag"] == "HW"
    assert art["n_variables"] == 833
    assert art["k"] == 17 and art["schedule"] == 3
    assert art["pair_build"] == "full"


def test_the_block_is_complete(art):
    """Eleven fits: ten stratified seeds plus the temporal protocol."""
    assert art["n_fits"] == 11
    assert art["stratified"]["n_seeds"] == 10
    assert len([r for r in art["rows"] if r["protocol"] == "temporal"]) == 1


def test_every_fit_succeeded_and_carries_a_cost(art):
    for r in art["rows"]:
        assert r["status"] == "ok", f"seed {r['seed']} did not succeed"
        assert r["metered_seconds"] > 0, f"seed {r['seed']} has no measured cost"


def test_total_cost_reconciles_against_the_rows(art):
    assert art["total_metered_seconds"] == pytest.approx(
        sum(r["metered_seconds"] for r in art["rows"]))


def test_the_paired_comparison_is_against_the_like_for_like_arm(art):
    """The comparator must be B1's dct/stratified arm, not B1's overall mean.

    This is the error the first draft of the analysis made. B1's overall mean
    (0.7351) averages in the weaker lg pool config and both temporal fits;
    quoting it would have inflated the reported gain from +0.026 to +0.056.
    The right baseline is hw_b1_dct stratified at 0.7671.
    """
    p = art["paired_vs_b1_dct"]
    assert p["n_seeds"] == 10, "the paired test must use all ten shared seeds"
    assert p["b1_dct_mean"] == pytest.approx(0.7671, abs=5e-4), (
        "the comparator is not B1's dct/stratified arm; check which baseline "
        "this was computed against")


def test_the_paired_effect_is_positive_and_excludes_zero(art):
    """The finding itself. If this ever fails, the claim must be rewritten."""
    p = art["paired_vs_b1_dct"]
    lo, hi = p["ci95_bootstrap"]
    assert p["mean_difference"] > 0
    assert lo > 0, f"95% CI [{lo}, {hi}] no longer excludes zero"
    assert p["seeds_favouring_b2"] == p["n_seeds"], (
        "the result is quoted as unanimous across seeds; it no longer is")


def test_b2_still_trails_the_classical_bar(art):
    """The null. Hard-coded so a future run that overturns it FAILS loudly
    rather than quietly passing under a claim that no longer holds."""
    assert art["stratified"]["auprc_mean"] < 0.8368, (
        "B2 now meets or beats full-feature CatBoost; A24's null and the "
        "proposal's claim must both be revisited")


def test_the_degeneracy_limitation_is_recorded(art):
    """tie_fraction ~0.92 is structural here and must not be dropped quietly."""
    assert art["stratified"]["tie_fraction_mean"] > 0.9
    assert "tie_fraction" in art["limitation"]


def test_h1b_endpoint_is_not_computed_over_b2(art):
    """B2 must not be able to displace the preregistered H1b endpoint.

    When B2 first ran it won score_gates' best-validation-AP selection, silently
    replacing the B1 grid H1b ranges over and deleting the H4 solver-fidelity
    line. The report must still emit that line with B2 present.

    VERIFIED BY INJECTION: reverting the score_gates cell filter to its former
    form regenerates a report with no H4 line and this test fails; restoring the
    filter passes it.
    """
    report = (ART.parent / "gate_report.md").read_text(encoding="utf-8")
    assert "minus exact proxy" in report, (
        "the H4 solver-fidelity line is missing from the gate report; B2 may "
        "have displaced the H1b cell selection again")

def test_the_artifact_regenerates_from_committed_code(art):
    """Appendix C claims every figure regenerates from the repository.

    This artifact was first written by a throwaway script, so the campaign's one
    headline positive result could not be reproduced by a fresh clone -- the
    numbers were right, but their provenance was manual. `summarize_b2.py` now
    rebuilds it from results.json with a seeded bootstrap, so the claim holds.
    """
    import subprocess
    import sys

    r = subprocess.run(
        [sys.executable, str(Path(__file__).resolve().parent / "summarize_b2.py"),
         "--check"], capture_output=True, text=True)
    assert r.returncode == 0, (
        "b2_hardware.json does not match a fresh regeneration: "
        + r.stdout + r.stderr)
