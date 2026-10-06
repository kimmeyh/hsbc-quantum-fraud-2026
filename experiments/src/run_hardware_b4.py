"""B4: the SPECTRA in-segment replication on Dirac-3, feasible cells only.

Block B4 of the frozen grid (PREREGISTRATION section 10): "SPECTRA
replication, 3 strongest in-segment cells x 5 seeds | 15 fits | ~450 QPU s |
gated on QCi grant + SPECTRA re-download". This is the replication half of
Experiment 5, segment transfer (H5), and F90 is its card.

IT RUNS 10 OF THE 15 CELLS, NOT ALL 15, and that is a reported subset rather
than a protocol change. energy_steel cannot produce the rate-matched control
H5(ii) requires on any of its five seeds: the pocket holds 918-950 of the test
fold's positives while the complement holds only 832-864, so a
size-and-rate-matched draw from outside the segment is arithmetically
impossible. Those five cells are reported `unscoreable`, which is an outcome
the gate table already has a column for (pass / fail / null / unscoreable).

`experiments/PREREGISTRATION.md` IS NOT AMENDED. Section 11 forbids an
amendment that changes a gate's pass/fail criterion, and H5(ii)'s control IS
that criterion; such a change would be a reported DEVIATION. Running a subset
of frozen cells needs no amendment. The repaired design -- a downsized matched
pair on both sides, repeated over draws -- is specified for PHASE 2 in F102,
where it is new specification against data that does not exist yet rather than
a retrofit onto observed results. Full analysis:
`docs/SPECTRA_CONTROL_FEASIBILITY.md`.

COST, and an open conflict this block settles. F90's card prices B4 from B2's
measured 82.4 s/fit at 833 variables; `HARDWARE_REQUEST_B4.md` line 43 prices
it from FourierWall2's rollout at 26-34 s/fit for 560-816 variables at this
exact ns/rx/schedule, and cites the frozen envelope of ~450 s. Both are
described as measured and they disagree by a factor of 2.4. The 10 feasible
fits are 5 at 816 variables and 5 at 560:

  - at the B2 anchor rate      : about 676 s
  - at the FourierWall2 rate   : about 250 s

The band is stated to the team lead as **250-680 s** rather than a single
number, because quoting either alone would present a contested figure as
settled -- which is the Sprint 11 defect that had a probe approved at "0-5
seconds" cost 10. B5 runs first and lands a fresh measurement.

Criterion H: the team lead approved B5 and B4 on 2026-10-05 ("both qci runs
are approved - no need to ask again this sprint") and directed that all
Dirac-3 calls wait until 18:00 local that day.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import data                                   # noqa: E402
import metered_call as mc                     # noqa: E402
import qubo_proxy                             # noqa: E402
import spectra_segment as ss                  # noqa: E402
import store                                  # noqa: E402

log = logging.getLogger("b4")

BLOCK = "B4"
ARM = "cvqboost_hw_spectra"
SEEDS = (42, 43, 44, 45, 46)

EXPECTED_SECONDS = ("250-680 s for 10 fits: ~676 s at B2's measured 82.4 s/fit "
                    "at 833 vars, ~250 s at HARDWARE_REQUEST_B4 line 43's "
                    "26-34 s/fit for 560-816 vars. The two anchors disagree "
                    "by 2.4x and both are described as measured")
EXPECTED_CEILING_S = 760.0
BLOCK_CAP_S = 760.0
ALLOCATION_FLOOR_S = 776.0

RESULTS = qubo_proxy.RESULTS
ARTIFACT = qubo_proxy.RESULTS_DIR / "b4_hardware.json"
WINDOW_HOUR = 18


def feasible_specs() -> list[dict]:
    """The cells whose H5(ii) control can actually be drawn.

    Feasibility is recomputed from the data every run, never hardcoded: if a
    data refresh moves a cell across the line, this runner follows it and
    `test_control_feasibility.py` fails loudly about the record being stale.
    """
    out = []
    for cell in ss.FROZEN_CELLS:
        name = cell["dataset"].replace("spectra_", "")
        for seed in SEEDS:
            split, _cols = ss._prep_spectra(name, seed)
            y = split.y_test.to_numpy()
            ip = split.X_test[ss.SEGMENT_FLAG].to_numpy().astype(bool)
            feas = ss.control_feasibility(ip, y)
            out.append(dict(block=BLOCK, dataset=cell["dataset"], cell=name,
                            seed=seed, config_hash=cell["config_hash"],
                            feasible=feas["feasible"], feasibility=feas))
    return out


def _done() -> set:
    """Successful B4 cells already in results.json. Idempotent before the
    first approval, not after the first over-spend (Sprint 18 IMP-3)."""
    if not RESULTS.exists():
        return set()
    try:
        rows = json.loads(RESULTS.read_text(encoding="utf-8"))["rows"]
    except Exception as exc:                              # noqa: BLE001
        raise SystemExit(
            f"B4 refuses to submit: results.json is unreadable ({exc}). A "
            "runner that cannot read its own ledger cannot know what it has "
            "already paid for.")
    return {(r["arm"], r.get("dataset"), r["seed"])
            for r in rows
            if r.get("block") == BLOCK and r.get("status") != "failed"}


def _spent() -> float:
    if not RESULTS.exists():
        return 0.0
    rows = json.loads(RESULTS.read_text(encoding="utf-8"))["rows"]
    return sum(float(r.get("metered_seconds") or 0)
               for r in rows if r.get("block") == BLOCK)


def _window_open(now: datetime | None = None) -> bool:
    return (now or datetime.now()).hour >= WINDOW_HOUR


def _fit_one(client, spec: dict, dry_run: bool) -> dict:
    """One SPECTRA cell on hardware. Mirrors `proxy_dry_run_cell` exactly up
    to the solve, so the only difference between the PROJ and HW rows is where
    the weights came from."""
    name = spec["cell"]
    cell = ss.frozen_cell_by_name(name)
    split, cols = ss._prep_spectra(name, spec["seed"])
    n_features = len(cols)
    assert n_features == cell["config"]["n_features"], (
        f"{name}: frozen cell expects {cell['config']['n_features']} "
        f"features, got {n_features}")

    Xtr = ss.coerce_features_to_numeric(split.X_train[cols]).to_numpy(dtype="float32")
    Xte = ss.coerce_features_to_numeric(split.X_test[cols]).to_numpy(dtype="float32")
    y_train01 = split.y_train.to_numpy()
    y_test01 = split.y_test.to_numpy()
    in_pocket_test = split.X_test[ss.SEGMENT_FLAG].to_numpy().astype(bool)
    y_pm1 = np.where(y_train01 == 1, 1, -1)

    schedule = cell["config"]["weak_cls_schedule"]
    n_vars = data.qubo_vars(n_features, schedule, pair_build="sequential")
    lam = cell["config"]["lambda_coef_alpha"] * len(y_pm1)

    clf = qubo_proxy.build_pool(Xtr, y_pm1, schedule, weak_type="dct",
                                pair_build="sequential", lambda_coef=lam)
    H_tr = qubo_proxy.h_matrix(clf, Xtr)
    H_te = qubo_proxy.h_matrix(clf, Xte)

    if dry_run:
        return {"arm": ARM, "block": BLOCK, "dataset": spec["dataset"],
                "seed": spec["seed"], "config_hash": spec["config_hash"],
                "n_vars_expected": n_vars,
                # h_matrix is (n_vars, n_rows): the weak-learner count is
                # shape[0]. shape[1] is the row count, which printed 22,039
                # "weak classifiers" for a 560-variable cell in the first dry run.
                "n_weak_classifiers": H_tr.shape[0],
                "n_train_rows": H_tr.shape[1],
                "evidence_tag": "SIM", "metered_seconds": 0,
                "status": "dry_run", "features_used": list(cols)}

    rec = mc.CallRecord(
        label=f"b4_{name}_{spec['seed']}",
        degree=2, n_variables=n_vars,
        n_samples=cell["config"]["num_samples"],
        expected_seconds=EXPECTED_SECONDS)

    # J = HH^T + lam*I, C = -2Hy -- copied from qubo_proxy.solve_simplex_qp,
    # which is the identical Hamiltonian eqc-models ships to Dirac-3 (ADR-0002).
    # h_matrix returns (n_vars, n_rows), so the contraction is H @ H.T; the
    # transposed form H.T @ H builds an (n_rows x n_rows) matrix instead, which
    # at 22,039 rows is a 3.6 GB allocation rather than a wrong-but-small answer.
    J = (H_tr @ H_tr.T).astype(np.float64) + lam * np.eye(n_vars)
    C = (-2.0 * H_tr @ y_pm1).astype(np.float64)
    body = {"job_submission": {
        "problem_config": {
            "quadratic_linearly_constrained_binary_optimization": None},
        "device_config": {"dirac-3": {
            "num_samples": cell["config"]["num_samples"],
            "relaxation_schedule": cell["config"]["relaxation_schedule"],
            "sum_constraint": 1.0}},
        "job_name": f"b4_{name}_{spec['seed']}",
        "_J": J.tolist(), "_C": C.tolist()}}

    resp = mc.run_metered(client, body, rec)
    sols = (resp.get("results", {}) or {}).get("solutions")
    if not sols:
        raise RuntimeError("no solutions in the Dirac-3 response")

    # EVERY returned sample is stored, not only the lowest-energy one (F90
    # acceptance (c)). That is what makes F20's multi-sample ensembling cost no
    # further device time.
    all_w = [np.asarray(s, dtype="float64") for s in sols]
    w = all_w[0]
    assert len(w) == n_vars, f"solution width {len(w)} != {n_vars}"

    p_test = np.clip((w @ H_te + 1.0) / 2.0, 0.0, 1.0)

    # Weight cosine against the classical solve: forced sparsity under A31's
    # ~200-learner resolution limit is the EXPECTED mechanism here, not a
    # defect, so it is recorded rather than checked against a threshold.
    w_cls = qubo_proxy.solve_simplex_qp(H_tr, y_pm1, lam)
    denom = float(np.linalg.norm(w) * np.linalg.norm(w_cls))
    cosine = float(w @ w_cls / denom) if denom > 0 else None

    seg = ss.evaluate_in_segment(y_test01, p_test, in_pocket_test,
                                 spec["seed"], label="target")
    from sklearn.metrics import average_precision_score, roc_auc_score

    # The train-test gap beside every win (F90 acceptance, 2026-10-03): the
    # in-segment wins in the prior work came with a gap well above XGBoost's,
    # one case 0.98 train to 0.59 test. A win without its gap is not reportable.
    # h_matrix returns (n_vars, n_rows), so `w @ H` is the row-wise score --
    # the same orientation `proxy_dry_run_cell` uses for H_te. Checked, not
    # assumed: `w @ H_tr.T` runs without error and returns n_vars values
    # instead of n_rows, which would score the wrong axis silently.
    p_train = np.clip((w @ H_tr + 1.0) / 2.0, 0.0, 1.0)
    train_ap = float(average_precision_score(y_train01, p_train))
    test_ap = float(average_precision_score(y_test01, p_test))

    return {
        "arm": ARM, "block": BLOCK, "dataset": spec["dataset"],
        "seed": spec["seed"], "protocol": "stratified",
        "config_hash": spec["config_hash"],
        "n_vars_expected": n_vars, "n_weak_classifiers": H_tr.shape[0],
        "n_train_rows": H_tr.shape[1],
        "evidence_tag": "HW",
        "metered_seconds": rec.measured_seconds,
        "metered_seconds_parsed": rec.measured_seconds is not None,
        "job_id": rec.job_id, "status": rec.status, "retry_count": 0,
        "features_used": list(cols),
        "weight_cosine_vs_classical": cosine,
        "n_samples_returned": len(all_w),
        "all_samples": [s.tolist() for s in all_w],
        "metrics": {"auprc": test_ap,
                    "auc_roc": float(roc_auc_score(y_test01, p_test)),
                    "train_auprc": train_ap,
                    "train_test_ap_gap": round(train_ap - test_ap, 4)},
        "in_segment": seg,
        "timestamps": {"submitted_utc": rec.submitted_utc,
                       "finished_utc": rec.finished_utc},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max-calls", type=int, default=10)
    ap.add_argument("--ignore-window", action="store_true")
    args = ap.parse_args()

    print(f"BLOCK {BLOCK}: SPECTRA in-segment replication on Dirac-3")
    print("  computing cell feasibility from the data ...", flush=True)
    all_specs = feasible_specs()
    feasible = [s for s in all_specs if s["feasible"]]
    infeasible = [s for s in all_specs if not s["feasible"]]

    done = _done()
    todo = [s for s in feasible
            if (ARM, s["dataset"], s["seed"]) not in done]

    print(f"  cells in the frozen grid : {len(all_specs)}")
    print(f"  FEASIBLE (control drawable): {len(feasible)}")
    print(f"  unscoreable (reported)   : {len(infeasible)}  "
          f"{sorted({s['cell'] for s in infeasible})}")
    print(f"  already complete         : {len(done)}")
    print(f"  CALL COUNT now           : {min(len(todo), args.max_calls)}")
    print(f"  EXPECTED SECONDS         : {EXPECTED_SECONDS}")
    print(f"  provenance               : CONTESTED, band quoted; B5 lands a "
          f"fresh measurement first")
    print(f"  block cap                : {BLOCK_CAP_S} s")
    print(f"  spent on {BLOCK} so far      : {_spent():.1f} s")
    print(f"  approved                 : team lead 2026-10-05, window 18:00 local")
    print()
    for s in infeasible:
        print(f"    unscoreable: {s['cell']} seed {s['seed']} -- "
              f"{s['feasibility']['reason'][:88]}")
    print()

    if not todo:
        print("Nothing to do: every feasible B4 cell is already complete.")
        return 0

    if args.dry_run:
        for s in todo[:args.max_calls]:
            r = _fit_one(None, s, dry_run=True)
            print(f"  [dry] {s['cell']:18s} seed={s['seed']} "
                  f"vars={r['n_vars_expected']} pool={r['n_weak_classifiers']}")
        print("\nDry run: nothing submitted, nothing spent.")
        return 0

    # A TEST PROCESS MAY NEVER SPEND DEVICE SECONDS (Sprint 21). Two of my own
    # window-guard tests invoked this runner with `--max-calls 1` and checked
    # for "REFUSING" only AFTER the subprocess returned, so once the 18:00
    # window opened the guard correctly allowed the run and the tests
    # submitted real jobs -- 20:57 and 21:02 local on 2026-10-05, no Criterion
    # H statement read by anyone. Nothing was billed by luck alone: a
    # malformed job body and an SSL error.
    #
    # The tests are fixed; this is the structural fix. The allocation has no
    # undo, and a runner a test can fire is one careless parametrize away from
    # spending the balance.
    if "PYTEST_CURRENT_TEST" in os.environ or "pytest" in sys.modules:
        print("REFUSING: a metered run was invoked from a test process. "
              "Tests exercise --dry-run and source-level checks only; "
              "spending device seconds requires a human-invoked run.")
        return 5

    if not (_window_open() or args.ignore_window):
        print(f"REFUSING: the team lead set the Dirac-3 window at "
              f"{WINDOW_HOUR}:00 local and it is {datetime.now():%H:%M}. "
              f"Re-run after the window, or pass --ignore-window to override "
              f"an explicit instruction.")
        return 3

    _load_env()
    from qci_client import QciClient
    client = QciClient(api_token=os.environ["QCI_TOKEN"],
                       url=os.environ["QCI_API_URL"])

    bal = mc.balance(client)
    if bal is not None and bal - EXPECTED_CEILING_S < ALLOCATION_FLOOR_S:
        print(f"REFUSING: balance {bal} s minus this block's ceiling "
              f"{EXPECTED_CEILING_S} s would breach the "
              f"{ALLOCATION_FLOOR_S} s floor.")
        return 4

    rows, spent = [], 0.0
    t0 = time.perf_counter()
    for i, spec in enumerate(todo[:args.max_calls], 1):
        if spent >= BLOCK_CAP_S:
            print(f"  block cap {BLOCK_CAP_S} s reached; stopping with "
                  f"{len(rows)} fits")
            break
        print(f"  [{i}/{min(len(todo), args.max_calls)}] {spec['cell']} "
              f"seed={spec['seed']} ...", flush=True)
        row = _fit_one(client, spec, dry_run=False)
        rows.append(row)
        spent += float(row.get("metered_seconds") or 0)
        store.append_row(row)
        _write_artifact(rows, infeasible, spent, t0, complete=False)

    _write_artifact(rows, infeasible, spent, t0, complete=True)
    print(f"\nB4 done: {len(rows)} fits, {spent:.1f} metered seconds.")
    return 0


def _write_artifact(rows, infeasible, spent, t0, complete: bool) -> None:
    """Written after EVERY fit (F65): a runner that built its artifact once at
    the end lost a billed B2 fit to a shell teardown."""
    ARTIFACT.write_text(json.dumps({
        "note": ("B4: SPECTRA in-segment replication on Dirac-3, the 10 cells "
                 "whose H5(ii) control can be drawn. The 5 energy_steel cells "
                 "are reported unscoreable; see "
                 "docs/SPECTRA_CONTROL_FEASIBILITY.md."),
        "generator": "experiments/src/run_hardware_b4.py",
        "evidence_tag": "HW",
        "block": BLOCK, "arm": ARM,
        "complete": bool(complete),
        "fits": len(rows),
        "total_metered_seconds": round(spent, 2),
        "elapsed_sec": round(time.perf_counter() - t0, 1),
        "unscoreable_cells": [
            {"dataset": s["dataset"], "seed": s["seed"],
             "reason": s["feasibility"].get("reason"),
             "segment_positives": s["feasibility"]["segment_positives"],
             "complement_positives": s["feasibility"]["complement_positives"]}
            for s in infeasible],
        "rows": rows,
    }, indent=2), encoding="utf-8")


def _load_env() -> None:
    env = Path(__file__).resolve().parents[2] / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
    for k in ("QCI_TOKEN", "QCI_API_URL"):
        if not os.environ.get(k):
            raise SystemExit(f"{k} is not set; B4 cannot submit.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    raise SystemExit(main())
