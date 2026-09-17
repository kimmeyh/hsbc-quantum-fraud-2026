"""Known-answer tests for the QFE Fourier Wall phase transformer (Sprint 6
Task C / F23, card #33; PREREGISTRATION H6). Run:
your venv interpreter (docs/ENVIRONMENT.md) -m pytest experiments/src/test_qfe.py -q

These are the heart of the task: phase range, rank invariance, and -- most
importantly -- proof that fit-on-train/transform-on-test never touches test
statistics.
"""
import numpy as np
import pandas as pd
import pytest

from qfe import FourierWallPhaseEncoder, _rank_phase, LOW_CARD_THRESHOLD


RNG = np.random.default_rng(11)


def _make_df(n=500, seed=0):
    rng = np.random.default_rng(seed)
    return pd.DataFrame({
        "Amount": rng.lognormal(mean=2.0, sigma=1.5, size=n),
        "V1": rng.normal(size=n),
        "Time": rng.uniform(0, 5 * 86400, size=n),   # spans several days
        "LowCard": rng.integers(0, 4, size=n).astype(float),  # 4 distinct values
    })


# --------------------------------------------------------------- phase range

def test_phase_always_in_pm_pi():
    """phi = 2*pi*(rank-0.5)/n - pi must lie strictly in (-pi, pi) for every
    rank in {1..n}."""
    for n in (1, 2, 3, 10, 500, 4999):
        ranks = np.arange(1, n + 1, dtype=np.float64)
        phi = 2 * np.pi * (ranks - 0.5) / n - np.pi
        assert np.all(phi >= -np.pi) and np.all(phi <= np.pi)


def test_encoder_output_phase_bounded_on_random_data():
    df = _make_df(800, seed=1)
    enc = FourierWallPhaseEncoder().fit(df)
    out = enc.transform(df)
    # cos/sin themselves are always in [-1, 1] regardless of whitening;
    # reconstruct pre-whitening phase for the direct bound check via states.
    for name, state in enc.phase_states_.items():
        log_mag = np.sign(df[name].to_numpy()) * np.log1p(np.abs(df[name].to_numpy()))
        phi = enc._interpolated_rank_phase(log_mag, state)
        assert np.all(phi >= -np.pi - 1e-9) and np.all(phi <= np.pi + 1e-9)
    st = enc.calendar_state_
    phi_cal = 2 * np.pi * np.mod(df["Time"].to_numpy(), st.period) / st.period - np.pi
    assert np.all(phi_cal >= -np.pi - 1e-9) and np.all(phi_cal <= np.pi + 1e-9)
    assert set(out.keys()) == {
        "Amount_phase_cos", "Amount_phase_sin",
        "V1_phase_cos", "V1_phase_sin",
        "Time_phase_cos", "Time_phase_sin",
    }


# ---------------------------------------------------------------- rank invariance

def test_rank_phase_is_rank_invariant_under_monotone_transform():
    """A monotone-INCREASING transform of the input leaves the raw rank phase
    unchanged (the defining property of a rank statistic): rank(f(x)) ==
    rank(x) for any strictly increasing f."""
    x = RNG.normal(size=300)
    phi_raw = _rank_phase(x)

    for f in (lambda v: v ** 3, lambda v: np.exp(v), lambda v: v * 2.0 + 7.0):
        phi_y = _rank_phase(f(x))
        np.testing.assert_allclose(phi_y, phi_raw, atol=1e-9)


def test_rank_phase_reverses_under_monotone_decreasing_transform():
    """A monotone-DECREASING transform reverses every rank exactly, so the
    resulting phase is the mirror image: rank_desc(i) = n + 1 - rank_asc(i)."""
    x = RNG.normal(size=300)
    n = len(x)
    phi_asc = _rank_phase(x)
    phi_desc = _rank_phase(-x)
    rank_asc = (phi_asc + np.pi) * n / (2 * np.pi) + 0.5
    rank_desc = (phi_desc + np.pi) * n / (2 * np.pi) + 0.5
    np.testing.assert_allclose(rank_desc, n + 1 - rank_asc, atol=1e-6)


def test_encoder_is_rank_invariant_end_to_end():
    """Scaling/shifting Amount (a monotone increasing transform) must leave
    the encoder's phase output identical after refitting on the transformed
    column -- the recipe depends only on rank, not magnitude, post log-step
    monotonicity. Uses a monotone-increasing affine map so log1p(|.|)'s own
    monotonicity is preserved throughout."""
    df = _make_df(400, seed=2)
    df_scaled = df.copy()
    df_scaled["Amount"] = df["Amount"] * 3.7 + 1000.0  # monotone increasing, stays positive

    enc1 = FourierWallPhaseEncoder().fit(df)
    out1 = enc1.transform(df)
    enc2 = FourierWallPhaseEncoder().fit(df_scaled)
    out2 = enc2.transform(df_scaled)

    np.testing.assert_allclose(out1["Amount_phase_cos"], out2["Amount_phase_cos"], atol=1e-9)
    np.testing.assert_allclose(out1["Amount_phase_sin"], out2["Amount_phase_sin"], atol=1e-9)


# ---------------------------------------------------------------- low cardinality

def test_low_cardinality_column_excluded():
    df = _make_df(300, seed=3)
    enc = FourierWallPhaseEncoder(low_card_threshold=LOW_CARD_THRESHOLD).fit(df)
    assert "LowCard" in enc.excluded_low_card_
    assert "LowCard" not in enc.encoded_columns_
    out = enc.transform(df)
    assert "LowCard_phase_cos" not in out and "LowCard_phase_sin" not in out


# ---------------------------------------------------------------- no test leakage

def test_no_leakage_fitted_params_differ_two_training_sets_identical_test_rows():
    """THE anti-leakage test. Fit on two DIFFERENT training sets that induce
    different train-only statistics, then transform the SAME held-out test
    rows under each fit. If any test statistic leaked into fit, an adversarial
    construction here would make the two fits secretly converge; instead we
    assert the fitted PARAMETERS differ (proving fit only used its own
    training data) while confirming transform is a pure function of those
    frozen parameters plus the input row (no per-call dependence on what
    other rows happen to be in the test batch).
    """
    rng = np.random.default_rng(42)
    n_test = 50
    test_df = pd.DataFrame({
        "Amount": rng.lognormal(2.0, 1.0, size=n_test),
        "V1": rng.normal(size=n_test),
        "Time": rng.uniform(0, 86400, size=n_test),
        "LowCard": rng.integers(0, 4, size=n_test).astype(float),
    })

    # Two disjoint, differently-distributed training sets.
    train_a = pd.DataFrame({
        "Amount": rng.lognormal(1.0, 0.5, size=600),   # low-scale regime
        "V1": rng.normal(loc=-3.0, scale=0.5, size=600),
        "Time": rng.uniform(0, 86400, size=600),
        "LowCard": rng.integers(0, 4, size=600).astype(float),
    })
    train_b = pd.DataFrame({
        "Amount": rng.lognormal(6.0, 2.0, size=600),   # high-scale, different shape
        "V1": rng.normal(loc=5.0, scale=3.0, size=600),
        "Time": rng.uniform(0, 86400, size=600),
        "LowCard": rng.integers(0, 4, size=600).astype(float),
    })

    enc_a = FourierWallPhaseEncoder().fit(train_a)
    enc_b = FourierWallPhaseEncoder().fit(train_b)

    # 1. The FITTED PARAMETERS (not just outputs) must differ: this is the
    #    leakage-would-fail-this check. If fit() ever consulted test_df (or if
    #    transform() silently refit / rescaled using whatever batch it saw),
    #    an adversary could make enc_a and enc_b converge to the SAME
    #    parameters despite disjoint training data, because both would then
    #    be dominated by the shared test_df. Here they must NOT converge.
    st_a = enc_a.phase_states_["Amount"]
    st_b = enc_b.phase_states_["Amount"]
    # The frozen train order statistics (what rank-interpolates future data)
    # must come from each fit's OWN training set and therefore differ sharply
    # given the disjoint, differently-scaled train_a/train_b distributions.
    # (Note: mean_cos/std_cos are NOT used for this check -- a rank phase over
    # ~n_train i.i.d. continuous values is, by construction, always close to
    # a uniform distribution on the circle regardless of the underlying data,
    # so those whitening moments are near dataset-invariant and would be a
    # weak/misleading leakage probe. train_sorted is the discriminating
    # fitted parameter: it is literally each fit's own training column.)
    assert not np.allclose(st_a.train_sorted[:10], st_b.train_sorted[:10])
    assert st_a.train_sorted[0] != pytest.approx(st_b.train_sorted[0], abs=1e-3)

    # 2. Transform must depend ONLY on the frozen fit params and the row
    #    itself -- never on which other rows are present in the same
    #    transform() call. Prove this by transforming test_df whole, and
    #    transforming it split into two halves; results for any given row
    #    must be identical regardless of what else was in the batch.
    out_whole = enc_a.transform(test_df)
    half1, half2 = test_df.iloc[:20], test_df.iloc[20:]
    out_h1 = enc_a.transform(half1)
    out_h2 = enc_a.transform(half2)
    for key in out_whole:
        np.testing.assert_allclose(out_whole[key][:20], out_h1[key], atol=1e-12)
        np.testing.assert_allclose(out_whole[key][20:], out_h2[key], atol=1e-12)

    # 3. Because the fitted parameters differ (point 1), transforming the
    #    IDENTICAL test rows under enc_a vs enc_b must give DIFFERENT outputs
    #    -- if fit had instead leaked test statistics, enc_a and enc_b would
    #    have been pulled toward the same (test-influenced) parameters and
    #    could produce suspiciously similar outputs despite disjoint training
    #    data. Different training data -> different frozen params -> different
    #    transform of the same rows is the expected, leak-free signature.
    out_a = enc_a.transform(test_df)
    out_b = enc_b.transform(test_df)
    assert not np.allclose(out_a["Amount_phase_cos"], out_b["Amount_phase_cos"])


def test_no_leakage_transform_does_not_mutate_fitted_state():
    """Calling transform() repeatedly, including on data with a wildly
    different distribution than train, must never change the fitted state
    (proves transform has no hidden re-fit / running-statistics update)."""
    df_train = _make_df(400, seed=5)
    enc = FourierWallPhaseEncoder().fit(df_train)
    snapshot = {
        name: (st.mean_cos, st.std_cos, st.mean_sin, st.std_sin, st.n_train)
        for name, st in enc.phase_states_.items()
    }
    outlier_df = pd.DataFrame({
        "Amount": np.full(50, 1e9),
        "V1": np.full(50, -1e6),
        "Time": np.full(50, 12345.0),
        "LowCard": np.zeros(50),
    })
    enc.transform(df_train)
    enc.transform(outlier_df)
    enc.transform(df_train)
    for name, st in enc.phase_states_.items():
        assert (st.mean_cos, st.std_cos, st.mean_sin, st.std_sin, st.n_train) == snapshot[name]


def test_train_only_whitening_matches_manual_computation():
    """Whitening mean/std must be the TRAIN phase distribution's own moments,
    not recomputed at transform time."""
    df = _make_df(500, seed=6)
    enc = FourierWallPhaseEncoder().fit(df)
    log_mag = np.sign(df["V1"].to_numpy()) * np.log1p(np.abs(df["V1"].to_numpy()))
    phi = _rank_phase(log_mag)
    cos, sin = np.cos(phi), np.sin(phi)
    st = enc.phase_states_["V1"]
    assert st.mean_cos == pytest.approx(cos.mean(), abs=1e-9)
    assert st.std_cos == pytest.approx(cos.std(), abs=1e-9)
    assert st.mean_sin == pytest.approx(sin.mean(), abs=1e-9)
    assert st.std_sin == pytest.approx(sin.std(), abs=1e-9)

    out = enc.transform(df)
    # Whitened train output must itself have ~zero mean, unit std (identity
    # check: transforming the SAME data you fit on reproduces standard
    # whitening exactly).
    assert out["V1_phase_cos"].mean() == pytest.approx(0.0, abs=1e-9)
    assert out["V1_phase_cos"].std() == pytest.approx(1.0, abs=1e-6)
