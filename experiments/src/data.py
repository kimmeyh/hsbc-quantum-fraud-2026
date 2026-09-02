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
_DATA = Path(__file__).resolve().parents[1] / "data"
SPECTRA_DIR = _DATA / "spectra"
IEEE_CIS_DIR = _DATA / "ieee-cis"

SPECTRA_NAMES = ("energy_steel", "oilgas_gasturbine", "maintenance_ai4i", "telecom_churn")
SPECTRA_ROWS = {"energy_steel": 35040, "oilgas_gasturbine": 36733,
                "maintenance_ai4i": 10000, "telecom_churn": 3150}

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


_CIS_STRING_COLS = frozenset(
    ["ProductCD", "card4", "card6", "P_emaildomain", "R_emaildomain",
     "DeviceType", "DeviceInfo"]
    + [f"M{i}" for i in range(1, 10)]
    + [f"id_{i:02d}" for i in range(12, 39)]
)


def _cis_dtypes(path) -> dict:
    """float32 for every numeric column (halves memory vs pandas' float64
    default, the standard practice for this dataset); strings stay object."""
    cols = pd.read_csv(path, nrows=0).columns
    dt = {}
    for c in cols:
        if c == "TransactionID":
            dt[c] = "int32"
        elif c == "isFraud":
            dt[c] = "int8"
        elif c not in _CIS_STRING_COLS:
            dt[c] = "float32"
    return dt


def load_ieee_cis_train() -> pd.DataFrame:
    """IEEE-CIS train: transaction left-joined with identity on TransactionID.
    Feature engineering (D-normalization, UID aggregates) happens downstream
    inside folds per PREREGISTRATION v1.1 section 5, never here."""
    tx_path = IEEE_CIS_DIR / "train_transaction.csv"
    id_path = IEEE_CIS_DIR / "train_identity.csv"
    tx = pd.read_csv(tx_path, dtype=_cis_dtypes(tx_path))
    ident = pd.read_csv(id_path, dtype=_cis_dtypes(id_path))
    df = tx.merge(ident, on="TransactionID", how="left")
    assert len(df) == 590540, f"unexpected IEEE-CIS train rows: {len(df)}"
    assert "isFraud" in df.columns
    return df


def load_spectra(name: str) -> pd.DataFrame:
    """One SPECTRA dataset with the leak-free contract: {target, target_real,
    in_pocket} are labels/flags, never features (FourierWall2 leakage lesson)."""
    assert name in SPECTRA_NAMES, name
    df = pd.read_csv(SPECTRA_DIR / f"spectra_{name}.csv")
    assert len(df) == SPECTRA_ROWS[name], f"{name}: unexpected rows {len(df)}"
    for col in ("target", "target_real", "in_pocket"):
        assert col in df.columns, f"{name}: missing {col}"
    return df


def spectra_features(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c not in ("target", "target_real", "in_pocket")]


def validate_all() -> dict:
    """Sprint 1 acceptance check: every dataset loads with validated shape."""
    report = {}
    ulb = load_ulb()
    report["ulb"] = {"rows": len(ulb), "frauds": int(ulb[LABEL_COL].sum())}
    cis = load_ieee_cis_train()
    report["ieee_cis"] = {"rows": len(cis), "cols": cis.shape[1],
                          "fraud_rate": round(float(cis["isFraud"].mean()), 4)}
    for name in SPECTRA_NAMES:
        s = load_spectra(name)
        report[f"spectra_{name}"] = {"rows": len(s),
                                     "features": len(spectra_features(s))}
    return report


def qubo_vars(n_features: int, schedule: int, pair_build: str = "sequential") -> int:
    """Weak-classifier count = Dirac variable count for CVQBoost schedules.

    Amendment A2: the sequential strategy (mandatory on Windows) caps pairs at
    the top-correlated n(n-3)/2, so singles+pairs total C(n,2) exactly (verified
    on hardware: n=15 -> 105 @ schedule 2, 560 @ schedule 3). The full-pair
    build (multi_processing, Linux/WSL2; amendment A3) uses all C(n,2) pairs,
    adding n variables."""
    from math import comb

    assert pair_build in ("sequential", "full"), pair_build
    v = n_features
    if schedule >= 2:
        pairs = comb(n_features, 2) if pair_build == "full" else max(
            0, n_features * (n_features - 3) // 2)
        v += pairs
    if schedule >= 3:
        v += comb(n_features, 3)
    return v
