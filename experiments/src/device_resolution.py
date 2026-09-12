"""What Dirac-3 can actually represent, measured against our own Hamiltonians.

F57. The submission claimed that hardware agreeing with the classical proxy on
the frozen pool "confirms" convexity, and that the agreement "bounds any effect
of Dirac-3's continuous-variable resolution". Both readings are wrong, and the
second is backwards.

QCi's user guide documents an effective analog resolution of about 200:1 (23 dB):
two coupling terms are distinguishable only if their difference exceeds the
largest term divided by 200. On the frozen pool the diagonal is 510,705 while
the off-diagonals span 12.0 -- so every coefficient difference sits roughly two
hundred times BELOW what the device can see. Quantised at that resolution the
problem collapses to a constant off-diagonal plus a constant diagonal, whose
simplex minimiser is exactly uniform.

Hardware returning uniform is therefore FORCED by the device's resolution. It is
not evidence about solver fidelity, and it cannot bound a resolution effect,
because it IS the resolution effect.

The same limit explains B2, which the submission left unexplained. With the sum
constraint at 1, the expected resolution is about 1/200 = 0.005 per weight, while
a diffuse optimum over 833 learners averages 0.0012. Such a vector is not
representable, so the device must return something sparser -- which is what the
retained responses show, and what the 0.83 weight cosine measures. B2's "weak
fidelity" is the device solving a sparsified version of the problem it was given.

That is also the strongest argument for the sparse Phase 2 formulation: a device
that cannot represent diffuse weights over hundreds of learners has a native
problem class, and it is cardinality-constrained selection.

    python experiments/src/device_resolution.py

Zero metered seconds: reads cached pools and retained responses only.
"""
from __future__ import annotations

import glob
import json
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qubo_proxy as qp  # noqa: E402
import store  # noqa: E402

RESULTS = Path(__file__).resolve().parents[1] / "results"
POOLS = RESULTS / "pools"
RESP = POOLS / "hw_responses"
OUT = RESULTS / "device_resolution.json"

# QCi Dirac-3 user guide v0.0.4: the device "struggles to distinguish very small
# coupling terms due to its effective analog resolution limit, which is
# approximately 200:1, or 23 dB"; two couplings are distinguishable only if
# their difference exceeds the maximum term divided by 200.
DYNAMIC_RANGE = 200.0
SUM_CONSTRAINT = 1.0


def _hamiltonian(path: str):
    d = np.load(path)
    H = d["H_tr"].astype(np.float64)
    y = np.where(d["y_tr01"] == 1, 1, -1).astype(np.float64)
    lam = qp.LAMBDA_MULT * len(y)
    J = H @ H.T + lam * np.eye(H.shape[0])
    C = -2.0 * (H @ y)
    return J, C


def _coefficient_spread(J: np.ndarray, C: np.ndarray) -> dict:
    """Can the device tell this problem's coefficients apart at all?"""
    off = J[~np.eye(J.shape[0], dtype=bool)]
    max_term = float(max(abs(J).max(), abs(C).max()))
    resolvable = max_term / DYNAMIC_RANGE
    off_spread = float(off.max() - off.min())
    lin_spread = float(C.max() - C.min())
    return {
        "n_variables": int(J.shape[0]),
        "diagonal": float(J[0, 0]),
        "off_diagonal_min": float(off.min()),
        "off_diagonal_max": float(off.max()),
        "off_diagonal_spread": off_spread,
        "linear_spread": lin_spread,
        "max_abs_coefficient": max_term,
        "resolvable_difference": resolvable,
        "off_diagonal_spread_over_resolvable": off_spread / resolvable,
        "linear_spread_over_resolvable": lin_spread / resolvable,
        "off_diagonal_resolvable": bool(off_spread >= resolvable),
        "linear_resolvable": bool(lin_spread >= resolvable),
    }


def _quantised_minimiser(J: np.ndarray, C: np.ndarray) -> dict:
    """Solve the problem the DEVICE can see, not the one we sent it."""
    n = J.shape[0]
    step = float(max(abs(J).max(), abs(C).max())) / DYNAMIC_RANGE
    Jq = np.round(J / step) * step
    Cq = np.round(C / step) * step
    off_q = Jq[~np.eye(n, dtype=bool)]

    L = float(np.linalg.eigvalsh(Jq)[-1]) * 2.0 + 1e-9
    w = np.full(n, 1.0 / n)
    z, t = w.copy(), 1.0
    for _ in range(20000):
        g = 2.0 * (Jq @ z) + Cq
        w_new = qp._project_simplex(z - g / L)
        t_new = (1.0 + np.sqrt(1.0 + 4.0 * t * t)) / 2.0
        z = w_new + ((t - 1.0) / t_new) * (w_new - w)
        w, t = w_new, t_new
    uniform = np.full(n, 1.0 / n)
    return {
        "distinct_off_diagonal_values_after_quantisation": int(len(np.unique(off_q))),
        "distinct_linear_values_after_quantisation": int(len(np.unique(Cq))),
        "l1_from_uniform": float(np.abs(w - uniform).sum()),
    }


def _observed_sparsity() -> dict:
    """What the device actually returned on the 833-variable block.

    The saved responses are reprs and numpy elides long arrays with "...", so
    the full weight vector is not recoverable. What IS recoverable is the range
    of the values it did print and whether exact zeros appear -- which is the
    qualitative part the resolution argument predicts.
    """
    vals, zeros_seen, n_files = [], 0, 0
    for f in sorted(glob.glob(str(RESP / "hw_b2_full*.json"))):
        text = json.loads(Path(f).read_text(encoding="utf-8"))
        if not isinstance(text, str):
            text = json.dumps(text)
        m = re.search(r"solutions=array\(\[\[(.{0,4000}?)\]\]", text, re.S)
        if not m:
            continue
        n_files += 1
        body = m.group(1)
        if re.search(r"\b0\.\s", body):
            zeros_seen += 1
        nums = [float(x) for x in re.findall(r"0\.\d+", body)]
        vals.extend([x for x in nums if x > 0])
    if not vals:
        return {}
    return {
        "n_responses_parsed": n_files,
        "fits_showing_exact_zeros": zeros_seen,
        "nonzero_weight_min": round(min(vals), 7),
        "nonzero_weight_max": round(max(vals), 7),
        "note": ("Response reprs elide long arrays, so these are the printed "
                 "values rather than the full vectors. Exact zeros appearing at "
                 "all is the qualitative prediction; the printed magnitudes "
                 "sitting below the expected resolution is the quantitative one."),
    }


def main() -> int:
    pools = sorted(glob.glob(str(POOLS / "h_*_free_dct_full.npz")))
    if not pools:
        raise SystemExit(
            f"no cached pools under {POOLS}. They are gitignored (47 MB) and "
            "rebuildable via scripts/wsl_build_pools.sh.")

    per_pool = []
    for path in pools:
        J, C = _hamiltonian(path)
        rec = {"pool": Path(path).stem}
        rec.update(_coefficient_spread(J, C))
        rec.update(_quantised_minimiser(J, C))
        per_pool.append(rec)

    b2_vars = 833
    out = {
        "note": ("Dirac-3 documented 200:1 analog resolution against our own "
                 "Hamiltonians. Establishes that hardware agreement on the "
                 "frozen pool is FORCED rather than informative, and that the "
                 "833-variable block weaker weight agreement is the expected "
                 "consequence of a diffuse optimum below the representable "
                 "resolution."),
        "generator": "experiments/src/device_resolution.py",
        "source": "QCi Dirac-3 User Guide v0.0.4 (200:1, or 23 dB)",
        "evidence_tag": "SIM",
        "dynamic_range": DYNAMIC_RANGE,
        "frozen_pool": {
            "n_pools": len(per_pool),
            "off_diagonal_spread_max": max(r["off_diagonal_spread"] for r in per_pool),
            "resolvable_difference_min": min(r["resolvable_difference"] for r in per_pool),
            "any_coefficient_difference_resolvable": any(
                r["off_diagonal_resolvable"] or r["linear_resolvable"] for r in per_pool),
            "quantised_l1_from_uniform_max": max(
                r["l1_from_uniform"] for r in per_pool),
            "verdict": ("Every coefficient difference is below the resolvable "
                        "difference, so the problem the device can represent is "
                        "a constant off-diagonal plus a constant diagonal, whose "
                        "simplex minimiser is exactly uniform. Hardware agreement "
                        "with the proxy on this pool is forced and carries no "
                        "information about solver fidelity."),
        },
        "diffuse_weight_limit": {
            "sum_constraint": SUM_CONSTRAINT,
            "expected_weight_resolution": SUM_CONSTRAINT / DYNAMIC_RANGE,
            "b2_n_variables": b2_vars,
            "b2_uniform_weight": round(SUM_CONSTRAINT / b2_vars, 7),
            "uniform_weight_below_resolution": bool(
                SUM_CONSTRAINT / b2_vars < SUM_CONSTRAINT / DYNAMIC_RANGE),
            "max_learners_representable_uniformly": int(DYNAMIC_RANGE),
            "verdict": ("A uniform vector over more than about 200 learners has "
                        "per-weight mass below the expected resolution, so the "
                        "device cannot represent it and must return a sparser "
                        "solution. The 0.83 weight cosine is the measured "
                        "consequence, not a solver failure."),
        },
        "b2_observed": _observed_sparsity(),
        "per_pool": per_pool,
    }
    store.atomic_write_json(OUT, out)
    fp = out["frozen_pool"]
    print(f"frozen pool: off-diagonal spread up to {fp['off_diagonal_spread_max']:.1f} "
          f"against a resolvable difference of {fp['resolvable_difference_min']:.0f}")
    print(f"  any difference resolvable? {fp['any_coefficient_difference_resolvable']}")
    print(f"  quantised minimiser L1 from uniform: {fp['quantised_l1_from_uniform_max']:.2e}")
    dw = out["diffuse_weight_limit"]
    print(f"B2: uniform weight {dw['b2_uniform_weight']} vs resolution "
          f"{dw['expected_weight_resolution']} -> "
          f"{'NOT representable' if dw['uniform_weight_below_resolution'] else 'representable'}")
    print(f"written: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
