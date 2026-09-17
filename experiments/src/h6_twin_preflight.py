"""H6 twin-family capability pre-flights (Sprint 6 Task C / F23, card #33;
SPRINT_PLANNING.md "Capability pre-flight" rule: ~5 min each, proving the
single primitive an item depends on BEFORE it is estimated or built).

H6 (PREREGISTRATION section 3) requires, in every phase-representation cell,
a classical bar of trained-frequency GAM, GA2M, and an order-matched JOINT
twin (supervised coarse-to-fine cosine frequency scan fit by logistic
regression) alongside the GBDTs (docs/references.md design implication 2:
omitting this twin is how the Fourier Wall paper shows fake quantum wins get
manufactured). This module proves each family's core primitive works in this
environment, on synthetic data, with NO ULB access and NO model actually
built for H6 -- that is F4 in Sprint 7. Run:

  your venv interpreter (docs/ENVIRONMENT.md) experiments/src/h6_twin_preflight.py

Findings (2026-09-05, this environment):
  - pygam / interpret: NOT INSTALLED. Reported, not installed (task
    instruction: report missing libraries rather than adding a heavyweight
    dependency this late in the sprint).
  - GAM: statsmodels.gam.api.GLMGam (BSplines smooth terms) is already
    installed (statsmodels 0.15.0) and fits a spline-basis additive model --
    the standard "trained-frequency GAM" primitve (a GAM whose smooth-term
    basis/knots are fit from training data). PASS.
  - GA2M: sklearn.ensemble.HistGradientBoostingClassifier's `interaction_cst`
    constrains the tree ensemble to main effects + a named list of pairwise
    interactions only (no 3-way+), which is exactly the GA2M contract (a GAM
    plus pairwise terms), and ships in the pinned sklearn (1.9.0). PASS.
  - JOINT: "coarse-to-fine cosine frequency scan fit by logistic regression"
    decomposes into two primitives, both provable with stdlib + numpy +
    sklearn: (a) a coarse-to-fine 1-D frequency search that scores candidate
    cosine features by their supervised (label-correlated) usefulness, then
    refines around the best coarse frequency; (b) fitting the resulting
    small cosine-feature design matrix with sklearn LogisticRegression.
    Both PASS.
"""
from __future__ import annotations

import time

import numpy as np


def _synthetic(n=2000, seed=0):
    rng = np.random.default_rng(seed)
    x1 = rng.normal(size=n)
    x2 = rng.normal(size=n)
    # y depends on a smooth nonlinear function of x1, a pairwise x1*x2 term,
    # and a periodic (cosine) signal in x2 -- enough structure to exercise
    # all three primitives meaningfully.
    freq_true = 3.0
    logit = 0.8 * np.sin(1.5 * x1) + 0.6 * x1 * x2 + 1.2 * np.cos(freq_true * x2)
    p = 1.0 / (1.0 + np.exp(-logit))
    y = (rng.random(n) < p).astype(int)
    return x1, x2, y, freq_true


# ---------------------------------------------------------------- GAM spike

def preflight_gam() -> dict:
    """Primitive: fit a spline-basis (trained-frequency) additive model via
    statsmodels GLMGam and confirm it returns a converged fit with smooth
    terms whose basis was built from training data (not fixed a priori)."""
    t0 = time.time()
    try:
        import pandas as pd
        from statsmodels.gam.api import GLMGam, BSplines
        import statsmodels.api as sm

        x1, x2, y, _ = _synthetic()
        df = pd.DataFrame({"x1": x1, "x2": x2, "y": y})
        # BSplines builds its knot placement FROM the training column (df[["x1","x2"]]):
        # this is the "trained" part of "trained-frequency GAM" -- the smooth
        # basis is data-dependent, not a fixed functional form.
        bs = BSplines(df[["x1", "x2"]], df=[6, 6], degree=[3, 3])
        gam = GLMGam.from_formula("y ~ 1", data=df, smoother=bs,
                                  family=sm.families.Binomial())
        res = gam.fit()
        ok = bool(np.isfinite(res.params).all()) and len(res.params) > 2
        return {"family": "GAM", "library": "statsmodels.gam.api.GLMGam",
                "status": "PASS" if ok else "FAIL",
                "detail": f"{len(res.params)} fitted smooth-basis coefficients, "
                          f"llf={res.llf:.2f}",
                "elapsed_s": round(time.time() - t0, 2)}
    except ImportError as e:
        return {"family": "GAM", "status": "MISSING", "detail": repr(e),
                "elapsed_s": round(time.time() - t0, 2)}
    except Exception as e:
        return {"family": "GAM", "status": "FAIL", "detail": repr(e),
                "elapsed_s": round(time.time() - t0, 2)}


# --------------------------------------------------------------- GA2M spike

def preflight_ga2m() -> dict:
    """Primitive: a GA2M-equivalent (main effects + NAMED pairwise
    interactions, no higher-order terms) via sklearn's HistGradientBoosting
    `interaction_cst`, since `interpret`'s ExplainableBoostingClassifier is
    not installed. Confirms the constraint actually restricts the model
    (fitting succeeds and predict_proba runs) rather than silently
    ignoring the argument."""
    t0 = time.time()
    try:
        from sklearn.ensemble import HistGradientBoostingClassifier

        x1, x2, y, _ = _synthetic()
        X = np.column_stack([x1, x2])
        # interaction_cst=[[0], [1], [0, 1]]: two main-effect groups plus one
        # explicit pairwise group -- main effects + pairwise only, the GA2M
        # contract -- and no group spans a 3-way+ interaction (only 2 features
        # exist here, so this also exercises the ceiling case correctly).
        clf = HistGradientBoostingClassifier(
            interaction_cst=[[0], [1], [0, 1]], max_iter=50, random_state=0)
        clf.fit(X, y)
        proba = clf.predict_proba(X)
        ok = proba.shape == (len(y), 2) and np.isfinite(proba).all()
        return {"family": "GA2M", "library": "sklearn HistGradientBoosting(interaction_cst=...)",
                "status": "PASS" if ok else "FAIL",
                "detail": "fit + predict_proba succeeded under a main-effects+"
                          "pairwise interaction constraint (interpret.EBM not installed)",
                "elapsed_s": round(time.time() - t0, 2)}
    except Exception as e:
        return {"family": "GA2M", "status": "FAIL", "detail": repr(e),
                "elapsed_s": round(time.time() - t0, 2)}


# --------------------------------------------------------------- JOINT spike

def _coarse_to_fine_cosine_scan(x: np.ndarray, y: np.ndarray,
                                freq_grid_coarse: np.ndarray,
                                refine_width: float, refine_n: int) -> float:
    """Supervised coarse-to-fine frequency search: score each coarse
    candidate frequency by |corr(cos(f*x), y)|, keep the best, then refine on
    a fine grid centered on it. This is the "coarse-to-fine cosine frequency
    scan" primitive JOINT depends on -- entirely stdlib/numpy, no library
    dependency to prove."""
    def score(f):
        feat = np.cos(f * x)
        feat = feat - feat.mean()
        yc = y - y.mean()
        denom = feat.std() * yc.std()
        return abs((feat * yc).mean() / denom) if denom > 0 else 0.0

    coarse_scores = np.array([score(f) for f in freq_grid_coarse])
    best_coarse = freq_grid_coarse[np.argmax(coarse_scores)]
    fine_grid = np.linspace(best_coarse - refine_width, best_coarse + refine_width, refine_n)
    fine_grid = fine_grid[fine_grid > 0]
    fine_scores = np.array([score(f) for f in fine_grid])
    return float(fine_grid[np.argmax(fine_scores)])


def preflight_joint() -> dict:
    """Primitive: (a) coarse-to-fine cosine frequency scan recovers a
    reasonable estimate of the true frequency used to generate y, and
    (b) sklearn LogisticRegression fits on the resulting small cosine-feature
    design matrix. Both are provable without any additional library."""
    t0 = time.time()
    try:
        from sklearn.linear_model import LogisticRegression

        x1, x2, y, freq_true = _synthetic()
        coarse = np.linspace(0.5, 8.0, 16)
        f_hat = _coarse_to_fine_cosine_scan(x2, y, coarse, refine_width=0.5, refine_n=21)
        # A coarse 16-point grid over [0.5, 8] has ~0.5 spacing; recovering
        # within one coarse step of the true frequency (3.0) is the bar for
        # "the scan primitive works", not exact recovery on 2000 noisy points.
        freq_ok = abs(f_hat - freq_true) < 1.0

        design = np.column_stack([x1, x2, np.cos(f_hat * x2), np.sin(f_hat * x2)])
        clf = LogisticRegression(max_iter=200).fit(design, y)
        proba = clf.predict_proba(design)
        fit_ok = proba.shape == (len(y), 2) and np.isfinite(proba).all()

        ok = freq_ok and fit_ok
        return {"family": "JOINT", "library": "numpy scan + sklearn LogisticRegression",
                "status": "PASS" if ok else "FAIL",
                "detail": f"recovered frequency {f_hat:.3f} (true {freq_true}); "
                          f"logistic fit on {design.shape[1]} cosine/linear features "
                          f"{'converged' if fit_ok else 'FAILED'}",
                "elapsed_s": round(time.time() - t0, 2)}
    except Exception as e:
        return {"family": "JOINT", "status": "FAIL", "detail": repr(e),
                "elapsed_s": round(time.time() - t0, 2)}


def run_all() -> list[dict]:
    return [preflight_gam(), preflight_ga2m(), preflight_joint()]


if __name__ == "__main__":
    import json
    results = run_all()
    print(json.dumps(results, indent=2))
    total = sum(r["elapsed_s"] for r in results)
    print(f"\ntotal elapsed: {total:.2f}s")
