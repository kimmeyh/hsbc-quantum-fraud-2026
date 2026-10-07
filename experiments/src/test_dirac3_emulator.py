"""The Dirac-3 emulator (F17): exact mode IS the proxy; emulate mode adds
resolution, sample spread and cost, each anchored to a measurement.

Sprint 22 Task D. Synthetic problems only: zero metered, no dataset.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "src"))
sys.path.insert(0, str(ROOT / "experiments" / "phase2" / "src"))

import qubo_proxy as qp            # noqa: E402
import dirac3_emulator as em       # noqa: E402


class _Model:
    def __init__(self, J, C):
        self._J, self._C = J, C


@pytest.fixture(scope="module")
def problem():
    rng = np.random.default_rng(3)
    H = np.where(rng.random((12, 300)) > 0.5, 1.0, -1.0)
    y = np.where(rng.random(300) > 0.5, 1, -1)
    lam = 600.0
    J = (H @ H.T).astype(np.float64) + lam * np.eye(12)
    C = (-2.0 * H @ y).astype(np.float64)
    return H, y, lam, J, C


def test_exact_mode_returns_the_proxys_answer(problem):
    """The claim that justifies 'it does not replace the proxy, it wraps it':
    exact mode on J, C gives qubo_proxy.solve_simplex_qp's weights."""
    H, y, lam, J, C = problem
    w_proxy = qp.solve_simplex_qp(H, y, lam)
    r = em.Dirac3Emulator("exact").solve(_Model(J, C), num_samples=1)
    w = np.asarray(r["results"]["solutions"][0])
    assert np.allclose(w, w_proxy, atol=1e-8)


def test_emulate_returns_num_samples_distinct_answers_on_the_simplex(problem):
    *_, J, C = problem
    r = em.Dirac3Emulator("emulate", seed=1).solve(_Model(J, C), num_samples=8)
    sols = [np.asarray(s) for s in r["results"]["solutions"]]
    assert len(sols) == 8 and len(r["results"]["energies"]) == 8
    for s in sols:
        assert np.all(s >= -1e-12) and abs(s.sum() - 1.0) < 1e-9
    assert len({tuple(np.round(s, 9)) for s in sols}) > 1, (
        "8 identical samples: the spread the device shows is not emulated")


def test_quantization_drops_what_a31_says_is_unresolvable():
    a = np.array([1000.0, 4.0, 2.0, -999.0])
    q = em.quantize(a, levels=200)          # step = 5.0
    assert q[1] == 5.0 and q[2] == 0.0, (
        "below half a step (2.5) rounds to zero; 4.0 rounds to one step")
    assert q[0] == 1000.0


def test_the_cost_model_lands_within_ten_percent_of_every_measured_block():
    """Fitted, so it must reproduce the blocks it was fitted to -- to the
    precision the data allows.

    The first version demanded each block's measured RANGE and failed at 816
    variables (81.7 s against 84-90). The data contradict a pure size model:
    B4 at 816 variables cost MORE (mean 86.8 s) than B2 at 833 (mean 82.4 s),
    so cost depends on more than variable count -- most likely the problem's
    coefficient structure. The n**2 model is within 7% of every block mean
    (-6.6% at 560, -5.9% at 816, +3.3% at 833); this pins it at 10% rather
    than tuning the model to one block.
    """
    c = em.fit_cost_coefficient()
    for n, measured_mean in ((560, 41.2), (816, 86.8), (833, 82.4)):
        est = em.estimate_cost_s(n, c=c)
        assert abs(est - measured_mean) / measured_mean <= 0.10, (
            f"{n} vars: estimate {est} s vs measured mean {measured_mean} s")
    assert em.estimate_cost_s(91, c=c) == em.COST_FLOOR_S


def test_cost_scales_with_samples_and_relaxation():
    c = 1e-4
    base = em.estimate_cost_s(800, 8, 2, c=c)
    assert em.estimate_cost_s(800, 16, 2, c=c) == pytest.approx(2 * base, abs=0.1)
    assert em.estimate_cost_s(800, 8, 4, c=c) == pytest.approx(3.8 * base, abs=0.1)


def _evidence_snapshot() -> dict[str, str]:
    """Hashes of both evidence directories, by the root guard's own code."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("_guard_snap",
                                                  ROOT / "conftest.py")
    g = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(g)
    files = g._evidence_files()
    assert files, "the evidence listing is empty; nothing would be compared"
    return g._hashes(files)


def test_the_emulator_never_writes_evidence(problem):
    """BEHAVIOR, not source text (PR #159 review: the source check missed
    write_bytes, np.save, json.dump and Path.open). Every public path runs --
    both solve modes, the cost fit that reads results.json, the estimate --
    and neither evidence directory may change."""
    *_, J, C = problem
    before = _evidence_snapshot()
    em.Dirac3Emulator("exact").solve(_Model(J, C), num_samples=1)
    em.Dirac3Emulator("emulate", seed=2).solve(_Model(J, C), num_samples=4)
    em.estimate_cost_s(500, 8, 2, c=em.fit_cost_coefficient())
    assert _evidence_snapshot() == before


def test_sparsity_counts_only_exact_zeros():
    """The device returns exact zeros; a tolerance would blur the pattern the
    F17 acceptance test compares (emulator_sparsity.py)."""
    import emulator_sparsity as es
    s = es.sparsity([0.0, 0.0, 1e-12, 0.5, 0.5])
    assert s["zero_fraction"] == pytest.approx(0.4)
    assert s["nonzero_min"] == pytest.approx(1e-12)
    assert s["nonzero_max"] == pytest.approx(0.5)
    assert es.sparsity([0.0, 0.0])["nonzero_min"] is None
