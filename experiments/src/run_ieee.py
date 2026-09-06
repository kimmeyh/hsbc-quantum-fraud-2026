"""IEEE-CIS classical arms under the preregistered protocol (F3 Task B).

This is the protocol run that `ieee_baseline.py` explicitly is not. That script
established one honest thing -- the pipeline runs at 590k scale and lands in the
published band -- on raw joined features with no engineered aggregates, and
labelled itself a SCALE CHECK for exactly that reason. This module runs the
reduced Deotte recipe the preregistration specifies: D-normalization, UID
aggregates with the UID itself excluded, V-column reduction, the section 4 item 4
controls, and GroupKFold-by-month rolling origin.

Two properties matter more than the numbers it produces.

FIT INSIDE THE FOLD. Every fitted object -- feature aggregates, V-column
selection, the item 4 filters, the model -- is fitted on the training months of
one fold and applied to that fold's evaluation month. A single aggregate fitted
across the whole frame would leak the future into every earlier fold, and the
resulting metric would look better and mean nothing.

DEDUPLICATE FIRST. Section 4 item 7, per dataset. Six rows on IEEE-CIS, none of
them fraud, so the effect is nil; amendment A17 is why it happens anyway.

Usage:
    python experiments/src/run_ieee.py --smoke     # 40k rows, 1 fold, fast
    python experiments/src/run_ieee.py             # full protocol run
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import data
import ieee_controls
import ieee_features
import ieee_loader
import ieee_splits
import store

OUT = Path(__file__).resolve().parents[1] / "results" / "ieee_classical.json"
LABEL = "isFraud"
SEED = 42

# Section 6 fixes the budget at 100 Optuna trials per arm per dataset. This
# module runs the FIXED configurations rather than the search: the search is a
# separate, longer job, and running it inside the fold loop would multiply
# 100 trials by 3 folds by 3 arms. Defaults here are the tuned ULB settings,
# carried as a HYPOTHESIS per the config-provenance rule and flagged as such in
# the output, since ULB is 0.17% prevalence and IEEE-CIS is 3.5%.
ARMS = {
    "xgboost": dict(max_depth=6, n_estimators=400, learning_rate=0.05,
                    subsample=0.8, colsample_bytree=0.8, n_jobs=-1,
                    eval_metric="aucpr", tree_method="hist"),
    "lightgbm": dict(num_leaves=64, n_estimators=400, learning_rate=0.05,
                     subsample=0.8, colsample_bytree=0.8, n_jobs=-1,
                     verbose=-1),
    "catboost": dict(depth=6, iterations=400, learning_rate=0.05,
                     verbose=0, thread_count=-1),
}


def _fit_predict(arm: str, X_tr, y_tr, X_ev):
    if arm == "xgboost":
        from xgboost import XGBClassifier
        m = XGBClassifier(**ARMS[arm])
    elif arm == "lightgbm":
        from lightgbm import LGBMClassifier
        m = LGBMClassifier(**ARMS[arm])
    else:
        from catboost import CatBoostClassifier
        m = CatBoostClassifier(**ARMS[arm])
    t0 = time.time()
    m.fit(X_tr, y_tr)
    return m.predict_proba(X_ev)[:, 1], round(time.time() - t0, 1)


def _numeric(df: pd.DataFrame) -> pd.DataFrame:
    """GBDTs here take numeric input; object columns that survived the recipe
    are dropped rather than silently label-encoded, which would invent an
    ordering that does not exist."""
    return df.select_dtypes(include=[np.number])



def _jsonable(o):
    """Coerce numpy scalars to Python types before serialization.

    pandas returns int32/int64 and float32 for things like a month label, and
    json refuses them with a TypeError raised at write time -- AFTER the run has
    finished and the compute is spent. Coerce on the way in.
    """
    import numpy as _np
    if isinstance(o, dict):
        return {k: _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonable(v) for v in o]
    if isinstance(o, _np.generic):
        return o.item()
    return o

def run(smoke: bool = False) -> dict:
    from sklearn.metrics import average_precision_score, roc_auc_score

    raw = data.load_ieee_cis_train()
    df, n_dupes = ieee_loader.dedupe_ieee(raw)
    if smoke:
        # Sample ACROSS the timespan, not the first 40k rows. Taking the head
        # lands entirely inside month 0, and the rolling-origin splitter then
        # correctly refuses ("need at least 4 month buckets, found 1"). A smoke
        # mode that cannot exercise the temporal protocol tests nothing that
        # matters here.
        df = (df.sort_values("TransactionDT")
                .iloc[::max(1, len(df) // 60_000)]
                .reset_index(drop=True))

    folds = ieee_splits.rolling_origin_folds(df)
    ieee_splits.assert_no_temporal_leakage(df, folds)
    if smoke:
        folds = folds[:1]

    rows, control_records = [], []
    for fi, fold in enumerate(folds):
        parts = ieee_splits.split_xy(df, fold)
        tr_df, ev_df = parts["X_train"], parts["X_eval"]
        y_tr, y_ev = parts["y_train"].to_numpy(), parts["y_eval"].to_numpy()

        # Feature recipe fitted on THIS fold's training months only.
        pipe = ieee_features.IEEEFeaturePipeline()
        Xtr = _numeric(pipe.fit_transform(tr_df))
        Xev = _numeric(pipe.transform(ev_df)).reindex(columns=Xtr.columns)

        # Section 4 item 4, also training-rows-only.
        day_tr = ieee_features.add_day(tr_df).to_numpy()
        ctrl = ieee_controls.apply_item4_controls(Xtr, y_tr, day_tr, seed=SEED)
        keep = ctrl["features"] or list(Xtr.columns)
        ctrl["fold"] = fi
        ctrl["eval_month"] = int(fold.eval_month)
        control_records.append(ctrl)

        Xtr_k, Xev_k = Xtr[keep], Xev[keep]
        for arm in ARMS:
            p, secs = _fit_predict(arm, Xtr_k, y_tr, Xev_k)
            rows.append({
                "arm": arm, "dataset": "ieee-cis", "protocol": "rolling_origin",
                "fold": fi, "eval_month": int(fold.eval_month),
                "seed": None,            # temporal folds are not seeded
                "n_train": int(len(y_tr)), "n_eval": int(len(y_ev)),
                "n_features": int(len(keep)),
                "auprc": float(average_precision_score(y_ev, p)),
                "auc_roc": float(roc_auc_score(y_ev, p)),
                "eval_prevalence": float(y_ev.mean()),
                "fit_seconds": secs,
                "evidence_tag": "SIM",
            })
            print(f"  fold {fi} ({fold.eval_month}) {arm:9s} "
                  f"AUPRC {rows[-1]['auprc']:.4f}  AUC {rows[-1]['auc_roc']:.4f}  "
                  f"({secs}s, {len(keep)} feats)")

    out = {
        "dataset": "ieee-cis",
        "protocol": "GroupKFold-by-month rolling origin, prereg section 5",
        "smoke": smoke,
        "rows_raw": len(raw),
        "rows_after_dedupe": len(df),
        "exact_duplicates_removed": n_dupes,
        "config_provenance": (
            "GBDT hyperparameters carried from the tuned ULB settings as a "
            "HYPOTHESIS, not a setting: ULB is 0.17% prevalence and IEEE-CIS is "
            "3.5%, a 20x difference. Reported as-is; the section 6 100-trial "
            "search on this dataset is a separate job."),
        "item4_controls": control_records,
        "per_fold": rows,
    }

    by_arm = {}
    for arm in ARMS:
        vals = [r["auprc"] for r in rows if r["arm"] == arm]
        if vals:
            by_arm[arm] = {"mean_auprc": float(np.mean(vals)),
                           "min": float(np.min(vals)), "max": float(np.max(vals)),
                           "n_folds": len(vals)}
    out["by_arm"] = by_arm
    store.atomic_write_json(OUT, _jsonable(out))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    print(f"IEEE-CIS classical arms{' (SMOKE)' if args.smoke else ''}")
    out = run(smoke=args.smoke)
    print(f"\nrows {out['rows_raw']} -> {out['rows_after_dedupe']} "
          f"({out['exact_duplicates_removed']} exact duplicates removed)")
    for arm, s in out["by_arm"].items():
        print(f"  {arm:9s} mean AUPRC {s['mean_auprc']:.4f} "
              f"[{s['min']:.4f}, {s['max']:.4f}] over {s['n_folds']} fold(s)")
    for c in out["item4_controls"]:
        print(f"  fold {c['fold']} item4: {c['n_features_start']} -> "
              f"{c['n_after_time_consistency']} -> {c['n_after_adversarial']} features")
    return 0


if __name__ == "__main__":
    sys.exit(main())
