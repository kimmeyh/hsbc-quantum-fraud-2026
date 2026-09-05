"""Mixed-family weak-learner pool (F31, amendment A11, LABELED EXPLORATORY).

Sprint 5 measured why the frozen arm's optimizer contributes nothing: the pool
is degenerate. Off-diagonal Gram entries average 170,234.4 against a diagonal of
170,235, so any two of the 91 depth-limited trees agree on 99.999% of training
rows, and the solved optimum sits within 1.6e-07 of uniform. With interchangeable
learners uniform IS the optimum, and no solver -- quantum or classical -- can do
useful work. The frozen configuration therefore cannot answer the question the
submission asks.

Loke et al. (ICAART 2026) reach mean AUC-PR above 0.8 on the same Dirac-3
hardware and the same benchmark family with a HETEROGENEOUS pool (KNN, LDA,
logistic regression, XGBoost) against our 0.767. This module builds that kind of
pool and asks whether the optimum leaves uniform.

Implementation note: eqc-models' QBoostClassifier takes ONE `weak_cls_type` per
build, so heterogeneity is achieved by building a pool per family on the SAME
train fold and concatenating along the learner axis. That is valid because rows
of H are learners and columns are training rows, so any stack sharing a fold
forms a consistent J = H diag(sw) H' with the same column space.

SCOPE (A11): exploratory. Not a gate. H1b and every frozen gate keep their
committed scoring and are NOT rescored. Differences are tested against the A5
minimum detectable effect of 0.0268, never reported as a win on sign alone.

Usage: python experiments/src/mixed_pool.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import data
import mechanism_controls as mc
import qubo_proxy as qp
import store

OUT = Path(__file__).resolve().parents[1] / "results" / "mixed_pool.json"
SEEDS = (42, 43, 44, 45, 46, 47, 48, 49, 50, 51)

# The Loke et al. families, intersected with what eqc-models supports.
# xgb is excluded from the default set: it builds one gradient-boosted model per
# feature subset and dominates build time without adding a distinct decision
# geometry that lda/lg/knn do not already supply. Recorded so the choice is
# visible rather than silent.
FAMILIES = ("dct", "lda", "lg", "knn")

K_FEATURES = 13
MDE = 0.0268  # A5 minimum detectable effect


def build_mixed(X_tr, X_va, X_te, y_pm1, schedule: int,
                families=FAMILIES) -> dict:
    """Build one pool per family on a shared fold; concatenate along learners."""
    H_tr, H_va, H_te, provenance = [], [], [], []
    for fam in families:
        t0 = time.time()
        clf = qp.build_pool(X_tr, y_pm1, schedule=schedule, weak_type=fam,
                            pair_build="seq")
        h_tr = qp.h_matrix(clf, X_tr)
        H_tr.append(h_tr)
        H_va.append(qp.h_matrix(clf, X_va))
        H_te.append(qp.h_matrix(clf, X_te))
        provenance.append({"family": fam, "n_learners": int(h_tr.shape[0]),
                           "build_seconds": round(time.time() - t0, 2)})
    return {"H_tr": np.vstack(H_tr), "H_va": np.vstack(H_va),
            "H_te": np.vstack(H_te), "provenance": provenance}


def diversity(H: np.ndarray, max_pairs: int = 4000, seed: int = 0) -> dict:
    """Pool diversity measured BEFORE any optimization.

    The Gram ratio is the headline: off-diagonal / diagonal near 1.0 means the
    learners are interchangeable and the optimizer has nothing to choose
    between. Pairwise disagreement is the same fact in per-row terms.
    """
    n, m = H.shape
    G = H @ H.T
    diag = float(np.mean(np.diag(G)))
    off = float((G.sum() - np.trace(G)) / (n * n - n)) if n > 1 else float("nan")

    rng = np.random.default_rng(seed)
    pairs = min(max_pairs, n * (n - 1) // 2)
    dis = []
    for _ in range(pairs):
        i, j = rng.integers(0, n, 2)
        if i != j:
            dis.append(float((H[i] != H[j]).mean()))
    return {
        "n_learners": int(n),
        "gram_diagonal": diag,
        "gram_offdiagonal_mean": off,
        "gram_ratio": off / diag if diag else float("nan"),
        "pairwise_disagreement_mean": float(np.mean(dis)) if dis else float("nan"),
        "pairwise_disagreement_max": float(np.max(dis)) if dis else float("nan"),
        "distinct_learner_rows": int(len(np.unique(H, axis=0))),
    }


def run_seed(seed: int, schedule: int = 2) -> dict:
    from sklearn.metrics import average_precision_score as AP

    df = data.load_ulb()
    split = data.stratified_split(df, seed)
    cols = data.top_k_features(split.X_train, split.y_train, K_FEATURES, seed=seed)
    X_tr = split.X_train[cols].to_numpy(np.float32)
    X_va = split.X_val[cols].to_numpy(np.float32)
    X_te = split.X_test[cols].to_numpy(np.float32)
    y_pm1 = np.where(split.y_train.to_numpy() == 1, 1, -1).astype(np.float64)
    y_va, y_te = split.y_val.to_numpy(), split.y_test.to_numpy()

    pool = build_mixed(X_tr, X_va, X_te, y_pm1, schedule)
    H_tr, H_va, H_te = pool["H_tr"], pool["H_va"], pool["H_te"]
    n = H_tr.shape[0]

    lam = qp.LAMBDA_MULT * len(y_pm1)
    w = mc.solve_weighted(H_tr, y_pm1, lam, np.ones(len(y_pm1)))
    w_u = np.full(n, 1.0 / n)

    def score(weights, H):
        return np.clip((weights @ H + 1.0) / 2.0, 0.0, 1.0)

    ap_solved_te, ap_uniform_te = float(AP(y_te, score(w, H_te))), float(AP(y_te, score(w_u, H_te)))
    return {
        "seed": seed,
        "schedule": schedule,
        "families": list(FAMILIES),
        "provenance": pool["provenance"],
        "diversity": diversity(H_tr, seed=seed),
        "l1_from_uniform": float(np.abs(w - w_u).sum()),
        "max_weight_over_uniform": float(w.max() * n),
        "cosine_to_uniform": float(w @ w_u / (np.linalg.norm(w) * np.linalg.norm(w_u))),
        "ap_solved_val": float(AP(y_va, score(w, H_va))),
        "ap_uniform_val": float(AP(y_va, score(w_u, H_va))),
        "ap_solved_test": ap_solved_te,
        "ap_uniform_test": ap_uniform_te,
        "ap_difference": ap_solved_te - ap_uniform_te,
        "distinct_scores_solved": int(len(np.unique(w @ H_te))),
        "distinct_scores_uniform": int(len(np.unique(w_u @ H_te))),
    }


def main() -> int:
    rows = []
    for seed in SEEDS:
        t0 = time.time()
        r = run_seed(seed)
        r["wall_seconds"] = round(time.time() - t0, 1)
        rows.append(r)
        print(f"seed {seed}: {r['diversity']['n_learners']:3d} learners  "
              f"AP solved {r['ap_solved_test']:.4f} uniform {r['ap_uniform_test']:.4f} "
              f"diff {r['ap_difference']:+.4f}  L1 {r['l1_from_uniform']:.3e}  "
              f"({r['wall_seconds']}s)")

    d = np.array([r["ap_difference"] for r in rows])
    l1 = np.array([r["l1_from_uniform"] for r in rows])
    summary = {
        "n_seeds": len(rows),
        "ap_difference_mean": float(d.mean()),
        "ap_difference_sd": float(d.std(ddof=1)),
        "ap_difference_min": float(d.min()),
        "ap_difference_max": float(d.max()),
        "seeds_positive": int((d > 0).sum()),
        "mde": MDE,
        "exceeds_mde": bool(abs(d.mean()) > MDE),
        "l1_from_uniform_mean": float(l1.mean()),
        "l1_from_uniform_min": float(l1.min()),
        "l1_from_uniform_max": float(l1.max()),
        "ap_solved_mean": float(np.mean([r["ap_solved_test"] for r in rows])),
        "ap_uniform_mean": float(np.mean([r["ap_uniform_test"] for r in rows])),
        "gram_ratio_mean": float(np.mean([r["diversity"]["gram_ratio"] for r in rows])),
    }
    out = {
        "amendment": "A11",
        "status": "LABELED EXPLORATORY -- not a preregistered gate; frozen gates unchanged",
        "question": ("Does the CVQBoost optimizer do useful work on a pool that "
                     "is NOT degenerate?"),
        "comparator": ("Frozen dct-only pool: gram ratio 0.999994, L1 from uniform "
                       "8.0e-08, AP difference +0.0022 (tie-breaking, not optimization)"),
        "summary": summary,
        "per_seed": rows,
    }
    store.atomic_write_json(OUT, out)

    print(f"\nmixed pool over {summary['n_seeds']} seeds")
    print(f"  gram ratio        {summary['gram_ratio_mean']:.6f}  (frozen: 0.999994)")
    print(f"  L1 from uniform   {summary['l1_from_uniform_mean']:.3e}  (frozen: 8.0e-08)")
    print(f"  AP solved         {summary['ap_solved_mean']:.4f}")
    print(f"  AP uniform        {summary['ap_uniform_mean']:.4f}")
    print(f"  difference        {summary['ap_difference_mean']:+.4f} "
          f"(SD {summary['ap_difference_sd']:.4f}, {summary['seeds_positive']}/{len(rows)} positive)")
    print(f"  vs MDE {MDE}      {'EXCEEDS' if summary['exceeds_mde'] else 'BELOW -- report as directional only'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
