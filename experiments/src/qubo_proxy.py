"""CVQBoost proxy pipeline (ADR-0002; PREREGISTRATION 4/6; amendments A2/A3/A4).

Builds weak pools via eqc-models' OWN builders (pool identity with hardware,
required by G0b and H4), replicates the exact Dirac Hamiltonian read from
eqc-models 0.21.0 source (J = H H^T + lambda*I, C = -2 H y, sum_constraint=1.0,
w >= 0), and solves it classically with accelerated projected gradient on the
simplex. F18 invariants enforced: {-1,+1} label mapping, explicit sequential
strategy, constructed-attribute round-trip assert, n<4 schedule guard.

KNOWN FAILURE MODES / LONG-RUN NOTES:
- Full-config pools (top-17, schedule 3, 816 classifiers) take minutes per seed
  to build; free-tier pools (78) take seconds. Rows checkpoint like run_classical.
- The full-pair build (amendment A3) requires fork: run `build` inside WSL with
  --pair-build full; the saved .npz is then solved on Windows with `solve`.
- eqc-models prints solver/build chatter to stdout; harmless.

Usage:
  python experiments/src/qubo_proxy.py run --config free --weak-type dct
  python experiments/src/qubo_proxy.py run --config free --weak-type lg --seeds 42
  python experiments/src/qubo_proxy.py build --seed 42 --config free --weak-type dct \
      --pair-build full --out experiments/results/pools/h_42_free_dct_full.npz   # WSL
  python experiments/src/qubo_proxy.py solve --npz <path>                        # Windows
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import data
import store

log = logging.getLogger("frd.proxy")
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(name)s %(levelname)s %(message)s")

RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"
RESULTS = RESULTS_DIR / "results.json"
POOLS_DIR = RESULTS_DIR / "pools"

SEEDS = tuple(range(42, 52))
CONFIGS = {
    # frozen starting configs (prereg 4; A2-corrected variable counts)
    "free": {"k": 13, "schedule": 2},   # 78 vars sequential / 91 full-pair
    "full": {"k": 17, "schedule": 3},   # 816 vars sequential / 833 full-pair
}
FIXED = {"relaxation_schedule": 2, "num_samples": 8}   # frozen, not tuned
LAMBDA_MULT = 2.0                                      # lambda_coef = 2 * n_train


# ---------------------------------------------------------------- pool build

def build_pool(X_tr: np.ndarray, y_pm1: np.ndarray, schedule: int,
               weak_type: str, pair_build: str,
               weak_params: dict | None = None,
               lambda_coef: float | None = None):
    """Build the weak pool with eqc-models' own builder; return the classifier.
    F18: attribute round-trip assert; n<4 guard; explicit strategy.
    weak_params / lambda_coef default to the frozen starting config; the
    section-6 tuning (F22) passes explicit values."""
    from eqc_models.ml.classifierqboost import QBoostClassifier

    n = X_tr.shape[1]
    if schedule >= 2 and n < 4:
        raise ValueError(f"schedule {schedule} impossible for n={n} features "
                         "(pair cap n(n-3)/2 <= 0); use schedule 1")
    strategy = "multi_processing" if pair_build == "full" else "sequential"
    cfg = dict(lambda_coef=(LAMBDA_MULT * len(y_pm1) if lambda_coef is None
                            else lambda_coef),
               weak_cls_schedule=schedule, weak_cls_type=weak_type,
               weak_cls_params=dict(weak_params or {}),
               weak_cls_strategy=strategy, **FIXED)
    clf = QBoostClassifier(**cfg)
    for k, v in cfg.items():   # F18 invariant: silent-kwarg-drop guard
        assert getattr(clf, k) == v, f"constructed attr mismatch: {k}"
    if pair_build == "full":
        clf._build_weak_classifiers_mp(X_tr, y_pm1)
    else:
        clf._build_weak_classifiers_sq(X_tr, y_pm1)
    return clf


def h_matrix(clf, X: np.ndarray) -> np.ndarray:
    from eqc_models.ml.classifierqboost import _compute_h_matrix
    return _compute_h_matrix(clf.h_list, clf.ind_list, X)


# ------------------------------------------------------------- simplex solve

def _project_simplex(v: np.ndarray) -> np.ndarray:
    """Euclidean projection onto {w >= 0, sum w = 1} (Duchi et al. 2008)."""
    u = np.sort(v)[::-1]
    css = np.cumsum(u)
    rho = np.nonzero(u * np.arange(1, len(v) + 1) > (css - 1))[0][-1]
    theta = (css[rho] - 1.0) / (rho + 1.0)
    return np.maximum(v - theta, 0.0)


def solve_simplex_qp(H: np.ndarray, y: np.ndarray, lam: float,
                     max_iter: int = 5000, tol: float = 1e-10) -> np.ndarray:
    """Minimize w'Jw + C'w with J = HH^T + lam*I, C = -2Hy, on the simplex --
    the identical Hamiltonian eqc-models ships to Dirac-3, solved classically
    by accelerated projected gradient (FISTA)."""
    J = (H @ H.T).astype(np.float64) + lam * np.eye(H.shape[0])
    C = (-2.0 * H @ y).astype(np.float64)
    L = float(np.linalg.eigvalsh(J)[-1]) * 2.0 + 1e-9   # Lipschitz of grad
    w = np.full(H.shape[0], 1.0 / H.shape[0])
    z, t = w.copy(), 1.0
    obj = lambda w_: float(w_ @ J @ w_ + C @ w_)
    prev = obj(w)
    for _ in range(max_iter):
        grad = 2.0 * (J @ z) + C
        w_new = _project_simplex(z - grad / L)
        t_new = (1.0 + np.sqrt(1.0 + 4.0 * t * t)) / 2.0
        z = w_new + ((t - 1.0) / t_new) * (w_new - w)
        w, t = w_new, t_new
        cur = obj(w)
        if abs(prev - cur) <= tol * (1.0 + abs(prev)):
            break
        prev = cur
    return w


# ------------------------------------------------------------------ pipeline

def _done_keys() -> set:
    if not RESULTS.exists():
        return set()
    return {(r["arm"], r.get("config"), r.get("pool_variant"),
             r.get("pair_build"), r["seed"])
            for r in json.loads(RESULTS.read_text())["rows"]}


def _prep(seed: int, k: int):
    df = data.load_ulb().drop_duplicates().reset_index(drop=True)
    split = data.stratified_split(df, seed)
    cols = data.top_k_features(split.X_train, split.y_train, k, seed=seed)
    Xtr = split.X_train[cols].to_numpy(np.float32)
    Xva = split.X_val[cols].to_numpy(np.float32)
    Xte = split.X_test[cols].to_numpy(np.float32)
    y_pm1 = np.where(split.y_train.to_numpy() == 1, 1, -1)
    return split, cols, Xtr, Xva, Xte, y_pm1


def _score_and_row(w, H_va, H_te, split, cols, config, weak_type, pair_build,
                   seed, n_pool, t0):
    import metrics
    # Raw ensemble scores are exactly in [-1, 1] (simplex weights, +/-1 outputs);
    # (s+1)/2 is a monotone affine map to [0, 1] (AP/AUC invariant) so the
    # calibration block gets valid pseudo-probabilities.
    p_val = np.clip((w @ H_va + 1.0) / 2.0, 0.0, 1.0)
    p_test = np.clip((w @ H_te + 1.0) / 2.0, 0.0, 1.0)
    m = metrics.summarize(split.y_test.to_numpy(), split.y_val.to_numpy(),
                          p_val, p_test, seed=seed)
    cfg_hash = store.config_hash(
        {"config": config, "weak_type": weak_type, "pair_build": pair_build,
         "fixed": FIXED, "lambda_mult": LAMBDA_MULT, "cfg": CONFIGS[config]})
    pred_file = store.save_predictions(cfg_hash, seed, "stratified",
                                       split.y_val.to_numpy(), p_val,
                                       split.y_test.to_numpy(), p_test,
                                       arm="cvqboost_proxy")
    row = {
        "arm": "cvqboost_proxy",
        "dataset": "ulb", "protocol": "stratified", "seed": seed,
        "config": config, "pool_variant": weak_type, "pair_build": pair_build,
        "n_weak_classifiers": int(n_pool),
        "config_hash": cfg_hash,
        "predictions_file": pred_file,
        "features_used": cols,
        "metrics": m,
        "val_auprc": float(metrics.average_precision_score(
            split.y_val.to_numpy(), p_val)),
        "evidence_tag": "SIM",
        "metered_seconds": 0, "retry_count": 0,
        "timestamps": {"started": t0,
                       "finished": time.strftime("%Y-%m-%dT%H:%M:%S")},
    }
    store.append_row(row)
    log.info("[PROXY] %s/%s/%s seed=%d pool=%d test_ap=%.4f val_ap=%.4f",
             config, weak_type, pair_build, seed, n_pool,
             m["auprc"], row["val_auprc"])


def cmd_run(args) -> None:
    """Sequential-build proxy rows, checkpointed (Windows path)."""
    done = _done_keys()
    seeds = args.seeds or SEEDS
    for seed in seeds:
        key = ("cvqboost_proxy", args.config, args.weak_type, "sequential", seed)
        if key in done:
            log.info("[PROXY] %s exists, skipping", key)
            continue
        t0 = time.strftime("%Y-%m-%dT%H:%M:%S")
        split, cols, Xtr, Xva, Xte, y_pm1 = _prep(seed, CONFIGS[args.config]["k"])
        clf = build_pool(Xtr, y_pm1, CONFIGS[args.config]["schedule"],
                         args.weak_type, "sequential")
        H_tr, H_va, H_te = (h_matrix(clf, X) for X in (Xtr, Xva, Xte))
        w = solve_simplex_qp(H_tr, y_pm1, LAMBDA_MULT * len(y_pm1))
        _score_and_row(w, H_va, H_te, split, cols, args.config, args.weak_type,
                       "sequential", seed, len(clf.h_list), t0)


def cmd_build(args) -> None:
    """Build one pool and save H matrices (runs on either platform; the
    full-pair build only works where fork exists, i.e. WSL/Linux)."""
    t0 = time.strftime("%Y-%m-%dT%H:%M:%S")
    split, cols, Xtr, Xva, Xte, y_pm1 = _prep(args.seed, CONFIGS[args.config]["k"])
    clf = build_pool(Xtr, y_pm1, CONFIGS[args.config]["schedule"],
                     args.weak_type, args.pair_build)
    H_tr, H_va, H_te = (h_matrix(clf, X) for X in (Xtr, Xva, Xte))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out, H_tr=H_tr, H_va=H_va, H_te=H_te,
                        y_tr01=split.y_train.to_numpy(),
                        y_va=split.y_val.to_numpy(),
                        y_te=split.y_test.to_numpy())
    meta = {"seed": args.seed, "config": args.config, "weak_type": args.weak_type,
            "pair_build": args.pair_build, "features": cols,
            "n_pool": len(clf.h_list), "started": t0,
            "finished": time.strftime("%Y-%m-%dT%H:%M:%S")}
    out.with_suffix(".meta.json").write_text(json.dumps(meta, indent=1))
    log.info("[BUILD] %s: pool=%d -> %s", meta, len(clf.h_list), out)


def cmd_solve(args) -> None:
    """Solve a saved pool npz and append its row (Windows path for WSL builds)."""
    npz = np.load(args.npz)
    meta = json.loads(Path(args.npz).with_suffix(".meta.json").read_text())
    key = ("cvqboost_proxy", meta["config"], meta["weak_type"],
           meta["pair_build"], meta["seed"])
    if key in _done_keys():
        log.info("[PROXY] %s exists, skipping", key)
        return
    t0 = time.strftime("%Y-%m-%dT%H:%M:%S")
    split, cols, *_ = _prep(meta["seed"], CONFIGS[meta["config"]]["k"])
    assert cols == meta["features"], "feature mismatch vs saved pool"
    y_pm1 = np.where(npz["y_tr01"] == 1, 1, -1)
    w = solve_simplex_qp(npz["H_tr"], y_pm1, LAMBDA_MULT * len(y_pm1))
    _score_and_row(w, npz["H_va"], npz["H_te"], split, cols, meta["config"],
                   meta["weak_type"], meta["pair_build"], meta["seed"],
                   meta["n_pool"], t0)


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_run = sub.add_parser("run")
    p_run.add_argument("--config", choices=list(CONFIGS), required=True)
    p_run.add_argument("--weak-type", default="dct")
    p_run.add_argument("--seeds", type=int, nargs="*", default=None)
    p_build = sub.add_parser("build")
    p_build.add_argument("--seed", type=int, required=True)
    p_build.add_argument("--config", choices=list(CONFIGS), required=True)
    p_build.add_argument("--weak-type", default="dct")
    p_build.add_argument("--pair-build", choices=["sequential", "full"],
                         default="sequential")
    p_build.add_argument("--out", required=True)
    p_solve = sub.add_parser("solve")
    p_solve.add_argument("--npz", required=True)
    args = ap.parse_args()
    {"run": cmd_run, "build": cmd_build, "solve": cmd_solve}[args.cmd](args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
