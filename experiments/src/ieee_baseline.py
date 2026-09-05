"""IEEE-CIS classical baseline, minimal and labeled (Sprint 5, review response).

WHY THIS EXISTS AND WHAT IT IS NOT. HSBC's problem statement is framed around
higher transaction volumes and richer feature sets, and the full preregistered
IEEE-CIS protocol (the reduced Deotte recipe, UID aggregates, time-consistency
and adversarial filters, GroupKFold-by-month rolling origin) is Phase 2 work.
This script establishes ONE thing a Phase 1 proposal can honestly quote: that
the pipeline runs at that scale and produces a classical AUPRC in the published
leakage-free band.

It is therefore labeled a SCALE CHECK, not a protocol run:
  - raw joined features only, no engineered UID aggregates
  - a single stratified split, not the preregistered temporal protocol
  - three seeds, not ten
  - tuned-parameter reuse from ULB, not a fresh 100-trial study
Any number it produces is reported as [SIM] and explicitly marked as outside
the preregistered IEEE-CIS cells, so it can never be mistaken for H3 evidence.

Usage: python experiments/src/ieee_baseline.py
"""
from __future__ import annotations

import json
import logging
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import data
import store

log = logging.getLogger("frd.ieee")
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(name)s %(levelname)s %(message)s")

OUT = Path(__file__).resolve().parents[1] / "results" / "ieee_scale_check.json"
SEEDS = (42, 43, 44)


def main() -> int:
    from sklearn.metrics import average_precision_score, roc_auc_score
    from sklearn.model_selection import train_test_split
    from xgboost import XGBClassifier

    t0 = time.time()
    df = data.load_ieee_cis_train()
    y = df["isFraud"].astype(int)
    X = df.drop(columns=["isFraud", "TransactionID"])
    # object columns: label-encode by category code (no target information used)
    for c in X.columns:
        if X[c].dtype == object:
            X[c] = X[c].astype("category").cat.codes.astype("int32")
    log.info("[IEEE] loaded %d rows x %d features, prevalence %.4f, %.0fs",
             len(X), X.shape[1], float(y.mean()), time.time() - t0)

    rows = []
    for seed in SEEDS:
        X_tr, X_te, y_tr, y_te = train_test_split(
            X, y, test_size=0.20, stratify=y, random_state=seed)
        X_tr2, X_val, y_tr2, y_val = train_test_split(
            X_tr, y_tr, test_size=0.10, stratify=y_tr, random_state=seed)
        ratio = float((y_tr2 == 0).sum() / max((y_tr2 == 1).sum(), 1))
        m = XGBClassifier(n_estimators=2000, early_stopping_rounds=50,
                          eval_metric="aucpr", tree_method="hist", n_jobs=-1,
                          max_depth=8, learning_rate=0.05, subsample=0.8,
                          colsample_bytree=0.8, scale_pos_weight=np.sqrt(ratio),
                          random_state=seed)
        m.fit(X_tr2, y_tr2, eval_set=[(X_val, y_val)], verbose=False)
        p = m.predict_proba(X_te)[:, 1]
        ap = float(average_precision_score(y_te, p))
        auc = float(roc_auc_score(y_te, p))
        rows.append({"seed": seed, "auprc": ap, "auc_roc": auc,
                     "prevalence": float(y_te.mean()),
                     "best_iteration": int(m.best_iteration)})
        log.info("[IEEE] seed=%d AUPRC=%.4f AUC=%.4f prevalence=%.4f",
                 seed, ap, auc, float(y_te.mean()))

    aps = [r["auprc"] for r in rows]
    rec = {
        "label": "IEEE-CIS SCALE CHECK, not a preregistered cell",
        "caveats": [
            "raw joined features only; no engineered UID aggregates (Phase 2)",
            "single stratified split, not the preregistered temporal protocol",
            "3 seeds, not the 10 used for primary cells",
            "parameters carried from ULB tuning, not a fresh 100-trial study",
        ],
        "evidence_tag": "SIM",
        "rows": len(X), "features": int(X.shape[1]),
        "mean_auprc": float(np.mean(aps)),
        "sd_auprc": float(np.std(aps, ddof=1)),
        "mean_auc_roc": float(np.mean([r["auc_roc"] for r in rows])),
        "per_seed": rows,
        "wall_seconds": round(time.time() - t0, 1),
    }
    store.atomic_write_json(OUT, rec)
    log.info("[IEEE] scale check: mean AUPRC %.4f (SD %.4f), mean AUC %.4f over %d seeds",
             rec["mean_auprc"], rec["sd_auprc"], rec["mean_auc_roc"], len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
