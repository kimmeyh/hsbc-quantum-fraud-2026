"""Sprint 1 task 4: pilot seed-variance run (PREREGISTRATION v1.1 section 8.3).

Purpose: estimate the across-seed SD of test AUPRC on ULB to produce the
minimum-detectable-effect statement required before any hardware approval.
This is a VARIANCE PILOT with fixed, documented XGBoost settings; it is NOT
the G0 gate run (G0 uses the full 100-trial tuned model in Sprint 2).

Run: your venv interpreter (docs/ENVIRONMENT.md) experiments/src/pilot_variance.py
Writes: experiments/results/pilot_variance.json, experiments/PILOT_VARIANCE.md
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import data as D
import metrics as M

from sklearn.metrics import average_precision_score
from xgboost import XGBClassifier

SEEDS = (42, 43, 44, 45, 46, 47, 48, 49, 50, 51)

# Fixed pilot settings (documented; deliberately mid-range, not tuned).
PILOT_PARAMS = dict(
    n_estimators=2000, learning_rate=0.05, max_depth=8,
    subsample=0.9, colsample_bytree=0.9, min_child_weight=5,
    tree_method="hist", eval_metric="aucpr", early_stopping_rounds=50,
    n_jobs=-1,
)


def main() -> None:
    df = D.load_ulb()
    # G0c preprocessing: log-Amount, Time retained, exact duplicates removed.
    n0 = len(df)
    df = df.drop_duplicates()
    dup_count = n0 - len(df)
    df["Amount"] = np.log1p(df["Amount"])

    aps = []
    for seed in SEEDS:
        t0 = time.time()
        s = D.stratified_split(df, seed=seed)
        ratio = float((s.y_train == 0).sum() / s.y_train.sum())
        model = XGBClassifier(random_state=seed, scale_pos_weight=ratio, **PILOT_PARAMS)
        model.fit(s.X_train, s.y_train, eval_set=[(s.X_val, s.y_val)], verbose=False)
        ap = float(average_precision_score(s.y_test, model.predict_proba(s.X_test)[:, 1]))
        aps.append(ap)
        print(f"seed {seed}: test AP {ap:.4f} ({time.time()-t0:.0f}s)", flush=True)

    aps_arr = np.array(aps)
    sd = float(aps_arr.std(ddof=1))
    mde10 = M.mde(sd, 10)
    out = {
        "purpose": "seed-variance pilot (NOT the G0 tuned run)",
        "dataset": "ULB", "protocol": "stratified 60/20/20", "seeds": list(SEEDS),
        "duplicates_removed": int(dup_count),
        "pilot_params": {k: v for k, v in PILOT_PARAMS.items() if k != "n_jobs"},
        "test_ap_per_seed": aps, "mean_ap": float(aps_arr.mean()), "sd_ap": sd,
        "mde_10_seeds_alpha05_power80": mde10,
        "evidence_tag": "[SIM]",
    }
    res_dir = Path(__file__).parents[1] / "results"
    res_dir.mkdir(exist_ok=True)
    (res_dir / "pilot_variance.json").write_text(json.dumps(out, indent=1))

    md = f"""# Pilot Variance and Minimum Detectable Effect

Sprint 1 task 4, run {time.strftime('%Y-%m-%d')}. Evidence tag [SIM]. This is the
seed-variance pilot required by PREREGISTRATION v1.1 section 8.3 before any
hardware approval; it is not the G0 tuned baseline (Sprint 2).

- Dataset: ULB, stratified 60/20/20, seeds 42-51, G0c preprocessing
  (log-Amount, Time retained, {dup_count} exact duplicates removed).
- Fixed pilot XGBoost (untuned, documented in pilot_variance.py).
- Test AUPRC per seed: {', '.join(f'{a:.4f}' for a in aps)}
- Mean {aps_arr.mean():.4f}, across-seed SD {sd:.4f}.
- **Minimum detectable across-seed mean delta-AP (10 seeds, alpha 0.05,
  power 0.80): {mde10:.4f}.** Observed H1b margins below this value are
  reported as indistinguishable, not as wins, per the frozen protocol.
"""
    (Path(__file__).parents[1] / "PILOT_VARIANCE.md").write_text(md)
    print(f"mean {aps_arr.mean():.4f}  sd {sd:.4f}  MDE(10) {mde10:.4f}")
    print("PILOT COMPLETE")


if __name__ == "__main__":
    main()
