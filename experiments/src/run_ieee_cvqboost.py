"""CVQBoost proxy arms on IEEE-CIS, both pool configurations (F3 Task C).

Team lead scope decision, 2026-09-05: run BOTH pools.

  - FROZEN: one family of depth-limited decision trees, the preregistered
    configuration every prior result is measured against. Carried for
    continuity; dropping it would break comparability with H1b, G0b and the
    whole hardware campaign.
  - TUNED: the four-family pool from F33 (dct, lda, lg, knn) with fit-time class
    weighting, where the accuracy was measured to live. On ULB it beat the
    frozen pool by +0.0319 at matched size, 10 of 10 seeds, exceeding the MDE.

Running only one would either lose comparability or omit the configuration the
evidence favours, which is why both run.

WHAT THIS TESTS THAT ULB CANNOT. ULB is 0.17% prevalence over 30 anonymized
components; IEEE-CIS is 3.5% over several hundred engineered features. The F33
finding was that fit-time class weighting drives the gain -- an intervention
whose entire purpose is coping with extreme imbalance. At 3.5% prevalence, 20x
ULB's rate, that mechanism has far less to do. A tuned-pool advantage that
shrinks or vanishes here would SUPPORT the F33 mechanism rather than contradict
it, and the plan says so in advance so the result is not read defensively.

Zero metered seconds. Feature count is held at the A12 free-tier ceiling so the
configuration stays hardware-runnable if a grant lands.

Usage:
    python experiments/src/run_ieee_cvqboost.py --smoke
    python experiments/src/run_ieee_cvqboost.py
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comparators as cmp
import data
import ieee_controls
import ieee_features
import ieee_loader
import ieee_splits
import mechanism_controls as mcx
import mixed_pool as mp
import qubo_proxy as qp
import store
import tuned_pool as tp

PROGRESS = Path(__file__).resolve().parents[1] / "results" / "ieee_cvq_progress.json"


def _progress(stage: str, **fields) -> None:
    """Heartbeat, so a long run is distinguishable from a hung one."""
    import datetime as _dt
    import json as _json
    rec = {"stage": stage, "at": _dt.datetime.now().isoformat(timespec="seconds"), **fields}
    try:
        PROGRESS.parent.mkdir(parents=True, exist_ok=True)
        PROGRESS.write_text(_json.dumps(rec, indent=2, default=str) + "\n")
    except Exception:                      # noqa: BLE001
        pass
    print(f"[{rec['at']}] {stage}: " +
          ", ".join(f"{k}={v}" for k, v in fields.items()), flush=True)

OUT = Path(__file__).resolve().parents[1] / "results" / "ieee_cvqboost.json"
K_FEATURES = 6            # four families x (6 + C(6,2)) = 60 vars, under A12's 100

# Pool construction is subsampled on IEEE-CIS. This is a COST decision with a
# protocol consequence, so it is stated rather than hidden.
#
# WHY: the H matrix requires every weak learner to predict on every training
# row. KNN has no training cost but its predict is O(n_train x n_query), so at
# 495,902 training rows the 21 KNN learners alone are ~5e11 distance
# computations per fold, single-threaded. The first attempt spent 84 minutes
# without finishing ONE fold and was killed by its own timeout.
#
# WHY THIS IS DEFENSIBLE: the weights are a 60-dimensional quantity fitted from
# the Gram matrix of learner agreements. That matrix converges long before
# half a million rows -- F31 measured its structure stably on ULB's 170k. The
# preregistration's H1c row ladder {25k, 50k, 100k, 200k, 400k} already treats
# subsampling at fixed feature count as an accepted device.
#
# WHAT IT COSTS: the weak learners see a sample, not the full fold. Reported
# with every figure, and the sample is drawn from the TRAINING rows only, so it
# cannot touch the evaluation month.
POOL_SUBSAMPLE_N = 100_000
SCHEDULE = 2
SEED = 42
# The ULB A5 MDE (0.0268) is NOT reused here. It was computed from pilot SEED
# variance over ten stratified splits at 0.17% prevalence; IEEE-CIS is three
# temporal FOLDS at 3.5%. Section 8 item 3 asks for an MDE computed from the
# design in question, and three folds cannot support one credibly. Differences
# are therefore reported DESCRIPTIVELY, with the fold spread stated, rather
# than against a threshold that does not apply (F3 pre-run audit finding 4).
ULB_MDE_DO_NOT_REUSE = 0.0268
MDE = None


def _top_k_numeric(X, y, k: int) -> list[str]:
    """Mutual-information top-k on TRAINING rows only, matching the ULB rule."""
    from sklearn.feature_selection import mutual_info_classif
    Xn = X.select_dtypes(include=[np.number]).fillna(0.0)
    mi = mutual_info_classif(Xn, y, random_state=SEED)
    order = np.argsort(mi)[::-1]
    return [Xn.columns[i] for i in order[:k]]


def _score(w, H):
    return np.clip((w @ H + 1.0) / 2.0, 0.0, 1.0)


def _solve(H_tr, y_pm1):
    lam = qp.LAMBDA_MULT * len(y_pm1)
    return mcx.solve_weighted(H_tr, y_pm1, lam, np.ones(len(y_pm1)))



def _jsonable(o):
    """Coerce numpy scalars to Python types before serialization.

    pandas returns int32/int64 and float32 for things like a month label, and
    json refuses them with a TypeError raised at write time -- AFTER the run has
    finished and the compute is spent. Coerce on the way in.
    """
    import numpy as _np
    if isinstance(o, dict):
        return {k: _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonable(v) for v in o]
    if isinstance(o, _np.generic):
        return o.item()
    return o

def run(smoke: bool = False) -> dict:
    from sklearn.metrics import average_precision_score as AP

    raw = data.load_ieee_cis_train()
    df, n_dupes = ieee_loader.dedupe_ieee(raw)
    if smoke:
        # Sample ACROSS the timespan, not the first 40k rows. Taking the head
        # lands entirely inside month 0, and the rolling-origin splitter then
        # correctly refuses ("need at least 4 month buckets, found 1"). A smoke
        # mode that cannot exercise the temporal protocol tests nothing that
        # matters here.
        df = (df.sort_values("TransactionDT")
                .iloc[::max(1, len(df) // 60_000)]
                .reset_index(drop=True))

    folds = ieee_splits.rolling_origin_folds(df)
    ieee_splits.assert_no_temporal_leakage(df, folds)
    if smoke:
        folds = folds[:1]

    rows = []
    for fi, fold in enumerate(folds):
        parts = ieee_splits.split_xy(df, fold)
        tr_df, ev_df = parts["X_train"], parts["X_eval"]
        y_tr, y_ev = parts["y_train"].to_numpy(), parts["y_eval"].to_numpy()

        pipe = ieee_features.IEEEFeaturePipeline()
        Xtr_all = pipe.fit_transform(tr_df)
        Xev_all = pipe.transform(ev_df)

        day_tr = ieee_features.add_day(tr_df).to_numpy()
        Xtr_num = Xtr_all.select_dtypes(include=[np.number])
        _progress("item4_start", fold=fi, n_features=Xtr_num.shape[1])
        ctrl = ieee_controls.apply_item4_controls(Xtr_num, y_tr, day_tr, seed=SEED)
        surviving = ctrl["features"] or list(Xtr_num.columns)
        _progress("item4_done", fold=fi, kept=len(surviving),
                  rounds=ctrl.get("adversarial_rounds"),
                  hit_round_cap=ctrl.get("adversarial_hit_round_cap"))

        cols = _top_k_numeric(Xtr_num[surviving], y_tr, K_FEATURES)
        X_tr = Xtr_num[cols].fillna(0.0).to_numpy(np.float32)
        X_ev = (Xev_all.select_dtypes(include=[np.number])
                .reindex(columns=cols).fillna(0.0).to_numpy(np.float32))
        y_pm1_full = np.where(y_tr == 1, 1, -1).astype(np.float64)

        # Subsample the POOL-CONSTRUCTION rows (training only; the evaluation
        # month is untouched and every AP below is computed on all of it).
        if len(y_tr) > POOL_SUBSAMPLE_N:
            rs = np.random.default_rng(SEED)
            idx = rs.choice(len(y_tr), size=POOL_SUBSAMPLE_N, replace=False)
            X_pool, y_pool = X_tr[idx], y_pm1_full[idx]
        else:
            idx = np.arange(len(y_tr))
            X_pool, y_pool = X_tr, y_pm1_full
        _progress("pool_rows", fold=fi, train_rows=int(len(y_tr)),
                  pool_rows=int(len(y_pool)),
                  pool_fraud=float((y_pool > 0).mean()))
        y_pm1 = y_pool

        # FROZEN arm: single family, library defaults.
        t0 = time.time()
        clf = qp.build_pool(X_pool, y_pool, schedule=SCHEDULE, weak_type="dct",
                            pair_build="seq")
        H_tr, H_ev = qp.h_matrix(clf, X_pool), qp.h_matrix(clf, X_ev)
        w = _solve(H_tr, y_pool)
        frozen_ap = float(AP(y_ev, _score(w, H_ev)))
        frozen_n = H_tr.shape[0]
        _progress("frozen_built", fold=fi, n_learners=int(frozen_n),
                  seconds=round(time.time() - t0, 1), ap=round(frozen_ap, 4))

        # TUNED arm: the F33 selected configuration, same fold and features.
        sel = tp.CANDIDATES["balanced_shallow_knn"]
        H_tr_t, H_ev_t, prov = [], [], []
        for fam, wp in sel.items():
            t1 = time.time()
            c = qp.build_pool(X_pool, y_pool, schedule=SCHEDULE, weak_type=fam,
                              pair_build="seq", weak_params=wp)
            h_tr_f = qp.h_matrix(c, X_pool)
            H_tr_t.append(h_tr_f)
            H_ev_t.append(qp.h_matrix(c, X_ev))
            prov.append({"family": fam, "params": dict(wp)})
            # Per-family heartbeat: the first attempt went silent for 84 minutes
            # inside this loop, so the cost was invisible until a CPU counter
            # revealed it. One line per family makes it obvious.
            _progress("family_built", fold=fi, family=fam,
                      n_learners=int(h_tr_f.shape[0]),
                      seconds=round(time.time() - t1, 1))
        H_tr_t, H_ev_t = np.vstack(H_tr_t), np.vstack(H_ev_t)
        w_t = _solve(H_tr_t, y_pm1)
        n_t = H_tr_t.shape[0]
        w_ut = np.full(n_t, 1.0 / n_t)
        tuned_ap = float(AP(y_ev, _score(w_t, H_ev_t)))
        tuned_uniform_ap = float(AP(y_ev, _score(w_ut, H_ev_t)))

        rows.append({
            "fold": fi, "eval_month": int(fold.eval_month),
            "n_train": int(len(y_tr)), "n_eval": int(len(y_ev)),
            "pool_rows": int(len(y_pm1)),
            "eval_prevalence": float(y_ev.mean()),
            "k_features": K_FEATURES, "features": cols,
            "frozen": {"n_variables": int(frozen_n), "ap": frozen_ap},
            "tuned": {"n_variables": int(n_t), "ap": tuned_ap,
                      "ap_uniform": tuned_uniform_ap,
                      "solved_minus_uniform": tuned_ap - tuned_uniform_ap,
                      "provenance": prov,
                      "gram_ratio": mp.diversity(H_tr_t, seed=SEED)["gram_ratio"]},
            "item4": {k: ctrl[k] for k in ("n_features_start",
                                           "n_after_time_consistency",
                                           "n_after_adversarial")},
            "evidence_tag": "SIM",
        })
        _progress("fold_done", fold=fi, eval_month=int(fold.eval_month),
                  frozen_ap=round(frozen_ap, 4), tuned_ap=round(tuned_ap, 4),
                  delta=round(tuned_ap - frozen_ap, 4),
                  frozen_vars=int(frozen_n), tuned_vars=int(n_t))

    fa = np.array([r["frozen"]["ap"] for r in rows])
    ta = np.array([r["tuned"]["ap"] for r in rows])
    d = ta - fa

    # Route the cross-arm difference through the guard: same k, same protocol,
    # same split, so it is a legitimate paired comparison -- and if a future
    # edit breaks that, this raises instead of serializing a bad number.
    tuned_arm = cmp.ArmSpec("tuned four-family", k=K_FEATURES,
                            protocol="rolling_origin", split="test",
                            dataset="ieee-cis")
    frozen_arm = cmp.ArmSpec("frozen single-family", k=K_FEATURES,
                             protocol="rolling_origin", split="test",
                             dataset="ieee-cis")
    headline = cmp.reported_difference(tuned_arm, float(ta.mean()),
                                       frozen_arm, float(fa.mean()))

    out = {
        "dataset": "ieee-cis",
        "protocol": "GroupKFold-by-month rolling origin",
        "smoke": smoke,
        "rows_after_dedupe": len(df),
        "exact_duplicates_removed": n_dupes,
        "pool_subsample": {
            "n": POOL_SUBSAMPLE_N,
            "applies_to": "weak-learner construction only; every AP is "
                          "computed on the full evaluation month",
            "reason": "KNN H-matrix build is O(n_train x n_query); the "
                      "unsubsampled first attempt did not finish one fold "
                      "in 84 minutes",
        },
        "scope_decision": ("both pools per the team lead 2026-09-05: frozen for "
                           "continuity with every prior result, tuned as the "
                           "configuration F33 measured the accuracy to live in"),
        "prediction_recorded_in_advance": (
            "F33 attributed the tuned pool's gain to FIT-TIME CLASS WEIGHTING, an "
            "intervention for extreme imbalance. IEEE-CIS is 3.5% prevalence "
            "against ULB's 0.17%, so that mechanism has far less to do here and "
            "the tuned advantage is expected to SHRINK. A smaller gap supports "
            "the mechanism; it does not contradict F33."),
        "frozen_mean_ap": float(fa.mean()),
        "tuned_mean_ap": float(ta.mean()),
        "paired_delta_mean": float(d.mean()),
        "paired_delta_sd": float(d.std(ddof=1)) if len(d) > 1 else None,
        "folds_positive": int((d > 0).sum()),
        "n_folds": len(rows),
        "matched_comparison": headline,
        "ulb_reference": {"paired_delta": 0.0319, "folds_positive": "10/10",
                          "note": "ULB, k=6, 10 seeds, exceeded the ULB MDE"},
        "mde_note": (
            "No MDE is applied to these figures. The ULB value of 0.0268 comes "
            "from pilot seed variance over ten stratified splits at 0.17% "
            "prevalence; this design is three temporal folds at 3.5%. Borrowing "
            "it would test against a threshold computed for a different dataset "
            "and a different split design. Three folds cannot support a credible "
            "MDE of their own, so differences are reported descriptively with "
            "the fold spread stated."),
        "per_fold": rows,
    }
    store.atomic_write_json(OUT, _jsonable(out))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    print(f"IEEE-CIS CVQBoost, both pools{' (SMOKE)' if args.smoke else ''}")
    o = run(smoke=args.smoke)
    print(f"\nfrozen mean AP {o['frozen_mean_ap']:.4f}")
    print(f"tuned  mean AP {o['tuned_mean_ap']:.4f}")
    print(f"paired delta   {o['paired_delta_mean']:+.4f} "
          f"({o['folds_positive']}/{o['n_folds']} folds positive)")
    print("no MDE applied; see mde_note in the results file")
    print(f"ULB reference: +0.0319, 10/10 seeds")
    return 0


if __name__ == "__main__":
    sys.exit(main())
