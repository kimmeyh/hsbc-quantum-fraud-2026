"""H6 representation effect: does a phase representation shift the delta?

PREREGISTRATION section 3, H6, EXPLORATORY:

    the QFE phase representation (exact Fourier Wall recipe) is given to EVERY
    arm. Question: does it shift the quantum-minus-classical delta? Every H6
    cell's classical bar includes trained-frequency GAM, GA2M, and an
    order-matched JOINT twin (supervised k-way cosine search fit by logistic
    regression) in addition to the GBDTs, per the Fourier Wall's demonstration
    that omitting the twin manufactures fake quantum wins.

WHY THE TWINS ARE THE POINT, not extra rigor.

A phase representation hands every arm access to periodic structure. If the
classical bar contains no model that can ALSO exploit periodic structure, then
any quantum-minus-classical gap measured under that representation is an
artifact of an unfair comparison rather than a finding. The Fourier Wall result
is precisely that omitting the order-matched twin is how apparent quantum wins
get manufactured. So a cell missing a twin is not reported at all.

WHAT IS MEASURED, and why a single number does not answer the question.

The hypothesis is about a SHIFT. So each cell is run twice, once on the
baseline representation and once with the QFE phase block appended, and the
reported quantity is

    delta_QFE - delta_baseline,   where delta = quantum AP - best classical AP

A large delta under QFE means nothing on its own; it has to be compared with
the same delta computed without the representation.

RUNTIME, sized before this file was written (Sprint 8 improvement 1). GAM was
the one unbounded term and was piloted: statsmodels GLMGam with BSplines scales
linearly, 0.0 / 0.2 / 0.4 s at 5k / 20k / 60k rows. With measured GBDT fits
from ieee_classical.json the whole run is under 10 minutes.

PREMISE FALSIFIER (Sprint 8 improvement 2). The premise is that a phase
representation COULD shift the delta. It is disproved if the two deltas differ
by less than the seed-to-seed noise of the delta itself, which this module
computes and reports. That is a real answer, not a failed run.

Usage:
    python experiments/src/run_h6.py --smoke     # 1 seed, fast
    python experiments/src/run_h6.py
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score

sys.path.insert(0, str(Path(__file__).resolve().parent))
import data
import qfe
import store

OUT = Path(__file__).resolve().parents[1] / "results" / "h6_representation.json"
SMOKE_OUT = Path(__file__).resolve().parents[1] / "results" / "h6_representation_smoke.json"
PROGRESS = Path(__file__).resolve().parents[1] / "results" / "h6_progress.json"

SEEDS = tuple(range(42, 52))
SCHEDULE = 2             # frozen relaxation_schedule, not tuned here

# NO top-k reduction here, deliberately, and this differs from the standard
# proxy pipeline (qubo_proxy._prep reduces to k=13 via top_k_features before
# building the pool).
#
# H6 asks whether giving EVERY arm the phase representation shifts the delta.
# A top-13 selection by relevance would exclude the phase columns outright --
# on ULB the best of them ranks about 14th -- so reducing first would hand the
# quantum arm a pool with no phase information in it and the hypothesis could
# not be tested at all.
#
# The cost is that this arm is not the frozen k=13 configuration. The pool is
# built over every column: 30 in the baseline representation and 90 under QFE,
# which at a sequential pair build is 435 and 4,005 variables against the
# frozen arm's 78. That is legitimate here only because H6 runs entirely on the
# classical proxy [SIM], where no device ceiling applies. It would NOT be a
# runnable hardware configuration, and A.6 says so.


def _progress(stage: str, **fields) -> None:
    rec = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "stage": stage, **fields}
    try:
        PROGRESS.parent.mkdir(parents=True, exist_ok=True)
        PROGRESS.write_text(json.dumps(rec, indent=2, default=str) + "\n")
    except Exception:                                          # noqa: BLE001
        pass
    print(f"[{rec['at']}] {stage}: "
          + ", ".join(f"{k}={v}" for k, v in fields.items()), flush=True)


CHECKPOINT = Path(__file__).resolve().parents[1] / "results" / "h6_cells_partial.json"


def _checkpoint(cells: list[dict], smoke: bool) -> None:
    """Write every completed cell IN FULL after each one.

    The first full run lost 8 cells and 3h 12m to a crash on the ninth, because
    results were written only by _summarize() at the end. Worse, the heartbeat
    recorded only the delta, so the completed cells could not even be audited
    afterwards -- the per-arm scores needed to check whether a defective twin
    had been the best classical arm were simply gone.

    This writes the whole cell record, per-arm scores included, so a crash
    costs the CURRENT cell and nothing before it.
    """
    if smoke:
        return
    try:
        store.atomic_write_json(CHECKPOINT, {"cells": cells, "n": len(cells)})
    except Exception:                                          # noqa: BLE001
        pass


# --------------------------------------------------------------- the twins --
# Each twin is the primitive proven in h6_twin_preflight.py (Sprint 6), which
# established that pygam and interpret are NOT installed and are not needed.

def _relevance(X_tr, y_tr):
    """|Pearson correlation| of each column with the label, TRAIN ONLY.

    Scale-free, unlike variance. Variance ranking is what invalidated the first
    complete H6 run: ULB's Time column has variance 2.3e9 while QFE phase
    columns are whitened to unit variance, so a phase column could never be
    picked and both twins saw identical inputs in 10 of 10 seeds.
    """
    yc = y_tr - y_tr.mean()
    ys = yc.std()
    if ys == 0:
        return np.zeros(X_tr.shape[1])
    xs = X_tr.std(axis=0)
    # A constant column has no correlation and must not win by dividing by ~0.
    safe = np.where(xs > 0, xs, np.inf)
    return np.abs((X_tr - X_tr.mean(axis=0)).T @ yc) / (len(yc) * safe * ys)


def _rank_columns(X_tr, y_tr, k: int, n_raw: int | None = None):
    """Top-k columns, GUARANTEEING the twin sees the representation under test.

    A pure top-k ranking cannot honour H6. Section 3 requires the phase
    representation to be given to EVERY arm, but measured on ULB the best phase
    column ranks 14th by supervised relevance (|corr| 0.055) against 0.318 for
    the top raw column -- the phase columns are genuinely weaker predictors on
    a dataset whose V-columns are already PCA components. Rank by variance and
    they never appear; rank by correlation and they still never appear. The
    selector is not being unfair, it is simply doing its job, and the effect is
    that the twin never receives the treatment.

    So the budget is SPLIT: the best raw columns plus the best phase columns,
    each by relevance. Under QFE every twin demonstrably gets phase inputs.
    Under baseline there are no phase columns and the twin spends its whole
    budget on raw ones, which is correct -- the treatment is absent because it
    is absent, not because the selector hid it.

    n_raw: index where the phase block starts. None means no phase block.
    """
    rel = _relevance(X_tr, y_tr)
    if n_raw is None or n_raw >= X_tr.shape[1]:
        return np.argsort(-rel)[:k]

    # Half the budget to the representation, at least one column each way, so
    # the twin is order-matched with the quantum arm rather than a straw man.
    n_phase = max(1, k // 2)
    n_keep_raw = max(1, k - n_phase)
    raw = np.argsort(-rel[:n_raw])[:n_keep_raw]
    phase = n_raw + np.argsort(-rel[n_raw:])[:n_phase]
    return np.concatenate([raw, phase])


def _fit_gam(X_tr, y_tr, X_te, max_terms: int = 6, n_raw=None):
    """Trained-frequency GAM: statsmodels GLMGam with BSplines smooth terms.

    "Trained-frequency" means the spline basis is FIT from training data rather
    than fixed a priori, which is what makes this a fair periodic-structure
    baseline instead of a straw man.
    """
    import statsmodels.api as sm
    from statsmodels.gam.api import BSplines, GLMGam

    # BSplines cost grows with term count, so the twin gets the k columns most
    # correlated with the label rather than all of them. See _rank_columns for
    # why this is NOT variance.
    order = _rank_columns(X_tr, y_tr, max_terms, n_raw)
    Xs_tr, Xs_te = X_tr[:, order], X_te[:, order]
    df = [6] * Xs_tr.shape[1]
    bs = BSplines(Xs_tr, df=df, degree=[3] * Xs_tr.shape[1])
    gam = GLMGam(y_tr, exog=np.ones((len(y_tr), 1)), smoother=bs,
                 family=sm.families.Binomial()).fit()

    # Transform test data through the FITTED basis, never a new one. Building
    # a second BSplines on test data places knots by the TEST distribution, so
    # coefficients learned against the training basis get applied to a
    # different basis -- a silent scoring error, not just the
    # NotImplementedError it eventually raised on a seed whose test rows fell
    # outside the training knots.
    #
    # Clip to the training range first: a spline has no basis beyond its
    # outermost knots, so the honest reading is that this twin does not
    # extrapolate past what it saw. Dropping the offending rows instead would
    # change the test set for one arm and make the comparison unfair.
    # `exog_smooth` takes RAW values, which predict() transforms itself through
    # the fitted smoother -- it is not a basis. Passing a pre-built basis makes
    # predict transform it a second time, and passing raw test values makes it
    # transform points outside the fitted knots. Clip, then hand over raw.
    lo, hi = Xs_tr.min(axis=0), Xs_tr.max(axis=0)
    return np.asarray(gam.predict(np.ones((len(X_te), 1)),
                                  exog_smooth=np.clip(Xs_te, lo, hi)))


def _fit_ga2m(X_tr, y_tr, X_te):
    """GA2M: main effects plus PAIRWISE interactions only, no 3-way or higher.

    sklearn's interaction_cst="pairwise" is exactly the GA2M contract and ships
    in the pinned sklearn, so this needs no new dependency.
    """
    from sklearn.ensemble import HistGradientBoostingClassifier

    m = HistGradientBoostingClassifier(max_iter=200, interaction_cst="pairwise",
                                       random_state=0)
    m.fit(X_tr, y_tr)
    return m.predict_proba(X_te)[:, 1]


def _fit_joint(X_tr, y_tr, X_te, n_cols: int = 8, n_raw=None,
               coarse=(0.25, 0.5, 1.0, 2.0, 4.0, 8.0)):
    """ORDER-MATCHED JOINT twin: coarse-to-fine cosine scan + logistic.

    This is the twin the Fourier Wall paper says must not be omitted. It is
    given the SAME order of representational freedom as the phase encoding --
    cosine terms at learned frequencies -- so that if periodic structure is
    what helps, the classical bar can use it too.

    Frequencies are searched on TRAIN ONLY, by supervised correlation with the
    label, then refined around the best coarse value.
    """
    order = _rank_columns(X_tr, y_tr, n_cols, n_raw)
    feats_tr, feats_te = [], []
    yc = y_tr - y_tr.mean()

    for col in order:
        v_tr, v_te = X_tr[:, col], X_te[:, col]
        best_f, best_score = None, -np.inf
        for f in coarse:
            s = abs(float(np.dot(np.cos(f * v_tr) - np.cos(f * v_tr).mean(), yc)))
            if s > best_score:
                best_f, best_score = f, s
        # Refine around the winning coarse frequency: the "fine" half.
        for f in np.linspace(best_f * 0.6, best_f * 1.6, 7):
            s = abs(float(np.dot(np.cos(f * v_tr) - np.cos(f * v_tr).mean(), yc)))
            if s > best_score:
                best_f, best_score = float(f), s
        feats_tr += [np.cos(best_f * v_tr), np.sin(best_f * v_tr)]
        feats_te += [np.cos(best_f * v_te), np.sin(best_f * v_te)]

    D_tr = np.column_stack(feats_tr)
    D_te = np.column_stack(feats_te)
    lr = LogisticRegression(max_iter=500, class_weight="balanced")
    lr.fit(D_tr, y_tr)
    return lr.predict_proba(D_te)[:, 1]


def _fit_gbdts(X_tr, y_tr, X_te):
    """The three tuned GBDT arms, weighting-only per section 7."""
    from catboost import CatBoostClassifier
    from lightgbm import LGBMClassifier
    from xgboost import XGBClassifier

    pos = float((y_tr == 1).sum())
    spw = (len(y_tr) - pos) / pos if pos > 0 else 1.0
    out = {}

    m = XGBClassifier(max_depth=6, n_estimators=300, learning_rate=0.05,
                      subsample=0.8, colsample_bytree=0.8, n_jobs=-1,
                      eval_metric="aucpr", tree_method="hist",
                      scale_pos_weight=spw)
    m.fit(X_tr, y_tr)
    out["xgboost"] = m.predict_proba(X_te)[:, 1]

    m = LGBMClassifier(num_leaves=64, n_estimators=300, learning_rate=0.05,
                       subsample=0.8, colsample_bytree=0.8, n_jobs=-1,
                       verbose=-1, scale_pos_weight=spw)
    m.fit(X_tr, y_tr)
    out["lightgbm"] = m.predict_proba(X_te)[:, 1]

    m = CatBoostClassifier(depth=6, iterations=300, learning_rate=0.05,
                           verbose=0, thread_count=-1,
                           auto_class_weights="Balanced")
    m.fit(X_tr, y_tr)
    out["catboost"] = m.predict_proba(X_te)[:, 1]
    return out


# ------------------------------------------------------------ the quantum --

def _fit_cvqboost_proxy(X_tr, y_tr, X_te, seed: int):
    """CVQBoost via the exact classical proxy of the identical Hamiltonian.

    [SIM], zero metered seconds. The proxy solves J = HH^T + lambda*I,
    C = -2Hy on the simplex, which is the objective eqc-models ships to
    Dirac-3, so this measures the formulation rather than the device.
    """
    import qubo_proxy as qp

    # eqc-models' builder takes labels in {-1,+1}. Passing 0/1 would train
    # every weak learner against the wrong target, silently.
    y_pm1 = np.where(np.asarray(y_tr) == 1, 1.0, -1.0)

    clf = qp.build_pool(X_tr, y_pm1, schedule=SCHEDULE, weak_type="dct",
                        pair_build="seq")
    H_tr = qp.h_matrix(clf, X_tr)
    lam = qp.LAMBDA_MULT * len(y_pm1)          # frozen lambda_coef = 2 * n_train
    w = qp.solve_simplex_qp(H_tr, y_pm1, lam)
    H_te = qp.h_matrix(clf, X_te)
    return H_te.T @ w


def _cell(X_tr, y_tr, X_te, y_te, seed: int, representation: str,
          n_raw: int | None = None) -> dict:
    """One H6 cell: every arm and every twin on one representation."""
    t0 = time.time()
    scores = {}

    gbdts = _fit_gbdts(X_tr, y_tr, X_te)
    for name, s in gbdts.items():
        scores[name] = float(average_precision_score(y_te, s))

    # The classical bar is INCOMPLETE without all three twins, so any failure
    # here fails the cell rather than quietly reporting a weaker bar.
    scores["gam"] = float(average_precision_score(
        y_te, _fit_gam(X_tr, y_tr, X_te, n_raw=n_raw)))
    scores["ga2m"] = float(average_precision_score(y_te, _fit_ga2m(X_tr, y_tr, X_te)))
    scores["joint"] = float(average_precision_score(
        y_te, _fit_joint(X_tr, y_tr, X_te, n_raw=n_raw)))

    scores["cvqboost"] = float(average_precision_score(
        y_te, _fit_cvqboost_proxy(X_tr, y_tr, X_te, seed)))

    classical = {k: v for k, v in scores.items() if k != "cvqboost"}
    best_classical = max(classical, key=classical.get)

    return {
        "seed": seed,
        "representation": representation,
        "n_features": int(X_tr.shape[1]),
        "scores": scores,
        "best_classical_arm": best_classical,
        "best_classical_ap": classical[best_classical],
        "cvqboost_ap": scores["cvqboost"],
        # delta = quantum minus the BEST classical bar, which is the only
        # comparison the Fourier Wall argument permits.
        "delta": scores["cvqboost"] - classical[best_classical],
        "twins_present": ["gam", "ga2m", "joint"],
        "seconds": round(time.time() - t0, 1),
        "evidence_tag": "SIM",
    }


def run(smoke: bool = False) -> dict:
    seeds = SEEDS[:1] if smoke else SEEDS
    # Section 4: remove the 1,081 exact duplicates BEFORE splitting. load_ulb()
    # does NOT do this, and every compliant runner in this repo calls
    # drop_duplicates() immediately after it (run_classical, qubo_proxy,
    # run_hardware, mixed_pool, pilot_variance). Amendment A17 records what
    # happens when a new module skips this step: three exploratory fold
    # builders trained on 284,807 rows against every comparator's 283,726, and
    # the violation was invisible for two sprints because those arms were only
    # ever compared against each other. This module is new code, which is
    # exactly the condition that produced A17.
    n_raw = 284_807                       # asserted by the loader
    df = data.load_ulb().drop_duplicates().reset_index(drop=True)
    _progress("loaded", rows_raw=n_raw, rows=len(df),
              exact_duplicates_removed=n_raw - len(df), seeds=len(seeds))

    cells = []
    for seed in seeds:
        sp = data.stratified_split(df, seed)
        X_tr, y_tr = sp.X_train, sp.y_train
        X_te, y_te = sp.X_test, sp.y_test

        # BASELINE representation: the features as they are.
        cells.append(_cell(np.asarray(X_tr), np.asarray(y_tr),
                           np.asarray(X_te), np.asarray(y_te), seed, "baseline"))
        _progress("cell_done", seed=seed, representation="baseline",
                  delta=round(cells[-1]["delta"], 4))
        _checkpoint(cells, smoke)

        # QFE representation: the SAME features plus the phase block. The
        # encoder is fitted on TRAIN ONLY -- fitting it on the full frame would
        # leak the test distribution into the ranks.
        enc = qfe.FourierWallPhaseEncoder()
        enc.fit(X_tr)
        # transform() returns {column_name: array}, not a matrix. Assemble in a
        # FIXED column order taken from the fitted encoder, so train and test
        # blocks line up; dict iteration order would be a silent misalignment.
        P_tr, P_te = enc.transform(X_tr), enc.transform(X_te)
        order = sorted(P_tr)
        assert sorted(P_te) == order, "train/test phase blocks disagree"
        Xq_tr = np.hstack([np.asarray(X_tr, dtype=float),
                           np.column_stack([P_tr[c] for c in order])])
        Xq_te = np.hstack([np.asarray(X_te, dtype=float),
                           np.column_stack([P_te[c] for c in order])])

        cells.append(_cell(Xq_tr, np.asarray(y_tr), Xq_te, np.asarray(y_te),
                           seed, "qfe", n_raw=np.asarray(X_tr).shape[1]))
        _progress("cell_done", seed=seed, representation="qfe",
                  delta=round(cells[-1]["delta"], 4))
        _checkpoint(cells, smoke)

    return _summarize(cells, smoke)


def _summarize(cells: list[dict], smoke: bool) -> dict:
    base = [c["delta"] for c in cells if c["representation"] == "baseline"]
    qfe_d = [c["delta"] for c in cells if c["representation"] == "qfe"]

    shift = float(np.mean(qfe_d) - np.mean(base))
    # Paired, because both representations run on the SAME seed and split.
    paired = np.asarray(qfe_d) - np.asarray(base)
    noise = float(np.std(paired, ddof=1)) if len(paired) > 1 else float("nan")

    out = {
        "hypothesis": "H6 representation effect, EXPLORATORY",
        "dataset": "ulb",
        "smoke": smoke,
        "scoring_rule": ("prereg section 3: every cell's classical bar carries "
                         "trained-frequency GAM, GA2M and an order-matched "
                         "JOINT twin alongside the GBDTs"),
        "mean_delta_baseline": float(np.mean(base)),
        "mean_delta_qfe": float(np.mean(qfe_d)),
        # THE reported quantity. A delta under one representation says nothing
        # on its own; the hypothesis is about the shift between them.
        "representation_shift": shift,
        "paired_shift_sd": noise,
        "n_seeds": len(base),
        "premise_falsified": bool(abs(shift) < noise) if noise == noise else None,
        "premise_falsifier": ("the premise -- that a phase representation could "
                              "shift the delta -- is disproved when |shift| is "
                              "below the paired seed-to-seed SD of the shift"),
        "cells": cells,
        "evidence_tag": "SIM",
    }
    store.atomic_write_json(SMOKE_OUT if smoke else OUT, out)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    print(f"H6 representation effect{' (SMOKE)' if args.smoke else ''}")
    out = run(smoke=args.smoke)
    print(f"\n  baseline mean delta: {out['mean_delta_baseline']:+.4f}")
    print(f"  QFE      mean delta: {out['mean_delta_qfe']:+.4f}")
    print(f"  SHIFT:               {out['representation_shift']:+.4f} "
          f"(paired SD {out['paired_shift_sd']:.4f})")
    if out["premise_falsified"]:
        print("  => shift is within seed noise: the representation does NOT "
              "move the delta. That is the answer, not a failure.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
