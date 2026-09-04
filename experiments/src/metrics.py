"""Evaluation and statistics per PREREGISTRATION.md v1.1 section 9.

Implements: step-wise average precision with tie reporting and prevalence,
stratified BCa bootstrap CIs (2,000 resamples), identical-index paired
delta-AP machinery, Wilson intervals for precision/recall, dual operating
points (max-F1 and fixed alert budget), equal-mass-binned ECE with
reliability-diagram data, Brier reported as a joint score only, and the
across-seed t-interval that decides H1b-primary.

BCa acceleration note: the acceleration constant is computed by a
class-stratified block jackknife (delete-one-block over N_JACK_BLOCKS
blocks) rather than delete-one-observation, because a full jackknife of
average precision over ~10^5 rows is computationally prohibitive. The
bias-correction term z0 uses the full bootstrap distribution. This
approximation is documented here and in the proposal appendix.
"""
from __future__ import annotations

import numpy as np
from scipy import stats
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score

N_BOOT = 2000
N_JACK_BLOCKS = 100
ECE_BINS = 15


# ---------------------------------------------------------------- resampling

def stratified_indices(y: np.ndarray, rng: np.random.Generator, n_boot: int = N_BOOT) -> np.ndarray:
    """(n_boot, n) index matrix resampling within each class stratum, so every
    resample keeps the exact class counts. Reused verbatim across paired arms."""
    y = np.asarray(y)
    pos = np.flatnonzero(y == 1)
    neg = np.flatnonzero(y == 0)
    out = np.empty((n_boot, len(y)), dtype=np.int64)
    out[:, : len(pos)] = rng.choice(pos, size=(n_boot, len(pos)), replace=True)
    out[:, len(pos):] = rng.choice(neg, size=(n_boot, len(neg)), replace=True)
    return out


def _jackknife_blocks(y: np.ndarray, rng: np.random.Generator) -> list[np.ndarray]:
    """Class-stratified partition into N_JACK_BLOCKS blocks (keep-mask per block)."""
    y = np.asarray(y)
    assign = np.empty(len(y), dtype=np.int64)
    for cls in (0, 1):
        idx = np.flatnonzero(y == cls)
        perm = rng.permutation(len(idx))
        assign[idx[perm]] = np.arange(len(idx)) % N_JACK_BLOCKS
    return [np.flatnonzero(assign != b) for b in range(N_JACK_BLOCKS)]


def _bca_interval(theta_hat: float, boot: np.ndarray, jack: np.ndarray,
                  alpha: float = 0.05) -> tuple[float, float]:
    boot = np.asarray(boot)
    boot = boot[np.isfinite(boot)]
    if len(boot) == 0:
        return float("nan"), float("nan")
    p0 = np.clip(np.mean(boot < theta_hat), 1e-6, 1 - 1e-6)
    z0 = stats.norm.ppf(p0)
    jm = jack.mean()
    num = np.sum((jm - jack) ** 3)
    den = 6.0 * (np.sum((jm - jack) ** 2) ** 1.5)
    a = num / den if den != 0 else 0.0
    lo_hi = []
    for z in (stats.norm.ppf(alpha / 2), stats.norm.ppf(1 - alpha / 2)):
        adj = stats.norm.cdf(z0 + (z0 + z) / (1 - a * (z0 + z)))
        lo_hi.append(float(np.quantile(boot, np.clip(adj, 0, 1))))
    return lo_hi[0], lo_hi[1]


def bca_ci(y: np.ndarray, p: np.ndarray, metric: str = "auprc",
           n_boot: int = N_BOOT, seed: int = 0) -> dict:
    """Stratified BCa CI for AUPRC or AUC-ROC. Prereg 9: 2,000 resamples."""
    y = np.asarray(y); p = np.asarray(p)
    fn = average_precision_score if metric == "auprc" else roc_auc_score
    rng = np.random.default_rng(seed)
    theta = float(fn(y, p))
    idx = stratified_indices(y, rng, n_boot)
    boot = np.array([fn(y[i], p[i]) for i in idx])
    jack = np.array([fn(y[k], p[k]) for k in _jackknife_blocks(y, rng)])
    lo, hi = _bca_interval(theta, boot, jack)
    return {"metric": metric, "point": theta, "ci95": [lo, hi],
            "n_boot": n_boot, "method": "stratified-BCa-blockjack"}


def paired_delta_ci(y: np.ndarray, p_a: np.ndarray, p_b: np.ndarray,
                    metric: str = "auprc", n_boot: int = N_BOOT, seed: int = 0) -> dict:
    """BCa CI on metric(A) - metric(B) with IDENTICAL resample indices on both
    arms (prereg 9). The H1b per-seed support statistic."""
    y = np.asarray(y); p_a = np.asarray(p_a); p_b = np.asarray(p_b)
    fn = average_precision_score if metric == "auprc" else roc_auc_score
    rng = np.random.default_rng(seed)
    theta = float(fn(y, p_a) - fn(y, p_b))
    idx = stratified_indices(y, rng, n_boot)
    boot = np.array([fn(y[i], p_a[i]) - fn(y[i], p_b[i]) for i in idx])
    jack = np.array([fn(y[k], p_a[k]) - fn(y[k], p_b[k])
                     for k in _jackknife_blocks(y, rng)])
    lo, hi = _bca_interval(theta, boot, jack)
    return {"metric": metric, "diff": theta, "ci95": [lo, hi],
            "excludes_zero": bool(lo > 0 or hi < 0), "n_boot": n_boot,
            "method": "paired-stratified-BCa-blockjack"}


def seed_mean_t_interval(deltas: list[float], alpha: float = 0.05) -> dict:
    """t-interval on the across-seed mean of per-seed paired deltas.
    THE decision rule for H1b-primary (prereg 3)."""
    d = np.asarray(deltas, dtype=float)
    n = len(d)
    m = float(d.mean())
    se = float(d.std(ddof=1) / np.sqrt(n)) if n > 1 else float("nan")
    tcrit = stats.t.ppf(1 - alpha / 2, df=n - 1) if n > 1 else float("nan")
    lo, hi = m - tcrit * se, m + tcrit * se
    return {"n_seeds": n, "mean": m, "se": se, "ci95": [float(lo), float(hi)],
            "excludes_zero": bool(lo > 0 or hi < 0)}


def mde(seed_sd: float, n_seeds: int, alpha: float = 0.05, power: float = 0.80) -> float:
    """Minimum detectable across-seed mean delta for a paired one-sample t-test
    (prereg 8.3). Margins below this are reported as indistinguishable."""
    df = n_seeds - 1
    return float((stats.t.ppf(1 - alpha / 2, df) + stats.t.ppf(power, df))
                 * seed_sd / np.sqrt(n_seeds))


# ------------------------------------------------------------------- metrics

def tie_fraction(p: np.ndarray) -> float:
    p = np.asarray(p)
    return float(1.0 - len(np.unique(p)) / len(p))


HEALTH_MODE_SHARE_MAX = 0.90
HEALTH_MIN_DISTINCT = 50


def score_health(p: np.ndarray) -> dict:
    """Amendment A6 (Sprint 3 retro improvement 1): score-distribution health.
    Degenerate score vectors (most rows sharing one value, or only a handful
    of distinct levels) make alert-budget and calibration metrics weak
    evidence even when ranking metrics are valid. WARN when the modal score
    covers > HEALTH_MODE_SHARE_MAX of rows or fewer than HEALTH_MIN_DISTINCT
    distinct values exist."""
    p = np.asarray(p)
    _, counts = np.unique(p, return_counts=True)
    n_distinct = int(len(counts))
    mode_share = float(counts.max() / len(p)) if len(p) else 0.0
    return {"n_distinct": n_distinct, "mode_share": mode_share,
            "warn": bool(mode_share > HEALTH_MODE_SHARE_MAX
                         or n_distinct < HEALTH_MIN_DISTINCT)}


def wilson_interval(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Wilson score interval (prereg 9; Brown-Cai-DasGupta)."""
    if n == 0:
        return float("nan"), float("nan")
    z = stats.norm.ppf(1 - alpha / 2)
    ph = k / n
    denom = 1 + z * z / n
    center = (ph + z * z / (2 * n)) / denom
    half = z * np.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / denom
    return float(center - half), float(center + half)


def threshold_max_f1(y_val: np.ndarray, p_val: np.ndarray) -> float:
    from sklearn.metrics import precision_recall_curve
    prec, rec, thr = precision_recall_curve(y_val, p_val)
    f1 = 2 * prec * rec / np.clip(prec + rec, 1e-12, None)
    return float(thr[max(int(np.nanargmax(f1[:-1])), 0)])


def threshold_alert_budget(p_val: np.ndarray, alert_rate: float = 0.005) -> float:
    """Threshold flagging the top alert_rate fraction (fixed alert budget
    operating point, prereg 9; handbook card-precision@k analogue)."""
    return float(np.quantile(np.asarray(p_val), 1 - alert_rate))


def evaluate_at(y: np.ndarray, p: np.ndarray, threshold: float, label: str) -> dict:
    y = np.asarray(y); p = np.asarray(p)
    yhat = (p >= threshold).astype(int)
    tp = int(((yhat == 1) & (y == 1)).sum()); fp = int(((yhat == 1) & (y == 0)).sum())
    fn = int(((yhat == 0) & (y == 1)).sum()); tn = int(((yhat == 0) & (y == 0)).sum())
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"operating_point": label, "threshold": float(threshold),
            "precision": precision, "precision_wilson95": wilson_interval(tp, tp + fp),
            "recall": recall, "recall_wilson95": wilson_interval(tp, tp + fn),
            "f1": f1, "confusion": {"tn": tn, "fp": fp, "fn": fn, "tp": tp}}


def calibration_report(y: np.ndarray, p: np.ndarray, n_bins: int = ECE_BINS) -> dict:
    """Equal-mass-binned ECE plus reliability-diagram data (prereg 9; Roelofs).
    Brier is included ONLY as a joint score, never a calibration measure."""
    y = np.asarray(y); p = np.asarray(p)
    order = np.argsort(p)
    bins = np.array_split(order, n_bins)
    rows, ece = [], 0.0
    for b in bins:
        if len(b) == 0:
            continue
        conf, acc = float(p[b].mean()), float(y[b].mean())
        rows.append({"n": len(b), "mean_pred": conf, "frac_pos": acc})
        ece += (len(b) / len(y)) * abs(conf - acc)
    return {"ece_equal_mass": float(ece), "n_bins": n_bins, "reliability": rows,
            "brier_joint_score": float(brier_score_loss(y, p))}


def summarize(y: np.ndarray, p_val_y: np.ndarray, p_val: np.ndarray,
              p_test: np.ndarray, seed: int = 0, alert_rate: float = 0.005) -> dict:
    """Full per-run test summary. Thresholds and calibration inputs come from
    validation only (leakage rule); y/p_test are held-out test rows."""
    y = np.asarray(y)
    prevalence = float(y.mean())
    out = {
        "auprc": float(average_precision_score(y, p_test)),
        "prevalence": prevalence,
        "auprc_baseline_equals_prevalence": prevalence,
        "auc_roc": float(roc_auc_score(y, p_test)),
        "tie_fraction": tie_fraction(p_test),
        "auprc_ci": bca_ci(y, p_test, "auprc", seed=seed),
        "auc_ci": bca_ci(y, p_test, "auc", seed=seed),
        "operating_points": [
            evaluate_at(y, p_test, threshold_max_f1(p_val_y, p_val), "max_f1_on_val"),
            evaluate_at(y, p_test, threshold_alert_budget(p_val, alert_rate),
                        f"alert_budget_{alert_rate}"),
        ],
        "calibration": calibration_report(y, p_test),
        "score_health": score_health(p_test),   # A6
    }
    return out
