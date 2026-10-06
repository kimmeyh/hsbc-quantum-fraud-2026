"""B4: the SPECTRA in-segment replication on Dirac-3, feasible cells only.

Block B4 of the frozen grid (PREREGISTRATION section 10): "SPECTRA
replication, 3 strongest in-segment cells x 5 seeds | 15 fits | ~450 QPU s".
The replication half of Experiment 5, segment transfer (H5); F90 is its card.

SUBMITS THROUGH eqc-models, EXACTLY AS B2 AND B3 DID. `QBoostClassifier.fit`
builds the weak-learner pool and the Hamiltonian and makes ONE metered call,
with the configuration `spectra_segment.FROZEN_CELLS` encodes: schedule 3,
8 samples, relaxation schedule 2, lambda = 2 x n_train, sequential pool build.
B2 ran that identical configuration (only `pair_build` and dataset differ),
which is why its 82.4 s/fit is the cost anchor. The first version of this
runner hand-built the job body instead, with invented field names, and QCi
rejected it; see `eqc_submit.py`.

IT RUNS 10 OF THE 15 CELLS, a reported subset needing no amendment.
energy_steel cannot produce the rate-matched control H5(ii) requires on any of
its five seeds (pocket 918-950 test positives, complement 832-864), so those
five cells are `unscoreable` -- an outcome the gate table already has a column
for. `experiments/PREREGISTRATION.md` is NOT amended (section 11).
`docs/SPECTRA_CONTROL_FEASIBILITY.md` has the analysis.

COST is quoted as a band, 250-680 s, because the two anchors disagree by 2.4x
and both are described as measured: B2's 82.4 s/fit at 833 variables gives
~676 s; `HARDWARE_REQUEST_B4.md` line 43's 26-34 s/fit gives ~250 s. B5 runs
first and lands a fresh measurement.

WINDOW: on or after 07:30 local Eastern, 2026-10-06 (team lead). Approval for
B5 and B4 was given 2026-10-05 for this sprint.
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
import eqc_submit                             # noqa: E402
import metered_call as mc                     # noqa: E402
import metrics                                # noqa: E402
import qubo_proxy                             # noqa: E402
import spectra_segment as ss                  # noqa: E402
import store                                  # noqa: E402

log = logging.getLogger("b4")

BLOCK = "B4"
ARM = "cvqboost_hw_spectra"
SEEDS = (42, 43, 44, 45, 46)
WEAK_CLS_TYPE = "dct"            # the proxy dry run's pool type, and B3's

EXPECTED_SECONDS = ("250-680 s for 10 fits: ~676 s at B2's measured 82.4 s/fit "
                    "at 833 vars, ~250 s at HARDWARE_REQUEST_B4 line 43's "
                    "26-34 s/fit for 560-816 vars. The two anchors disagree "
                    "by 2.4x and both are described as measured")
EXPECTED_CEILING_S = 760.0
BLOCK_CAP_S = 760.0
ALLOCATION_FLOOR_S = 776.0

RESULTS = qubo_proxy.RESULTS
ARTIFACT = qubo_proxy.RESULTS_DIR / "b4_hardware.json"
RESP_DIR = qubo_proxy.RESULTS_DIR / "pools" / "hw_responses"

# The team lead's window: replaced 2026-10-06 ("the runners' time check is
# artificial and can be replaced by 7:30am EST"). A START TIME, not a daily
# hour: the first version used `hour >= 18`, which closed again at midnight.
WINDOW_START = datetime(2026, 10, 6, 7, 30)


def feasible_specs() -> list[dict]:
    """The cells whose H5(ii) control can actually be drawn, recomputed from
    the data every run -- never a hardcoded cell list (AST-guarded)."""
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
    return (now or datetime.now()) >= WINDOW_START


def _cfg(cell: dict, n_train: int) -> dict:
    """The QBoostClassifier configuration, read from FROZEN_CELLS."""
    c = cell["config"]
    return dict(lambda_coef=c["lambda_coef_alpha"] * n_train,
                weak_cls_schedule=c["weak_cls_schedule"],
                weak_cls_type=WEAK_CLS_TYPE,
                weak_cls_params=dict(c["weak_cls_params"]),
                weak_cls_strategy=c["weak_cls_strategy"],
                relaxation_schedule=c["relaxation_schedule"],
                num_samples=c["num_samples"])


def _dynamic_range(clf):
    try:
        return float(clf.get_dynamic_range())
    except Exception:                                  # noqa: BLE001
        return None


def _fit_one(spec: dict, client, dry_run: bool) -> dict:
    """One SPECTRA cell. Identical code for the dry and the real run, except
    that the dry run swaps the cloud solver for `eqc_submit.offline_solver`."""
    from eqc_models.ml.classifierqboost import QBoostClassifier

    name = spec["cell"]
    cell = ss.frozen_cell_by_name(name)
    split, cols = ss._prep_spectra(name, spec["seed"])
    assert len(cols) == cell["config"]["n_features"], (
        f"{name}: frozen cell expects {cell['config']['n_features']} "
        f"features, got {len(cols)}")

    def X(df):
        return ss.coerce_features_to_numeric(df[cols]).to_numpy(dtype="float32")

    Xtr, Xva, Xte = X(split.X_train), X(split.X_val), X(split.X_test)
    y_train01 = split.y_train.to_numpy()
    y_val01 = split.y_val.to_numpy()
    y_test01 = split.y_test.to_numpy()
    in_pocket_test = split.X_test[ss.SEGMENT_FLAG].to_numpy().astype(bool)
    y_pm1 = np.where(y_train01 == 1, 1, -1)

    cfg = _cfg(cell, len(y_pm1))
    n_vars = ss.data.qubo_vars(len(cols), cfg["weak_cls_schedule"],
                               pair_build="sequential")
    api = dict(api_url=os.environ.get("QCI_API_URL"),
               api_token=os.environ.get("QCI_TOKEN"))

    def make_clf():
        clf = QBoostClassifier(**api, **cfg)
        for k, v in cfg.items():
            assert getattr(clf, k) == v, f"constructed attr mismatch: {k}"
        return clf

    def make_record(attempt):
        return mc.CallRecord(label=f"b4_{name}_{spec['seed']}_a{attempt + 1}",
                             degree=2, n_variables=n_vars,
                             n_samples=cfg["num_samples"],
                             expected_seconds=EXPECTED_SECONDS)

    sent: list = []
    t0 = time.strftime("%Y-%m-%dT%H:%M:%S")
    if dry_run:
        with eqc_submit.offline_solver(sent):
            clf = make_clf()
            resp = clf.fit(Xtr, y_pm1)
        fit = {"clf": clf, "resp": resp, "attempts": 1, "metered_seconds": 0.0,
               "parsed": True, "error": None, "job_id": None}
    else:
        fit = eqc_submit.metered_fit(make_clf, Xtr, y_pm1, make_record, client)

    row = {
        "arm": ARM, "block": BLOCK, "dataset": spec["dataset"],
        "seed": spec["seed"], "protocol": "stratified",
        "config": f"b4_{name}", "pool_variant": WEAK_CLS_TYPE,
        "pair_build": "sequential",
        "config_hash": spec["config_hash"],
        "hw_config": {k: (v if k != "weak_cls_params" else dict(v))
                      for k, v in cfg.items()},
        "n_vars_expected": n_vars,
        "features_used": list(cols),
        "evidence_tag": "SIM" if dry_run else "HW",
        "retry_count": max(0, fit["attempts"] - 1),
        "metered_seconds": fit["metered_seconds"],
        "metered_seconds_parsed": fit["parsed"],
        "job_id": fit["job_id"],
        "timestamps": {"started": t0, "finished": None},
    }

    if fit["clf"] is None:
        row.update({"status": "failed", "error": fit["error"], "metrics": None})
        row["timestamps"]["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        return row

    clf, resp = fit["clf"], fit["resp"]

    # Every returned sample is kept, not only the lowest-energy one (F90
    # acceptance (c)), so F20's multi-sample ensembling costs no further
    # device time. The full response is the record; the row carries the count.
    samples = (resp.get("results", {}) or {}).get("solutions", []) \
        if isinstance(resp, dict) else []
    if not dry_run:
        RESP_DIR.mkdir(parents=True, exist_ok=True)
        (RESP_DIR / f"b4_{name}_stratified_{spec['seed']}.json").write_text(
            json.dumps(resp, default=str, indent=1), encoding="utf-8")

    w_hw = np.asarray(clf.params, dtype=np.float64)
    H_tr = qubo_proxy.h_matrix(clf, Xtr)
    w_px = qubo_proxy.solve_simplex_qp(H_tr, y_pm1, cfg["lambda_coef"])
    denom = float(np.linalg.norm(w_hw) * np.linalg.norm(w_px))
    cosine = float(w_hw @ w_px / denom) if denom > 0 else None

    def score(Xm):
        return np.clip((clf.predict_raw(Xm) + 1.0) / 2.0, 0.0, 1.0)

    p_val, p_test, p_train = score(Xva), score(Xte), score(Xtr)
    m = metrics.summarize(y_test01, y_val01, p_val, p_test, seed=spec["seed"])
    train_ap = float(metrics.average_precision_score(y_train01, p_train))
    seg = ss.evaluate_in_segment(y_test01, p_test, in_pocket_test,
                                 spec["seed"], label="target")

    row.update({
        "status": "ok" if fit["parsed"] else "ok_unmetered",
        "n_weak_classifiers": len(clf.h_list),
        "n_samples_returned": len(samples),
        "all_samples": "full response in " + (
            "(dry run, not written)" if dry_run else
            f"pools/hw_responses/b4_{name}_stratified_{spec['seed']}.json"),
        "weight_cosine_vs_classical": cosine,
        # Measured per fit; the dry run found 8.1-8.3 dB, inside A31's ~23 dB.
        "dynamic_range_db": _dynamic_range(clf),
        "metrics": {**m,
                    "train_auprc": train_ap,
                    "train_test_ap_gap": round(train_ap - m["auprc"], 4)},
        "in_segment": seg,
        "solver_args_sent": sent[0] if sent else None,
    })
    row["timestamps"]["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="run the full library path with the cloud solver "
                         "stubbed; one cell per dataset; spends nothing")
    ap.add_argument("--max-calls", type=int, default=10)
    args = ap.parse_args()

    # Refusals come FIRST for a real run, before any data is touched. A TEST
    # PROCESS MAY NEVER SPEND DEVICE SECONDS (Sprint 21: my own window tests
    # submitted two real jobs on 2026-10-05; nothing was billed by luck), and
    # in CI the SPECTRA files are absent, so a refusal placed after the data
    # load would crash on a missing file instead of refusing.
    if not args.dry_run:
        if "PYTEST_CURRENT_TEST" in os.environ or "pytest" in sys.modules:
            print("REFUSING: a metered run was invoked from a test process. "
                  "Tests exercise --dry-run and source-level checks only; "
                  "spending device seconds requires a human-invoked run.")
            return 5
        if not (_window_open()):
            print(f"REFUSING: the team lead set the Dirac-3 window to open at "
                  f"{WINDOW_START:%Y-%m-%d %H:%M} local and it is "
                  f"{datetime.now():%Y-%m-%d %H:%M}.")
            return 3

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
    print("  provenance               : CONTESTED, band quoted; B5 lands a "
          "fresh measurement first")
    print(f"  submission               : eqc_models QBoostClassifier, as B2/B3")
    print(f"  block cap                : {BLOCK_CAP_S} s")
    print(f"  spent on {BLOCK} so far      : {_spent():.1f} s")
    print(f"  approved                 : team lead 2026-10-05; window from "
          f"{WINDOW_START:%Y-%m-%d %H:%M} local")
    print()
    for s in infeasible:
        print(f"    unscoreable: {s['cell']} seed {s['seed']} -- "
              f"{s['feasibility']['reason'][:88]}")
    print()

    if not todo:
        print("Nothing to do: every feasible B4 cell is already complete.")
        return 0

    if args.dry_run:
        seen, picks = set(), []
        for s in todo:
            if s["cell"] not in seen:
                seen.add(s["cell"])
                picks.append(s)
        for s in picks:
            r = _fit_one(s, None, dry_run=True)
            sa = r.get("solver_args_sent") or {}
            print(f"  [dry] {s['cell']:18s} seed={s['seed']} "
                  f"status={r['status']} sent: vars={sa.get('n_variables')} "
                  f"samples={sa.get('num_samples')} "
                  f"rx={sa.get('relaxation_schedule')} "
                  f"sum={sa.get('sum_constraint')} "
                  f"range={sa.get('dynamic_range_db') or 0:.1f} dB "
                  f"pool={r.get('n_weak_classifiers')}")
        print("\nDry run: the library built and handed over every request; "
              "the cloud solver was stubbed. Nothing submitted, nothing spent.")
        return 0

    _load_env()
    from qci_client import QciClient
    client = QciClient(api_token=os.environ["QCI_TOKEN"],
                       url=os.environ["QCI_API_URL"])

    bal = eqc_submit._balance_or_none(client)
    if bal is None:
        print("REFUSING: the allocation balance cannot be read, so the floor "
              "cannot be enforced.")
        return 4
    if bal - EXPECTED_CEILING_S < ALLOCATION_FLOOR_S:
        print(f"REFUSING: balance {bal} s minus this block's ceiling "
              f"{EXPECTED_CEILING_S} s would breach the "
              f"{ALLOCATION_FLOOR_S} s floor.")
        return 4

    rows, spent, failed = [], 0.0, 0
    t0 = time.perf_counter()
    for i, spec in enumerate(todo[:args.max_calls], 1):
        if spent >= BLOCK_CAP_S:
            print(f"  block cap {BLOCK_CAP_S} s reached; stopping with "
                  f"{len(rows)} fits")
            break
        print(f"  [{i}/{min(len(todo), args.max_calls)}] {spec['cell']} "
              f"seed={spec['seed']} ...", flush=True)
        row = _fit_one(spec, client, dry_run=False)
        rows.append(row)
        spent += float(row.get("metered_seconds") or 0)
        failed += row["status"] == "failed"
        store.append_row(row)
        _write_artifact(rows, infeasible, spent, t0, complete=False)
        print(f"      {row['status']}  {row.get('metered_seconds')} s  "
              f"auprc={(row.get('metrics') or {}).get('auprc')}", flush=True)

    _write_artifact(rows, infeasible, spent, t0, complete=True)
    print(f"\nB4 done: {len(rows)} fits, {failed} failed, "
          f"{spent:.1f} metered seconds.")
    return 1 if failed else 0


def _write_artifact(rows, infeasible, spent, t0, complete: bool) -> None:
    """Written after EVERY fit (F65)."""
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
    }, indent=2, default=str), encoding="utf-8")


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
