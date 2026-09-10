"""F42 finding F12: what actually produced the +0.0319?

The paper reports +0.0319 AUPRC for the tuned four-family pool over the frozen
single-family pool at matched k=6, 10 of 10 seeds, exceeding the 0.0268 MDE. The
review's objection is that THREE things changed at once -- learner families,
fit-time class weighting, and distance-weighted kNN -- while the only
decomposition offered was a Gram-ratio, not an AUPRC one. A reader cannot tell
which change bought the gain.

Second objection, separate and sharper: the winning configuration was SELECTED on
seed 42 and then evaluated on ten seeds INCLUDING seed 42. That is a mild
optimistic bias and the 9-seed figure should be stated alongside.

This runner answers both by adding the one arm the campaign never ran: the same
four families with NO class weighting (`defaults` in tuned_pool.CANDIDATES),
same splits, same k, same solver. The ladder becomes

    frozen 1-family  ->  4 families, no weighting  ->  4 families + weighting

so each step is attributable. Zero metered seconds, classical proxy throughout.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

import store
import tuned_pool

RESULTS = Path(__file__).resolve().parents[1] / "results"
OUT = RESULTS / "gain_decomposition.json"

K = 6                      # the matched comparison size
SELECTION_SEED = 42        # excluded in the leave-one-out figure

# The ladder. SELECTED is the configuration the campaign actually chose and the
# one the published +0.0319 belongs to -- decomposing any other arm answers a
# question nobody asked.
SELECTED = "balanced_shallow_knn"
ARMS = ("defaults", "balanced", SELECTED)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", help="2 seeds, for wiring only")
    args = ap.parse_args()

    seeds = tuned_pool.SEEDS[:2] if args.smoke else tuned_pool.SEEDS
    t0 = time.perf_counter()
    rows = []

    for seed in seeds:
        split, X_tr, X_va, X_te, y_pm1 = tuned_pool._fold(seed, K)
        cell = {"seed": int(seed)}
        for label in ARMS:
            pool = tuned_pool.build_tuned(
                X_tr, X_va, X_te, y_pm1,
                tuned_pool.CANDIDATES[label], k_schedule=2)
            ev = tuned_pool.evaluate(pool, y_pm1, split.y_val.to_numpy(), split.y_test.to_numpy(),
                                     want_test=True)
            cell[label] = float(ev["ap_solved_test"])
        rows.append(cell)
        print("  seed %d: %s" % (seed, "  ".join(
            f"{a} {cell[a]:.4f}" for a in ARMS)), flush=True)

    # PER-SEED frozen comparator, as the published comparison uses. Differencing
    # against a pooled mean would discard the pairing the design exists for.
    published = json.loads((RESULTS / "tuned_vs_frozen_k6.json").read_text(
        encoding="utf-8"))
    frozen_by_seed = {r["seed"]: r["frozen_k6"] for r in published["per_seed"]}
    frozen = np.array([frozen_by_seed[r["seed"]] for r in rows])

    arm = {a: np.array([r[a] for r in rows]) for a in ARMS}

    def stat(a, b, label):
        d = a - b
        return {"label": label, "mean": float(d.mean()),
                "sd": float(d.std(ddof=1)) if len(d) > 1 else None,
                "n_positive": int((d > 0).sum()), "n": int(len(d))}

    families = stat(arm["defaults"], frozen,
                    "families only (4-family defaults minus frozen 1-family)")
    weighting = stat(arm["balanced"], arm["defaults"],
                     "class weighting only (same families)")
    knn = stat(arm[SELECTED], arm["balanced"],
               "kNN change only (shallow tree + distance-weighted k=3)")
    total = stat(arm[SELECTED], frozen, "all three (the published +0.0319)")

    keep = [i for i, r in enumerate(rows) if r["seed"] != SELECTION_SEED]
    loo = stat(arm[SELECTED][keep], frozen[keep],
               f"all three, excluding the selection seed {SELECTION_SEED}")

    out = {
        "note": ("F42/F12: AUPRC decomposition of the +0.0319 tuned-pool gain, plus "
                 "the leave-one-out figure on the selection seed. Classical proxy "
                 "throughout; zero metered seconds."),
        "generator": "experiments/src/run_gain_decomposition.py",
        "evidence_tag": "SIM",
        "smoke": bool(args.smoke),
        "k": K,
        "frozen_k6_comparator_per_seed": {str(r["seed"]): frozen_by_seed[r["seed"]] for r in rows},
        "mde": 0.0268,
        "elapsed_sec": round(time.perf_counter() - t0, 2),
        "per_seed": rows,
        "published_mean_delta": published["mean_delta"],
        "decomposition": {"families": families, "weighting": weighting,
                          "knn": knn, "total": total,
                          "leave_out_selection_seed": loo},
    }
    store.atomic_write_json(OUT, out)

    print()
    for d in (families, weighting, knn, total, loo):
        flag = "EXCEEDS MDE" if abs(d["mean"]) > 0.0268 else "below MDE"
        sd = "n/a" if d["sd"] is None else f"{d['sd']:.4f}"
        print(f"  {d['label']:<62} {d['mean']:+.4f} "
              f"(SD {sd}, {d['n_positive']}/{d['n']}) {flag}")
    print(f"\nwritten: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
