"""Known-answer tests for the mixed-family pool (F31, amendment A11).

The claims these protect are the ones the submission would rest on, so each is
tested against a constructed case with a known answer rather than against the
measured data:

- concatenating per-family H matrices is only valid if the stack shares a train
  fold and preserves the learner axis
- the diversity metric must actually separate a degenerate pool from a diverse
  one, or it cannot support the central claim
- the solver must be indifferent to learner ORDER, since concatenation order is
  an implementation detail with no statistical meaning
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mechanism_controls as mc
import mixed_pool as mp


def test_diversity_separates_degenerate_from_diverse():
    """The metric must distinguish the two regimes, or it proves nothing.

    Degenerate: every learner votes identically -> gram ratio 1.0, zero
    disagreement. Diverse: independent votes -> ratio near 0, disagreement
    near 0.5.
    """
    rng = np.random.default_rng(0)
    rows = 500

    identical = np.repeat(rng.choice([-1.0, 1.0], size=(1, rows)), 20, axis=0)
    dgn = mp.diversity(identical, seed=0)
    assert dgn["gram_ratio"] == pytest.approx(1.0)
    assert dgn["pairwise_disagreement_mean"] == pytest.approx(0.0)
    assert dgn["distinct_learner_rows"] == 1

    independent = rng.choice([-1.0, 1.0], size=(20, rows))
    div = mp.diversity(independent, seed=0)
    assert abs(div["gram_ratio"]) < 0.2
    assert div["pairwise_disagreement_mean"] == pytest.approx(0.5, abs=0.08)
    assert div["distinct_learner_rows"] == 20


def test_gram_ratio_matches_the_frozen_pool_regime():
    """A pool that agrees on 99.999% of rows must report a ratio ~0.99999.

    This is the Sprint 5 finding restated as a test: if the metric did not
    reproduce it, the mixed-pool comparison would be meaningless.
    """
    rng = np.random.default_rng(1)
    rows = 100_000
    base = rng.choice([-1.0, 1.0], size=rows)
    H = np.tile(base, (10, 1))
    for i in range(1, 10):  # flip 0.001% of entries, so agreement is 0.99999
        flip = rng.choice(rows, size=max(1, rows // 100_000), replace=False)
        H[i, flip] *= -1
    d = mp.diversity(H, seed=1)
    assert d["gram_ratio"] > 0.9999
    assert d["pairwise_disagreement_mean"] < 1e-4


def test_solver_is_invariant_to_learner_order():
    """Concatenation order is an implementation detail with no meaning.

    Permuting learners must permute the weights identically and leave the
    objective unchanged.
    """
    rng = np.random.default_rng(2)
    n_learners, rows = 12, 800
    H = rng.choice([-1.0, 1.0], size=(n_learners, rows))
    y = rng.choice([-1.0, 1.0], size=rows)
    lam = 2.0 * rows
    sw = np.ones(rows)

    w = mc.solve_weighted(H, y, lam, sw)
    perm = rng.permutation(n_learners)
    w_perm = mc.solve_weighted(H[perm], y, lam, sw)

    np.testing.assert_allclose(w[perm], w_perm, atol=1e-6)


def test_concatenation_preserves_the_learner_axis():
    """Stacking must add learners, never rows, or J is malformed."""
    rng = np.random.default_rng(3)
    rows = 300
    a = rng.choice([-1.0, 1.0], size=(5, rows))
    b = rng.choice([-1.0, 1.0], size=(7, rows))
    stacked = np.vstack([a, b])

    assert stacked.shape == (12, rows)
    np.testing.assert_array_equal(stacked[:5], a)
    np.testing.assert_array_equal(stacked[5:], b)

    J = stacked @ stacked.T
    assert J.shape == (12, 12)
    assert np.allclose(J, J.T), "J must be symmetric"
    assert np.linalg.eigvalsh(J)[0] > -1e-6, "J must be PSD by construction"


def test_uniform_weights_are_optimal_on_a_degenerate_pool():
    """The Sprint 5 result as a known answer: interchangeable learners leave
    the optimum at uniform, so any 'gain' over uniform is not optimization."""
    rng = np.random.default_rng(4)
    rows = 2_000
    base = rng.choice([-1.0, 1.0], size=rows)
    H = np.tile(base, (15, 1))  # perfectly interchangeable
    y = np.where(rng.random(rows) < 0.2, base, -base)

    w = mc.solve_weighted(H, y, 2.0 * rows, np.ones(rows))
    w_u = np.full(15, 1.0 / 15)
    assert np.abs(w - w_u).sum() < 1e-6

    # and the scores are identical, so AP cannot differ
    np.testing.assert_allclose(w @ H, w_u @ H, atol=1e-9)


def test_families_are_supported_by_the_builder():
    """Guard against a silent typo in FAMILIES: eqc-models raises on unknown
    weak_cls_type, and a mistyped family would otherwise fail deep in a run."""
    supported = {"dct", "nb", "lg", "gp", "knn", "lda", "qda", "lgb", "xgb"}
    assert set(mp.FAMILIES) <= supported
    assert len(mp.FAMILIES) >= 2, "a mixed pool needs at least two families"
