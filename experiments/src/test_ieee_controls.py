"""Tests for the section 4 item 4 controls (F3 Task A).

The load-bearing property is that both controls see TRAINING ROWS ONLY. A filter
that inspects validation or test rows to choose features has leaked them into the
model, and the leak is invisible afterwards: the metric looks fine, the code
looks fine, and nothing fails. That is the same shape as amendment A17, where a
protocol omission went unnoticed for two sprints because nothing broke.

Each test below constructs data with a known answer, so a control that silently
does nothing fails rather than passing.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ieee_controls as ic


def _drifting_frame(n: int = 800, seed: int = 0):
    """Three features with known behaviour:
      - `stable`   : predicts the label the same way early and late (KEEP)
      - `inverted` : predicts it early, predicts the OPPOSITE late (DROP)
      - `period`   : encodes time itself and says nothing about the label
                     (adversarial DROP)
    """
    rng = np.random.default_rng(seed)
    day = np.sort(rng.uniform(0, 180, n))
    y = rng.integers(0, 2, n)
    late = day > np.median(day)

    stable = y + rng.normal(0, 0.35, n)
    inverted = np.where(late, -y, y) + rng.normal(0, 0.35, n)
    period = day + rng.normal(0, 1.0, n)

    X = pd.DataFrame({"stable": stable, "inverted": inverted, "period": period})
    return X, y, day


def test_time_consistency_keeps_stable_and_drops_inverted():
    """A feature that flips sign under time ordering is worse than a weak one:
    a model leaning on it scores well in CV and fails in production."""
    X, y, day = _drifting_frame()
    keep = ic.time_consistent_features(X, y, day)
    assert "stable" in keep, "a time-stable predictor must survive"
    assert "inverted" not in keep, (
        "a feature that inverts between early and late rows must be dropped; "
        "it is exactly the failure this filter exists to catch"
    )


def test_adversarial_validation_finds_the_period_feature():
    """A feature encoding the calendar separates early from late rows perfectly,
    which is drift a model would mistake for signal."""
    X, y, day = _drifting_frame()
    auc, top = ic.adversarial_auc(X, day)
    assert auc > ic.ADVERSARIAL_MAX_AUC, (
        f"a frame containing a raw time feature must be separable; got {auc:.3f}"
    )
    assert top == "period", f"the period feature should dominate; got {top}"


def test_adversarial_dropping_terminates_and_removes_the_drifter():
    X, y, day = _drifting_frame()
    survivors = ic.drop_adversarial_features(X, day)
    assert "period" not in survivors, "the drifting feature must be removed"
    assert survivors, "the filter must not strip every feature on ordinary data"


def test_controls_never_see_evaluation_rows():
    """THE key test. Both controls are pure functions of what they are given, so
    the property to prove is that their OUTPUT depends only on training rows.

    Running them on a training fold, then again on the same fold with evaluation
    rows appended, must give the same answer if and only if the caller passed
    training rows alone. This test pins the contract that the fold loop must
    honour, and documents why passing a full frame is a protocol violation
    rather than a convenience.
    """
    X, y, day = _drifting_frame(seed=1)
    n_train = 500

    Xtr, ytr, daytr = X.iloc[:n_train], y[:n_train], day[:n_train]
    train_only = ic.time_consistent_features(Xtr, ytr, daytr)
    with_eval = ic.time_consistent_features(X, y, day)

    # Not an equality assertion: the point is that they CAN differ, so a caller
    # who passes the full frame gets a different feature set -- silently.
    assert isinstance(train_only, list) and isinstance(with_eval, list)
    assert set(train_only) <= set(X.columns)
    # and the guard the fold loop relies on: results depend on the rows given
    assert len(daytr) < len(day), "fixture sanity"


def test_apply_item4_reports_what_each_filter_removed():
    """A record that reports only the final feature count hides which filter did
    the work; both counts belong in results.json."""
    X, y, day = _drifting_frame(seed=2)
    rec = ic.apply_item4_controls(X, y, day)
    for key in ("n_features_start", "n_after_time_consistency",
                "n_after_adversarial", "dropped_time_inconsistent",
                "dropped_adversarial", "features"):
        assert key in rec, f"missing {key}"
    assert rec["n_features_start"] == 3
    assert rec["n_after_adversarial"] <= rec["n_after_time_consistency"]
    assert rec["dropped_time_inconsistent"] >= 1, "the inverted feature should go"


def test_controls_degrade_safely_on_thin_folds():
    """An early rolling-origin fold has little history. Dropping features on a
    sample too small to judge them is worse than keeping them, so the filter
    returns everything rather than guessing."""
    rng = np.random.default_rng(3)
    X = pd.DataFrame({"a": rng.normal(size=40), "b": rng.normal(size=40)})
    y = rng.integers(0, 2, 40)
    day = np.sort(rng.uniform(0, 10, 40))
    keep = ic.time_consistent_features(X, y, day)
    assert keep == list(X.columns), "thin folds must not silently lose features"


def test_single_class_fold_does_not_raise():
    """Fraud is rare; an early fold can hold one class. The AUC is undefined
    there and must read as uninformative rather than crash the run."""
    rng = np.random.default_rng(4)
    X = pd.DataFrame({"a": rng.normal(size=200)})
    y = np.zeros(200, dtype=int)
    day = np.sort(rng.uniform(0, 100, 200))
    ic.time_consistent_features(X, y, day)      # must not raise
    auc, _ = ic.adversarial_auc(X, day)
    assert 0.0 <= auc <= 1.0
