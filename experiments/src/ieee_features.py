"""IEEE-CIS reduced feature recipe, preregistered (PREREGISTRATION.md v1.1
section 5.3). Sprint 6 Task B (F3 prep, issue #32): PREPARATION ONLY.

This module builds the feature pass. It fits and transforms; it never
trains a model arm and never writes experiments/results/results.json.
Execution (fitting an arm and reporting a metric) is F3 in Sprint 7.

Preregistered recipe (verbatim from section 5.3), implemented here:
  1. D-column time normalization: Dn = D - TransactionDT/86400, for
     D1, D2, D4, D10, D11, D15 only (the six the prereg names).
  2. UID = card1 + addr1 + floor(day - D1); the UID itself is EXCLUDED
     from the model (prereg: "the UID itself EXCLUDED"). It exists only
     as a train-fold grouping key for the aggregates below.
  3. UID aggregations, exactly the named list: TransactionAmt mean/std,
     C1-C14 means, D4/D9/D10/D15 aggregates (mean, fit on train fold only).
  4. Frequency encodings of card1_addr1 and card1_addr1_P_emaildomain.
  5. V-column reduction: group by missing-value pattern, then drop columns
     within a group correlated above 0.75 with an already-kept column,
     keeping the higher-cardinality column of the pair.

Every fitted quantity (aggregate means/stds, frequency tables, V-columns
kept, correlation drops) is fit on training rows only and applied to
validation/test via `transform`, per section 5 rule 1 (fit-on-train-only,
inside a fold). This module exposes that fit/transform split explicitly
so callers never accidentally fit on combined data.

JUDGMENT CALLS (prereg silent; documented per Task B instructions):
  - UID formula: prereg section 5.3 says "card1 + addr1 + floor(day - D1)".
    Read literally (not the community `card1_addr1` string-concat variant
    quoted in docs/research-baselines-best-practices.md, which is a
    different paper's exact wording, not ours) as the SUM card1 + addr1
    plus the floored day-offset, all combined into one grouping key via
    string concatenation of the three integer parts (conservative: avoids
    silently reinterpreting the frozen document; a footnote is kept here
    if the team lead later clarifies this differently).
  - day := TransactionDT // 86400 (whole days since a fixed reference),
    the standard derivation implied by "Dn = D - TransactionDT/86400"
    elsewhere in the same section; no other epoch is given.
  - "D9" appears in the named aggregate list but D9 is documented
    (Kaggle competition notes) as an hour-of-day feature already, not a
    timedelta; it is aggregated as-is (no D-normalization applied to D9,
    matching the prereg's D-normalization list which excludes D9).
  - V-column correlation reduction: "keep highest cardinality" is applied
    within each missing-pattern group, correlation computed on TRAIN ROWS
    ONLY with NaNs pairwise-dropped (conservative: a fit on fewer, complete
    pairs rather than an imputed value that could bias grouping).
  - Frequency encodings are fit (value -> count) on TRAIN ONLY and applied
    to val/test by lookup; unseen combinations at val/test map to 0
    (conservative: unseen combos get no frequency signal rather than a
    guessed smoothed value).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

# Section 5.3, verbatim column lists.
D_NORMALIZE_COLS = ("D1", "D2", "D4", "D10", "D11", "D15")
UID_AGG_D_COLS = ("D4", "D9", "D10", "D15")
UID_AGG_C_COLS = tuple(f"C{i}" for i in range(1, 15))
FREQ_ENCODE_COLS = ("card1_addr1", "card1_addr1_P_emaildomain")
V_CORR_THRESHOLD = 0.75


def add_day(df: pd.DataFrame) -> pd.Series:
    """Whole days since the dataset's reference epoch (documented judgment
    call above: day = TransactionDT // 86400)."""
    return (df["TransactionDT"] // 86400).astype("int32")


def normalize_d_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Dn = D - TransactionDT/86400 for the six preregistered D-columns.
    Returns df with additional f"{col}_n" columns; raw D-columns retained
    (the prereg does not say to drop them, only to add the normalized
    version -- conservative choice, documented in the module docstring)."""
    out = df.copy()
    day_frac = df["TransactionDT"] / 86400.0
    for col in D_NORMALIZE_COLS:
        if col in out.columns:
            out[f"{col}_n"] = out[col] - day_frac
    return out


def compute_uid(df: pd.DataFrame, day: pd.Series) -> pd.Series:
    """UID = card1 + addr1 + floor(day - D1); UID is a grouping KEY only,
    never a model feature (prereg: "the UID itself EXCLUDED"). card1/addr1
    NaNs are filled with a sentinel string before concatenation so rows
    with a missing addr1 still group deterministically (conservative: they
    group together as "unknown address", never silently dropped)."""
    card1 = df["card1"].fillna(-1).astype("int64").astype(str)
    addr1 = df["addr1"].fillna(-1).astype("int64").astype(str)
    d1 = df["D1"].fillna(0)
    day_offset = np.floor(day - d1).astype("int64").astype(str)
    return card1 + "_" + addr1 + "_" + day_offset


@dataclass
class UIDAggregates:
    """Fitted (train-only) UID aggregate table plus the frequency-encoding
    tables named in section 5.3. `transform` applies all of them by
    left-join / lookup; unseen keys at val/test get NaN (aggregates) or 0
    (frequency counts), never a value estimated from non-train rows."""
    uid_table: pd.DataFrame = field(default_factory=pd.DataFrame)
    freq_tables: dict = field(default_factory=dict)

    def fit(self, df: pd.DataFrame, uid: pd.Series) -> "UIDAggregates":
        g = df.assign(_uid=uid).groupby("_uid")
        agg = pd.DataFrame(index=g.size().index)
        agg["uid_TransactionAmt_mean"] = g["TransactionAmt"].mean()
        agg["uid_TransactionAmt_std"] = g["TransactionAmt"].std()
        for c in UID_AGG_C_COLS:
            if c in df.columns:
                agg[f"uid_{c}_mean"] = g[c].mean()
        for c in UID_AGG_D_COLS:
            if c in df.columns:
                agg[f"uid_{c}_mean"] = g[c].mean()
        self.uid_table = agg

        freq = {}
        for col in FREQ_ENCODE_COLS:
            if col in df.columns:
                freq[col] = df[col].value_counts()
        self.freq_tables = freq
        return self

    def transform(self, df: pd.DataFrame, uid: pd.Series) -> pd.DataFrame:
        out = df.copy()
        joined = self.uid_table.reindex(uid.values)
        joined.index = out.index
        out = pd.concat([out, joined], axis=1)
        for col, counts in self.freq_tables.items():
            if col in out.columns:
                out[f"{col}_freq"] = out[col].map(counts).fillna(0).astype("float32")
        return out


def build_card1_addr1(df: pd.DataFrame) -> pd.DataFrame:
    """Adds the two composite columns section 5.3 names for frequency
    encoding (card1_addr1, card1_addr1_P_emaildomain), as plain string
    concatenations. These composite columns are inputs to frequency
    encoding only, never raw model features themselves."""
    out = df.copy()
    card1 = out["card1"].fillna(-1).astype("int64").astype(str)
    addr1 = out["addr1"].fillna(-1).astype("int64").astype(str)
    out["card1_addr1"] = card1 + "_" + addr1
    if "P_emaildomain" in out.columns:
        email = out["P_emaildomain"].fillna("missing").astype(str)
        out["card1_addr1_P_emaildomain"] = out["card1_addr1"] + "_" + email
    return out


@dataclass
class VColumnReducer:
    """V-column reduction by missing-pattern grouping then within-group
    correlation pruning (section 5.3: ">0.75, keep highest cardinality").
    Fit on train only; transform just selects the kept columns (a pure
    column subset, so there is nothing to leak at transform time)."""
    keep: list = field(default_factory=list)

    def fit(self, df: pd.DataFrame, threshold: float = V_CORR_THRESHOLD) -> "VColumnReducer":
        v_cols = [c for c in df.columns if c.startswith("V") and c[1:].isdigit()]
        if not v_cols:
            self.keep = []
            return self

        na_mask = df[v_cols].isna()

        # Per-column missingness signature (not per-row): two V-columns are
        # in the same "missing-pattern group" when they are NaN on the same
        # set of rows (the Deotte-recipe definition this section follows).
        col_groups: dict = {}
        for col in v_cols:
            sig = na_mask[col].values.tobytes()
            col_groups.setdefault(sig, []).append(col)

        kept: list = []
        for _, cols in col_groups.items():
            if len(cols) == 1:
                kept.append(cols[0])
                continue
            # cardinality (train-only) breaks correlation ties, highest kept.
            cardinality = {c: df[c].nunique(dropna=True) for c in cols}
            ordered = sorted(cols, key=lambda c: cardinality[c], reverse=True)
            group_keep: list = []
            for c in ordered:
                corr_hit = False
                for k in group_keep:
                    r = df[[c, k]].corr().iloc[0, 1]
                    if pd.notna(r) and abs(r) > threshold:
                        corr_hit = True
                        break
                if not corr_hit:
                    group_keep.append(c)
            kept.extend(group_keep)

        self.keep = sorted(kept, key=lambda c: int(c[1:]))
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        v_cols = [c for c in df.columns if c.startswith("V") and c[1:].isdigit()]
        drop = [c for c in v_cols if c not in self.keep]
        return df.drop(columns=drop)


@dataclass
class IEEEFeaturePipeline:
    """Fit-on-train-only wrapper composing the full section 5.3 recipe.
    `fit_transform(train_df)` then `transform(val_or_test_df)` is the only
    supported order (mirrors data.py's fit-inside-fold contract)."""
    uid_agg: UIDAggregates = field(default_factory=UIDAggregates)
    v_reducer: VColumnReducer = field(default_factory=VColumnReducer)
    uid_col_dropped: bool = True

    def _prep(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
        df = normalize_d_columns(df)
        df = build_card1_addr1(df)
        day = add_day(df)
        uid = compute_uid(df, day)
        return df, day, uid

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df, day, uid = self._prep(df)
        self.uid_agg.fit(df, uid)
        self.v_reducer.fit(df)
        out = self.uid_agg.transform(df, uid)
        out = self.v_reducer.transform(out)
        return self._finalize(out)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df, day, uid = self._prep(df)
        out = self.uid_agg.transform(df, uid)
        out = self.v_reducer.transform(out)
        return self._finalize(out)

    def _finalize(self, df: pd.DataFrame) -> pd.DataFrame:
        # UID itself is a key, never a feature (prereg: "explicitly EXCLUDED").
        # The composite frequency-source columns are likewise dropped once
        # their *_freq encoding has been produced -- keeping the raw
        # high-cardinality string would leak the same identity information
        # the UID exclusion rule is meant to prevent.
        drop = [c for c in ("card1_addr1", "card1_addr1_P_emaildomain") if c in df.columns]
        # Section 5 item 5: "no identifier column enters any model raw."
        # TransactionID is a row key and TransactionDT is the raw clock -- a
        # model given the clock can memorise WHEN fraud occurred in the training
        # months, which is the leak rolling-origin evaluation exists to prevent.
        # Both survived into the feature matrix until the F3 pre-run audit. The
        # adversarial control happened to remove them, but it stops at a round
        # cap, so that was luck rather than compliance: on a fold where twenty
        # other features ranked higher, the raw clock would have gone in.
        # Dropping here makes it a property of the recipe instead.
        drop += [c for c in ("TransactionID", "TransactionDT") if c in df.columns]
        return df.drop(columns=drop)
