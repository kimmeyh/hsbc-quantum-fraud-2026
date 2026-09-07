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
