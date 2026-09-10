"""F42 finding F11: is the lambda=0 optimum unique, or a face of the simplex?

The proposal says "the penalty term is positive, so the optimum is unique" and
separately that "the optimum stays uniform even at zero penalty". The first is
true for lambda > 0. The second overstates: at lambda = 0 the Gram matrix is
rank-one to numerical precision, so the minimiser set is a large face of the
simplex and a solver started at uniform returns uniform by construction.

Two reviewers reached this from opposite directions. GPT-6 Astra MEASURED a
solve at lambda=0 landing L1 0.198 from uniform; Fable 5.1 explained WHY the
minimiser is not unique there. This settles it with a spread rather than a
single solve: many random starts, and we report how far apart they land and how
little the objective distinguishes them.

Reuses the ten committed pools, so no refit: the Gram matrices are already
built. Zero metered seconds -- this is a classical solve throughout [SIM].
"""
from __future__ import annotations

import argparse
import glob
import time
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

import store

RESULTS = Path(__file__).resolve().parents[1] / "results"
POOLS = sorted(glob.glob(str(RESULTS / "pools" / "h_*_free_dct_full.npz")))
OUT = RESULTS / "lambda0_spread.json"

N_STARTS = 20
SEED = 20260909


def _hamiltonian(path: str):
    # Plain numeric arrays; no allow_pickle needed.
    d = np.load(path)
    H = d["H_tr"].astype(float)
    y = np.where(d["y_tr01"] == 1, 1, -1).astype(float)
    # The frozen objective, at lambda = 0: J = H H^T, C = -2 H y.
    return H @ H.T, -2.0 * (H @ y), H.shape[0]


def _solve(J, C, w0):
    obj = lambda w: w @ J @ w + C @ w          # noqa: E731
    r = minimize(obj, w0, method="SLSQP", bounds=[(0.0, 1.0)] * len(w0),
                 constraints=[{"type": "eq", "fun": lambda w: w.sum() - 1.0}],
                 options={"maxiter": 500, "ftol": 1e-12})
    w = np.clip(r.x, 0.0, None)
    s = w.sum()
    w = w / s if s > 0 else np.full_like(w, 1.0 / len(w))
    return w, float(obj(w))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--starts", type=int, default=N_STARTS)
    args = ap.parse_args()

    if not POOLS:
        raise SystemExit(
            "no pools under experiments/results/pools/ (gitignored, so a "
            "fresh clone has none). Build them before regenerating this "
            "evidence -- otherwise numpy raises a bare ValueError from "
            "inside the summary and the prerequisite is invisible.")

    rng = np.random.default_rng(SEED)
    t0 = time.perf_counter()
    per_seed = []

    for path in POOLS:
        J, C, n = _hamiltonian(path)
        uniform = np.full(n, 1.0 / n)
        _, obj_uniform = _solve(J, C, uniform)   # solved FROM uniform

        sols, objs = [], []
        for _ in range(args.starts):
            w, o = _solve(J, C, rng.dirichlet(np.ones(n)))
            sols.append(w)
            objs.append(o)
        S = np.array(sols)

        l1_from_uniform = np.abs(S - uniform).sum(axis=1)
        # Pairwise L1 between random-start solutions: how big is the face?
        pair = [np.abs(S[i] - S[j]).sum()
                for i in range(len(S)) for j in range(i + 1, len(S))]

        per_seed.append({
            "pool": Path(path).stem,
            "n_variables": int(n),
            "starts": int(args.starts),
            "obj_from_uniform": obj_uniform,
            "obj_random_min": float(np.min(objs)),
            "obj_random_max": float(np.max(objs)),
            "obj_relative_spread": float((np.max(objs) - np.min(objs)) / abs(np.mean(objs))),
            "l1_from_uniform_mean": float(l1_from_uniform.mean()),
            "l1_from_uniform_max": float(l1_from_uniform.max()),
            "l1_pairwise_mean": float(np.mean(pair)),
            "l1_pairwise_max": float(np.max(pair)),
        })

    out = {
        "note": ("F42/F11: lambda=0 minimiser set on the frozen pools. Reuses the "
                 "committed Gram matrices; no refit, zero metered seconds."),
        "generator": "experiments/src/run_lambda0_spread.py",
        "evidence_tag": "SIM",
        "lambda": 0.0,
        "starts_per_pool": int(args.starts),
        "rng_seed": SEED,
        "elapsed_sec": round(time.perf_counter() - t0, 2),
        "per_seed": per_seed,
        "summary": {
            "l1_from_uniform_mean": float(np.mean([r["l1_from_uniform_mean"] for r in per_seed])),
            "l1_from_uniform_max": float(np.max([r["l1_from_uniform_max"] for r in per_seed])),
            "l1_pairwise_mean": float(np.mean([r["l1_pairwise_mean"] for r in per_seed])),
            "obj_relative_spread_max": float(np.max([r["obj_relative_spread"] for r in per_seed])),
        },
    }
    store.atomic_write_json(OUT, out)

    s = out["summary"]
    print(f"pools {len(per_seed)}, {args.starts} random starts each, "
          f"{out['elapsed_sec']}s")
    print(f"  L1 from uniform : mean {s['l1_from_uniform_mean']:.4f}  "
          f"max {s['l1_from_uniform_max']:.4f}")
    print(f"  L1 between starts: mean {s['l1_pairwise_mean']:.4f}")
    print(f"  objective relative spread, worst pool: {s['obj_relative_spread_max']:.3e}")
    print(f"written: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
