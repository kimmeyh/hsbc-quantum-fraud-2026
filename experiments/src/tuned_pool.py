"""Tuned mixed pool (F33, amendment A13, LABELED EXPLORATORY).

F31 established that a heterogeneous pool makes the CVQBoost optimizer do real
work: the optimum leaves uniform (L1 0.127 against 8.0e-08) and the gain
survives both tie-breaking controls. It bought no ACCURACY, though. Absolute
AUPRC was 0.7565, below the frozen single-family pool's 0.7681 and well below
the >0.8 Loke et al. (ICAART 2026) report on the same hardware and the same
benchmark family.

So the open question is what the remaining gap is made of. Two candidates:

  (a) learner QUALITY -- our families run at library defaults while theirs are
      tuned, so the pool is diverse but individually weak; or
  (b) something structural about the formulation that tuning cannot reach.

This module tests (a). The specific intervention is fit-time imbalance handling,
which no prior control has varied: Sprint 5's class-weighted control reweighted
the ENSEMBLE OBJECTIVE and left the learners themselves untouched, which is
precisely why it could not move a degenerate pool. Weighting a learner during
its own fit is a different operation, and at 0.17% prevalence it is the one that
decides whether a weak learner predicts anything but the negative class.

Two stages, so the expensive stage runs once:
  1. sweep on seed 42, selecting on VALIDATION AP (repo-wide selection rule);
  2. the selected configuration over ten seeds, reporting exactly what
     mixed_pool.py reports so the two are directly comparable.

SCOPE (A13): exploratory. Not a gate. H1b and every frozen gate keep their
committed scoring. Differences are tested against the A5 minimum detectable
effect of 0.0268 and never reported as a win on sign alone. The Loke comparison
is a DESIGN comparison; we do not claim to reproduce their number.

Usage:
    python experiments/src/tuned_pool.py --sweep     # stage 1, seed 42
    python experiments/src/tuned_pool.py             # stage 2, 10 seeds
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
import mixed_pool as mp
import qubo_proxy as qp
import comparators as cmp
import store

SWEEP_OUT = Path(__file__).resolve().parents[1] / "results" / "tuned_pool_sweep.json"
OUT = Path(__file__).resolve().parents[1] / "results" / "tuned_pool.json"
SEEDS = (42, 43, 44, 45, 46, 47, 48, 49, 50, 51)
TUNING_SEED = 42
MDE = 0.0268
FREE_TIER_MAX_VARS = 100          # amendment A12, established empirically

# Comparators. The k of each is part of its identity: differencing across
# different k reports the feature count as if it were the treatment effect.
FROZEN_POOL_AP = 0.7681           # single-family dct, k=13, 91 vars (Sprint 4/5)
MIXED_POOL_AP = 0.7565            # F31 four-family untuned, k=13, 312 vars
FROZEN_K6_AP = 0.7629             # single-family dct rebuilt at k=6, 10 seeds
                                  # (tuned_vs_frozen_k6.json). THE MATCHED ONE.
LOKE_REPORTED_AP = 0.80           # ICAART 2026, heterogeneous pool, same hardware

# Candidate configurations. Each is (label, {family: weak_params}).
# "balanced" is the intervention under test: class_weight at FIT time, so a
# learner is penalised for ignoring the 0.17% positive class while it is being
# built, rather than being reweighted afterwards in the ensemble objective.
CANDIDATES = {
    "defaults": {
        "dct": {"max_depth": 2, "random_state": 0},
        "lda": {},
        "lg": {"max_iter": 300},
        "knn": {"n_neighbors": 5},
    },
    "balanced": {
        "dct": {"max_depth": 2, "class_weight": "balanced", "random_state": 0},
        "lda": {},
        "lg": {"max_iter": 300, "class_weight": "balanced"},
        "knn": {"n_neighbors": 5},
    },
    "balanced_deeper": {
        "dct": {"max_depth": 4, "class_weight": "balanced", "random_state": 0},
        "lda": {},
        "lg": {"max_iter": 300, "class_weight": "balanced", "C": 0.1},
        "knn": {"n_neighbors": 15},
    },
    "balanced_shallow_knn": {
        "dct": {"max_depth": 3, "class_weight": "balanced", "random_state": 0},
        "lda": {},
        "lg": {"max_iter": 300, "class_weight": "balanced"},
        "knn": {"n_neighbors": 3, "weights": "distance"},
    },
}


def build_tuned(X_tr, X_va, X_te, y_pm1, params: dict, k_schedule: int = 2) -> dict:
    """One pool per family at ITS OWN hyperparameters, concatenated on the
    learner axis. Valid because rows of H are learners and columns are training
    rows, so any stack sharing a train fold forms a consistent Hamiltonian."""
    H_tr, H_va, H_te, prov = [], [], [], []
    for fam, wp in params.items():
        t0 = time.time()
        clf = qp.build_pool(X_tr, y_pm1, schedule=k_schedule, weak_type=fam,
                            pair_build="seq", weak_params=wp)
        h = qp.h_matrix(clf, X_tr)
        H_tr.append(h)
        H_va.append(qp.h_matrix(clf, X_va))
        H_te.append(qp.h_matrix(clf, X_te))
        prov.append({"family": fam, "params": dict(wp),
                     "n_learners": int(h.shape[0]),
                     "build_seconds": round(time.time() - t0, 2)})
    return {"H_tr": np.vstack(H_tr), "H_va": np.vstack(H_va),
            "H_te": np.vstack(H_te), "provenance": prov}


def _fold(seed: int, k: int):
    # DEDUPLICATE BEFORE SPLITTING. The frozen protocol removes 1,081 exact
    # duplicates before any split, and every other arm's loader does so
    # (qubo_proxy, run_classical, run_hardware, pilot_variance). This path did
    # not, so it trained on 284,807 rows against every comparator's 283,726 --
    # a protocol violation, and the reason a regeneration of the matched
    # comparator disagreed with its own committed figures on all ten seeds
    # (PR #41 review finding 5 follow-through).
    df = data.load_ulb().drop_duplicates().reset_index(drop=True)
    split = data.stratified_split(df, seed)
    cols = data.top_k_features(split.X_train, split.y_train, k, seed=seed)
    return (split,
            split.X_train[cols].to_numpy(np.float32),
            split.X_val[cols].to_numpy(np.float32),
            split.X_test[cols].to_numpy(np.float32),
            np.where(split.y_train.to_numpy() == 1, 1, -1).astype(np.float64))


def evaluate(pool: dict, y_pm1, y_va, y_te, want_test: bool) -> dict:
    """Solve and score. `want_test` gates TEST reads: the sweep must never see
    test AP, or selection would be contaminated (repo-wide selection rule)."""
    from sklearn.metrics import average_precision_score as AP

    H_tr, H_va, H_te = pool["H_tr"], pool["H_va"], pool["H_te"]
    n = H_tr.shape[0]
    lam = qp.LAMBDA_MULT * len(y_pm1)
    w = mc.solve_weighted(H_tr, y_pm1, lam, np.ones(len(y_pm1)))
    w_u = np.full(n, 1.0 / n)
    sc = lambda wt, H: np.clip((wt @ H + 1.0) / 2.0, 0.0, 1.0)

    out = {
        "n_variables": int(n),
        "fits_free_tier": bool(n <= FREE_TIER_MAX_VARS),
        "diversity": mp.diversity(H_tr, seed=0),
        "l1_from_uniform": float(np.abs(w - w_u).sum()),
        "max_weight_over_uniform": float(w.max() * n),
        "ap_solved_val": float(AP(y_va, sc(w, H_va))),
        "ap_uniform_val": float(AP(y_va, sc(w_u, H_va))),
    }
    if want_test:
        ap_s, ap_u = float(AP(y_te, sc(w, H_te))), float(AP(y_te, sc(w_u, H_te)))
        out.update({"ap_solved_test": ap_s, "ap_uniform_test": ap_u,
                    "ap_difference": ap_s - ap_u})
    return out


def sweep() -> int:
    """Stage 1: seed 42 only, selection on VALIDATION AP. No test read."""
    split, X_tr, X_va, X_te, y_pm1 = _fold(TUNING_SEED, k=6)
    y_va, y_te = split.y_val.to_numpy(), split.y_test.to_numpy()

    rows = []
    for label, params in CANDIDATES.items():
        pool = build_tuned(X_tr, X_va, X_te, y_pm1, params)
        r = evaluate(pool, y_pm1, y_va, y_te, want_test=False)
        r.update({"label": label, "params": {f: dict(p) for f, p in params.items()},
                  "provenance": pool["provenance"]})
        rows.append(r)
        print(f"{label:22s} {r['n_variables']:3d} vars  val AP {r['ap_solved_val']:.4f} "
              f"(uniform {r['ap_uniform_val']:.4f})  L1 {r['l1_from_uniform']:.4f}  "
              f"gram {r['diversity']['gram_ratio']:.6f}")

    feasible = [r for r in rows if r["fits_free_tier"]]
    best = max(feasible or rows, key=lambda r: r["ap_solved_val"])
    store.atomic_write_json(SWEEP_OUT, {
        "stage": "sweep", "seed": TUNING_SEED,
        # Finding 8: stage 2 reads its parameters from this file, so an edit to
        # CANDIDATES between the two stages would silently run a stale config
        # under a label that no longer matches the source. Both artifacts carry
        # this hash and stage 2 refuses a mismatch.
        "candidates_hash": store.config_hash(CANDIDATES),
        "selection_rule": "highest VALIDATION AP among free-tier-feasible configs; "
                          "test AP is NOT read at this stage",
        "selected": best["label"], "candidates": rows,
    })
    print(f"\nSELECTED on validation AP: {best['label']} "
          f"({best['n_variables']} vars, val AP {best['ap_solved_val']:.4f})")
    return 0


def main() -> int:
    if "--sweep" in sys.argv:
        return sweep()

    if not SWEEP_OUT.exists():
        raise SystemExit("run --sweep first: stage 2 uses the configuration it selected")
    sel = json.loads(SWEEP_OUT.read_text())
    current = store.config_hash(CANDIDATES)
    recorded = sel.get("candidates_hash")
    if recorded is not None and recorded != current:
        raise SystemExit(
            "CANDIDATES has changed since the sweep ran "
            f"(sweep {recorded[:12]}, current {current[:12]}). Stage 2 would run "
            "the OLD parameters under a label that no longer matches the source, "
            "and the paper quotes this run. Re-run --sweep."
        )
    label = sel["selected"]
    params = next(c["params"] for c in sel["candidates"] if c["label"] == label)
    print(f"stage 2: '{label}' over {len(SEEDS)} seeds\n")

    rows = []
    for seed in SEEDS:
        t0 = time.time()
        split, X_tr, X_va, X_te, y_pm1 = _fold(seed, k=6)
        pool = build_tuned(X_tr, X_va, X_te, y_pm1, params)
        r = evaluate(pool, y_pm1, split.y_val.to_numpy(), split.y_test.to_numpy(),
                     want_test=True)
        r.update({"seed": seed, "label": label, "wall_seconds": round(time.time() - t0, 1)})
        rows.append(r)
        print(f"seed {seed}: AP {r['ap_solved_test']:.4f} (uniform {r['ap_uniform_test']:.4f}, "
              f"diff {r['ap_difference']:+.4f})  L1 {r['l1_from_uniform']:.4f}  "
              f"({r['wall_seconds']}s)")

    ap = np.array([r["ap_solved_test"] for r in rows])
    d = np.array([r["ap_difference"] for r in rows])
    l1 = np.array([r["l1_from_uniform"] for r in rows])
    summary = {
        "configuration": label,
        "n_seeds": len(rows),
        "ap_mean": float(ap.mean()), "ap_sd": float(ap.std(ddof=1)),
        "ap_difference_mean": float(d.mean()),
        "ap_difference_sd": float(d.std(ddof=1)),
        "seeds_positive": int((d > 0).sum()),
        "exceeds_mde": bool(abs(d.mean()) > MDE),
        "l1_from_uniform_mean": float(l1.mean()),
        "gram_ratio_mean": float(np.mean([r["diversity"]["gram_ratio"] for r in rows])),
    }

    # PR #41 review findings 2 and 3. This module previously computed
    # vs_frozen_pool and vs_untuned_mixed by raw subtraction and persisted them,
    # even though both constants are k=13 figures and this arm runs at k=6 --
    # exactly the order-mismatched comparison comparators.py was written to
    # forbid, in the one module that actually differences across
    # configurations. The guard was dead code: nothing imported it. Route the
    # comparison through it so a mismatch RAISES instead of serializing a
    # misleading number, and record why the cross-k differences are absent.
    tuned_arm = cmp.ArmSpec(label=f"tuned {label}", k=6, protocol="stratified",
                            split="test")
    matched = cmp.ArmSpec(label="frozen single-family k=6", k=6,
                          protocol="stratified", split="test")
    summary["matched_comparison"] = cmp.reported_difference(
        tuned_arm, float(ap.mean()), matched, FROZEN_K6_AP, mde=MDE)
    summary["cross_k_comparisons_withheld"] = (
        "vs_frozen_pool and vs_untuned_mixed are NOT reported: both constants "
        "are k=13 figures and this arm is k=6, so the difference would carry the "
        "feature-count effect as if it were the treatment. comparators.py "
        "refuses them. The matched k=6 comparison above is what the paper uses.")
    store.atomic_write_json(OUT, {
        "amendment": "A13",
        "candidates_hash": current,
        "status": "LABELED EXPLORATORY -- not a gate; frozen gates unchanged",
        "question": "Is the mixed pool's accuracy gap learner quality and tuning, "
                    "or something tuning cannot reach?",
        "comparators": {"frozen_single_family": FROZEN_POOL_AP,
                        "untuned_mixed": MIXED_POOL_AP,
                        "loke_reported": LOKE_REPORTED_AP},
        "summary": summary, "per_seed": rows,
    })

    print(f"\n{label} over {summary['n_seeds']} seeds")
    print(f"  AP                {summary['ap_mean']:.4f} (SD {summary['ap_sd']:.4f})")
    mc_ = summary["matched_comparison"]
    print(f"  vs frozen k=6     {mc_['difference']:+.4f}  (matched: {FROZEN_K6_AP})")
    print(f"                    {mc_['reporting_guidance']}")
    print(f"  vs Loke reported  {ap.mean() - LOKE_REPORTED_AP:+.4f}  (~0.80, "
          f"different protocol; context only, not a matched difference)")
    print(f"  solved - uniform  {summary['ap_difference_mean']:+.4f} "
          f"({summary['seeds_positive']}/{len(rows)} positive)  "
          f"{'EXCEEDS' if summary['exceeds_mde'] else 'BELOW'} the {MDE} MDE")
    print(f"  L1 from uniform   {summary['l1_from_uniform_mean']:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
