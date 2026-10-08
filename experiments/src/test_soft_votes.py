"""F20's soft-vote matrix is the hard-vote matrix with confidence restored.

Sprint 22 Task E. The soft vote must use the SAME learner on the SAME feature
subset as the hard vote, or the comparison measures a different pool rather
than the vote. These guards pin that on a small synthetic pool: zero metered,
no dataset needed.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "src"))
sys.path.insert(0, str(ROOT / "experiments" / "phase2" / "src"))

import qubo_proxy as qp          # noqa: E402
import soft_votes as sv          # noqa: E402


@pytest.fixture(scope="module")
def pool():
    rng = np.random.default_rng(7)
    X = rng.normal(size=(400, 5)).astype("float32")
    y = np.where(X[:, 0] + 0.5 * X[:, 1] * X[:, 2] + rng.normal(0, 0.5, 400) > 0,
                 1, -1)
    clf = qp.build_pool(X, y, 2, weak_type="dct", pair_build="sequential",
                        lambda_coef=800.0)
    return clf, X


def test_soft_and_hard_matrices_have_the_same_shape(pool):
    clf, X = pool
    assert sv.soft_h_matrix(clf, X).shape == qp.h_matrix(clf, X).shape


def test_soft_votes_lie_in_minus_one_to_one(pool):
    clf, X = pool
    S = sv.soft_h_matrix(clf, X)
    assert S.min() >= -1.0 - 1e-12 and S.max() <= 1.0 + 1e-12


def test_soft_votes_agree_in_sign_with_the_hard_votes(pool):
    """The hard vote is the argmax of the same probability, so wherever the
    soft vote is not exactly zero its sign must equal the hard vote. A soft
    matrix built from a DIFFERENT learner or feature slice would fail this."""
    clf, X = pool
    S = sv.soft_h_matrix(clf, X)
    H = qp.h_matrix(clf, X)
    nonzero = np.abs(S) > 1e-9
    assert np.array_equal(np.sign(S[nonzero]), H[nonzero])


def test_soft_votes_carry_more_than_the_sign(pool):
    """If every soft vote were exactly +/-1 the arm would be the hard arm
    under another name, and the comparison would be vacuous."""
    clf, X = pool
    S = sv.soft_h_matrix(clf, X)
    assert np.mean((np.abs(S) > 1e-9) & (np.abs(S) < 1 - 1e-9)) > 0.0


def test_raw_predict_proba_is_degenerate_on_the_frozen_pool(pool):
    """The finding behind the Laplace default, kept measurable: unlimited-
    depth trees have pure leaves, so raw predict_proba is exactly 0 or 1 and
    the 'soft' vote equals the hard vote. This guard caught that on its first
    run. If a future library or config change makes leaves impure, this test
    fails and the Laplace choice should be revisited."""
    clf, X = pool
    S = sv.soft_h_matrix(clf, X, mode="proba")
    assert np.mean(np.abs(S) < 1 - 1e-9) == 0.0


def test_laplace_votes_shrink_with_leaf_size(pool):
    """A leaf decided by one row is a weaker signal than a large leaf: the
    smallest |vote| must be the one-row value, 2*(2/3)-1 = 1/3."""
    clf, X = pool
    S = sv.soft_h_matrix(clf, X)
    assert np.isclose(np.abs(S).min(), 1.0 / 3.0, atol=1e-9)


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


@pytest.mark.parametrize("part", ["soft", "ensemble", "classical",
                                  "ensemble-emulated"])
def test_every_part_writes_only_its_own_output(part, tmp_path, monkeypatch):
    """BEHAVIOR, not source text (PR #159 review: the source check flagged a
    write only when `.write_text(` and `results.json` shared a line, and
    every write here goes through a variable). The real `main()` runs with
    the expensive fits stubbed and OUT_DIR pointed at a scratch directory:
    exactly one file may appear there, and no evidence file may change."""
    stub = {"rows": [], "summary": {"stub": True}}
    monkeypatch.setattr(sv, "run_soft", lambda heartbeat: stub)
    for name in ("run_ensemble", "run_classical", "run_ensemble_emulated"):
        monkeypatch.setattr(sv, name, lambda: stub)
    monkeypatch.setattr(sv, "OUT_DIR", tmp_path)
    monkeypatch.setattr(sys, "argv", ["soft_votes.py", part])
    before = _evidence_snapshot()
    assert sv.main() == 0
    assert len(list(tmp_path.iterdir())) == 1
    assert _evidence_snapshot() == before
