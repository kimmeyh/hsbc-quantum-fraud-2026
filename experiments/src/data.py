"""Data loading and splitting per PREREGISTRATION.md.

ULB source files live in the existing XGBvHQXGB checkout; nothing is copied.
All feature selection is fit on train only (leakage rule).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_selection import mutual_info_classif

ULB_CSV = Path(r"D:\Data\Harold\github\XGBvHQXGB\datasets\creditcard.csv")
SPECTRA_DIR = Path(__file__).resolve().parents[1] / "data" / "spectra"

STRATIFIED_SEEDS = (42, 43, 44, 45, 46)
LABEL_COL = "Class"
TIME_COL = "Time"


@dataclass
class Split:
    X_train: pd.DataFrame
    y_train: pd.Series
    X_val: pd.DataFrame
    y_val: pd.Series
    X_test: pd.DataFrame
    y_test: pd.Series
    protocol: str
    seed: int | None


def load_ulb() -> pd.DataFrame:
    df = pd.read_csv(ULB_CSV)
    assert LABEL_COL in df.columns and TIME_COL in df.columns
    assert df[LABEL_COL].sum() == 492 and len(df) == 284807, "unexpected ULB variant"
    return df


def stratified_split(df: pd.DataFrame, seed: int) -> Split:
    """60/20/20 stratified on the label (prereg: stratified protocol)."""
    from sklearn.model_selection import train_test_split

    X = df.drop(columns=[LABEL_COL])
    y = df[LABEL_COL]
    X_train, X_rest, y_train, y_rest = train_test_split(
        X, y, test_size=0.40, stratify=y, random_state=seed
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_rest, y_rest, test_size=0.50, stratify=y_rest, random_state=seed
    )
    return Split(X_train, y_train, X_val, y_val, X_test, y_test, "stratified", seed)


def temporal_split(df: pd.DataFrame) -> Split:
    """70/10/20 by time order (prereg: temporal protocol; single split, no resampling)."""
    df = df.sort_values(TIME_COL, kind="stable").reset_index(drop=True)
    n = len(df)
    i_tr, i_va = int(n * 0.70), int(n * 0.80)
    X = df.drop(columns=[LABEL_COL])
    y = df[LABEL_COL]
    return Split(
        X.iloc[:i_tr], y.iloc[:i_tr],
        X.iloc[i_tr:i_va], y.iloc[i_tr:i_va],
        X.iloc[i_va:], y.iloc[i_va:],
        "temporal", None,
    )


def top_k_features(X_train: pd.DataFrame, y_train: pd.Series, k: int, seed: int = 0) -> list[str]:
    """Mutual-information top-k, computed on train only (prereg feature rule)."""
    mi = mutual_info_classif(X_train, y_train, random_state=seed)
    order = np.argsort(mi)[::-1]
    return [X_train.columns[i] for i in order[:k]]


def qubo_vars(n_features: int, schedule: int) -> int:
    """Weak-classifier count = Dirac variable count for CVQBoost schedules."""
    from math import comb

    v = n_features
    if schedule >= 2:
        v += comb(n_features, 2)
    if schedule >= 3:
        v += comb(n_features, 3)
    return v
