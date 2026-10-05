"""An infeasible matched control is an OUTCOME, never a crash.

Sprint 21. `matched_random_segment` draws H5(ii)'s negative control from the
COMPLEMENT of the segment, matching the segment's exact size and exact
positive count. That requires at least as many positives and negatives outside
the segment as inside it.

On energy_steel the pocket holds 918-950 of the test fold's positives and the
complement holds only 832-864, so the draw is impossible on all five frozen
seeds. The library correctly asserts and raises; the SCORING path must not,
because the gate table already has a column for `unscoreable` and the ten
feasible cells in the same run still have to score.

These guards pin that behavior, and they pin the counts, so a future change to
the split or the pocket definition that silently makes energy_steel "feasible"
again has to explain itself.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

SRC = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC))

import spectra_segment as ss  # noqa: E402


def _toy(n_seg_pos, n_seg_neg, n_out_pos, n_out_neg):
    """A labeled vector with a segment mask, built to exact counts."""
    y = np.array([1] * n_seg_pos + [0] * n_seg_neg
                 + [1] * n_out_pos + [0] * n_out_neg)
    seg = np.zeros(len(y), dtype=bool)
    seg[: n_seg_pos + n_seg_neg] = True
    return seg, y


def test_a_feasible_cell_reports_feasible_with_its_counts():
    seg, y = _toy(60, 40, 200, 300)
    f = ss.control_feasibility(seg, y)
    assert f["feasible"] is True
    assert f["segment_positives"] == 60
    assert f["complement_positives"] == 200
    assert "reason" not in f, "a feasible cell needs no reason"


def test_too_few_positives_outside_is_infeasible_and_says_so():
    seg, y = _toy(60, 40, 10, 300)
    f = ss.control_feasibility(seg, y)
    assert f["feasible"] is False
    assert "60 positives needed, 10 available" in f["reason"]
    assert "short 50" in f["reason"], (
        "the shortfall is the actionable number and must be stated")


def test_too_few_negatives_outside_is_infeasible_and_says_so():
    seg, y = _toy(10, 90, 200, 20)
    f = ss.control_feasibility(seg, y)
    assert f["feasible"] is False
    assert "90 negatives needed, 20 available" in f["reason"]


def test_an_infeasible_cell_is_unscoreable_rather_than_an_exception():
    """The whole point: the scoring path reports, it does not raise.

    Before this, `evaluate_in_segment` called `matched_random_segment`
    unguarded, so one infeasible cell aborted the run and the nine feasible
    cells beside it produced nothing.
    """
    seg, y = _toy(60, 40, 10, 300)
    # Scores are irrelevant to feasibility; any aligned vector will do.
    rng = np.random.default_rng(0)
    p = rng.random(len(y))

    res = ss.evaluate_in_segment(y, p, seg, seed=42)

    assert res["in_segment"]["status"] == "scored", (
        "the in-segment half is feasible and must still score")
    assert res["random_control"]["status"] == "unscoreable"
    assert res["edge"] is None, "no edge without a control to subtract"
    assert "cannot be drawn from the complement" in \
        res["random_control"]["reason"]


def test_matched_random_segment_itself_still_raises():
    """The library contract is unchanged: a caller asking for an impossible
    draw gets an exception, not a silently wrong control. Only the scoring
    path routes around it."""
    seg, y = _toy(60, 40, 10, 300)
    with pytest.raises(AssertionError, match="positives"):
        ss.matched_random_segment(seg, np.random.default_rng(0), y)


# ---- the real data, which is why any of this exists -------------------------

EXPECTED = {
    # cell: (seeds that are feasible, seeds that are not)
    "telecom_churn": ((42, 43, 44, 45, 46), ()),
    "energy_steel": ((), (42, 43, 44, 45, 46)),
    "oilgas_gasturbine": ((42, 43, 44, 45, 46), ()),
}


@pytest.mark.parametrize("cell_name", sorted(EXPECTED))
def test_the_frozen_cells_feasibility_is_what_the_record_says(cell_name):
    """10 of 15 frozen cells are feasible, and WHICH ten is pinned.

    If a data refresh or a split change moves any cell across this line, this
    test fails and the record in docs/SPECTRA_CONTROL_FEASIBILITY.md has to be
    updated deliberately rather than discovered later.
    """
    want_ok, want_bad = EXPECTED[cell_name]
    got_ok, got_bad = [], []
    for seed in (42, 43, 44, 45, 46):
        try:
            split, _cols = ss._prep_spectra(cell_name, seed)
        except Exception as exc:                       # noqa: BLE001
            pytest.skip(f"SPECTRA data unavailable for {cell_name}: "
                        f"{type(exc).__name__}")
        y = split.y_test.to_numpy()
        ip = split.X_test[ss.SEGMENT_FLAG].to_numpy().astype(bool)
        (got_ok if ss.control_feasibility(ip, y)["feasible"]
         else got_bad).append(seed)

    assert tuple(got_ok) == want_ok and tuple(got_bad) == want_bad, (
        f"{cell_name} feasibility changed: feasible {got_ok} (expected "
        f"{list(want_ok)}), infeasible {got_bad} (expected {list(want_bad)}). "
        "Update docs/SPECTRA_CONTROL_FEASIBILITY.md and this table together.")


def test_energy_steel_is_short_on_positives_not_negatives():
    """The DIRECTION of the shortfall is the finding.

    energy_steel's pocket holds roughly three quarters of the test fold's
    positives, which is why the complement runs out of them. Negatives are
    abundant (around 4,900 outside against ~310 inside). A future change that
    made this a negative shortfall would be a different defect wearing the
    same error message.
    """
    try:
        split, _cols = ss._prep_spectra("energy_steel", 42)
    except Exception as exc:                           # noqa: BLE001
        pytest.skip(f"SPECTRA data unavailable: {type(exc).__name__}")
    y = split.y_test.to_numpy()
    ip = split.X_test[ss.SEGMENT_FLAG].to_numpy().astype(bool)
    f = ss.control_feasibility(ip, y)

    assert f["feasible"] is False
    assert f["segment_positives"] > f["complement_positives"], (
        "the positives shortfall is the whole finding")
    assert f["segment_negatives"] < f["complement_negatives"], (
        "negatives were never the constraint; if they are now, this is a "
        "different defect and the analysis document is stale")
