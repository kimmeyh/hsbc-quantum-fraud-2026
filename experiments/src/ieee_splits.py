"""IEEE-CIS temporal protocol: GroupKFold-by-month rolling origin
(PREREGISTRATION.md v1.1 section 8.2: "IEEE-CIS: GroupKFold by calendar
month with 3-fold rolling-origin evaluation"). Sprint 6 Task B (F3 prep,
issue #32): PREPARATION ONLY -- this builds and tests the splitter; it
never fits a model arm and never writes results.json.

Rolling origin, not plain GroupKFold: fold i's training set is every row
from months strictly BEFORE fold i's evaluation month(s), never rows from
a later month, and never rows from the same month held out for evaluation.
This is stricter than sklearn's GroupKFold (which would let a "future"
month's rows train while a "past" month is held out for some other fold)
and matches section 5 rule 5 ("aggregates use only rows strictly before
the split boundary").

JUDGMENT CALL (prereg silent on fold boundaries): with ~6.1 month-buckets
(day // 30) in the 182-day train file, 3-fold rolling-origin evaluation
uses the LAST 3 months as the three held-out evaluation windows in turn
(months 4, 5, 6 held out one at a time), each trained on every month
strictly before it (so fold on month 4 trains on months 0-3, fold on
month 5 trains on months 0-4, fold on month 6 trains on months 0-5).
Months 0-3 are never themselves evaluation windows: a rolling-origin
scheme needs a non-trivial training prefix, and month 0 in particular is
a partial bucket (the file starts at TransactionDT=86400, day index 1,
so month 0 spans days 1-29 only, see ieee_features.add_day). This gives
the preregistered "3-fold" count while keeping every fold's training
prefix non-empty and every held-out month whole. Documented here rather
than silently choosing a different boundary.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from ieee_features import add_day

LABEL_COL = "isFraud"
N_ROLLING_FOLDS = 3


@dataclass
class TemporalFold:
    train_idx: pd.Index
    eval_idx: pd.Index
    train_months: tuple
    eval_month: int


def month_of(df: pd.DataFrame) -> pd.Series:
    """Calendar-month bucket used as the GroupKFold group (documented
    judgment call: day // 30, see module docstring and ieee_features.add_day)."""
    return (add_day(df) // 30).astype("int32")


def rolling_origin_folds(df: pd.DataFrame, n_folds: int = N_ROLLING_FOLDS) -> list[TemporalFold]:
    """Build the preregistered 3-fold rolling-origin schedule. Each fold's
    training index holds only rows from months strictly before its eval
    month; the eval month itself is fully held out (no row from the eval
    month ever appears in a training index, current fold or otherwise)."""
    month = month_of(df)
    months = sorted(month.unique())
    if len(months) < n_folds + 1:
        raise ValueError(
            f"need at least {n_folds + 1} month buckets for {n_folds}-fold "
            f"rolling origin, found {len(months)}: {months}")

    eval_months = months[-n_folds:]
    folds = []
    for em in eval_months:
        train_months = tuple(m for m in months if m < em)
        train_idx = df.index[month.isin(train_months)]
        eval_idx = df.index[month == em]
        folds.append(TemporalFold(train_idx, eval_idx, train_months, em))
    return folds


def assert_no_temporal_leakage(df: pd.DataFrame, folds: list[TemporalFold]) -> None:
    """Hard invariant check: for every fold, no eval-month row's index
    appears in that fold's training index, and every training row's month
    is strictly less than the eval month. Raises AssertionError on any
    violation; callers (and the test suite) rely on this never being a
    silent no-op."""
    month = month_of(df)
    for f in folds:
        overlap = set(f.train_idx) & set(f.eval_idx)
        assert not overlap, f"fold eval={f.eval_month}: train/eval index overlap {overlap}"
        train_month_vals = month.loc[f.train_idx]
        assert (train_month_vals < f.eval_month).all(), (
            f"fold eval={f.eval_month}: training rows from month(s) "
            f">= eval month found: {sorted(train_month_vals[train_month_vals >= f.eval_month].unique())}")
        eval_month_vals = month.loc[f.eval_idx]
        assert (eval_month_vals == f.eval_month).all()


def split_xy(df: pd.DataFrame, fold: TemporalFold) -> dict:
    """Convenience: materialize X/y for one fold's train and eval rows.
    Matches data.py's Split-style naming (X_train/y_train/X_eval/y_eval);
    no validation carve-out here (the H3 ladder and B3 grid handle their
    own dedicated-validation fold downstream, per section 6)."""
    y = df[LABEL_COL]
    X = df.drop(columns=[LABEL_COL])
    return {
        "X_train": X.loc[fold.train_idx], "y_train": y.loc[fold.train_idx],
        "X_eval": X.loc[fold.eval_idx], "y_eval": y.loc[fold.eval_idx],
        "train_months": fold.train_months, "eval_month": fold.eval_month,
    }
