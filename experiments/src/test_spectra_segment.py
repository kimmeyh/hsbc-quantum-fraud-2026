"""Known-answer tests for SPECTRA in-segment machinery (H5; Sprint 6 F24, card #34).

Covers: the leak-free contract (a test that FAILS if target/target_real/
in_pocket ever reach a feature matrix), the matched random-segment control's
exact size/base-rate match, the >=50-test-positives rule enforced in code
(not merely documented), and the 3 frozen cells' config hashes being stable
and distinct.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

SRC = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC))

import spectra_segment as seg  # noqa: E402


# --------------------------------------------------------------- leak guard

def test_assert_no_label_leak_passes_clean_features():
    seg.assert_no_label_leak(["a", "b", "c"])  # no raise


@pytest.mark.parametrize("leaked_col", ["target", "target_real", "in_pocket"])
def test_assert_no_label_leak_fails_on_each_label_column(leaked_col):
    with pytest.raises(AssertionError):
        seg.assert_no_label_leak(["a", "b", leaked_col])


def test_assert_no_label_leak_fails_on_all_three_at_once():
    with pytest.raises(AssertionError):
        seg.assert_no_label_leak(["target", "target_real", "in_pocket", "safe_col"])


def _toy_spectra_df(n=400, seed=0):
    rng = np.random.default_rng(seed)
    x1 = rng.normal(size=n)
    x2 = rng.normal(size=n)
    in_pocket = (rng.random(n) < 0.2).astype(int)
    target = (rng.random(n) < np.where(in_pocket == 1, 0.6, 0.2)).astype(int)
    target_real = (rng.random(n) < 0.15).astype(int)
    return pd.DataFrame({"x1": x1, "x2": x2, "in_pocket": in_pocket,
                         "target_real": target_real, "target": target})


def test_spectra_split_drops_other_label_and_active_label_but_keeps_in_pocket():
    df = _toy_spectra_df()
    split = seg.spectra_split(df, seed=42, label_col="target")
    assert "target" not in split.X_train.columns
    assert "target_real" not in split.X_train.columns
    assert "in_pocket" in split.X_train.columns
    # y is exactly the dropped label column's values.
    assert set(split.y_train.unique()) <= {0, 1}


def test_segment_feature_cols_excludes_in_pocket_and_passes_leak_guard():
    df = _toy_spectra_df()
    split = seg.spectra_split(df, seed=42, label_col="target")
    cols = seg.segment_feature_cols(split.X_train)
    assert "in_pocket" not in cols
    assert set(cols) == {"x1", "x2"}


# SPECTRA CSVs are gitignored like the other raw datasets. Skip where they are
# absent (clean checkout, CI) and run normally where they are present.
import data as _data

_SPECTRA_PRESENT = all(
    (_data.SPECTRA_DIR / f"spectra_{_n}.csv").exists() for _n in _data.SPECTRA_NAMES)


@pytest.mark.skipif(not _SPECTRA_PRESENT,
                    reason="SPECTRA CSVs not on disk (expected on a clean checkout)")
def test_real_spectra_loader_feature_list_never_contains_labels():
    """End-to-end guard using the real frozen loader (data.py), not the toy
    fixture: data.spectra_features must never emit a label/flag column."""
    import data

    for name in data.SPECTRA_NAMES:
        df = data.load_spectra(name)
        feats = data.spectra_features(df)
        seg.assert_no_label_leak(feats)   # fails the whole suite if it ever leaks


# -------------------------------------------------- matched random control

def test_matched_random_segment_matches_size_and_base_rate_exactly():
    rng_data = np.random.default_rng(1)
    n = 5000
    y = (rng_data.random(n) < 0.3).astype(int)
    in_pocket = np.zeros(n, dtype=bool)
    # Build a pocket with a base rate that differs sharply from the overall 0.3.
    pocket_idx = rng_data.choice(n, size=200, replace=False)
    in_pocket[pocket_idx] = True
    y[pocket_idx] = (rng_data.random(200) < 0.8).astype(int)   # pocket base rate ~0.8

    rng = np.random.default_rng(7)
    control = seg.matched_random_segment(in_pocket, rng, y)

    assert control.sum() == in_pocket.sum()
    assert y[control].sum() == y[in_pocket].sum()
    # The control is drawn from the full pool, not restricted to the pocket
    # itself in general (a random draw could coincide, but is not required to).
    assert control.dtype == bool and control.shape == in_pocket.shape


def test_matched_random_segment_is_reproducible_given_the_same_rng_state():
    rng_data = np.random.default_rng(2)
    n = 1000
    y = (rng_data.random(n) < 0.25).astype(int)
    in_pocket = np.zeros(n, dtype=bool)
    in_pocket[:80] = True

    c1 = seg.matched_random_segment(in_pocket, np.random.default_rng(99), y)
    c2 = seg.matched_random_segment(in_pocket, np.random.default_rng(99), y)
    np.testing.assert_array_equal(c1, c2)


def test_matched_random_segment_feasibility_is_a_pool_subset_invariant():
    """Feasibility against the COMPLEMENT pool (revised, PR #36 finding 3).

    The control is drawn from rows OUTSIDE the segment, so matching is no longer
    automatic: a pocket holding more than half the positives (or negatives)
    cannot be size- and rate-matched from what remains, and the function's
    asserts SHOULD fire there. That is a real constraint of a valid control, not
    a defect -- the previous version could always match only because it was
    allowed to reuse the segment's own rows.

    SPECTRA pockets are a small fraction of each split, so this holds in
    practice; the test exercises the feasible regime and confirms the
    infeasible one raises rather than silently returning an overlapping control.
    """
    rng_data = np.random.default_rng(11)
    for trial in range(20):
        n = rng_data.integers(20, 500)
        rate = rng_data.uniform(0.05, 0.95)
        y = (rng_data.random(n) < rate).astype(int)
        if y.sum() == 0 or y.sum() == n:
            continue
        # feasible regime: pocket at most a third of the rows, as SPECTRA's are
        pocket_size = int(rng_data.integers(1, max(2, n // 3)))
        pocket_idx = rng_data.choice(n, size=pocket_size, replace=False)
        in_pocket = np.zeros(n, dtype=bool)
        in_pocket[pocket_idx] = True
        n_pos, n_neg = int(y[in_pocket].sum()), int((~y.astype(bool))[in_pocket].sum())
        if n_pos > int(y.sum()) - n_pos or n_neg > int((y == 0).sum()) - n_neg:
            continue                      # genuinely infeasible against the complement
        control = seg.matched_random_segment(in_pocket, np.random.default_rng(trial), y)
        assert control.sum() == in_pocket.sum()
        assert y[control].sum() == y[in_pocket].sum()
        assert not (control & in_pocket).any(), "control must be disjoint"

    # and the infeasible case must RAISE rather than return an overlapping control
    y_small = np.array([1, 1, 1, 0])
    pocket = np.array([True, True, False, False])   # 2 of 3 positives in-segment
    with pytest.raises(AssertionError):
        seg.matched_random_segment(pocket, np.random.default_rng(0), y_small)


# --------------------------------------------------- >=50 rule enforcement

def _scores_perfectly_separating(y):
    # Perfect ranking: score == y plus tiny noise to avoid literal ties.
    rng = np.random.default_rng(0)
    return y.astype(float) + rng.normal(scale=1e-6, size=len(y))


def test_evaluate_in_segment_unscoreable_below_floor():
    n = 300
    y = np.zeros(n, dtype=int)
    y[:20] = 1              # only 20 positives overall
    in_pocket = np.zeros(n, dtype=bool)
    in_pocket[:49] = True   # 49-row pocket, at most 20 positives -- well under 50
    p = _scores_perfectly_separating(y)

    result = seg.evaluate_in_segment(y, p, in_pocket, seed=42)
    assert result["in_segment"]["status"] == "unscoreable"
    assert result["random_control"]["status"] == "not_computed"
    assert result["edge"] is None


def test_evaluate_in_segment_scored_when_floor_cleared():
    rng = np.random.default_rng(3)
    n = 4000
    y = (rng.random(n) < 0.3).astype(int)
    in_pocket = np.zeros(n, dtype=bool)
    pocket_idx = rng.choice(n, size=400, replace=False)
    in_pocket[pocket_idx] = True
    # Force the pocket to carry >=50 positives.
    y[pocket_idx[:120]] = 1
    p = _scores_perfectly_separating(y)

    result = seg.evaluate_in_segment(y, p, in_pocket, seed=42)
    assert result["in_segment"]["status"] == "scored"
    assert result["in_segment"]["n_positives"] >= seg.MIN_TEST_POSITIVES
    assert result["random_control"]["status"] in ("scored", "unscoreable")
    if result["random_control"]["status"] == "scored":
        assert result["random_control"]["n"] == result["in_segment"]["n"]
        assert result["random_control"]["n_positives"] == result["in_segment"]["n_positives"]
        assert result["edge"] is not None
        assert set(result["edge"]) == {"auc_roc", "auprc"}


def test_min_test_positives_constant_is_50():
    """Pin the H5(ii) floor (applied here to H5i replication cells too) so a
    silent edit cannot loosen the rule without a visible test failure."""
    assert seg.MIN_TEST_POSITIVES == 50


def test_evaluate_across_seeds_reports_dropped_seeds_never_silently():
    calls = {"n": 0}

    def fit_and_score(seed):
        calls["n"] += 1
        rng = np.random.default_rng(seed)
        n = 200
        y = (rng.random(n) < 0.3).astype(int)
        in_pocket = np.zeros(n, dtype=bool)
        in_pocket[:10] = True   # tiny pocket -> always unscoreable
        p = _scores_perfectly_separating(y)
        return y, p, in_pocket

    out = seg.evaluate_across_seeds(fit_and_score, seeds=(1, 2, 3))
    assert calls["n"] == 3
    assert out["n_seeds_scored"] == 0
    assert out["n_seeds_dropped"] == 3
    assert "edge_auprc_mean" not in out


# ------------------------------------------------------------- frozen cells

def test_three_frozen_cells_registered():
    assert len(seg.FROZEN_CELLS) == 3


def test_frozen_cells_have_distinct_stable_config_hashes():
    hashes = [c["config_hash"] for c in seg.FROZEN_CELLS]
    assert len(set(hashes)) == 3
    assert all(isinstance(h, str) and len(h) == 16 for h in hashes)


def test_frozen_cells_config_hash_is_deterministic():
    import store

    for cell in seg.FROZEN_CELLS:
        recomputed = store.config_hash(cell["config"])
        assert recomputed == cell["config_hash"]


def test_frozen_cell_lookup_by_name():
    cell = seg.frozen_cell_by_name("energy_steel")
    assert cell["dataset"] == "spectra_energy_steel"
    cell2 = seg.frozen_cell_by_name("spectra_oilgas_gasturbine")
    assert cell2["dataset"] == "spectra_oilgas_gasturbine"
    with pytest.raises(KeyError):
        seg.frozen_cell_by_name("not_a_real_cell")


def test_frozen_cells_are_all_schedule_3_target_label():
    for cell in seg.FROZEN_CELLS:
        assert cell["config"]["weak_cls_schedule"] == 3
        assert cell["config"]["label"] == "target"


def test_frozen_cells_variable_counts_fit_device_ceiling():
    """Section 5 / A2: schedule-3 vars = n + C(n,2) + C(n,3) (sequential build);
    the device ceiling is 949 (amendment A2). All 3 frozen cells must fit."""
    import data

    for cell in seg.FROZEN_CELLS:
        n = cell["config"]["n_features"]
        v = data.qubo_vars(n, 3, pair_build="sequential")
        assert v <= 949, f"{cell['dataset']}: {v} vars exceeds device ceiling"


def test_matched_control_is_disjoint_from_the_segment():
    """PR #36 review finding 3. The control was drawn from the FULL pool, so it
    shared rows with the segment it controls for (~20% overlap on a 400-row
    segment in 2000 rows). The reported edge is in-segment minus control, so
    shared rows pull it toward zero and bias H5(i) against detecting a real
    effect. Size, base rate and reproducibility were all tested; disjointness
    was not, which is why the defect shipped.
    """
    import numpy as np
    from spectra_segment import matched_random_segment

    rng = np.random.default_rng(0)
    n = 2000
    y = (rng.random(n) < 0.25).astype(int)
    in_pocket = np.zeros(n, dtype=bool)
    in_pocket[rng.choice(n, size=400, replace=False)] = True

    control = matched_random_segment(in_pocket, rng, y)

    overlap = int((control & in_pocket).sum())
    assert overlap == 0, f"control shares {overlap} rows with the segment"
    assert control.sum() == in_pocket.sum(), "control must match segment size"
    assert y[control].sum() == y[in_pocket].sum(), "control must match positive count"
