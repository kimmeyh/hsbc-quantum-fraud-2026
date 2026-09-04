"""A7 exploratory: small-lambda proxy sweep (zero metered). Selected dct config, seed 42."""
import sys, json
sys.path.insert(0, "/mnt/d/Data/Harold/github/hsbc-quantum-fraud-2026/experiments/src")
import numpy as np, metrics, qubo_proxy as qp
split, cols, Xtr, Xva, Xte, y = qp._prep(42, 13)
clf = qp.build_pool(Xtr, y, 2, "dct", "full", weak_params={}, lambda_coef=1.0)
H_tr, H_va = qp.h_matrix(clf, Xtr), qp.h_matrix(clf, Xva)
n = len(y)
print(f"pool={len(clf.h_list)} n_train={n}  (ridge term = alpha*n_train; diag(HH^T)={float((H_tr[0]@H_tr[0])):.0f})")
out = []
for a in (0.0, 0.001, 0.01, 0.1, 0.5, 1.0, 2.0, 4.0):
    w = qp.solve_simplex_qp(H_tr, y, a * n)
    s = np.clip((w @ H_va + 1) / 2, 0, 1)
    ap = float(metrics.average_precision_score(split.y_val.to_numpy(), s))
    h = metrics.score_health(s)
    nz = int((w > 1e-6).sum()); top = float(np.sort(w)[::-1][:1].sum())
    out.append(dict(alpha=a, val_ap=ap, warn=h["warn"], mode=h["mode_share"], distinct=h["n_distinct"], active=nz, max_w=top))
    print(f"alpha={a:<6} val_AP={ap:.4f} warn={h['warn']!s:<5} mode={h['mode_share']:.3f} distinct={h['n_distinct']:<6} active_w={nz:<3} max_w={top:.4f}")
json.dump(out, open("/mnt/d/Data/Harold/github/hsbc-quantum-fraud-2026/experiments/results/lambda_sweep.json","w"), indent=1)
