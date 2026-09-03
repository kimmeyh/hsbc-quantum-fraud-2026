"""Known-answer tests for the CVQBoost proxy solve (ADR-0002, amendment A4)."""
import numpy as np
import pytest

from qubo_proxy import _project_simplex, solve_simplex_qp, build_pool


def test_projection_known_answer():
    # Already on simplex: unchanged.
    w = np.array([0.2, 0.3, 0.5])
    np.testing.assert_allclose(_project_simplex(w), w, atol=1e-12)
    # Single dominant coordinate.
    v = np.array([10.0, 0.0, 0.0])
    np.testing.assert_allclose(_project_simplex(v), [1.0, 0.0, 0.0], atol=1e-12)
    # Result is always a distribution.
    rng = np.random.default_rng(0)
    for _ in range(20):
        p = _project_simplex(rng.normal(size=50) * 10)
        assert abs(p.sum() - 1.0) < 1e-9 and (p >= 0).all()


def test_simplex_qp_matches_slsqp():
    """FISTA solve must match scipy SLSQP on the identical Hamiltonian
    (the F17 feasibility note's precedent solver) to ~1e-6 in objective."""
    from scipy.optimize import minimize

    rng = np.random.default_rng(42)
    n_cls, n_rec = 12, 300
    H = np.where(rng.random((n_cls, n_rec)) > 0.5, 1.0, -1.0).astype(np.float32)
    y = np.where(rng.random(n_rec) > 0.8, 1.0, -1.0)
    lam = 2.0 * n_rec
    J = (H @ H.T).astype(np.float64) + lam * np.eye(n_cls)
    C = -2.0 * H @ y

    obj = lambda w: float(w @ J @ w + C @ w)
    w_fista = solve_simplex_qp(H, y, lam)
    res = minimize(obj, np.full(n_cls, 1 / n_cls), jac=lambda w: 2 * J @ w + C,
                   method="SLSQP", bounds=[(0, None)] * n_cls,
                   constraints=[{"type": "eq", "fun": lambda w: w.sum() - 1.0}],
                   options={"maxiter": 500, "ftol": 1e-12})
    assert abs(w_fista.sum() - 1.0) < 1e-8 and (w_fista >= -1e-12).all()
    assert obj(w_fista) <= res.fun + 1e-6 * (1 + abs(res.fun))


def test_low_n_schedule_guard():
    """F18: schedule>=2 with n<4 must raise a real error, not eqc's empty assert."""
    X = np.random.default_rng(0).random((50, 3)).astype(np.float32)
    y = np.where(np.random.default_rng(1).random(50) > 0.5, 1, -1)
    with pytest.raises(ValueError, match="schedule"):
        build_pool(X, y, schedule=2, weak_type="dct", pair_build="sequential")


def test_pool_count_matches_a2_formula():
    """Sequential pool size must equal data.qubo_vars (amendment A2)."""
    import data

    rng = np.random.default_rng(7)
    X = rng.random((200, 6)).astype(np.float32)
    y = np.where(rng.random(200) > 0.5, 1, -1)
    clf = build_pool(X, y, schedule=2, weak_type="dct", pair_build="sequential")
    assert len(clf.h_list) == data.qubo_vars(6, 2)  # = C(6,2) = 15
