"""B3: the IEEE-CIS arm on Dirac-3, at the size the ceiling used to forbid.

The frozen grid (preregistration section 10) specifies B3 as the IEEE-CIS
reduced-recipe subset at full config plus the H3 ladder cells. It never ran: A12
established a free-tier ceiling of 100 continuous variables, and
`run_ieee_cvqboost.py` was written to `K_FEATURES = 6` -- "four families x
C(6,2) = 4 x 15 = 60 vars, under A12's 100", in its own comment.

A21 lifted that ceiling, so the arm can run at the recipe the preregistration
specifies.

WHY THIS IS A SEPARATE RUNNER rather than a flag on the proxy one. That module's
`run()` is a 176-line function with no reusable cell builder, and it produced the
[SIM] figures already published. Refactoring it at T-2 to extract one risks
changing evidence that is already in the submission, for no benefit to this arm.
This runner reuses the pieces where the PROTOCOL actually lives -- the loader,
the rolling-origin splitter, its leakage assertion, and the same feature pass --
so the comparison stays honest: identical upstream, different solver.

COST AND SAFETY. Every call goes through `metered_call.run_metered`, so the job
id reaches disk before the wait and the cost is the allocation balance delta
rather than a response field that vanishes on the paid tier (F47). The run stops
on a cumulative ceiling: the team lead approved the block in advance and is
asleep, and B2's per-fit cost is unanchored.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

import numpy as np
from sklearn.metrics import average_precision_score as AP, roc_auc_score

sys.path.insert(0, str(Path(__file__).resolve().parent))

import data                        # noqa: E402
import ieee_loader                 # noqa: E402
import ieee_splits                 # noqa: E402
import metered_call as mc          # noqa: E402
import qubo_proxy as qp            # noqa: E402
import store                       # noqa: E402

REPO = Path(__file__).resolve().parents[2]
RESULTS = Path(__file__).resolve().parents[1] / "results"
OUT = RESULTS / "b3_hardware.json"

SCHEDULE = 2
K_LADDER = (5, 9, 13, 17)          # H3 ladder, preregistration section 3
SUM_CONSTRAINT = 1.0
NUM_SAMPLES = 8                    # frozen; matches every prior hardware fit

# Standing authorization 2026-09-10: 27 fits across B3 and B2, hard ceiling.
SPEND_CEILING_S = 600.0
MAX_FITS = 16


def vars_at(k: int, schedule: int = SCHEDULE) -> int:
    """Sequential pair build: k singles + k(k-3)/2 pairs."""
    return k + k * (k - 3) // 2 if schedule >= 2 else k


def spent_so_far() -> float:
    led = mc.load_ledger()
    return sum(float(c.get("measured_seconds") or 0.0) for c in led.get("calls", []))


def _load_env() -> None:
    p = REPO / ".env"
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def _fold_y(df, fold):
    return ieee_splits.split_xy(df, fold)["y_train"].to_numpy()


def _prepare_fold(df, fold, k: int):
    """Exactly the published [SIM] arm's preparation, then top-k at OUR k.

    Reuses run_ieee_cvqboost's own helpers rather than restating them. The whole
    point of B3 is that everything upstream of the solve is identical to the arm
    already published, so any difference in the result is attributable to the
    device rather than to a different feature set.

    An earlier version ran mutual information over every raw numeric column,
    skipping the feature pipeline and the item-4 adversarial leakage controls.
    That would have produced a [HW] arm that is not comparable to the [SIM] one
    -- and it stalled, because MI over 400+ columns on 590k rows is minutes per
    fold before anything useful happens.
    """
    import ieee_controls
    import ieee_features
    import run_ieee_cvqboost as ieee

    t0 = time.perf_counter()
    parts = ieee_splits.split_xy(df, fold)
    tr_df, ev_df = parts["X_train"], parts["X_eval"]
    y_tr, y_ev = parts["y_train"].to_numpy(), parts["y_eval"].to_numpy()

    pipe = ieee_features.IEEEFeaturePipeline()
    Xtr_all = pipe.fit_transform(tr_df)
    Xev_all = pipe.transform(ev_df)

    day_tr = ieee_features.add_day(tr_df).to_numpy()
    Xtr_num = Xtr_all.select_dtypes(include=[np.number])
    ctrl = ieee_controls.apply_item4_controls(Xtr_num, y_tr, day_tr, seed=ieee.SEED)
    surviving = ctrl["features"] or list(Xtr_num.columns)

    cols = ieee._top_k_numeric(Xtr_num[surviving], y_tr, k)
    X_tr = Xtr_num[cols].fillna(0.0).to_numpy(np.float32)
    X_ev = (Xev_all.select_dtypes(include=[np.number])
            .reindex(columns=cols).fillna(0.0).to_numpy(np.float32))
    return X_tr, X_ev, y_ev, round(time.perf_counter() - t0, 1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="build pools and report sizes; submit nothing")
    ap.add_argument("--ks", type=int, nargs="*", default=list(K_LADDER))
    ap.add_argument("--folds", type=int, default=None,
                    help="limit folds (default: all rolling-origin folds)")
    args = ap.parse_args()

    print(f"B3: IEEE-CIS on Dirac-3, schedule {SCHEDULE}")
    for k in args.ks:
        v = vars_at(k)
        flag = "  <- A12 would have refused this" if v > 100 else ""
        print(f"  k={k:>2} -> {v:>4} variables{flag}")
    print()

    raw = data.load_ieee_cis_train()
    df, n_dupes = ieee_loader.dedupe_ieee(raw)
    folds = ieee_splits.rolling_origin_folds(df)
    ieee_splits.assert_no_temporal_leakage(df, folds)
    if args.folds:
        folds = folds[:args.folds]
    print(f"{len(folds)} rolling-origin folds, {len(df):,} rows\n")

    client = None
    if not args.dry_run:
        _load_env()
        from qci_client import QciClient
        client = QciClient(api_token=os.environ["QCI_TOKEN"],
                           url=os.environ["QCI_API_URL"])

    rows: list[dict] = []
    fits = 0
    t_start = time.perf_counter()

    for k in args.ks:
        for fi, fold in enumerate(folds):
            if fits >= MAX_FITS:
                print(f"STOP: {MAX_FITS} fits reached (authorized count).")
                break
            spent = spent_so_far()
            if spent >= SPEND_CEILING_S:
                print(f"STOP: cumulative spend {spent:.0f}s reached the "
                      f"{SPEND_CEILING_S:.0f}s ceiling.")
                break

            Xp, Xe, yev, prep_s = _prepare_fold(df, fold, k)
            y_pm1 = np.where(_fold_y(df, fold) == 1, 1, -1)

            t0 = time.perf_counter()
            clf = qp.build_pool(Xp, y_pm1, SCHEDULE, "dct", "seq")
            H_tr, H_ev = qp.h_matrix(clf, Xp), qp.h_matrix(clf, Xe)
            build_s = time.perf_counter() - t0
            n_vars = H_tr.shape[0]
            print(f"k={k} fold={fi}: prep {prep_s:.0f}s, pool {n_vars} vars "
                  f"built in {build_s:.0f}s", flush=True)

            if args.dry_run:
                rows.append({"k": k, "fold": fi, "n_variables": int(n_vars),
                             "build_seconds": round(build_s, 1), "dry_run": True})
                continue

            rec = mc.CallRecord(
                label=f"b3_k{k}_fold{fi}", degree=2, n_variables=int(n_vars),
                n_samples=NUM_SAMPLES,
                expected_seconds="4-10s (28 degree-2 anchors, within 2x)")
            try:
                res = _submit_via_eqc(client, Xp, y_pm1, rec)
            except Exception as e:                    # noqa: BLE001
                print(f"  FAILED: {type(e).__name__}: {str(e)[:200]}")
                rows.append({"k": k, "fold": fi, "n_variables": int(n_vars),
                             "status": "failed", "error": str(e)[:300],
                             "job_id": rec.job_id,
                             "metered_seconds": rec.measured_seconds})
                fits += 1
                continue

            w = _weights(res, n_vars)
            scores_ev = np.clip((w @ H_ev + 1.0) / 2.0, 0.0, 1.0)
            rows.append({
                "k": k, "fold": fi, "n_variables": int(n_vars),
                "build_seconds": round(build_s, 1),
                "job_id": rec.job_id, "metered_seconds": rec.measured_seconds,
                "status": "ok", "evidence_tag": "HW",
                "auprc": float(AP(yev, scores_ev)),
                "auc_roc": float(roc_auc_score(yev, scores_ev)),
                "eval_prevalence": float(np.mean(yev)),
            })
            fits += 1
            print(f"  job={rec.job_id} cost={rec.measured_seconds}s "
                  f"AUPRC={rows[-1]['auprc']:.4f}", flush=True)
        else:
            continue
        break

    out = {
        "note": ("B3: IEEE-CIS arm on Dirac-3 at the frozen recipe. A12's 100-variable "
                 "ceiling forced the published [SIM] arm down to k=6; A21 lifted it."),
        "generator": "experiments/src/run_hardware_b3.py",
        "evidence_tag": "HW",
        "schedule": SCHEDULE,
        "k_ladder": list(args.ks),
        "num_samples": NUM_SAMPLES,
        "dry_run": bool(args.dry_run),
        "fits": fits,
        "total_metered_seconds": sum(float(r.get("metered_seconds") or 0) for r in rows),
        "elapsed_sec": round(time.perf_counter() - t_start, 1),
        "rows": rows,
    }
    store.atomic_write_json(OUT, out)
    print(f"\n{fits} fits, {out['total_metered_seconds']}s metered")
    print(f"written: {OUT}")
    return 0


def _submit_via_eqc(client, X, y_pm1, rec: "mc.CallRecord"):
    """Submit through eqc-models, so the Hamiltonian is THEIRS, not ours.

    ADR-0002 rests on the proxy and the device solving the same problem because
    both build their pools and operators through eqc-models. Hand-constructing a
    job body here would be a reimplementation that can drift, which is exactly
    what that ADR rejects.

    The cost and the job id still come from metered_call's discipline: balance
    read before and after, intent on disk before the call, outcome after. The id
    is recovered from the client's own job record, since QBoostClassifier.fit
    does not return it.
    """
    from eqc_models.ml.classifierqboost import QBoostClassifier

    rec.submitted_utc = mc._utc()
    rec.balance_before = mc.balance(client)
    log = mc.UnbufferedLog(mc.LOG_DIR / f"{rec.label}_{time.strftime('%Y%m%dT%H%M%S')}.log")
    log.write(f"INTENT {rec.label} vars={rec.n_variables} expected={rec.expected_seconds} "
              f"balance={rec.balance_before}")
    mc.append_ledger(rec)

    cfg = dict(lambda_coef=qp.LAMBDA_MULT * len(y_pm1),
               weak_cls_schedule=SCHEDULE, weak_cls_type="dct",
               weak_cls_params={}, weak_cls_strategy="sequential", **qp.FIXED)
    clf = QBoostClassifier(api_url=os.environ["QCI_API_URL"],
                           api_token=os.environ["QCI_TOKEN"], **cfg)
    try:
        resp = clf.fit(X, y_pm1)
        rec.status = "ok"
        return {"results": {"solutions": [list(getattr(resp, "solutions", [[]])[0])]}} \
            if hasattr(resp, "solutions") else resp
    except Exception as e:                            # noqa: BLE001
        rec.status = "failed"
        rec.error = f"{type(e).__name__}: {str(e)[:400]}"
        log.write(f"FAILED {rec.error}")
        raise
    finally:
        rec.balance_after = mc.balance(client)
        rec.measured_seconds = float(rec.balance_before - rec.balance_after)
        rec.finished_utc = mc._utc()
        log.write(f"BALANCE after={rec.balance_after} cost={rec.measured_seconds}")
        mc.append_ledger(rec)


def _weights(res, n_vars):
    sol = res["results"]["solutions"][0]
    w = np.asarray(sol, dtype=float)[:n_vars]
    s = w.sum()
    return w / s if s > 0 else np.full(n_vars, 1.0 / n_vars)


if __name__ == "__main__":
    raise SystemExit(main())
