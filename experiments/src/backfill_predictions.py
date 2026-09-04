"""Backfill per-row predictions for rows written before persistence (A7).

Deterministic re-derivation, NOT a re-run of the protocol: the same frozen
splits, features and tuned params reproduce the same model, and the script
ASSERTS the recomputed AUPRC matches the stored value before writing. Any
mismatch aborts that cell rather than silently overwriting evidence.

Classical arms only. Proxy and hardware rows need their pools, so they are
re-derived by qubo_proxy (cheap, cached) or left unbackfilled and reported.

Usage: python experiments/src/backfill_predictions.py [--tol 1e-9]
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import data
import run_classical as rc
import store

log = logging.getLogger("frd.backfill")
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(name)s %(levelname)s %(message)s")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tol", type=float, default=1e-9)
    args = ap.parse_args()

    rows = json.loads(store.RESULTS.read_text())["rows"]
    tuned = json.loads(rc.PARAMS.read_text())
    df, _ = rc._dedupe(data.load_ulb())
    done = skipped = mismatch = 0

    for r in rows:
        if r["arm"] not in rc.ARMS or r.get("predictions_file"):
            continue
        if store.prediction_path(r["config_hash"], r["seed"], r["protocol"]).exists():
            skipped += 1
            continue
        seed, fs = r["seed"], r["feature_set"]
        split = data.stratified_split(df, seed)
        cols = rc._features(split, fs, seed)
        assert cols == r["features_used"], f"feature drift for {r['arm']}/{fs}/{seed}"
        params = tuned[f"{r['arm']}:{fs}"]["params"]
        model, _es = rc._fit_final(r["arm"], params, split.X_train[cols], split.y_train,
                                   split.X_val[cols], split.y_val, seed)
        p_val = model.predict_proba(split.X_val[cols])[:, 1]
        p_test = model.predict_proba(split.X_test[cols])[:, 1]
        from sklearn.metrics import average_precision_score
        ap_now = float(average_precision_score(split.y_test.to_numpy(), p_test))
        ap_rec = float(r["metrics"]["auprc"])
        if abs(ap_now - ap_rec) > args.tol:
            log.error("[BACKFILL] MISMATCH %s/%s seed=%d: recomputed %.10f vs recorded "
                      "%.10f -- NOT written", r["arm"], fs, seed, ap_now, ap_rec)
            mismatch += 1
            continue
        store.save_predictions(r["config_hash"], seed, r["protocol"],
                               split.y_val.to_numpy(), p_val,
                               split.y_test.to_numpy(), p_test)
        done += 1
        log.info("[BACKFILL] %s/%s seed=%d ap=%.6f verified and stored",
                 r["arm"], fs, seed, ap_now)

    log.info("[BACKFILL] stored=%d already_present=%d mismatched=%d", done, skipped, mismatch)
    return 1 if mismatch else 0


if __name__ == "__main__":
    sys.exit(main())
