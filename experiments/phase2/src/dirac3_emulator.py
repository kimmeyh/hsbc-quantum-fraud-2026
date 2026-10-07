"""A Dirac-3 emulator: one tool, two modes (F17, Sprint 22 Task D, #163).

The team lead's direction (2026-10-06): build it, and decide whether it
replaces the proxy, extends it, or is one tool with two functions. **One tool
with two modes, and it does not replace the proxy.** `qubo_proxy.py` produced
Phase 1's filed evidence, so it is IMPORTED here, never edited
(`docs/PHASE_SEPARATION.md`).

  exact    The proxy's own algorithm -- FISTA projected gradient on the
           simplex, using `qubo_proxy._project_simplex` unchanged -- applied to
           the model's J and C. One solution. A test pins that it returns the
           same weights as `qubo_proxy.solve_simplex_qp`.

  emulate  What the device does that the proxy does not model, each piece
           anchored to a measurement rather than a guess:
           1. RESOLUTION. Coefficients are resolvable only to about 200:1
              (amendment A31, ~23 dB). J and C are quantized to steps of
              max|coefficient| / LEVELS; anything smaller rounds to zero.
           2. SAMPLES. `num_samples` distinct answers: each solve of the
              quantized problem starts from a different random point on the
              simplex and stops after a fixed iteration budget, so answers
              spread the way the device's 8 samples do.
           3. COST. `max(floor, c * n_vars**2) * num_samples / 8`, times 3.8 at
              relaxation schedule 4. Fitted to every metered CVQBoost fit in
              results.json: a ~4.4 s floor up to 91 variables, then roughly
              quadratic (41.2 s at 560, 86.8 s at 816, 82.4 s at 833, all at 8
              samples). Provenance: FITTED, not measured, for any other size.

It implements the `solve(model, sum_constraint=, relaxation_schedule=,
num_samples=)` interface of `eqc_models`' `Dirac3CloudSolver`, so
`emulated_solver()` swaps it in for the one network object and a real
QBoostClassifier / QSVMClassifier fit runs end to end against it, spending
nothing -- the same seam `eqc_submit.offline_solver` uses for dry runs.
It returns a plain dict, NOT the device's `SolutionResults`, so code that
saves or counts a response must be tested with `offline_solver`, which does
return the real type (PR #159 review).

What it is NOT: a model of the device's physics. It reproduces the
observable behavior this repository has measured (resolution, sample spread,
cost) and is validated against B4's stored device results in
`docs/phase2/F17_EMULATOR.md`.
"""
from __future__ import annotations

import json
from contextlib import contextmanager
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
import sys                                            # noqa: E402
sys.path.insert(0, str(ROOT / "experiments" / "src"))
import qubo_proxy as qp                               # noqa: E402  (Phase 1, read-only)

LEVELS = 200                 # A31: ~200:1 resolvable dynamic range (~23 dB)
# Mean metered seconds (4.44) of the 27 [HW] cvqboost rows in results.json
# with metered_seconds > 0 and n_vars_expected <= 91 (B1 22, G0b 5).
# Corrected in PR #159 review from "26 fits", which no filter reproduces.
COST_FLOOR_S = 4.4
RX4_FACTOR = 3.8             # relaxation 2 -> 4 cost ratio (F18 notes)
MAX_ITER_EXACT = 5000        # qubo_proxy.solve_simplex_qp's default
TOL_EXACT = 1e-10


def fit_cost_coefficient() -> float:
    """c in cost = c * n**2, least squares over the metered fits > 100 vars."""
    rows = json.loads((ROOT / "experiments" / "results" / "results.json")
                      .read_text(encoding="utf-8"))["rows"]
    pts = [(r["n_vars_expected"], float(r["metered_seconds"]))
           for r in rows
           if r.get("evidence_tag") == "HW"
           and str(r.get("arm", "")).startswith("cvqboost")
           and (r.get("metered_seconds") or 0) > 0
           and (r.get("n_vars_expected") or 0) > 100
           and (r.get("hw_config") or {}).get("num_samples", 8) == 8]
    n2 = np.array([n * n for n, _ in pts], dtype=np.float64)
    s = np.array([s for _, s in pts], dtype=np.float64)
    return float((n2 @ s) / (n2 @ n2))


def estimate_cost_s(n_vars: int, num_samples: int = 8,
                    relaxation_schedule: int = 2, c: float | None = None) -> float:
    c = fit_cost_coefficient() if c is None else c
    base = max(COST_FLOOR_S, c * n_vars * n_vars)
    factor = (num_samples / 8.0) * (RX4_FACTOR if relaxation_schedule == 4 else 1.0)
    return round(base * factor, 1)


def quantize(a: np.ndarray, levels: int = LEVELS) -> np.ndarray:
    """Round to steps of max|a| / levels; smaller entries vanish (A31)."""
    a = np.asarray(a, dtype=np.float64)
    m = float(np.max(np.abs(a))) if a.size else 0.0
    if m == 0.0:
        return a.copy()
    step = m / levels
    return np.round(a / step) * step


def _fista(J, C, w0, max_iter, tol):
    """The proxy's algorithm, on J and C directly: minimize w'Jw + C'w on the
    simplex. Mirrors qubo_proxy.solve_simplex_qp line for line; the
    projection IS the proxy's."""
    L = float(np.linalg.eigvalsh(J)[-1]) * 2.0 + 1e-9
    w = w0.copy()
    z, t = w.copy(), 1.0

    def obj(v):
        return float(v @ J @ v + C @ v)

    prev = obj(w)
    for _ in range(max_iter):
        grad = 2.0 * (J @ z) + C
        w_new = qp._project_simplex(z - grad / L)
        t_new = (1.0 + np.sqrt(1.0 + 4.0 * t * t)) / 2.0
        z = w_new + ((t - 1.0) / t_new) * (w_new - w)
        w, t = w_new, t_new
        cur = obj(w)
        if abs(prev - cur) <= tol * (1.0 + abs(prev)):
            break
        prev = cur
    return w, obj(w)


class Dirac3Emulator:
    """Drop-in for eqc_models' Dirac3CloudSolver: connect() and solve()."""

    def __init__(self, mode: str = "emulate", iters: int = 200,
                 seed: int = 0, levels: int = LEVELS):
        assert mode in ("exact", "emulate"), mode
        self.mode, self.iters, self.seed, self.levels = mode, iters, seed, levels
        self.last_cost_estimate_s: float | None = None

    def connect(self, *args, **kwargs):
        return None

    def solve(self, model, sum_constraint: float = 1.0,
              relaxation_schedule: int = 2, num_samples: int = 1, **kw):
        J = np.asarray(model._J, dtype=np.float64)
        C = np.asarray(model._C, dtype=np.float64).reshape(-1)
        n = C.shape[0]
        assert J.shape == (n, n), f"J {J.shape} vs C {n}"
        assert abs(sum_constraint - 1.0) < 1e-12, (
            "only the unit simplex is emulated (every block here uses 1.0)")
        self.last_cost_estimate_s = estimate_cost_s(
            n, num_samples, relaxation_schedule)

        if self.mode == "exact":
            w, e = _fista(J, C, np.full(n, 1.0 / n), MAX_ITER_EXACT, TOL_EXACT)
            sols, energies = [w], [e]
        else:
            Jq, Cq = quantize(J, self.levels), quantize(C, self.levels)
            rng = np.random.default_rng(self.seed)
            sols, energies = [], []
            for _ in range(int(num_samples)):
                w0 = rng.dirichlet(np.ones(n))
                w, _e = _fista(Jq, Cq, w0, self.iters, 0.0)
                sols.append(w)
                # Energy reported on the TRUE problem, as the device's
                # response reports it for the answer it returns.
                energies.append(float(w @ J @ w + C @ w))
        return {"results": {"energies": energies,
                            "solutions": [list(map(float, s)) for s in sols]},
                "emulated": {"mode": self.mode, "levels": self.levels,
                             "iters": self.iters,
                             "cost_estimate_s": self.last_cost_estimate_s}}


@contextmanager
def emulated_solver(mode: str = "emulate", **kwargs):
    """Swap the emulator in for the ONE network object, like
    eqc_submit.offline_solver: every other line of a real fit runs."""
    import eqc_models.ml.classifierbase as cb

    real = cb.Dirac3CloudSolver
    cb.Dirac3CloudSolver = lambda *a, **k: Dirac3Emulator(mode, **kwargs)
    try:
        yield
    finally:
        cb.Dirac3CloudSolver = real
