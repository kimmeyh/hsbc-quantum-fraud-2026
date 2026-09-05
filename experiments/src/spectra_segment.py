"""SPECTRA in-segment evaluation machinery (PREREGISTRATION H5; Sprint 6 F24, card #34).

Implements the H5(i) replication machinery: in-segment (`in_pocket==1`) metrics
paired with a MATCHED RANDOM-SEGMENT NEGATIVE CONTROL (same segment size, same
base rate, drawn from the complement pool at random) so an apparent in-segment
win can be told apart from a small-sample artifact on that slice. The reported
edge is in-segment minus random-segment (prereg H5(ii) language), applied here
to the H5(i) replication cells too, since the same small-sample risk applies.

Leak-free contract (FourierWall2_CVQBoost_Findings.md section 2, ADR-0003):
`target`, `target_real`, `in_pocket` are labels/flags, NEVER features. This
module never builds a feature matrix itself (data.spectra_features already
enforces the drop), but ships `assert_no_label_leak` so every caller that
assembles its own X can be pinned by a test.

The >= 50-test-positives-per-cell rule (prereg H5(ii), applied here to H5(i))
is enforced IN CODE: `evaluate_in_segment` returns status="unscoreable" and
computes no metric when the in-segment test-fold positive count is below
MIN_TEST_POSITIVES, rather than silently reporting a noisy number.

Frozen cells: see FROZEN_CELLS below (Sprint 6 Task D). Each entry's
config_hash is computed the same way as qubo_proxy/run_classical (store.config_hash
over the sorted-key payload) so it can be checked into results.json rows later
without re-deriving the hash by hand.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import data
import metrics
import store

LABEL_COLS = ("target", "target_real", "in_pocket")
SEGMENT_FLAG = "in_pocket"

# H5(ii)'s minimum-detectable-cell floor, applied here to every scored segment
# (in-segment and its matched random control alike): below this the cell is
# reported unscoreable, never as a noisy point estimate.
MIN_TEST_POSITIVES = 50

# H5(i): 5 seeds on the 3 strongest cells (prereg section 3).
SEGMENT_SEEDS = (42, 43, 44, 45, 46)


# --------------------------------------------------------------- leak guard

def assert_no_label_leak(feature_cols) -> None:
    """Fails loudly if any of the three label/flag columns reaches a feature
    matrix. Call this on the column list actually handed to a model, not on
    the raw dataframe (a raw df legitimately carries the labels)."""
    leaked = set(feature_cols) & set(LABEL_COLS)
    assert not leaked, f"leak-free contract violated: {sorted(leaked)} in features"


# ------------------------------------------------------------------- splits

def spectra_split(df: pd.DataFrame, seed: int, label_col: str):
    """60/20/20 stratified split on `label_col` (mirrors data.stratified_split,
    generalized to SPECTRA's three possible label columns). Returns a
    data.Split whose X_* still carries the `in_pocket` column (needed to
    recover the segment mask per split without re-deriving it from the full
    frame) but drops `label_col` itself and the other label column -- so X_*
    is exactly "covariates + in_pocket", never a bare feature matrix.

    Callers MUST additionally drop `in_pocket` (via segment_feature_cols, or
    data.spectra_features on the raw df) before fitting anything; this
    function only guarantees the OTHER label and the active label are gone."""
    from sklearn.model_selection import train_test_split

    other_label = [c for c in LABEL_COLS
                   if c not in (SEGMENT_FLAG, label_col)]
    y = df[label_col]
    X = df.drop(columns=other_label + [label_col])
    assert SEGMENT_FLAG in X.columns, "in_pocket must ride along for segment scoring"
    assert label_col not in X.columns and not set(other_label) & set(X.columns)
    X_train, X_rest, y_train, y_rest = train_test_split(
        X, y, test_size=0.40, stratify=y, random_state=seed)
    X_val, X_test, y_val, y_test = train_test_split(
        X_rest, y_rest, test_size=0.50, stratify=y_rest, random_state=seed)
    return data.Split(X_train, y_train, X_val, y_val, X_test, y_test, "stratified", seed)


def segment_feature_cols(X) -> list[str]:
    """The actual model-facing feature list from a spectra_split X_* frame:
    every column except `in_pocket` (the label_col and the other label are
    already gone per spectra_split's contract). Always pass the result
    through assert_no_label_leak before fitting."""
    cols = [c for c in X.columns if c != SEGMENT_FLAG]
    assert_no_label_leak(cols)
    return cols


# ------------------------------------------------------- matched random control

def matched_random_segment(in_pocket_mask: np.ndarray, rng: np.random.Generator,
                           y: np.ndarray) -> np.ndarray:
    """Draw a random segment of the SAME SIZE as in_pocket==1 and the SAME BASE
    RATE (positive count), from the COMPLEMENT of the segment. This is the negative
    control prereg H5(ii) requires: a genuine in-segment structural effect
    should beat this control, not just beat "the rest of the data" (which
    differs in both size and prevalence from the segment by construction).

    Construction: sample n_pos positives and n_neg negatives uniformly at
    random WITHOUT replacement from the label-stratified COMPLEMENT pools
    (rows outside the segment), matching
    the segment's exact size and exact positive count. This can only be
    matched exactly when the segment's size and base rate are jointly
    feasible against the full pool (asserted below); SPECTRA's pockets are a
    small fraction of each split so this always holds in practice.
    """
    in_pocket_mask = np.asarray(in_pocket_mask, dtype=bool)
    y = np.asarray(y)
    n_total = int(in_pocket_mask.sum())
    n_pos = int(y[in_pocket_mask].sum())
    n_neg = n_total - n_pos

    # Sample from the COMPLEMENT, never the full pool. Drawing from all rows
    # lets the control share rows with the segment it controls for (~20% overlap
    # measured on a 400-row segment in 2000 rows), and since the reported edge is
    # in-segment minus control, shared rows pull that difference toward zero and
    # bias H5(i) AGAINST detecting a real in-segment effect. The module contract
    # always said "complement pool"; the code did not implement it.
    outside = ~in_pocket_mask
    pos_idx = np.flatnonzero((y == 1) & outside)
    neg_idx = np.flatnonzero((y == 0) & outside)
    assert n_pos <= len(pos_idx), ("matched control needs more positives than exist "
                                   "OUTSIDE the segment")
    assert n_neg <= len(neg_idx), ("matched control needs more negatives than exist "
                                   "OUTSIDE the segment")

    chosen_pos = rng.choice(pos_idx, size=n_pos, replace=False)
    chosen_neg = rng.choice(neg_idx, size=n_neg, replace=False)
    control_idx = np.concatenate([chosen_pos, chosen_neg])
    control_mask = np.zeros(len(y), dtype=bool)
    control_mask[control_idx] = True
    return control_mask


# ------------------------------------------------------------- >=50 rule

def _scoreable(y_segment: np.ndarray) -> tuple[bool, int]:
    n_pos = int(np.asarray(y_segment).sum())
    return n_pos >= MIN_TEST_POSITIVES, n_pos


def _segment_metrics(y_seg: np.ndarray, p_seg: np.ndarray) -> dict:
    from sklearn.metrics import average_precision_score, roc_auc_score
    return {
        "n": int(len(y_seg)),
        "n_positives": int(np.asarray(y_seg).sum()),
        "auc_roc": float(roc_auc_score(y_seg, p_seg)),
        "auprc": float(average_precision_score(y_seg, p_seg)),
    }


def evaluate_in_segment(y_test: np.ndarray, p_test: np.ndarray,
                        in_pocket_test: np.ndarray, seed: int,
                        label: str = "target") -> dict:
    """Score the in_pocket==1 test slice AND its matched random-segment
    control, both gated by the >=50-test-positives rule (enforced here, not
    merely documented). `p_test` are model scores aligned index-for-index
    with y_test/in_pocket_test (same row order).

    Returns a dict always carrying `status` in {"scored", "unscoreable"} for
    EACH of "in_segment" and "random_control" independently, so a caller can
    tell exactly which half of the comparison failed the floor.
    """
    y_test = np.asarray(y_test)
    p_test = np.asarray(p_test)
    in_pocket_test = np.asarray(in_pocket_test, dtype=bool)

    seg_mask = in_pocket_test
    ok_seg, n_pos_seg = _scoreable(y_test[seg_mask])
    result = {"label": label, "seed": seed, "min_test_positives": MIN_TEST_POSITIVES}

    if not ok_seg:
        result["in_segment"] = {"status": "unscoreable", "n": int(seg_mask.sum()),
                                "n_positives": n_pos_seg,
                                "reason": f"n_positives {n_pos_seg} < {MIN_TEST_POSITIVES}"}
        result["random_control"] = {"status": "not_computed",
                                    "reason": "in-segment cell already unscoreable"}
        result["edge"] = None
        return result

    result["in_segment"] = {"status": "scored",
                            **_segment_metrics(y_test[seg_mask], p_test[seg_mask])}

    rng = np.random.default_rng(seed)
    ctrl_mask = matched_random_segment(seg_mask, rng, y_test)
    ok_ctrl, n_pos_ctrl = _scoreable(y_test[ctrl_mask])
    if not ok_ctrl:
        result["random_control"] = {"status": "unscoreable", "n": int(ctrl_mask.sum()),
                                    "n_positives": n_pos_ctrl,
                                    "reason": f"n_positives {n_pos_ctrl} < {MIN_TEST_POSITIVES}"}
        result["edge"] = None
        return result

    result["random_control"] = {"status": "scored",
                                **_segment_metrics(y_test[ctrl_mask], p_test[ctrl_mask])}
    # Matching check: control must share exact size and base rate with segment.
    assert result["random_control"]["n"] == result["in_segment"]["n"]
    assert result["random_control"]["n_positives"] == result["in_segment"]["n_positives"]

    result["edge"] = {
        "auc_roc": result["in_segment"]["auc_roc"] - result["random_control"]["auc_roc"],
        "auprc": result["in_segment"]["auprc"] - result["random_control"]["auprc"],
    }
    return result


def evaluate_across_seeds(fit_and_score_fn, label: str = "target",
                          seeds=SEGMENT_SEEDS) -> dict:
    """Run `fit_and_score_fn(seed) -> (y_test, p_test, in_pocket_test)` over
    the 5 H5(i) seeds and aggregate. Mean/std/CI are reported ONLY over seeds
    where BOTH in_segment and random_control were scoreable; the count of
    dropped seeds is always reported, never silently absorbed."""
    per_seed = []
    for seed in seeds:
        y_test, p_test, in_pocket_test = fit_and_score_fn(seed)
        per_seed.append(evaluate_in_segment(y_test, p_test, in_pocket_test, seed, label))

    scored = [r for r in per_seed if r["edge"] is not None]
    n_dropped = len(per_seed) - len(scored)
    out = {"label": label, "seeds": list(seeds), "per_seed": per_seed,
          "n_seeds_scored": len(scored), "n_seeds_dropped": n_dropped}
    if scored:
        for metric in ("auc_roc", "auprc"):
            vals = np.array([r["edge"][metric] for r in scored])
            out[f"edge_{metric}_mean"] = float(vals.mean())
            out[f"edge_{metric}_std"] = float(vals.std(ddof=1)) if len(vals) > 1 else 0.0
            if len(vals) > 1:
                ci = metrics.seed_mean_t_interval(list(vals))
                out[f"edge_{metric}_ci95"] = ci["ci95"]
            else:
                out[f"edge_{metric}_ci95"] = [None, None]
    return out


# --------------------------------------------------------- frozen cells (H5i)

# The 3 strongest in-segment cells, chosen from FourierWall2's tuned rollout
# (CVQBoost_Findings.md section 10, 2026-08-04, seed 20260804, single stochastic
# run per the doc's own caveat). Selection basis: `target` cells only (the
# genuine campaign task; `target_real` is either near-saturated -- energy_steel
# ROC 0.99998 vs 0.99964, a margin of 0.0003, not a meaningful effect -- or a
# CVQBoost LOSS in-segment for maintenance_ai4i and oilgas_gasturbine, or
# unscoreable for telecom_churn, 0 real positives in the pocket). Among the
# four `target` cells, maintenance_ai4i/target is EXCLUDED: it wins in-segment
# ROC (0.592 vs 0.574) but LOSES in-segment PR (0.593 vs 0.606), so it is not a
# clean win on both metrics the way the other three are.
#
# Evidence (train_spectra_<name>_target_..._summary.csv, single seed 20260804,
# test in-segment, quantum=CVQBoost vs classical=XGBoost):
#   telecom_churn:      n=101,  pos=50   ROC 0.8627 vs 0.7886 (+0.0741)  PR 0.8754 vs 0.7844 (+0.0910)
#   energy_steel:       n=1303, pos=980  ROC 0.8949 vs 0.8376 (+0.0574)  PR 0.9650 vs 0.9470 (+0.0180)
#   oilgas_gasturbine:  n=1352, pos=774  ROC 0.6677 vs 0.6325 (+0.0352)  PR 0.7543 vs 0.7335 (+0.0208)
# All three clear MIN_TEST_POSITIVES=50 on that historical split; telecom sits
# exactly at the floor, which is precisely why the rule must be code-enforced
# per seed here rather than assumed to hold (a different seed's stratified
# split can push a 101-row pocket below 50 positives). CONFIRMED by this
# module's own proxy dry run across the 5 H5(i) seeds (42-46, house stratified
# split, label=target): telecom_churn's test-fold pocket clears 50 positives
# at seeds 43/44/46 (52/52/57) but falls SHORT at seeds 42/45 (46/49) -- 2 of
# 5 seeds are unscoreable for this cell under the frozen rule. Report this
# per-seed pattern honestly in H5(i); never average over the unscoreable
# seeds as if they contributed a zero or a dropped-silently point.
#
# Config: the tuned rollout's config (CVQBoost_Findings.md sections 3/8):
# weak_cls_schedule=3, num_samples=8, relaxation_schedule=2,
# lambda_coef = 2 * n_train (adaptive, per dataset), weak_cls_params={} (default
# depth), leak-free features (data.spectra_features), sequential build (Windows).
# telecom_churn used the auto-reduced 17-feature set (dropped `age`) to fit the
# schedule-3 QUBO under the device ceiling (CVQBoost_Findings.md section 5/8);
# the other two datasets fit schedule 3 at their full leak-free feature count.

_FROZEN_BASE_CONFIG = {
    "weak_cls_schedule": 3, "num_samples": 8, "relaxation_schedule": 2,
    "lambda_coef_alpha": 2.0,   # lambda_coef = alpha * n_train, per dataset
    "weak_cls_params": {}, "weak_cls_strategy": "sequential",
    "label": "target", "leak_free": True,
}


def _frozen_cell(name: str, n_features: int, dropped_feature: str | None) -> dict:
    cfg = dict(_FROZEN_BASE_CONFIG, dataset=f"spectra_{name}", n_features=n_features,
              dropped_feature=dropped_feature)
    return {"dataset": f"spectra_{name}", "config": cfg,
           "config_hash": store.config_hash(cfg)}


FROZEN_CELLS = [
    _frozen_cell("telecom_churn", 17, "age"),
    _frozen_cell("energy_steel", 17, None),
    _frozen_cell("oilgas_gasturbine", 15, None),
]
FROZEN_CELL_NAMES = tuple(c["dataset"] for c in FROZEN_CELLS)


def frozen_cell_by_name(name: str) -> dict:
    for c in FROZEN_CELLS:
        if c["dataset"] == name or c["dataset"] == f"spectra_{name}":
            return c
    raise KeyError(name)


# ------------------------------------------------------- proxy dry run (B4)

# telecom_churn's auto-reduction drops the lowest-importance feature under
# the schedule-3 ceiling (CVQBoost_Findings.md sections 5/8); `age` was the
# one dropped in the FourierWall2 rollout and is reproduced verbatim here
# rather than re-derived, since re-deriving it is exactly the "re-tuning"
# the preregistration's provenance-disclosure clause (section 1) restricts to
# a held-out split -- this dry run is a proxy REPLICATION, not a re-tune.
_DROP_FEATURE = {"telecom_churn": "age"}


def coerce_features_to_numeric(X_df: pd.DataFrame) -> pd.DataFrame:
    """Numeric coercion for SPECTRA's raw covariates (some, e.g. energy_steel's
    `date`, `WeekStatus`, `Day_of_week`, are strings), ported verbatim from
    FourierWall2's `main.py::_coerce_features_to_numeric` (the function that
    actually produced every measured number in CVQBoost_Findings.md) so this
    proxy dry run replicates, rather than re-derives, the FourierWall2
    preprocessing: numeric columns pass through; numeric-like strings parse;
    datetime-like strings become unix seconds; remaining categoricals
    factorize to integer codes (fit per-split here, train-only, per the
    leakage rule -- FourierWall2 fit it jointly across the eval frames it
    built at once, which this per-split call intentionally does not
    reproduce, since a fresh factorization per split is the leak-free choice
    and produces the same codes for any column whose categories are stable).
    Any resulting NaN (unparseable values, or categories absent from a split)
    is imputed with the column median, then 0.0 as a last resort."""
    X_num = pd.DataFrame(index=X_df.index)
    for col in X_df.columns:
        series = X_df[col]
        if pd.api.types.is_numeric_dtype(series):
            X_num[col] = pd.to_numeric(series, errors="coerce")
            continue
        parsed_num = pd.to_numeric(series, errors="coerce")
        if float(parsed_num.notna().mean()) >= 0.95:
            X_num[col] = parsed_num
            continue
        parsed_dt = pd.to_datetime(series, errors="coerce", utc=True)
        if float(parsed_dt.notna().mean()) >= 0.95:
            X_num[col] = (parsed_dt.astype("int64")
                          .where(parsed_dt.notna(), np.nan) / 1_000_000_000.0)
            continue
        cat = series.astype("string").fillna("__NA__")
        codes, _ = pd.factorize(cat, sort=True)
        X_num[col] = codes.astype(float)
    if X_num.isna().any().any():
        X_num = X_num.fillna(X_num.median(numeric_only=True)).fillna(0.0)
    return X_num


def _prep_spectra(name: str, seed: int):
    df = data.load_spectra(name)
    split = spectra_split(df, seed, label_col="target")
    cols = segment_feature_cols(split.X_train)
    drop = _DROP_FEATURE.get(name)
    if drop is not None:
        assert drop in cols, f"{name}: expected drop candidate {drop!r} missing"
        cols = [c for c in cols if c != drop]
    assert_no_label_leak(cols)
    return split, cols


def proxy_dry_run_cell(name: str, seed: int) -> dict:
    """Zero-metered classical-proxy fit on one frozen SPECTRA cell: builds the
    identical weak-classifier pool and solves the identical Hamiltonian
    qubo_proxy.py solves for ULB (ADR-0002), here against SPECTRA's `target`
    label. Produces the expected-value numbers the B4 hardware request cites;
    NEVER touches Dirac-3 (evidence_tag is always PROJ, metered_seconds always 0).
    """
    import qubo_proxy

    cell = frozen_cell_by_name(name)
    split, cols = _prep_spectra(name, seed)
    n_features = len(cols)
    assert n_features == cell["config"]["n_features"], (
        f"{name}: frozen cell expects {cell['config']['n_features']} features, got {n_features}")

    Xtr = coerce_features_to_numeric(split.X_train[cols]).to_numpy(dtype="float32")
    Xte = coerce_features_to_numeric(split.X_test[cols]).to_numpy(dtype="float32")
    y_train01 = split.y_train.to_numpy()
    y_test01 = split.y_test.to_numpy()
    in_pocket_test = split.X_test[SEGMENT_FLAG].to_numpy().astype(bool)
    y_pm1 = np.where(y_train01 == 1, 1, -1)

    schedule = cell["config"]["weak_cls_schedule"]
    n_vars = data.qubo_vars(n_features, schedule, pair_build="sequential")

    clf = qubo_proxy.build_pool(Xtr, y_pm1, schedule, weak_type="dct",
                                pair_build="sequential",
                                lambda_coef=cell["config"]["lambda_coef_alpha"] * len(y_pm1))
    H_tr = qubo_proxy.h_matrix(clf, Xtr)
    H_te = qubo_proxy.h_matrix(clf, Xte)
    w = qubo_proxy.solve_simplex_qp(H_tr, y_pm1,
                                    cell["config"]["lambda_coef_alpha"] * len(y_pm1))
    p_test = np.clip((w @ H_te + 1.0) / 2.0, 0.0, 1.0)

    seg = evaluate_in_segment(y_test01, p_test, in_pocket_test, seed, label="target")
    from sklearn.metrics import average_precision_score, roc_auc_score
    overall = {"auc_roc": float(roc_auc_score(y_test01, p_test)),
              "auprc": float(average_precision_score(y_test01, p_test))}

    return {
        "dataset": cell["dataset"], "config_hash": cell["config_hash"], "seed": seed,
        "n_features": n_features, "n_weak_classifiers": int(len(clf.h_list)),
        "n_vars_expected": n_vars,
        "overall": overall, "in_segment": seg,
        "evidence_tag": "PROJ", "metered_seconds": 0,
    }


def proxy_dry_run(seeds=(42,)) -> list[dict]:
    """Run proxy_dry_run_cell over every frozen cell x seed. Default is a
    single seed (42) since this is a DRY RUN to set B4's expected values, not
    the H5(i) 5-seed replication itself (that runs on hardware, gated on B4
    approval)."""
    rows = []
    for cell in FROZEN_CELLS:
        name = cell["dataset"].removeprefix("spectra_")
        for seed in seeds:
            rows.append(proxy_dry_run_cell(name, seed))
    return rows


def main() -> int:
    import json as _json
    rows = proxy_dry_run()
    for r in rows:
        seg = r["in_segment"]["in_segment"]
        ctl = r["in_segment"]["random_control"]
        print(f"{r['dataset']:>28s} seed={r['seed']} vars={r['n_vars_expected']:>4d} "
              f"overall AP={r['overall']['auprc']:.4f} "
              f"seg({seg['status']})={seg.get('auprc', float('nan')):.4f} "
              f"ctl({ctl['status']})={ctl.get('auprc', float('nan')):.4f}")
    out_path = store.RESULTS_DIR / "spectra_proxy_dry_run.json"
    out_path.write_text(_json.dumps(rows, indent=1))
    print(f"written: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
