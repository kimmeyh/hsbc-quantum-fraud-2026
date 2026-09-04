"""Backfill proxy predictions from the SAVED pool matrices (Sprint 5 F26; A7).

Deterministic re-derivation, not a re-run: the cached .npz holds the exact H
matrices the original row used, so re-solving the identical Hamiltonian
reproduces the same weights and the same scores. Every cell ASSERTS the
recomputed AUPRC matches the recorded value before writing.

Hardware rows are NOT backfilled: their solution weights came from Dirac-3 and
were never persisted, so they cannot be re-derived without spending metered
seconds. They are reported as unbackfillable, which is the honest outcome; the
runner now persists predictions for every future hardware fit.

Usage: python experiments/src/backfill_proxy_predictions.py
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qubo_proxy as qp
import store

log = logging.getLogger("frd.backfill_proxy")
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(name)s %(levelname)s %(message)s")

TOL = 1e-6   # re-solve is iterative (FISTA); exact bit-equality is not expected


def main() -> int:
    from sklearn.metrics import average_precision_score

    rows = json.loads(qp.RESULTS.read_text())["rows"]
    done = skipped = mismatch = nopool = 0
    hw_rows = 0

    for r in rows:
        if r["arm"] == "cvqboost_hw":
            hw_rows += 1
            continue
        if r["arm"] != "cvqboost_proxy":
            continue
        seed = r["seed"]
        if store.prediction_path(r["config_hash"], seed, "stratified").exists():
            skipped += 1
            continue
        # only the full-pair dct pools were saved as standalone npz files
        pool = qp.POOLS_DIR / f"h_{seed}_free_dct_full.npz"
        if not (r.get("config") == "free" and r.get("pool_variant") == "dct"
                and r.get("pair_build") == "full" and pool.exists()):
            nopool += 1
            continue
        z = np.load(pool)
        y_pm1 = np.where(z["y_tr01"] == 1, 1, -1)
        w = qp.solve_simplex_qp(z["H_tr"], y_pm1, qp.LAMBDA_MULT * len(y_pm1))
        p_val = np.clip((w @ z["H_va"] + 1.0) / 2.0, 0.0, 1.0)
        p_test = np.clip((w @ z["H_te"] + 1.0) / 2.0, 0.0, 1.0)
        ap_now = float(average_precision_score(z["y_te"], p_test))
        ap_rec = float(r["metrics"]["auprc"])
        if abs(ap_now - ap_rec) > TOL:
            log.error("[BACKFILL] MISMATCH %s seed=%d: %.8f vs recorded %.8f -- NOT written",
                      r.get("config"), seed, ap_now, ap_rec)
            mismatch += 1
            continue
        store.save_predictions(r["config_hash"], seed, "stratified",
                               z["y_va"], p_val, z["y_te"], p_test)
        done += 1
        log.info("[BACKFILL] proxy %s/%s seed=%d ap=%.6f verified and stored",
                 r.get("config"), r.get("pool_variant"), seed, ap_now)

    log.info("[BACKFILL] proxy stored=%d already=%d no_saved_pool=%d mismatched=%d",
             done, skipped, nopool, mismatch)
    log.info("[BACKFILL] %d hardware rows NOT backfillable: Dirac-3 solution weights were "
             "never persisted and cannot be re-derived without metered calls. Future fits "
             "persist predictions at write time.", hw_rows)
    return 1 if mismatch else 0


if __name__ == "__main__":
    sys.exit(main())
