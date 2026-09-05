"""Quantum Feature Engineering (QFE): the Fourier Wall phase recipe as a
fitted, train-only transformer (PREREGISTRATION v1.1 H6; Sprint 6 Task C / F23,
card #33; docs/references.md design implications 1-2).

Exact recipe (Mancilla & Tagliani, "The Fourier Wall", arXiv:2607.15815,
section 6.4), applied identically to every H6 arm:
  1. Log magnitudes FIRST (log1p of the absolute value, sign-preserved) --
     magnitude compression happens before any rank/phase computation.
  2. Rank phase: phi = 2*pi*(rank - 0.5)/n - pi, rank computed on the
     log-magnitude column, so phi is a monotone (in fact rank-based, hence
     invariant to any monotone rescaling) function of the raw column.
  3. Calendar cycles: a designated column (ULB's Time, seconds since the
     first transaction) maps to a daily phase 2*pi*(t mod 86400)/86400 - pi,
     bypassing the rank/log path entirely (it is already a cyclic quantity).
  4. Train-only whitening: the encoded phase block (cos/sin pairs) is
     centered and scaled by TRAIN statistics only; fit() never looks at
     transform-time data.
  5. Low-cardinality columns (<= LOW_CARD_THRESHOLD distinct train values)
     are excluded from the encoded block -- a rank phase on a handful of
     ties is not a meaningful continuous phase, and including it would let a
     near-constant column masquerade as a quantum feature.

This module produces the REPRESENTATION only. It is not an arm, does not
touch results.json, and runs no model (Sprint 6 Task C is preparation only;
execution is F4 in Sprint 7).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

TWO_PI = 2.0 * np.pi
LOW_CARD_THRESHOLD = 12   # train-distinct-value ceiling below which a column
                          # is excluded from the encoded phase block (5 above)
DAY_SECONDS = 86400.0


def _rank_phase(values: np.ndarray, ranks_ref: np.ndarray | None = None) -> np.ndarray:
    """phi = 2*pi*(rank - 0.5)/n - pi, rank in {1..n} (average rank on ties).

    When `ranks_ref` is None, ranks are computed on `values` itself (the
    fit-time path). Transform-time uses interpolated ranks against the FROZEN
    train order statistics (see PhaseColumn.transform) so test rows never
    contribute their own rank statistics.
    """
    n = len(values)
    # average rank (1-indexed), ties share the mean rank -- scipy-equivalent,
    # implemented directly to avoid a scipy.stats dependency in the hot path.
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(n, dtype=np.float64)
    sorted_vals = values[order]
    i = 0
    while i < n:
        j = i
        while j + 1 < n and sorted_vals[j + 1] == sorted_vals[i]:
            j += 1
        avg_rank = (i + 1 + j + 1) / 2.0   # 1-indexed average rank over tie block
        ranks[order[i:j + 1]] = avg_rank
        i = j + 1
    phi = TWO_PI * (ranks - 0.5) / n - np.pi
    return phi


@dataclass
class _PhaseColumnState:
    """Frozen train-time state for one rank-phase column."""
    name: str
    train_sorted: np.ndarray      # sorted train LOG-MAGNITUDE values (for rank interpolation)
    n_train: int
    mean_cos: float
    std_cos: float
    mean_sin: float
    std_sin: float


@dataclass
class _CalendarColumnState:
    name: str
    period: float
    mean_cos: float
    std_cos: float
    mean_sin: float
    std_sin: float


@dataclass
class FourierWallPhaseEncoder:
    """Sklearn-style fit/transform QFE phase encoder.

    fit(X_train) computes, from TRAIN DATA ONLY:
      - which columns are low-cardinality (excluded from the encoded block)
      - the log-magnitude order statistics needed to rank-interpolate future
        (including test-time) values without looking at their own distribution
      - the whitening mean/std of the resulting cos/sin phase pair

    transform(X) applies the frozen recipe to any X (train, val, or test) and
    returns ONLY the new phase-encoded columns (cos, sin per encoded input
    column, plus the calendar cycle columns), never the raw inputs -- callers
    concatenate as needed. This mirrors sklearn's ColumnTransformer contract
    without adding a dependency.

    calendar_col: column mapped via the daily-cycle recipe instead of rank
    phase (ULB: "Time"). Excluded from the low-cardinality rank-phase path.
    """
    low_card_threshold: int = LOW_CARD_THRESHOLD
    calendar_col: str | None = "Time"
    calendar_period: float = DAY_SECONDS

    fitted_: bool = field(default=False, init=False)
    encoded_columns_: list[str] = field(default_factory=list, init=False)
    excluded_low_card_: list[str] = field(default_factory=list, init=False)
    phase_states_: dict = field(default_factory=dict, init=False)
    calendar_state_: _CalendarColumnState | None = field(default=None, init=False)

    # ---------------------------------------------------------------- fit

    def fit(self, X, columns: list[str] | None = None):
        """X: pandas DataFrame or 2D array. columns required if X is an array."""
        cols, arr = self._as_array(X, columns)
        self.encoded_columns_ = []
        self.excluded_low_card_ = []
        self.phase_states_ = {}
        self.calendar_state_ = None

        for j, name in enumerate(cols):
            col = arr[:, j].astype(np.float64)
            if name == self.calendar_col:
                self._fit_calendar(name, col)
                continue
            n_distinct = len(np.unique(col))
            if n_distinct <= self.low_card_threshold:
                self.excluded_low_card_.append(name)
                continue
            self._fit_rank_phase(name, col)
        self.fitted_ = True
        return self

    def _fit_rank_phase(self, name: str, col: np.ndarray) -> None:
        # Step 1: log magnitude BEFORE phase (sign-preserved log1p of |x|).
        log_mag = np.sign(col) * np.log1p(np.abs(col))
        # Step 2: rank phase on the log-magnitude column, TRAIN ranks only.
        phi = _rank_phase(log_mag)
        cos, sin = np.cos(phi), np.sin(phi)
        state = _PhaseColumnState(
            name=name,
            train_sorted=np.sort(log_mag),
            n_train=len(log_mag),
            mean_cos=float(cos.mean()), std_cos=float(cos.std() or 1.0),
            mean_sin=float(sin.mean()), std_sin=float(sin.std() or 1.0),
        )
        self.phase_states_[name] = state
        self.encoded_columns_.append(name)

    def _fit_calendar(self, name: str, col: np.ndarray) -> None:
        phi = TWO_PI * np.mod(col, self.calendar_period) / self.calendar_period - np.pi
        cos, sin = np.cos(phi), np.sin(phi)
        self.calendar_state_ = _CalendarColumnState(
            name=name, period=self.calendar_period,
            mean_cos=float(cos.mean()), std_cos=float(cos.std() or 1.0),
            mean_sin=float(sin.mean()), std_sin=float(sin.std() or 1.0),
        )

    # ---------------------------------------------------------------- transform

    def transform(self, X, columns: list[str] | None = None) -> dict:
        """Returns {output_col_name: np.ndarray} for every encoded phase
        column's whitened (cos, sin) pair plus the calendar cycle's, using
        ONLY frozen train-time statistics. Never fits on X."""
        if not self.fitted_:
            raise RuntimeError("FourierWallPhaseEncoder.transform called before fit")
        cols, arr = self._as_array(X, columns)
        col_index = {c: i for i, c in enumerate(cols)}
        out = {}

        for name, state in self.phase_states_.items():
            if name not in col_index:
                continue
            raw = arr[:, col_index[name]].astype(np.float64)
            log_mag = np.sign(raw) * np.log1p(np.abs(raw))
            phi = self._interpolated_rank_phase(log_mag, state)
            cos, sin = np.cos(phi), np.sin(phi)
            out[f"{name}_phase_cos"] = (cos - state.mean_cos) / state.std_cos
            out[f"{name}_phase_sin"] = (sin - state.mean_sin) / state.std_sin

        if self.calendar_state_ is not None and self.calendar_state_.name in col_index:
            st = self.calendar_state_
            raw = arr[:, col_index[st.name]].astype(np.float64)
            phi = TWO_PI * np.mod(raw, st.period) / st.period - np.pi
            cos, sin = np.cos(phi), np.sin(phi)
            out[f"{st.name}_phase_cos"] = (cos - st.mean_cos) / st.std_cos
            out[f"{st.name}_phase_sin"] = (sin - st.mean_sin) / st.std_sin

        return out

    def fit_transform(self, X, columns: list[str] | None = None) -> dict:
        return self.fit(X, columns).transform(X, columns)

    @staticmethod
    def _interpolated_rank_phase(values: np.ndarray, state: _PhaseColumnState) -> np.ndarray:
        """Map new (e.g. test) log-magnitude values to a phase using the
        FROZEN train order statistics only: each value's rank is its
        insertion position among the frozen train_sorted array (linear
        interpolation at ties/out-of-range), never recomputed from the new
        data's own distribution. This is what makes fit-on-train,
        transform-on-test leak-free: the only numbers consulted are
        state.train_sorted and state.n_train, captured at fit time."""
        n = state.n_train
        # searchsorted gives the count of train values <= v (left) and < v+eps;
        # use the midpoint of the [lo, hi] insertion range as a continuous
        # analogue of the average-rank tie handling used at fit time.
        lo = np.searchsorted(state.train_sorted, values, side="left")
        hi = np.searchsorted(state.train_sorted, values, side="right")
        rank = (lo + hi + 1) / 2.0   # 1-indexed average-position estimate
        rank = np.clip(rank, 1.0, n)
        return TWO_PI * (rank - 0.5) / n - np.pi

    @staticmethod
    def _as_array(X, columns):
        try:
            import pandas as pd
            if isinstance(X, pd.DataFrame):
                return list(X.columns), X.to_numpy()
        except ImportError:
            pass
        if columns is None:
            raise ValueError("columns required when X is not a DataFrame")
        return columns, np.asarray(X)


# ---------------------------------------------------------- representation tag

QFE_REPRESENTATION_TAG = "qfe_phase_v1"
"""results.json `features_used`/config representation tag (ADR-0006 recipe-
naming convention) for the H6 phase-encoded blocks produced by this module.
Frozen at Sprint 6 Task C; any recipe change is a new tag, never a silent
edit to this one (ADR-0006 / prereg section 11)."""
