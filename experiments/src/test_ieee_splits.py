"""Known-answer tests for ieee_splits.py, the GroupKFold-by-month
rolling-origin splitter (PREREGISTRATION.md v1.1 section 8.2). Sprint 6
Task B (F3 prep, issue #32): PREPARATION ONLY -- proves no temporal
leakage across folds; fits no model arm, writes no results.json row.

Run: your venv interpreter (docs/ENVIRONMENT.md) -m pytest experiments/src/test_ieee_splits.py -q
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import ieee_splits as S


def _make_fixture(n_months: int = 7, rows_per_month: int = 100, seed: int = 0) -> pd.DataFrame:
    """Synthetic frame spanning n_months calendar-month buckets (day // 30),
    starting at day 1 (TransactionDT=86400) exactly like the real file."""
    rng = np.random.default_rng(seed)
    rows = []
    tid = 2987000
    for m in range(n_months):
        day_lo, day_hi = m * 30 + 1, (m + 1) * 30  # stay inside bucket m (day // 30 == m)
        days = rng.integers(day_lo, day_hi, size=rows_per_month)
        for d in days:
            rows.append({
                "TransactionID": tid,
                "TransactionDT": int(d) * 86400 + int(rng.integers(0, 86400)),
                "isFraud": int(rng.random() < 0.03),
            })
            tid += 1
    df = pd.DataFrame(rows).sample(frac=1.0, random_state=seed).reset_index(drop=True)
    return df


def test_month_of_matches_day_over_30():
    df = _make_fixture()
    from ieee_features import add_day
    expected = (add_day(df) // 30).astype("int32")
    pd.testing.assert_series_equal(S.month_of(df), expected, check_names=False)


def test_rolling_origin_produces_three_folds_with_disjoint_eval_months():
    df = _make_fixture(n_months=7)
    folds = S.rolling_origin_folds(df)
    assert len(folds) == 3
    eval_months = [f.eval_month for f in folds]
    assert len(set(eval_months)) == 3
    assert eval_months == sorted(eval_months)  # rolling forward in time


def test_no_temporal_leakage_train_never_contains_future_eval_rows():
    """The load-bearing invariant: no fold's training index may contain a
    row belonging to ANY evaluation window at or after that fold's eval
    month, and the eval index for a fold is fully disjoint from its own
    training index. assert_no_temporal_leakage must not raise."""
    df = _make_fixture(n_months=7)
    folds = S.rolling_origin_folds(df)
    S.assert_no_temporal_leakage(df, folds)  # must not raise

    month = S.month_of(df)
    for f in folds:
        # Direct re-check, independent of the helper's own implementation:
        # every training row's month is strictly less than eval_month.
        assert (month.loc[f.train_idx] < f.eval_month).all()
        # No row index is shared between train and eval for this fold.
        assert set(f.train_idx).isdisjoint(set(f.eval_idx))


def test_later_fold_training_set_grows_and_stays_prefix_only():
    """A rolling-origin schedule's fold k+1 training set must be a
    superset of fold k's (strictly more history: it adds exactly fold k's
    own eval rows, since fold k's eval month becomes part of fold k+1's
    training prefix), and must never include ITS OWN eval rows or any
    row from a month at or after its own eval month (the real no-leakage
    invariant -- a later fold training on an earlier fold's now-past eval
    month is correct rolling-origin behavior, not leakage)."""
    df = _make_fixture(n_months=7)
    folds = S.rolling_origin_folds(df)
    for i, f in enumerate(folds):
        assert set(f.train_idx).isdisjoint(set(f.eval_idx)), (
            f"fold {i} (eval month {f.eval_month}) training set contains "
            "its own evaluation rows")
        if i > 0:
            assert set(folds[i - 1].train_idx) <= set(f.train_idx)
            # The growth is exactly the previous fold's eval rows (its
            # eval month is now part of this fold's training history).
            grown = set(f.train_idx) - set(folds[i - 1].train_idx)
            assert grown == set(folds[i - 1].eval_idx)


def test_assert_no_temporal_leakage_catches_injected_violation():
    """Negative control: deliberately construct a leaking fold and confirm
    the guard actually raises, so the test above is not vacuously true."""
    df = _make_fixture(n_months=7)
    folds = S.rolling_origin_folds(df)
    bad = folds[0]
    # Inject one row from the eval index into the training index.
    leaked_train_idx = bad.train_idx.append(bad.eval_idx[:1])
    bad_fold = S.TemporalFold(leaked_train_idx, bad.eval_idx, bad.train_months, bad.eval_month)
    with pytest.raises(AssertionError):
        S.assert_no_temporal_leakage(df, [bad_fold])


def test_too_few_months_raises():
    df = _make_fixture(n_months=3)
    with pytest.raises(ValueError):
        S.rolling_origin_folds(df)


def test_split_xy_shapes_and_label_removed_from_X():
    df = _make_fixture(n_months=7)
    folds = S.rolling_origin_folds(df)
    d = S.split_xy(df, folds[0])
    assert S.LABEL_COL not in d["X_train"].columns
    assert S.LABEL_COL not in d["X_eval"].columns
    assert len(d["X_train"]) == len(d["y_train"]) == len(folds[0].train_idx)
    assert len(d["X_eval"]) == len(d["y_eval"]) == len(folds[0].eval_idx)
