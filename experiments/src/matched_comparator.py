"""Frozen single-family pool rebuilt at matched k (PR #41 review finding 5).

The +0.0198 that the proposal, appendix and QCi letter all report is a PAIRED
per-seed difference between the F33 tuned four-family pool and the frozen
single-family pool AT THE SAME k=6, on the same splits. That comparator was
computed inline during Sprint 7 and its output committed as
`results/tuned_vs_frozen_k6.json`, but the code that produced it was never
committed -- so the appendix's claim that "every figure regenerates from the
repository" was false for the one figure the letter leads with.

This module is that generator. It reproduces the file exactly, so a reviewer, or
QCi, can ask how the comparator arm was built and get an answer: which feature
selection seed, which weak_params, which solver path.

Design note. The comparison is paired and matched by construction: for each seed
it takes the SAME split, the SAME top-k feature selection, and the SAME solver,
varying ONLY the pool composition (one dct family against four tuned families).
That is what makes the difference attributable to the pool rather than to
feature count -- and it matters here, because the frozen pool is measurably
worse at k=6 than at k=13 (0.7629 against 0.7681, amendment A15), so an
unmatched comparison would have inflated the result.

Usage: python experiments/src/matched_comparator.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comparators as cmp
import data
import mechanism_controls as mcx
import qubo_proxy as qp
import store
import tuned_pool as tp

OUT = Path(__file__).resolve().parents[1] / "results" / "tuned_vs_frozen_k6.json"
K_FEATURES = 6
SCHEDULE = 2
FROZEN_FAMILY = "dct"          # the frozen arm's single family
FROZEN_PARAMS: dict = {}       # library defaults, as the frozen arm uses


def frozen_ap_at_k(seed: int, k: int = K_FEATURES) -> float:
    """The frozen single-family arm's test AUPRC, built exactly as the tuned arm
    is except for the pool: same split, same feature selection, same solver."""
    from sklearn.metrics import average_precision_score as AP

    split, X_tr, X_va, X_te, y_pm1 = tp._fold(seed, k=k)
    clf = qp.build_pool(X_tr, y_pm1, schedule=SCHEDULE, weak_type=FROZEN_FAMILY,
                        pair_build="seq", weak_params=FROZEN_PARAMS)
    H_tr, H_te = qp.h_matrix(clf, X_tr), qp.h_matrix(clf, X_te)
    w = mcx.solve_weighted(H_tr, y_pm1, qp.LAMBDA_MULT * len(y_pm1),
                           np.ones(len(y_pm1)))
    return float(AP(split.y_test.to_numpy(),
                    np.clip((w @ H_te + 1.0) / 2.0, 0.0, 1.0)))


def main() -> int:
    tuned_path = Path(__file__).resolve().parents[1] / "results" / "tuned_pool.json"
    if not tuned_path.exists():
        raise SystemExit("run tuned_pool.py first: this pairs against its per-seed results")
    tuned = {r["seed"]: r["ap_solved_test"]
             for r in json.loads(tuned_path.read_text())["per_seed"]}

    rows = []
    for seed in tp.SEEDS:
        base = frozen_ap_at_k(seed)
        rows.append({"seed": seed, "frozen_k6": base, "tuned_k6": tuned[seed],
                     "delta": tuned[seed] - base})
        print(f"  seed {seed}: frozen {base:.4f}  tuned {tuned[seed]:.4f}  "
              f"delta {rows[-1]['delta']:+.4f}")

    d = np.array([r["delta"] for r in rows])
    frozen_mean = float(np.mean([r["frozen_k6"] for r in rows]))

    # Route the headline through the guard, so the file cannot record a
    # difference whose arms are mismatched (findings 2 and 3).
    tuned_arm = cmp.ArmSpec(label="tuned four-family", k=K_FEATURES,
                            protocol="stratified", split="test")
    frozen_arm = cmp.ArmSpec(label="frozen single-family", k=K_FEATURES,
                             protocol="stratified", split="test")
    headline = cmp.reported_difference(
        tuned_arm, float(np.mean([r["tuned_k6"] for r in rows])),
        frozen_arm, frozen_mean, mde=tp.MDE)

    store.atomic_write_json(OUT, {
        "note": "paired frozen-vs-tuned at matched k=6",
        "generator": "experiments/src/matched_comparator.py",
        "design": ("per seed: same split, same top-k feature selection, same "
                   "solver; ONLY the pool composition varies"),
        "frozen_arm": {"family": FROZEN_FAMILY, "params": FROZEN_PARAMS,
                       "k": K_FEATURES, "schedule": SCHEDULE,
                       "mean_ap": frozen_mean},
        "per_seed": rows,
        "mean_delta": float(d.mean()), "sd": float(d.std(ddof=1)),
        "n_positive": int((d > 0).sum()),
        "exceeds_mde": bool(abs(d.mean()) > tp.MDE),
        "headline": headline,
    })

    print(f"\nfrozen k=6 mean {frozen_mean:.4f} (k=13 figure is 0.7681, so k=6 is "
          f"{frozen_mean - 0.7681:+.4f} -- see A15)")
    print(f"paired delta {d.mean():+.4f} (SD {d.std(ddof=1):.4f}), "
          f"{int((d > 0).sum())}/{len(rows)} positive")
    print(headline["reporting_guidance"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
