"""Classical evidence campaign runner (Sprint 3 / F1, card #15; PREREGISTRATION 4-9, A4).

KNOWN FAILURE MODES / LONG-RUN NOTES:
- Full run is ~4-8h unattended (6 GBDT studies x 100 trials + 80 refits). Safe to
  kill and re-run: tuned params and result rows are checkpointed; done work skips.
- n_jobs=-1 saturates the CPU for hours; expect that.
- A crashed fit leaves no partial row (rows are appended atomically after scoring).
- Exact duplicates are removed BEFORE splitting (prereg 5.7); counts reported in
  the meta block of results.json.

Usage:
  python experiments/src/run_classical.py --smoke      # 2 trials, 5k rows, 2 seeds
  python experiments/src/run_classical.py              # full campaign (resumable)
  python experiments/src/run_classical.py --stage tune # tuning studies only
  python experiments/src/run_classical.py --stage refit
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import data
import metrics
import store
import tune

log = logging.getLogger("frd.classical")
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(name)s %(levelname)s %(message)s")

RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"
RESULTS = RESULTS_DIR / "results.json"
PARAMS = RESULTS_DIR / "tuned_params.json"

SEEDS = tuple(range(42, 52))          # prereg 8.1 primary
TUNING_SEED = 42
K_MATCHED = 13                        # H1b matched top-k
ARMS = ("xgboost", "lightgbm", "catboost", "logistic")
FEATURE_SETS = ("matched13", "full")


def _load(path: Path, default):
    return json.loads(path.read_text()) if path.exists() else default


def _dedupe(df):
    before = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    return df, before - len(df)


def _features(split, feature_set: str, seed: int) -> list[str]:
    if feature_set == "full":
        return list(split.X_train.columns)
    return data.top_k_features(split.X_train, split.y_train, K_MATCHED, seed=seed)


def _fit_final(arm: str, params: dict, X_tr, y_tr, X_val, y_val, seed: int):
    """Refit the tuned config on train with early stopping on the DEDICATED
    validation fold (never test; prereg 4). Returns (model, early_stop_info)."""
    if arm == "xgboost":
        from xgboost import XGBClassifier
        m = XGBClassifier(n_estimators=tune.MAX_ESTIMATORS,
                          early_stopping_rounds=tune.EARLY_STOP,
                          eval_metric="aucpr", tree_method="hist", n_jobs=-1,
                          random_state=seed, **params)
        m.fit(X_tr, y_tr, eval_set=[(X_val, y_val)], verbose=False)
        info = {"best_iteration": int(m.best_iteration),
                "patience": tune.EARLY_STOP, "monitored": "aucpr"}
    elif arm == "lightgbm":
        import lightgbm as lgb
        m = lgb.LGBMClassifier(n_estimators=tune.MAX_ESTIMATORS, n_jobs=-1,
                               random_state=seed, verbosity=-1, **params)
        # Pinned LightGBM 4.7: eval_X/eval_y is the current API (eval_set deprecated).
        m.fit(X_tr, y_tr, eval_X=X_val, eval_y=y_val,
              eval_metric="average_precision",
              callbacks=[lgb.early_stopping(tune.EARLY_STOP, verbose=False)])
        info = {"best_iteration": int(m.best_iteration_),
                "patience": tune.EARLY_STOP, "monitored": "average_precision"}
    elif arm == "catboost":
        from catboost import CatBoostClassifier
        m = CatBoostClassifier(iterations=tune.MAX_ESTIMATORS, od_type="Iter",
                               od_wait=tune.EARLY_STOP, eval_metric="PRAUC",
                               random_seed=seed, verbose=0, **params)
        m.fit(X_tr, y_tr, eval_set=(X_val, y_val))
        info = {"best_iteration": int(m.get_best_iteration()),
                "patience": tune.EARLY_STOP, "monitored": "PRAUC"}
    elif arm == "logistic":
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
        m = make_pipeline(StandardScaler(),
                          LogisticRegression(max_iter=2000, random_state=seed,
                                             **params))
        m.fit(X_tr, y_tr)
        info = {"best_iteration": None, "patience": None, "monitored": None}
    else:
        raise ValueError(arm)
    return m, info


def stage_tune(df, smoke: bool) -> dict:
    tuned = _load(PARAMS, {})
    n_trials = 2 if smoke else None
    split = data.stratified_split(df, TUNING_SEED)
    for arm in ARMS:
        for fs in FEATURE_SETS:
            key = f"{arm}:{fs}"
            if key in tuned:
                log.info("[TUNE] %s already tuned, skipping", key)
                continue
            cols = _features(split, fs, TUNING_SEED)
            t0 = time.time()
            study = tune.tune(arm, split.X_train[cols], split.y_train,
                              TUNING_SEED, n_trials=n_trials)
            tuned[key] = {
                "params": study.best_params,
                "cv_ap": study.best_value,
                "n_trials": len(study.trials),
                "wall_seconds": round(time.time() - t0, 1),
                "tuning_seed": TUNING_SEED,
                "features": cols,
            }
            store.atomic_write_json(PARAMS, tuned)
            log.info("[TUNE] %s done: cv_ap=%.4f trials=%d wall=%.0fs",
                     key, study.best_value, len(study.trials), tuned[key]["wall_seconds"])
    return tuned


def stage_refit(df, tuned: dict, dedupe_count: int, smoke: bool) -> None:
    store.update_meta(ulb_duplicates_removed=dedupe_count,
                      dataset_rows_after_dedupe=len(df))
    existing = _load(RESULTS, {"meta": {}, "rows": []})
    # .get: the store also holds proxy rows keyed by config/pool_variant instead.
    done = {(r["arm"], r.get("feature_set"), r["seed"]) for r in existing["rows"]}
    n_rows = len(existing["rows"])
    seeds = SEEDS[:2] if smoke else SEEDS
    for arm in ARMS:
        for fs in FEATURE_SETS:
            cfg = tuned[f"{arm}:{fs}"]
            for seed in seeds:
                if (arm, fs, seed) in done:
                    continue
                t0 = time.strftime("%Y-%m-%dT%H:%M:%S")
                split = data.stratified_split(df, seed)
                cols = _features(split, fs, seed)
                model, es = _fit_final(arm, cfg["params"],
                                       split.X_train[cols], split.y_train,
                                       split.X_val[cols], split.y_val, seed)
                p_val = model.predict_proba(split.X_val[cols])[:, 1]
                p_test = model.predict_proba(split.X_test[cols])[:, 1]
                cfg_hash = store.config_hash(
                    {"arm": arm, "fs": fs, "params": cfg["params"]})
                pred_file = store.save_predictions(
                    cfg_hash, seed, "stratified",
                    split.y_val.to_numpy(), p_val, split.y_test.to_numpy(), p_test,
                    arm=arm)
                row = {
                    "arm": arm,
                    "dataset": "ulb",
                    "protocol": "stratified",
                    "seed": seed,
                    "feature_set": fs,
                    "config_hash": cfg_hash,
                    "predictions_file": pred_file,
                    "features_used": cols,
                    "early_stopping": es,
                    "metrics": metrics.summarize(
                        split.y_test.to_numpy(), split.y_val.to_numpy(),
                        p_val, p_test, seed=seed),
                    "evidence_tag": "SIM",
                    "metered_seconds": 0,
                    "retry_count": 0,
                    "timestamps": {"started": t0,
                                   "finished": time.strftime("%Y-%m-%dT%H:%M:%S")},
                }
                store.append_row(row)
                n_rows += 1
                log.info("[REFIT] %s/%s seed=%d ap=%.4f (rows=%d)",
                         arm, fs, seed, row["metrics"]["auprc"], n_rows)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["tune", "refit", "all"], default="all")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    RESULTS_DIR.mkdir(exist_ok=True)

    df = data.load_ulb()
    if args.smoke:
        from sklearn.model_selection import train_test_split as _tts
        # 20k keeps ~34 positives so every stratified carve-out retains some
        # (5k starved CatBoost's eval fold: "No element of a positive class").
        df, _ = _tts(df, train_size=20000, stratify=df[data.LABEL_COL],
                     random_state=0)
        df = df.reset_index(drop=True)
    df, dupes = _dedupe(df)
    log.info("[DATA] ULB rows=%d duplicates_removed=%d", len(df), dupes)

    tuned = _load(PARAMS, {})
    if args.stage in ("tune", "all"):
        tuned = stage_tune(df, args.smoke)
    if args.stage in ("refit", "all"):
        stage_refit(df, tuned, dupes, args.smoke)
    log.info("[DONE] stage=%s", args.stage)
    return 0


if __name__ == "__main__":
    sys.exit(main())
