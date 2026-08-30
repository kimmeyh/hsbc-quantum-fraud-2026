"""Known-answer tests for metrics.py v1.1 (Sprint 1 acceptance criterion 2).
Run: .venv\\Scripts\\python.exe -m pytest experiments/src/test_metrics.py -q
"""
import numpy as np
import pytest
from scipy import stats

import metrics as M


RNG = np.random.default_rng(7)
N = 6000
Y = (RNG.random(N) < 0.03).astype(int)  # ~3% positives
GOOD = np.clip(0.45 * Y + 0.55 * RNG.random(N), 0, 1)  # informative, overlapping scores
NOISE = RNG.random(N)                                  # uninformative scores


def test_wilson_matches_statsmodels():
    sm = pytest.importorskip("statsmodels.stats.proportion")
    for k, n in [(5, 10), (98, 100), (0, 50), (37, 412)]:
        lo, hi = M.wilson_interval(k, n)
        slo, shi = sm.proportion_confint(k, n, alpha=0.05, method="wilson")
        assert lo == pytest.approx(slo, abs=1e-9)
        assert hi == pytest.approx(shi, abs=1e-9)


def test_stratified_indices_preserve_class_counts():
    idx = M.stratified_indices(Y, np.random.default_rng(0), n_boot=8)
    for row in idx:
        assert Y[row].sum() == Y.sum()
        assert len(row) == len(Y)


def test_bca_ci_covers_point_and_orders():
    r = M.bca_ci(Y, GOOD, "auprc", n_boot=400, seed=0)
    lo, hi = r["ci95"]
    assert lo < r["point"] < hi
    assert 0 <= lo <= hi <= 1


def test_bca_matches_scipy_on_simple_statistic():
    # Validate the BCa mechanics (z0 + jackknife acceleration) against scipy's
    # reference implementation on the mean of a skewed sample.
    x = np.random.default_rng(3).lognormal(size=400)
    boot_rng = np.random.default_rng(11)
    boot = np.array([x[boot_rng.integers(0, len(x), len(x))].mean() for _ in range(2000)])
    jack = np.array([np.delete(x, i).mean() for i in range(len(x))])
    lo, hi = M._bca_interval(float(x.mean()), boot, jack)
    ref = stats.bootstrap((x,), np.mean, n_resamples=2000, method="BCa",
                          random_state=12).confidence_interval
    assert lo == pytest.approx(ref.low, rel=0.05)
    assert hi == pytest.approx(ref.high, rel=0.05)


def test_paired_delta_identical_arms_is_zero():
    r = M.paired_delta_ci(Y, GOOD, GOOD, n_boot=200, seed=0)
    assert r["diff"] == 0.0
    assert r["ci95"][0] == pytest.approx(0.0, abs=1e-12)
    assert r["ci95"][1] == pytest.approx(0.0, abs=1e-12)
    assert not r["excludes_zero"]


def test_paired_delta_detects_real_gap():
    r = M.paired_delta_ci(Y, GOOD, NOISE, n_boot=400, seed=0)
    assert r["diff"] > 0
    assert r["excludes_zero"]


def test_seed_mean_t_interval():
    r = M.seed_mean_t_interval([0.02, 0.03, 0.025, 0.028, 0.022,
                                0.031, 0.027, 0.024, 0.026, 0.029])
    assert r["excludes_zero"] and r["mean"] == pytest.approx(0.0262, abs=1e-3)
    r0 = M.seed_mean_t_interval([0.01, -0.01, 0.005, -0.005, 0.0])
    assert not r0["excludes_zero"]


def test_mde_positive_and_scales_with_sd():
    assert M.mde(0.02, 10) > M.mde(0.01, 10) > 0


def test_calibration_perfectly_calibrated_scores():
    p = np.random.default_rng(5).random(200_000)
    y = (np.random.default_rng(6).random(200_000) < p).astype(int)
    rep = M.calibration_report(y, p)
    assert rep["ece_equal_mass"] < 0.01
    assert len(rep["reliability"]) == M.ECE_BINS


def test_operating_points_and_alert_budget():
    thr = M.threshold_alert_budget(GOOD, alert_rate=0.01)
    flagged = (GOOD >= thr).mean()
    assert flagged == pytest.approx(0.01, abs=0.005)
    ev = M.evaluate_at(Y, GOOD, thr, "alert_budget_0.01")
    assert ev["confusion"]["tp"] + ev["confusion"]["fn"] == Y.sum()
    lo, hi = ev["precision_wilson95"]
    assert lo - 1e-9 <= ev["precision"] <= hi + 1e-9


def test_tie_fraction():
    assert M.tie_fraction(np.array([0.1, 0.1, 0.2, 0.3])) == pytest.approx(0.25)
    assert M.tie_fraction(np.arange(10) / 10) == 0.0
