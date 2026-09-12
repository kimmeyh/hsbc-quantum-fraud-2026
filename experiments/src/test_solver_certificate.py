"""The classical comparator must certify its SOLUTION, not just its objective.

F49. `solve_weighted` used a relative-objective stopping test at 1e-10. The
frozen objective is nearly flat near its optimum, so that test fired while the
weights were still moving: the measured KKT residual was 4.6e-05 relative, and
every proxy-derived weight figure inherited it. Our own recomputation
reproduced the published +0.0022 exactly, because the figure and the error came
from the same under-converged solver -- which is why no existing test could see
it. It took an external reviewer solving the same problems independently.

These tests pin the certificate so the defect cannot return silently.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mechanism_controls as mcx  # noqa: E402
import qubo_proxy as qp  # noqa: E402

POOLS = Path(__file__).resolve().parents[1] / "results" / "pools"
ART = Path(__file__).resolve().parents[1] / "results" / "mechanism_controls.json"


def _pool(seed: int = 42):
    f = POOLS / f"h_{seed}_free_dct_full.npz"
    if not f.exists():
        pytest.skip("cached pools not present")
    d = np.load(f)
    H = d["H_tr"].astype(np.float64)
    y = np.where(d["y_tr01"] == 1, 1, -1).astype(np.float64)
    return H, y


def test_solver_returns_a_certified_solution():
    """The whole point of the card: the residual must actually be small."""
    H, y = _pool()
    w, res = mcx.solve_weighted(H, y, qp.LAMBDA_MULT * len(y),
                                np.ones(len(y)), return_residual=True)
    assert res <= mcx.KKT_RTOL, f"KKT residual {res:.3e} exceeds {mcx.KKT_RTOL:.0e}"
    assert w.min() >= -1e-12 and abs(w.sum() - 1.0) < 1e-9, "not on the simplex"


def test_the_old_stopping_rule_would_fail_this_bar():
    """Guards the REGRESSION, not just the fix.

    Reproduces the previous rule -- stop when the relative objective change is
    below 1e-10 -- and asserts its residual is orders of magnitude worse. If
    someone reinstates an objective-based test, this fails.

    This test IS the injection: it runs the defective stopping rule directly and
    measures that it fails the bar, rather than trusting that it would.
    """
    H, y = _pool()
    lam = qp.LAMBDA_MULT * len(y)
    J = (H @ H.T) + lam * np.eye(H.shape[0])
    C = -2.0 * (H @ y)
    L = float(np.linalg.eigvalsh(J)[-1]) * 2.0 + 1e-9
    w = np.full(H.shape[0], 1.0 / H.shape[0])
    z, t = w.copy(), 1.0
    obj = lambda v: float(v @ J @ v + C @ v)   # noqa: E731
    prev = obj(w)
    for _ in range(5000):
        g = 2.0 * (J @ z) + C
        w_new = qp._project_simplex(z - g / L)
        t_new = (1.0 + np.sqrt(1.0 + 4.0 * t * t)) / 2.0
        z = w_new + ((t - 1.0) / t_new) * (w_new - w)
        w, t = w_new, t_new
        cur = obj(w)
        if abs(prev - cur) <= 1e-10 * (1.0 + abs(prev)):
            break
        prev = cur
    old_res = mcx.kkt_residual(w, J, C)
    assert old_res > 1e-6, (
        f"the old objective-based rule now yields residual {old_res:.3e}; if that "
        f"is genuinely small this test's premise is stale, but check before relaxing")


def test_kkt_residual_detects_a_deliberately_bad_point():
    """A certificate that passes everything certifies nothing.

    This test IS the injection: it hands the residual a simplex vertex far from
    the optimum and requires it to be rejected, proving the certificate can fail.
    """
    H, y = _pool()
    lam = qp.LAMBDA_MULT * len(y)
    J = (H @ H.T) + lam * np.eye(H.shape[0])
    C = -2.0 * (H @ y)
    bad = np.zeros(H.shape[0])
    bad[0] = 1.0                       # a simplex vertex, far from the optimum
    assert mcx.kkt_residual(bad, J, C) > mcx.KKT_RTOL * 1e3


def test_the_artifact_ships_its_certificate():
    """A weight figure is only as good as the optimality of its solve, so the
    residual must travel with the number rather than live in a commit message."""
    import json
    if not ART.exists():
        pytest.skip("controls artifact not generated")
    ws = json.loads(ART.read_text(encoding="utf-8"))["weight_stats"]
    assert ws, "no weight stats recorded"
    for w in ws:
        assert "kkt_residual" in w, f"seed {w.get('seed')} ships no certificate"
        assert w["kkt_residual"] <= w["kkt_tolerance"]


def test_the_frozen_gain_stays_inside_the_tie_ambiguity():
    """The mechanism claim, restated as a bound rather than a rounding trick.

    The published argument was that rounding the solved scores to six decimals
    returns the uniform value. At the certified optimum the weight perturbation
    is ~25x larger and six decimals no longer collapses it, so that particular
    demonstration is gone. The claim it supported survives in a stronger form:
    the gain sits inside the range attainable by reordering WITHIN the uniform
    arm's tied block, so it is tie-breaking rather than signal.
    """
    import json
    import statistics as st
    if not ART.exists():
        pytest.skip("controls artifact not generated")
    d = json.loads(ART.read_text(encoding="utf-8"))
    gain = d["controls"]["frozen"]["mean"] - d["controls"]["uniform"]["mean"]
    span = st.mean(w["uniform_tie_ambiguity"]["span"] for w in d["weight_stats"])
    assert 0 < gain < span, (
        f"frozen-minus-uniform {gain:+.6f} is no longer inside the tie ambiguity "
        f"{span:.6f}; the 'optimization contributes nothing' claim must be revisited")
