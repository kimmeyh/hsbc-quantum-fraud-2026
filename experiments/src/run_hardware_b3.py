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
# The [SIM] ladder this arm is compared against subsamples POOL-CONSTRUCTION
# rows to 100,000 (`run_ieee_h3.py:57`). The first B3 run did NOT, so its pools
# saw the whole training fold -- 4.1x to 5.8x more rows than the arm it was
# quoted against, growing with the fold. That is not a speed detail: the QUBO's
# lambda_coef is LAMBDA_MULT * len(y), so the two arms did not even solve the
# same regularized objective, and the [HW]-over-[SIM] gap grew monotonically
# with k (+0.0000, +0.0112, +0.0294, +0.0330). Dirac-3 is a WORSE optimizer
# than the exact proxy, so hardware beating its own proxy could not have been
# the solver; it was the extra data. Found by adversarial review after the
# first run was published, which is why A22 needed superseding.
POOL_SUBSAMPLE_N = 100_000

SPEND_CEILING_S = 900.0   # raised from 600 by the team lead, 2026-09-10
MAX_FITS = 16


def vars_at(k: int, schedule: int = SCHEDULE) -> int:
    """Variable count for the sequential (pairs-only) build at schedule >= 2.

    The sequential build includes pairs but NOT singles: eqc-models with
    ``weak_cls_strategy="sequential"`` produces C(k, 2) = k*(k-1)/2
    classifiers (qubo_proxy.py: "78 vars sequential / 91 full-pair" at k=13).
    The expression ``k + k*(k-3)//2`` is algebraically equal to k*(k-1)//2 and
    was written to surface the eqc-models pair-cap guard (``n*(n-3)/2 <= 0``),
    not to imply k singles are present.
    """
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


def _prepare_fold_once(df, fold):
    """The EXPENSIVE half, done once per fold: pipeline + item-4 controls.

    Measured at 582s against a 9s pool build, and it does not depend on k --
    `apply_item4_controls(X_train, y_train, day_train, seed)` takes no k, and
    only the final top-k slice varies. Preparing once per fold and slicing per k
    is the same work in a different order: 12 cells x 591s = 2.0 hours becomes
    3 folds x 582s + 12 x 9s = 31 minutes.
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

    # Subsample POOL-CONSTRUCTION rows only, matching run_ieee_h3.py exactly:
    # same size, same default_rng(SEED), drawn once per fold and shared across
    # every k so the ladder rungs stay nested. The evaluation month is NOT
    # touched -- every AP below is computed on all of it.
    rs = np.random.default_rng(ieee.SEED)
    pool_idx = (rs.choice(len(y_tr), size=POOL_SUBSAMPLE_N, replace=False)
                if len(y_tr) > POOL_SUBSAMPLE_N else np.arange(len(y_tr)))

    return {
        "Xtr_num": Xtr_num, "Xev_num": Xev_all.select_dtypes(include=[np.number]),
        "surviving": surviving, "y_tr": y_tr, "y_ev": y_ev,
        "pool_idx": pool_idx,
        "n_train_rows": int(len(y_tr)),
        "n_pool_rows": int(len(pool_idx)),
        "prep_seconds": round(time.perf_counter() - t0, 1),
        "n_surviving": len(surviving),
    }


def _slice_at_k(prep: dict, k: int):
    """The CHEAP half: top-k over the surviving features, per k.

    X_tr is restricted to the fold's pool subsample so the pool is built on the
    same rows the [SIM] arm builds on. X_ev is untouched: evaluation always uses
    the whole month.
    """
    import run_ieee_cvqboost as ieee
    cols = ieee._top_k_numeric(prep["Xtr_num"][prep["surviving"]], prep["y_tr"], k)
    X_tr = prep["Xtr_num"][cols].fillna(0.0).to_numpy(np.float32)[prep["pool_idx"]]
    X_ev = prep["Xev_num"].reindex(columns=cols).fillna(0.0).to_numpy(np.float32)
    return X_tr, X_ev, cols


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

    def _write_artifact(rows, fits, args, t_start, complete):
        """Write the block artifact. Called after EVERY fit, not only at the end.

        F65. The runner used to build this dict once, after the loop, so a
        process that died after a billed call left NO artifact even though the
        money was spent. Sprint 12's first B2 fit did exactly that -- a WSL
        teardown on parent-shell exit, no traceback. Nothing was lost that time
        because the raw response, the predictions and a full results.json row
        had all persisted first, which was luck rather than structure.

        At roughly 5 seconds per B3 fit the loss would have been small; at the
        91 metered seconds a B2-class fit costs, one lost fit is real money
        against a finite allocation.

        `complete` records whether the loop finished, so a reader can tell a
        partial artifact from a whole one instead of guessing from the count.
        """
        out = {
            "note": ("B3: IEEE-CIS arm on Dirac-3 at the frozen recipe. A12's 100-variable "
                     "ceiling forced the published [SIM] arm down to k=6; A21 lifted it."),
            "generator": "experiments/src/run_hardware_b3.py",
            "evidence_tag": "HW",
            "schedule": SCHEDULE,
            "k_ladder": list(args.ks),
            "num_samples": NUM_SAMPLES,
            "dry_run": bool(args.dry_run),
            "complete": bool(complete),
            "fits": fits,
            "total_metered_seconds": sum(float(r.get("metered_seconds") or 0) for r in rows),
            "elapsed_sec": round(time.perf_counter() - t_start, 1),
            "by_k": _mean_by_k(rows),
            "rows": rows,
        }
        store.atomic_write_json(OUT, out)
        return out

    # Folds OUTSIDE, k INSIDE: prep is 582s per fold and does not depend on k,
    # so preparing once and slicing per k turns 2.0 hours into 31 minutes.
    stop_all = False
    for fi, fold in enumerate(folds):
        if stop_all:
            break
        print(f"--- fold {fi}: preparing (pipeline + item-4 controls) ---", flush=True)
        prep = _prepare_fold_once(df, fold)
        print(f"    prep {prep['prep_seconds']}s, {prep['n_surviving']} features "
              f"survived", flush=True)
        # Labels must follow the pool rows, not the full fold: Xp is subsampled
        # in _slice_at_k, so y_pm1 is indexed identically or the two misalign.
        y_pm1 = np.where(prep["y_tr"][prep["pool_idx"]] == 1, 1, -1).astype(np.float64)
        yev = prep["y_ev"]

        for k in args.ks:
            if fits >= MAX_FITS:
                print(f"STOP: {MAX_FITS} fits reached (authorized count).")
                stop_all = True
                break
            spent = spent_so_far()
            if spent >= SPEND_CEILING_S:
                print(f"STOP: cumulative spend {spent:.0f}s reached the "
                      f"{SPEND_CEILING_S:.0f}s ceiling.")
                stop_all = True
                break

            Xp, Xe, _cols = _slice_at_k(prep, k)
            prep_s = prep["prep_seconds"]

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
                _write_artifact(rows, fits, args, t_start, complete=False)
                continue

            w = _weights(res, n_vars)
            scores_ev = np.clip((w @ H_ev + 1.0) / 2.0, 0.0, 1.0)
            rows.append({
                "k": k, "fold": fi, "n_variables": int(n_vars),
                "build_seconds": round(build_s, 1),
                # Recorded so the artifact itself proves the [HW] and [SIM] arms
                # built their pools on the same rows. The first B3 run's whole
                # defect was invisible because nothing stored this.
                "n_train_rows": prep["n_train_rows"],
                "n_pool_rows": prep["n_pool_rows"],
                "job_id": rec.job_id, "metered_seconds": rec.measured_seconds,
                "status": "ok", "evidence_tag": "HW",
                "auprc": float(AP(yev, scores_ev)),
                "auc_roc": float(roc_auc_score(yev, scores_ev)),
                "eval_prevalence": float(np.mean(yev)),
            })
            fits += 1
            # Persist BEFORE printing: the artifact is the evidence, and a crash
            # between the billed call and the write is the case F65 exists for.
            _write_artifact(rows, fits, args, t_start, complete=False)
            print(f"  job={rec.job_id} cost={rec.measured_seconds}s "
                  f"AUPRC={rows[-1]['auprc']:.4f}", flush=True)

    _write_artifact(rows, fits, args, t_start, complete=True)
    total = sum(float(r.get("metered_seconds") or 0) for r in rows)
    print(f"\n{fits} fits, {total}s metered")
    print(f"written: {OUT}")
    return 0


def _mean_by_k(rows: list[dict]) -> list[dict]:
    """Fold means per k, STORED rather than recomputed in prose.

    The ladder is quoted in the papers as a mean over folds. A figure that lives
    only in a document and in nobody's artifact is exactly what F44 exists to
    prevent, so the runner persists the means it will be quoted by.
    """
    out = []
    for k in sorted({r["k"] for r in rows if r.get("status") == "ok"}):
        cells = [r for r in rows if r["k"] == k and r.get("status") == "ok"]
        if not cells:
            continue
        n = len(cells)
        out.append({
            "k": k,
            "n_variables": cells[0]["n_variables"],
            "folds": n,
            "auprc_mean": round(sum(c["auprc"] for c in cells) / n, 4),
            "auc_roc_mean": round(sum(c["auc_roc"] for c in cells) / n, 4),
            "eval_prevalence_mean": round(
                sum(c["eval_prevalence"] for c in cells) / n, 4),
            "metered_seconds": sum(float(c.get("metered_seconds") or 0) for c in cells),
            "evidence_tag": "HW",
        })
    return out


def _find_job_id(resp) -> str | None:
    """Recover the job id from whatever shape the response takes.

    `get_job_results` returns {"job_info": {"job_id": ...}} -- confirmed against
    the retained campaign jobs -- and eqc-models passes the response through.
    Searched rather than indexed, because the paid tier already changed one
    response format out from under a hardcoded path (the device_usage_s scrape).
    """
    seen: list[str] = []

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "job_id" and isinstance(v, str) and len(v) == 24:
                    seen.append(v)
                walk(v)
        elif isinstance(o, (list, tuple)):
            for v in o:
                walk(v)

    walk(resp if isinstance(resp, (dict, list, tuple))
         else getattr(resp, "__dict__", {}))
    if not seen:
        import re
        m = re.search(r"'job_id':\s*'([0-9a-f]{24})'", repr(resp))
        if m:
            seen.append(m.group(1))
    return seen[0] if seen else None


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
        rec.job_id = _find_job_id(resp)
        if rec.job_id:
            log.write(f"JOB_ID {rec.job_id}")
        else:
            rec.notes.append("job id not found in the response; result is not "
                             "retrievable by id (F47 gap)")
            log.write("WARNING no job id in response")
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
