"""Plumbing smoke test on SYNTHETIC data only (produces no preregistered results).
Run: .venv\\Scripts\\python.exe experiments\\src\\smoke_test.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
import pandas as pd
from sklearn.datasets import make_classification

import data as D
import metrics as M
import tune as T


def main() -> None:
    X, y = make_classification(
        n_samples=4000, n_features=12, weights=[0.97], flip_y=0.01, random_state=0
    )
    df = pd.DataFrame(X, columns=[f"V{i}" for i in range(12)])
    df[D.TIME_COL] = np.arange(len(df))
    df[D.LABEL_COL] = y

    s = D.stratified_split(df, seed=42)
    t = D.temporal_split(df)
    assert abs(len(s.X_train) / len(df) - 0.6) < 0.01 and t.protocol == "temporal"
    feats = D.top_k_features(s.X_train, s.y_train, k=5)
    assert len(feats) == 5
    assert D.qubo_vars(17, 3) == 833 and D.qubo_vars(13, 2) == 91

    for arm in ("xgboost", "lightgbm", "catboost", "logistic"):
        study = T.tune(arm, s.X_train, s.y_train, seed=42, n_trials=2)
        print(f"{arm}: best CV AP {study.best_value:.4f} over {len(study.trials)} trials")

    rng = np.random.default_rng(0)
    p_val = rng.random(len(s.y_val))
    p_test = rng.random(len(s.y_test))
    thr = M.tune_threshold(s.y_val.values, p_val)
    ev = M.evaluate(s.y_test.values, p_test, thr)
    ci = M.bootstrap_ci(s.y_test.values, p_test, n_boot=100)
    dci = M.bootstrap_diff_ci(s.y_test.values, p_test, rng.random(len(s.y_test)), n_boot=100)
    assert 0 <= ev["auprc"] <= 1 and len(ci["ci95"]) == 2 and "excludes_zero" in dci
    print("metrics plumbing OK")
    print("SMOKE TEST PASSED")


if __name__ == "__main__":
    main()
