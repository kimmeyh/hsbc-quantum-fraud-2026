"""Mechanism controls for the flat CVQBoost optimum (Sprint 5, external review).

An external review argued our attribution is probably wrong: we credit the
simplex constraint over correlated learners, but the more likely cause is the
UNWEIGHTED squared loss at 0.17% prevalence, where every learner that predicts
"not fraud" scores almost identically and the objective cannot separate them.

Three controls settle it, all classical, zero metered seconds:
  1. UNIFORM weights (w = 1/n). If this matches the solved optimum, the
     optimization step contributed nothing and we must say so plainly.
  2. CLASS-WEIGHTED objective: rebuild J and C with fraud rows weighted by
     inverse prevalence, then re-solve exactly. If the optimum stops being
     uniform, prevalence was the cause and the Phase 2 direction changes.
  3. UNCONSTRAINED stack: ridge and logistic on the same learner outputs with
     free signs, isolating the cost of the non-negative simplex form that
     Dirac-3 imposes as a hardware requirement rather than a modelling choice.

Usage: python experiments/src/mechanism_controls.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qubo_proxy as qp
import store

OUT = Path(__file__).resolve().parents[1] / "results" / "mechanism_controls.json"
SEEDS = (42, 43, 44, 45, 46, 47, 48, 49, 50, 51)


def solve_weighted(H, y, lam, sw):
    """Same simplex QP, but with per-row weights: J = H diag(sw) H^T + lam I,
    C = -2 H (sw * y). Reduces to the frozen objective when sw is all ones."""
    Hw = H * sw
    J = (Hw @ H.T).astype(np.float64) + lam * np.eye(H.shape[0])
    C = (-2.0 * (Hw @ y)).astype(np.float64)
    L = float(np.linalg.eigvalsh(J)[-1]) * 2.0 + 1e-9
    w = np.full(H.shape[0], 1.0 / H.shape[0])
    z, t = w.copy(), 1.0
    obj = lambda v: float(v @ J @ v + C @ v)
    prev = obj(w)
    for _ in range(5000):
        g = 2.0 * (J @ z) + C
        w_new = qp._project_simplex(z - g / L)
        t_new = (1.0 + np.sqrt(1.0 + 4.0 * t * t)) / 2.0
        z = w_new + ((t - 1.0) / t_new) * (w_new - w)
        w, t = w_new, t_new
        cur = obj(w)
        if abs(prev - cur) <= 1e-10 * (1.0 + abs(prev)):
            break
        prev = cur
    return w


def main() -> int:
    from sklearn.linear_model import LogisticRegression, RidgeClassifier
    from sklearn.metrics import average_precision_score

    rows = {"uniform": [], "frozen": [], "class_weighted": [],
            "ridge_free": [], "logistic_free": []}
    weight_stats = []

    for seed in SEEDS:
        pool = qp.POOLS_DIR / f"h_{seed}_free_dct_full.npz"
        if not pool.exists():
            continue
        z = np.load(pool)
        H_tr, H_te = z["H_tr"], z["H_te"]
        y_tr01, y_te = z["y_tr01"], z["y_te"]
        y_pm1 = np.where(y_tr01 == 1, 1, -1).astype(np.float64)
        n, lam = H_tr.shape[0], qp.LAMBDA_MULT * len(y_pm1)

        def ap(w):
            return float(average_precision_score(
                y_te, np.clip((w @ H_te + 1.0) / 2.0, 0.0, 1.0)))

        # 1. uniform
        w_u = np.full(n, 1.0 / n)
        rows["uniform"].append(ap(w_u))

        # frozen solve, for reference
        w_f = solve_weighted(H_tr, y_pm1, lam, np.ones(len(y_pm1)))
        rows["frozen"].append(ap(w_f))
        weight_stats.append({
            "seed": seed, "max_w": float(w_f.max()), "uniform_w": 1.0 / n,
            "max_over_uniform": float(w_f.max() * n),
            "l1_distance_from_uniform": float(np.abs(w_f - w_u).sum()),
            "cosine_to_uniform": float(w_f @ w_u / (np.linalg.norm(w_f) * np.linalg.norm(w_u))),
        })

        # 2. class-weighted objective (inverse prevalence on the positive class)
        prev = float((y_tr01 == 1).mean())
        sw = np.where(y_tr01 == 1, (1 - prev) / prev, 1.0).astype(np.float64)
        w_cw = solve_weighted(H_tr, y_pm1, lam, sw)
        rows["class_weighted"].append(ap(w_cw))
        weight_stats[-1]["class_weighted_max_over_uniform"] = float(w_cw.max() * n)
        weight_stats[-1]["class_weighted_l1_from_uniform"] = float(np.abs(w_cw - w_u).sum())

        # 3. unconstrained stacks on the same learner outputs
        Xtr, Xte = H_tr.T, H_te.T
        r = RidgeClassifier(alpha=1.0, class_weight="balanced").fit(Xtr, y_tr01)
        rows["ridge_free"].append(float(average_precision_score(
            y_te, r.decision_function(Xte))))
        lg = LogisticRegression(max_iter=1000, class_weight="balanced").fit(Xtr, y_tr01)
        rows["logistic_free"].append(float(average_precision_score(
            y_te, lg.predict_proba(Xte)[:, 1])))

    summary = {k: {"mean": float(np.mean(v)), "sd": float(np.std(v, ddof=1)), "n": len(v)}
               for k, v in rows.items() if v}
    out = {"question": "Is the flat optimum caused by the simplex constraint or by "
                       "unweighted squared loss at 0.17% prevalence?",
           "controls": summary, "per_seed": rows, "weight_stats": weight_stats}
    store.atomic_write_json(OUT, out)

    for k, v in summary.items():
        print(f"{k:16s} mean AP {v['mean']:.4f} (SD {v['sd']:.4f}, n={v['n']})")
    if weight_stats:
        w = weight_stats[0]
        print(f"\nfrozen solve, seed {w['seed']}: max weight is "
              f"{w['max_over_uniform']:.4f}x uniform, L1 distance from uniform "
              f"{w['l1_distance_from_uniform']:.4f}")
        print(f"class-weighted solve: max weight {w['class_weighted_max_over_uniform']:.4f}x "
              f"uniform, L1 distance {w['class_weighted_l1_from_uniform']:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
