"""Evaluation per PREREGISTRATION.md: all statement metrics, threshold tuned on
validation only, bootstrap 95% CIs (1000 resamples) on test."""
from __future__ import annotations

import numpy as np
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

N_BOOT = 1000


def tune_threshold(y_val: np.ndarray, p_val: np.ndarray) -> float:
    """Threshold maximizing F1 on the validation set (touched once per frozen config)."""
    from sklearn.metrics import precision_recall_curve

    prec, rec, thr = precision_recall_curve(y_val, p_val)
    f1 = 2 * prec * rec / np.clip(prec + rec, 1e-12, None)
    return float(thr[max(int(np.nanargmax(f1[:-1])), 0)])


def evaluate(y: np.ndarray, p: np.ndarray, threshold: float) -> dict:
    yhat = (p >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, yhat, labels=[0, 1]).ravel()
    return {
        "auprc": float(average_precision_score(y, p)),
        "auc_roc": float(roc_auc_score(y, p)),
        "f1": float(f1_score(y, yhat, zero_division=0)),
        "precision": float(precision_score(y, yhat, zero_division=0)),
        "recall": float(recall_score(y, yhat, zero_division=0)),
        "brier": float(brier_score_loss(y, p)),
        "threshold": float(threshold),
        "confusion": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
    }


def bootstrap_ci(y: np.ndarray, p: np.ndarray, metric: str = "auprc",
                 n_boot: int = N_BOOT, seed: int = 0) -> dict:
    fn = average_precision_score if metric == "auprc" else roc_auc_score
    rng = np.random.default_rng(seed)
    n = len(y)
    stats = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        if y[idx].sum() == 0:
            continue
        stats.append(fn(y[idx], p[idx]))
    lo, hi = np.percentile(stats, [2.5, 97.5])
    return {"metric": metric, "point": float(fn(y, p)), "ci95": [float(lo), float(hi)]}


def bootstrap_diff_ci(y: np.ndarray, p_a: np.ndarray, p_b: np.ndarray,
                      metric: str = "auprc", n_boot: int = N_BOOT, seed: int = 0) -> dict:
    """Paired bootstrap CI on metric(A) - metric(B); the H1b/H5 decision statistic."""
    fn = average_precision_score if metric == "auprc" else roc_auc_score
    rng = np.random.default_rng(seed)
    n = len(y)
    diffs = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        if y[idx].sum() == 0:
            continue
        diffs.append(fn(y[idx], p_a[idx]) - fn(y[idx], p_b[idx]))
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    return {
        "metric": metric,
        "diff": float(fn(y, p_a) - fn(y, p_b)),
        "ci95": [float(lo), float(hi)],
        "excludes_zero": bool(lo > 0 or hi < 0),
    }
