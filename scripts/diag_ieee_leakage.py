"""Diagnose the IEEE-CIS scale-check number: is 0.861 time leakage?

Our preregistration records the leakage-free reproduction band as 0.64-0.67,
so 0.861 demands an explanation before it goes anywhere near the paper.
Hypothesis: TransactionDT (raw timestamp) in the features plus a RANDOM split
lets the model interpolate across time, which is a known leakage path here.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments" / "src"))
import data
from sklearn.metrics import average_precision_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

df = data.load_ieee_cis_train()
y = df["isFraud"].astype(int)
X = df.drop(columns=["isFraud", "TransactionID"])
for c in X.columns:
    if X[c].dtype == object:
        X[c] = X[c].astype("category").cat.codes.astype("int32")
dt = df["TransactionDT"].to_numpy()


def run(Xu, label, temporal=False):
    if temporal:
        order = np.argsort(dt)
        n = len(order)
        tr, te = order[: int(n * 0.8)], order[int(n * 0.8):]
        X_tr, X_te, y_tr, y_te = Xu.iloc[tr], Xu.iloc[te], y.iloc[tr], y.iloc[te]
    else:
        X_tr, X_te, y_tr, y_te = train_test_split(
            Xu, y, test_size=0.2, stratify=y, random_state=42)
    X_a, X_v, y_a, y_v = train_test_split(
        X_tr, y_tr, test_size=0.1, stratify=y_tr, random_state=42)
    m = XGBClassifier(n_estimators=600, early_stopping_rounds=50, eval_metric="aucpr",
                      tree_method="hist", n_jobs=-1, max_depth=8, learning_rate=0.05,
                      subsample=0.8, colsample_bytree=0.8, random_state=42)
    m.fit(X_a, y_a, eval_set=[(X_v, y_v)], verbose=False)
    ap = float(average_precision_score(y_te, m.predict_proba(X_te)[:, 1]))
    print(f"{label}: AUPRC = {ap:.4f}", flush=True)
    return ap


a = run(X, "A. random split, TransactionDT INCLUDED (scale-check setup)")
b = run(X.drop(columns=["TransactionDT"]), "B. random split, TransactionDT REMOVED")
c = run(X.drop(columns=["TransactionDT"]), "C. TEMPORAL split, TransactionDT removed", temporal=True)
print(f"\nleakage attributable to the timestamp feature: {a - b:+.4f}")
print(f"leakage attributable to random (non-temporal) splitting: {b - c:+.4f}")
print(f"prereg leakage-free reproduction band: 0.64 to 0.67")
