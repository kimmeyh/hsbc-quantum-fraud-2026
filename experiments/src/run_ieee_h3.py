"""H3 regime dose-response ladder on IEEE-CIS (F3 Task D).

The preregistration, section 3:

  "H3 (regime dose-response, exploratory): on ULB and IEEE-CIS separately, run
   the frozen CVQBoost config and best GBDT at k in {5, 9, 13, 17} matched
   features; report the slope of delta-AUPRC vs k with a seed-clustered CI.
   Scored only if at least 3 ladder cells per dataset run; otherwise reported
   descriptively."

WHY THIS LADDER ANSWERS SOMETHING TASK C COULD NOT. Task C ran one k (=6) and
found both CVQBoost arms near the base rate, with a matched-feature control
showing LightGBM collapses the same way on the same six columns. That
established the restriction as the cause. It did NOT establish how the gap
behaves as the restriction lifts, which is exactly what H3 asks: does the
quantum-minus-classical difference improve, worsen or hold as k grows?

THE CEILING DOES NOT BIND HERE, AND THAT MATTERS. The A12 limit of 100
continuous degree-2 variables is a DEVICE limit -- the API refuses larger jobs.
A classical proxy solve never reaches the device, and F31 already ran 312
variables on the proxy. So the full ladder runs, and every cell is marked with
whether it WOULD fit the free tier. That converts the constraint from an
obstacle into a measurement: the ladder shows what the ceiling costs.

Zero metered seconds.

Usage: python experiments/src/run_ieee_h3.py [--smoke]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from math import comb
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import data
import ieee_controls
import ieee_features
import ieee_loader
import ieee_splits
import mechanism_controls as mcx
import qubo_proxy as qp
import store

OUT = Path(__file__).resolve().parents[1] / "results" / "ieee_h3_ladder.json"
PROGRESS = Path(__file__).resolve().parents[1] / "results" / "ieee_h3_progress.json"

K_LADDER = (5, 9, 13, 17)          # preregistered
SCHEDULE = 2
SEED = 42
FREE_TIER_MAX_VARS = 100           # A12; a DEVICE limit, not a proxy limit
POOL_SUBSAMPLE_N = 100_000         # same rationale as Task C


def _progress(stage: str, **fields) -> None:
    import datetime as _dt
    rec = {"stage": stage, "at": _dt.datetime.now().isoformat(timespec="seconds"), **fields}
    try:
        PROGRESS.parent.mkdir(parents=True, exist_ok=True)
        PROGRESS.write_text(json.dumps(rec, indent=2, default=str) + "\n")
    except Exception:                                  # noqa: BLE001
        pass
    print(f"[{rec['at']}] {stage}: " +
          ", ".join(f"{k}={v}" for k, v in fields.items()), flush=True)


def _jsonable(o):
    if isinstance(o, dict):
        return {k: _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonable(v) for v in o]
    if isinstance(o, np.generic):
        return o.item()
    return o


def run(smoke: bool = False) -> dict:
    from sklearn.feature_selection import mutual_info_classif
    from sklearn.metrics import average_precision_score as AP
    from lightgbm import LGBMClassifier

    raw = data.load_ieee_cis_train()
    df, n_dupes = ieee_loader.dedupe_ieee(raw)
    if smoke:
        df = (df.sort_values("TransactionDT")
                .iloc[::max(1, len(df) // 60_000)].reset_index(drop=True))

    folds = ieee_splits.rolling_origin_folds(df)
    ieee_splits.assert_no_temporal_leakage(df, folds)
    if smoke:
        folds = folds[:1]
    ks = K_LADDER[:2] if smoke else K_LADDER
    _progress("start", n_folds=len(folds), ladder=list(ks))

    cells = []
    for fi, fold in enumerate(folds):
        parts = ieee_splits.split_xy(df, fold)
        tr_df, ev_df = parts["X_train"], parts["X_eval"]
        y_tr, y_ev = parts["y_train"].to_numpy(), parts["y_eval"].to_numpy()

        pipe = ieee_features.IEEEFeaturePipeline()
        Xtr = pipe.fit_transform(tr_df).select_dtypes(include=[np.number])
        Xev = pipe.transform(ev_df).select_dtypes(include=[np.number])

        day_tr = ieee_features.add_day(tr_df).to_numpy()
        ctrl = ieee_controls.apply_item4_controls(Xtr, y_tr, day_tr, seed=SEED)
        surviving = ctrl["features"] or list(Xtr.columns)
        _progress("item4_done", fold=fi, kept=len(surviving))

        # One MI ranking per fold; the ladder takes prefixes of it, so the k=5
        # features are a strict subset of the k=9 features and so on. Ranking
        # once per k would let the feature SET change between rungs and the
        # ladder would confound "more features" with "different features".
        Xs = Xtr[surviving].fillna(0.0)
        mi = mutual_info_classif(Xs, y_tr, random_state=SEED)
        ranked = [surviving[i] for i in np.argsort(mi)[::-1]]

        # Subsample rows for pool construction only (Task C rationale).
        rs = np.random.default_rng(SEED)
        idx = (rs.choice(len(y_tr), size=POOL_SUBSAMPLE_N, replace=False)
               if len(y_tr) > POOL_SUBSAMPLE_N else np.arange(len(y_tr)))

        for k in ks:
            cols = ranked[:k]
            X_pool = Xtr[cols].fillna(0.0).to_numpy(np.float32)[idx]
            X_ev = Xev.reindex(columns=cols).fillna(0.0).to_numpy(np.float32)
            y_pool = np.where(y_tr[idx] == 1, 1, -1).astype(np.float64)

            t0 = time.time()
            clf = qp.build_pool(X_pool, y_pool, schedule=SCHEDULE,
                                weak_type="dct", pair_build="seq")
            H_tr, H_ev = qp.h_matrix(clf, X_pool), qp.h_matrix(clf, X_ev)
            w = mcx.solve_weighted(H_tr, y_pool,
                                   qp.LAMBDA_MULT * len(y_pool),
                                   np.ones(len(y_pool)))
            q_ap = float(AP(y_ev, np.clip((w @ H_ev + 1.0) / 2.0, 0.0, 1.0)))
            n_vars = int(H_tr.shape[0])

            # Best GBDT on the SAME k features -- the matched classical bar.
            g = LGBMClassifier(n_estimators=200, verbose=-1, n_jobs=-1)
            g.fit(Xtr[cols].fillna(0.0).iloc[idx], y_tr[idx])
            c_ap = float(AP(y_ev, g.predict_proba(
                Xev.reindex(columns=cols).fillna(0.0))[:, 1]))

            cells.append({
                "fold": fi, "eval_month": int(fold.eval_month), "k": k,
                "n_variables": n_vars,
                "fits_free_tier": bool(n_vars <= FREE_TIER_MAX_VARS),
                "cvqboost_ap": q_ap, "gbdt_ap": c_ap,
                "delta_auprc": q_ap - c_ap,
                "seconds": round(time.time() - t0, 1),
                "evidence_tag": "SIM",
            })
            _progress("cell_done", fold=fi, k=k, n_vars=n_vars,
                      cvq=round(q_ap, 4), gbdt=round(c_ap, 4),
                      delta=round(q_ap - c_ap, 4),
                      fits_free_tier=cells[-1]["fits_free_tier"])

    # Slope of delta-AUPRC against k. Scored only with >= 3 ladder cells per
    # the prereg; otherwise descriptive.
    ks_run = sorted({c["k"] for c in cells})
    by_k = {k: [c["delta_auprc"] for c in cells if c["k"] == k] for k in ks_run}
    means = [float(np.mean(by_k[k])) for k in ks_run]
    slope = None
    if len(ks_run) >= 2:
        slope = float(np.polyfit(ks_run, means, 1)[0])

    out = {
        "hypothesis": "H3 regime dose-response, EXPLORATORY",
        "dataset": "ieee-cis",
        "protocol": "GroupKFold-by-month rolling origin",
        "ladder": list(ks_run),
        "scoreable": len(ks_run) >= 3,
        "scoring_rule": ("prereg: scored only if at least 3 ladder cells per "
                         "dataset run; otherwise reported descriptively"),
        "ceiling_note": (
            "The A12 free-tier limit of 100 continuous degree-2 variables is a "
            "DEVICE limit and does not bind a classical proxy solve, so the full "
            "ladder runs. Each cell records whether it would fit the free tier, "
            "which turns the constraint into a measurement: the ladder shows "
            "what the ceiling costs."),
        "delta_by_k": {str(k): {"mean": float(np.mean(by_k[k])),
                                "n_folds": len(by_k[k])} for k in ks_run},
        "slope_delta_vs_k": slope,
        "cells": cells,
    }
    store.atomic_write_json(OUT, _jsonable(out))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    o = run(smoke=a.smoke)
    print("\nH3 ladder, delta-AUPRC (CVQBoost minus matched GBDT):")
    for k, s in o["delta_by_k"].items():
        fits = [c["fits_free_tier"] for c in o["cells"] if str(c["k"]) == k][0]
        print(f"  k={k:>2}  delta {s['mean']:+.4f}  over {s['n_folds']} fold(s)"
              f"  {'(fits free tier)' if fits else '(EXCEEDS free tier)'}")
    if o["slope_delta_vs_k"] is not None:
        print(f"\nslope of delta vs k: {o['slope_delta_vs_k']:+.5f} per feature")
    print("scoreable" if o["scoreable"] else "NOT scoreable; descriptive only")
    return 0


if __name__ == "__main__":
    sys.exit(main())
