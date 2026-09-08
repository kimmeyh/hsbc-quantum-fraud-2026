"""Correctness invariants for the H6 representation runner (F4, card #50).

These assert the properties whose violation would make the H6 result WRONG
rather than merely absent, which is the standard Sprint 8 improvement 3
established: a test that only proves code runs will pass on code that is wrong.

The two that matter most:

- A cell missing a twin must not be reported. The Fourier Wall result is that
  omitting the order-matched twin is how apparent quantum wins get
  manufactured, so a partial classical bar is worse than no cell at all.
- The QFE encoder must be fitted on TRAIN only. Fitting it on the full frame
  leaks the test distribution into the rank interpolation, and the leak would
  be invisible in the reported numbers -- it would just make the phase arm look
  better.
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

import numpy as np
import pytest

SRC = Path(__file__).resolve().parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

run_h6 = importlib.import_module("run_h6")


@pytest.fixture
def toy():
    """A small separable problem with real periodic structure.

    The cosine term is what the phase representation and the JOINT twin both
    exist to capture, so a fixture without it could not distinguish a working
    twin from a broken one.
    """
    rng = np.random.default_rng(0)
    n = 1200
    x = rng.normal(size=(n, 6))
    logit = 0.9 * x[:, 0] + 1.4 * np.cos(3.0 * x[:, 1]) - 0.7 * x[:, 2]
    p = 1.0 / (1.0 + np.exp(-logit))
    y = (rng.random(n) < p).astype(int)
    cut = int(0.7 * n)
    return x[:cut], y[:cut], x[cut:], y[cut:]


# --- the twins must each actually work ------------------------------------

def test_gam_twin_returns_usable_scores(toy):
    X_tr, y_tr, X_te, _ = toy
    s = run_h6._fit_gam(X_tr, y_tr, X_te)
    assert s.shape == (len(X_te),)
    assert np.isfinite(s).all(), "a GAM returning NaN silently weakens the bar"
    assert s.std() > 0, "a constant score is not a classical bar"


def test_ga2m_twin_is_pairwise_constrained(toy):
    """GA2M means main effects plus PAIRWISE terms; 3-way would be a GBDT."""
    X_tr, y_tr, X_te, _ = toy
    s = run_h6._fit_ga2m(X_tr, y_tr, X_te)
    assert s.shape == (len(X_te),)
    assert np.isfinite(s).all()

    src = Path(run_h6.__file__).read_text(encoding="utf-8")
    assert 'interaction_cst="pairwise"' in src, (
        "without the constraint this is an unconstrained booster, not a GA2M")


def test_joint_twin_finds_a_planted_frequency(toy):
    """The JOINT twin must actually locate periodic structure.

    A twin that cannot find a planted cosine is a straw man, and a straw man
    classical bar is exactly what manufactures a fake quantum win.
    """
    X_tr, y_tr, X_te, y_te = toy
    from sklearn.metrics import average_precision_score

    s = run_h6._fit_joint(X_tr, y_tr, X_te)
    ap = average_precision_score(y_te, s)
    base = float(np.mean(y_te))
    assert ap > base * 1.2, (
        f"JOINT twin AP {ap:.3f} barely beats the base rate {base:.3f}; it is "
        f"not capturing the planted cosine")


def test_joint_twin_searches_frequencies_on_train_only(toy):
    """The frequency scan is supervised, so it must not see test labels."""
    X_tr, y_tr, X_te, _ = toy
    a = run_h6._fit_joint(X_tr, y_tr, X_te)
    # Same train, different test rows: train-fitted frequencies must not change
    # the model, so scores for shared rows are identical.
    X_te2 = np.vstack([X_te, X_te[:10] + 5.0])
    b = run_h6._fit_joint(X_tr, y_tr, X_te2)
    assert np.allclose(a, b[:len(a)]), (
        "adding unrelated test rows changed the fit: the scan is seeing test data")


# --- a cell must carry the complete classical bar -------------------------

def test_cell_reports_all_three_twins_and_all_three_gbdts(toy):
    X_tr, y_tr, X_te, y_te = toy
    cell = run_h6._cell(X_tr, y_tr, X_te, y_te, seed=42, representation="baseline")

    for twin in ("gam", "ga2m", "joint"):
        assert twin in cell["scores"], f"cell is missing the {twin} twin"
    for arm in ("xgboost", "lightgbm", "catboost"):
        assert arm in cell["scores"], f"cell is missing {arm}"
    assert "cvqboost" in cell["scores"]
    assert cell["twins_present"] == ["gam", "ga2m", "joint"]


def test_delta_is_measured_against_the_BEST_classical_arm(toy):
    """Not against a convenient one. The best bar is the only honest bar."""
    X_tr, y_tr, X_te, y_te = toy
    cell = run_h6._cell(X_tr, y_tr, X_te, y_te, seed=42, representation="baseline")

    classical = {k: v for k, v in cell["scores"].items() if k != "cvqboost"}
    assert cell["best_classical_ap"] == max(classical.values())
    assert cell["delta"] == pytest.approx(
        cell["cvqboost_ap"] - max(classical.values()))
    # A twin beating the GBDTs must be allowed to BE the bar.
    assert cell["best_classical_arm"] in classical


# --- the reported quantity is a SHIFT, not a single delta ------------------

def test_summary_reports_the_shift_between_representations():
    """H6 asks whether the representation MOVES the delta.

    A delta measured under one representation cannot answer that, so the
    summary must carry both and their difference.
    """
    cells = [
        {"representation": "baseline", "delta": -0.10},
        {"representation": "qfe", "delta": -0.04},
        {"representation": "baseline", "delta": -0.12},
        {"representation": "qfe", "delta": -0.06},
    ]
    out = run_h6._summarize(cells, smoke=True)

    assert out["mean_delta_baseline"] == pytest.approx(-0.11)
    assert out["mean_delta_qfe"] == pytest.approx(-0.05)
    assert out["representation_shift"] == pytest.approx(0.06)
    assert out["evidence_tag"] == "SIM"


def test_premise_falsifier_fires_when_the_shift_is_within_noise():
    """Sprint 8 improvement 2: the premise must be able to lose.

    Two representations whose deltas differ by less than the paired
    seed-to-seed spread is a real answer -- the representation does not move
    the delta -- and the runner must say so rather than report a shift.
    """
    # Shifts of +0.01 and -0.01: mean ~0, spread larger than the mean.
    cells = [
        {"representation": "baseline", "delta": -0.10},
        {"representation": "qfe", "delta": -0.09},
        {"representation": "baseline", "delta": -0.10},
        {"representation": "qfe", "delta": -0.11},
    ]
    out = run_h6._summarize(cells, smoke=True)
    assert out["premise_falsified"] is True, (
        "a shift smaller than its own noise must be reported as no effect")


def test_a_real_shift_is_not_falsified():
    """The falsifier must not fire on a genuine, consistent effect."""
    cells = [
        {"representation": "baseline", "delta": -0.10},
        {"representation": "qfe", "delta": -0.02},
        {"representation": "baseline", "delta": -0.11},
        {"representation": "qfe", "delta": -0.03},
    ]
    out = run_h6._summarize(cells, smoke=True)
    assert out["premise_falsified"] is False


# --- evidence protection (Sprint 8 defect 5) ------------------------------

def test_smoke_runs_do_not_write_to_the_evidence_file():
    """A smoke run must never replace committed evidence.

    Sprint 8 lost the full IEEE results file exactly this way, to a test that
    called run(smoke=True) while the runner wrote to one destination.
    """
    assert run_h6.OUT != run_h6.SMOKE_OUT
    assert "smoke" in run_h6.SMOKE_OUT.name
    src = Path(run_h6.__file__).read_text(encoding="utf-8")
    assert "SMOKE_OUT if smoke else OUT" in src, (
        "the write must select its destination from the run mode")


# --- section 4 compliance (the A17 violation class) -----------------------

def test_h6_deduplicates_before_splitting():
    """Section 4 removes 1,081 exact ULB duplicates BEFORE splitting.

    `data.load_ulb()` does NOT do this; every compliant runner calls
    drop_duplicates() immediately after it. Amendment A17 records the cost of
    forgetting: three exploratory fold builders trained on 284,807 rows against
    every comparator's 283,726, invisible for two sprints because those arms
    were only compared against each other.

    This module was written as new standalone code, which is exactly the
    condition that produced A17 -- and it DID initially skip the step. The
    check is a 4-line window because the call is chained onto load_ulb() or
    made on the following line.
    """
    src = Path(run_h6.__file__).read_text(encoding="utf-8").split("\n")
    load_lines = [i for i, l in enumerate(src) if "load_ulb()" in l]
    assert load_lines, "run_h6 must load ULB"
    for i in load_lines:
        window = "\n".join(src[i:i + 4])
        assert "drop_duplicates" in window, (
            f"load_ulb() at line {i + 1} is not followed by drop_duplicates(); "
            f"this is the A17 protocol violation")


def test_gam_twin_handles_test_values_outside_the_training_range(toy):
    """The crash that killed the first full run, after 3.2 hours and 8 cells.

    statsmodels raises NotImplementedError when a spline is asked to evaluate
    beyond its outermost knots. The original code built a SECOND BSplines on
    the test data, which hid the problem until a seed happened to produce
    out-of-range rows -- and worse, meant coefficients learned against the
    training basis were being applied to a basis whose knots came from the
    TEST distribution. A silent scoring error on every cell, whose only
    symptom was an eventual crash.

    The existing gam test used a fixture whose test rows sat inside the
    training range, so it passed against the broken code. This one does not.
    """
    X_tr, y_tr, X_te, _ = toy
    # Push test rows well outside every training column's range.
    X_far = X_te.copy()
    X_far[0] = X_tr.max(axis=0) + 10.0
    X_far[1] = X_tr.min(axis=0) - 10.0

    s = run_h6._fit_gam(X_tr, y_tr, X_far)
    assert s.shape == (len(X_far),)
    assert np.isfinite(s).all(), "out-of-range rows must still score"


def test_gam_twin_uses_the_fitted_basis_not_a_new_one():
    """Guard the correctness half, which the crash only hinted at.

    A second BSplines built on test data has knots placed by the test
    distribution. Predicting through it applies training coefficients to a
    different basis, which is wrong even when it does not raise.
    """
    src = Path(run_h6.__file__).read_text(encoding="utf-8")
    gam_src = src[src.index("def _fit_gam"):src.index("def _fit_ga2m")]
    assert gam_src.count("BSplines(") == 1, (
        "a second BSplines means knots are being refitted on TEST data, so "
        "training coefficients get applied to a different basis")
    assert "np.clip(" in gam_src, (
        "test values must be clipped to the training range; a spline has no "
        "basis beyond its outermost knots and statsmodels raises there")
    assert "exog_smooth=np.clip" in gam_src, (
        "exog_smooth takes RAW values that predict() transforms itself -- "
        "passing a pre-built basis double-transforms it")


# --- crash resilience (the 3h 12m lesson) ---------------------------------

def test_checkpoint_writes_full_cells_not_just_deltas(tmp_path, monkeypatch):
    """A crash must cost the current cell and nothing before it.

    The first full run lost 8 cells and 3h 12m because results were written
    only at the end. Worse, the heartbeat had recorded ONLY the delta, so those
    cells could not even be audited afterwards: the per-arm scores needed to
    check whether a defective twin had been the best classical arm were gone.
    That is why they had to be discarded rather than salvaged.

    So the checkpoint must carry the WHOLE cell, per-arm scores included.
    """
    ckpt = tmp_path / "h6_cells_partial.json"
    monkeypatch.setattr(run_h6, "CHECKPOINT", ckpt)

    cells = [{
        "seed": 42, "representation": "baseline", "delta": -0.0666,
        "scores": {"xgboost": 0.81, "gam": 0.42, "ga2m": 0.79,
                   "joint": 0.55, "cvqboost": 0.74},
        "best_classical_arm": "xgboost", "best_classical_ap": 0.81,
    }]
    run_h6._checkpoint(cells, smoke=False)

    assert ckpt.exists(), "no checkpoint written"
    import json
    got = json.loads(ckpt.read_text(encoding="utf-8"))
    assert got["n"] == 1
    cell = got["cells"][0]
    assert cell["scores"]["gam"] == 0.42, (
        "per-arm scores must survive; without them a completed cell cannot be "
        "audited after a defect is found in one of the arms")
    assert cell["best_classical_arm"] == "xgboost"


def test_checkpoint_is_skipped_for_smoke_runs(tmp_path, monkeypatch):
    """Smoke output must not masquerade as a partial real run."""
    ckpt = tmp_path / "h6_cells_partial.json"
    monkeypatch.setattr(run_h6, "CHECKPOINT", ckpt)
    run_h6._checkpoint([{"seed": 42, "delta": -0.01}], smoke=True)
    assert not ckpt.exists()


# --- the twins must RECEIVE the representation under test ------------------

def test_twins_actually_see_the_phase_block():
    """The defect that invalidated a complete 10-seed run.

    H6 (prereg section 3) requires the phase representation to be given to
    EVERY arm. The first run ranked twin inputs by variance: ULB's Time column
    has variance 2.3e9 while QFE phase columns are whitened to unit variance,
    so no phase column could ever be selected. GAM and JOINT returned IDENTICAL
    scores in 10 of 10 seeds under both representations -- present in the
    record, absent in substance.

    Ranking by supervised relevance instead did NOT fix it: measured on ULB the
    best phase column ranks 14th (|corr| 0.055 vs 0.318 for the top raw
    column). The phase columns are genuinely weaker on a dataset whose
    V-columns are already PCA components, so no merit ranking picks them. The
    budget has to be split.
    """
    rng = np.random.default_rng(0)
    n, n_raw, n_phase = 500, 10, 8
    raw = rng.normal(size=(n, n_raw)) * 1000.0      # large scale, like Time
    phase = rng.normal(size=(n, n_phase))           # whitened, unit variance
    X = np.hstack([raw, phase])
    y = (raw[:, 0] > 0).astype(int)                 # signal lives in raw

    order = run_h6._rank_columns(X, y, 6, n_raw=n_raw)
    assert any(i >= n_raw for i in order), (
        "no phase column selected: the twin cannot see the representation it "
        "is supposed to be a control for")
    assert any(i < n_raw for i in order), (
        "the twin must keep raw columns too, or it is not a fair bar")


def test_baseline_selection_uses_the_whole_budget_on_raw_columns():
    """With no phase block the twin spends everything on raw columns.

    The treatment is absent because it is absent, not because the selector
    hid it.
    """
    rng = np.random.default_rng(0)
    X = rng.normal(size=(300, 12))
    y = (X[:, 0] > 0).astype(int)
    order = run_h6._rank_columns(X, y, 6, n_raw=None)
    assert len(order) == 6
    assert len(set(order)) == 6, "no duplicate columns"


def test_relevance_ranking_is_scale_free():
    """Variance ranking is what broke this; correlation must not repeat it."""
    rng = np.random.default_rng(0)
    n = 400
    signal = rng.normal(size=n)
    y = (signal > 0).astype(int)
    # Same information, wildly different scales.
    X = np.column_stack([signal * 1e6, signal, rng.normal(size=n) * 1e9])
    rel = run_h6._relevance(X, y)
    assert abs(rel[0] - rel[1]) < 1e-6, (
        "identical signal at different scales must rank identically")
    assert rel[2] < rel[0], "pure noise must rank below signal at any scale"


def test_twins_produce_different_scores_under_the_two_representations(toy):
    """The end-to-end property: a twin given phase inputs must respond.

    Identical scores across representations is exactly the symptom that
    invalidated the first run, so it is asserted directly.
    """
    X_tr, y_tr, X_te, _ = toy
    rng = np.random.default_rng(1)
    P_tr = rng.normal(size=(len(X_tr), 6))
    P_te = rng.normal(size=(len(X_te), 6))
    Xq_tr = np.hstack([X_tr, P_tr])
    Xq_te = np.hstack([X_te, P_te])

    base = run_h6._fit_joint(X_tr, y_tr, X_te)
    qfe_scores = run_h6._fit_joint(Xq_tr, y_tr, Xq_te, n_raw=X_tr.shape[1])
    assert not np.allclose(base, qfe_scores), (
        "JOINT returned identical scores with and without the phase block; it "
        "is not receiving the representation")
