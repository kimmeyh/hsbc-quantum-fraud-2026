"""B5: the sign-augmented primal QSVM arm on Dirac-3.

Block B5 of the frozen grid (PREREGISTRATION section 10): **12 fits, ~15
metered seconds, gated on the current balance**. Section 4 names the arm
"QSVM (sign-augmented primal, Dirac-3) -- cheap secondary arm, ~1 metered
second per fit". The F18 notes (Sprint 3) resolved every implementation
question as "B5 spec", with "amendment candidates: None".

SUBMITS THROUGH eqc-models' `QSVMClassifier`, the same library path B1-B3 used
for CVQBoost. The first version of this runner hand-built the job body, with
invented field names, and QCi rejected it ("400: Must specify one and only one
job under the job_submission.problem_config field"); see `eqc_submit.py`.

WHY SIGN AUGMENTATION. Dirac-3 continuous variables are non-negative, so a
primal SVM over raw features cannot express a negative weight. Stacking
`[X, -X]` lets a non-negative pair encode any signed weight; it is applied at
fit AND predict. The evidence inventory records an un-augmented QSVM scoring
0.18 AUC on anti-correlated features. The library adds one bias column, so 13
features become **27 variables** (2 x 13 + 1).

num_samples = 1, the library default. That is what "~1 metered second per fit"
implies under the ledger's billing rule (`ceil(sum(sample runtimes))`, about
0.5 s per sample at this size), and it is what the frozen ~15 s for 12 fits
prices. lambda_coef is the library default, 1.0.

WINDOW: on or after 07:30 local Eastern, 2026-10-06 (team lead).
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
import eqc_submit                             # noqa: E402
import metered_call as mc                     # noqa: E402
import metrics                                # noqa: E402
import qubo_proxy as qp                       # noqa: E402
import store                                  # noqa: E402

log = logging.getLogger("b5")

BLOCK = "B5"
ARM = "qsvm_hw"
SEEDS = qp.SEEDS                              # 42..51, the ten stratified seeds
TUNING_SEED = 42

EXPECTED_SECONDS = "~15 s total for 12 fits (~1.2 s/fit); frozen grid section 10"
EXPECTED_CEILING_S = 62.0
BLOCK_CAP_S = 62.0
ALLOCATION_FLOOR_S = 776.0

# B1's top-13 ULB features, so the secondary arm is comparable to the arm it
# is secondary to.
K_FEATURES = 13
NUM_SAMPLES = 1
RELAXATION_SCHEDULE = 2

RESULTS = qp.RESULTS
ARTIFACT = qp.RESULTS_DIR / "b5_hardware.json"
RESP_DIR = qp.RESULTS_DIR / "pools" / "hw_responses"

# The team lead's window, replaced 2026-10-06 ("can be replaced by 7:30am
# EST"). A START TIME, not a daily hour -- `hour >= 18` closed at midnight.
WINDOW_START = datetime(2026, 10, 6, 7, 30)


def sign_augment(X: np.ndarray) -> np.ndarray:
    """`[X, -X]`, applied at fit AND predict."""
    X = np.asarray(X, dtype="float64")
    return np.hstack([X, -X])


def n_variables(k: int) -> int:
    """Augmented features plus the library's bias column. 13 -> 27."""
    return 2 * k + 1


def specs():
    """The 12 fits: ten stratified seeds, one temporal, one tuning-seed
    repeat. The temporal row records `seed: None` (A8)."""
    for seed in SEEDS:
        yield dict(block=BLOCK, k=K_FEATURES, seed=seed, protocol="stratified")
    yield dict(block=BLOCK, k=K_FEATURES, seed=None, protocol="temporal")
    yield dict(block=BLOCK, k=K_FEATURES, seed=TUNING_SEED,
               protocol="stratified_repeat")


def _done() -> set:
    """Successful B5 cells already in results.json (Sprint 18 IMP-3)."""
    if not RESULTS.exists():
        return set()
    try:
        rows = json.loads(RESULTS.read_text(encoding="utf-8"))["rows"]
    except Exception as exc:                              # noqa: BLE001
        raise SystemExit(
            f"B5 refuses to submit: results.json is unreadable ({exc}). A "
            "runner that cannot read its own ledger cannot know what it has "
            "already paid for.")
    return {(r["arm"], r["seed"], r.get("protocol"))
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


def _fit_one(df, spec: dict, client, dry_run: bool) -> dict:
    from eqc_models.ml.classifierqsvm import QSVMClassifier

    split = (data.temporal_split(df) if spec["protocol"] == "temporal"
             else data.stratified_split(df, seed=spec["seed"]))
    cols = data.top_k_features(split.X_train, split.y_train, spec["k"],
                               seed=spec["seed"] or TUNING_SEED)

    Xtr = sign_augment(split.X_train[cols].to_numpy())
    Xva = sign_augment(split.X_val[cols].to_numpy())
    Xte = sign_augment(split.X_test[cols].to_numpy())
    y_pm1 = np.where(split.y_train.to_numpy() == 1, 1, -1)
    n_vars = n_variables(spec["k"])

    cfg = {"arm": ARM, "k": spec["k"], "sign_augmented": True,
           "num_samples": NUM_SAMPLES,
           "relaxation_schedule": RELAXATION_SCHEDULE,
           "lambda_coef": 1.0, "protocol": spec["protocol"],
           "n_variables": n_vars}
    api = dict(api_url=os.environ.get("QCI_API_URL"),
               api_token=os.environ.get("QCI_TOKEN"))

    def make_clf():
        return QSVMClassifier(relaxation_schedule=RELAXATION_SCHEDULE,
                              num_samples=NUM_SAMPLES, **api)

    def make_record(attempt):
        return mc.CallRecord(
            label=f"b5_{spec['protocol']}_{spec['seed']}_a{attempt + 1}",
            degree=2, n_variables=n_vars, n_samples=NUM_SAMPLES,
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
        "arm": ARM, "block": BLOCK, "dataset": "ulb",
        "seed": spec["seed"], "protocol": spec["protocol"],
        # score_gates keys any arm it does not special-case by
        # (arm, feature_set), with r["feature_set"] -- absent, it raises.
        "feature_set": f"ulb_top{spec['k']}_sign_augmented",
        "config_hash": store.config_hash(cfg),
        "hw_config": cfg,
        "n_variables": n_vars,
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
    if not dry_run:
        RESP_DIR.mkdir(parents=True, exist_ok=True)
        (RESP_DIR / f"b5_{spec['protocol']}_{spec['seed']}.json").write_text(
            json.dumps(resp, default=str, indent=1), encoding="utf-8")

    # predict_raw is the signed margin. With the weights on the simplex (sum
    # constraint 1) and features MinMax-scaled to [-1, 1], it lies in about
    # [-1, 1], so it maps to a score with the SAME (raw + 1) / 2 the CVQBoost
    # arms use (run_hardware.run_cell) -- one convention across arms.
    # summarize() needs [0, 1] for the Brier and calibration terms; the first
    # dry run through the library caught the raw margin reaching -0.19.
    # Monotone, so AUPRC and AUC-ROC are unchanged by it.
    def score(Xm):
        return np.clip((clf.predict_raw(Xm) + 1.0) / 2.0, 0.0, 1.0)

    p_val, p_test = score(Xva), score(Xte)
    m = metrics.summarize(split.y_test.to_numpy(), split.y_val.to_numpy(),
                          p_val, p_test, seed=spec["seed"] or TUNING_SEED)
    # The Hamiltonian's dynamic range, MEASURED per fit. The dry run found
    # 20.8-42.3 dB across the 12 cells, above A31's ~23 dB resolution limit on
    # 11 of them, so the device may not resolve the smallest coefficients.
    # Recorded beside every result rather than discovered afterwards.
    try:
        dr = float(clf.get_dynamic_range())
    except Exception:                                  # noqa: BLE001
        dr = None
    row.update({
        "status": "ok" if fit["parsed"] else "ok_unmetered",
        "metrics": m,
        "dynamic_range_db": dr,
        "above_a31_resolution_limit": None if dr is None else dr > 23.0,
        "solver_args_sent": sent[0] if sent else None,
    })
    row["timestamps"]["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="run the full library path with the cloud solver "
                         "stubbed; spends nothing")
    ap.add_argument("--max-calls", type=int, default=12)
    args = ap.parse_args()

    # Refusals come FIRST for a real run, before ULB is loaded. A TEST PROCESS
    # MAY NEVER SPEND DEVICE SECONDS (Sprint 21: my own window tests submitted
    # two real jobs on 2026-10-05; nothing was billed by luck), and in CI the
    # ULB file is absent, so a refusal after the load would crash instead.
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

    all_specs = list(specs())
    done = _done()
    todo = [s for s in all_specs
            if (ARM, s["seed"], s["protocol"]) not in done]

    print(f"BLOCK {BLOCK}: sign-augmented primal QSVM on Dirac-3 (ULB)")
    print(f"  cells total      : {len(all_specs)}")
    print(f"  already complete : {len(done)}")
    print(f"  CALL COUNT now   : {min(len(todo), args.max_calls)}")
    print(f"  EXPECTED SECONDS : {EXPECTED_SECONDS}")
    print("  provenance       : MEASURED at ~1 s/fit on hardware per the F18 "
          "notes; the frozen grid states ~15 s for 12 fits")
    print(f"  conservative cap : {EXPECTED_CEILING_S} s (block cap {BLOCK_CAP_S} s)")
    print(f"  variables/fit    : {n_variables(K_FEATURES)} "
          f"({K_FEATURES} features sign-augmented, plus bias)")
    print(f"  num_samples      : {NUM_SAMPLES}, relaxation schedule "
          f"{RELAXATION_SCHEDULE}")
    print("  submission       : eqc_models QSVMClassifier")
    print(f"  spent on {BLOCK} so far: {_spent():.1f} s")
    print(f"  approved         : team lead 2026-10-05; window from "
          f"{WINDOW_START:%Y-%m-%d %H:%M} local")
    print()

    # A dry run spends nothing and exists to exercise the submission path, so
    # it never depends on what results.json already holds. The first version
    # returned "Nothing to do" once the real block had run, which made its
    # guard fail the morning B5 completed -- a test depending on live repository
    # state, the F97 class.
    if not todo and not args.dry_run:
        print("Nothing to do: every B5 cell is already complete.")
        return 0

    df = data.load_ulb().drop_duplicates().reset_index(drop=True)

    if args.dry_run:
        for s in all_specs[:args.max_calls]:
            r = _fit_one(df, s, None, dry_run=True)
            sa = r.get("solver_args_sent") or {}
            print(f"  [dry] {s['protocol']:18s} seed={str(s['seed']):4s} "
                  f"status={r['status']} sent: vars={sa.get('n_variables')} "
                  f"samples={sa.get('num_samples')} "
                  f"rx={sa.get('relaxation_schedule')} "
                  f"sum={sa.get('sum_constraint')} "
                  f"range={sa.get('dynamic_range_db') or 0:.1f} dB")
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
    for i, spec in enumerate(todo[:args.max_calls], 1):
        if spent >= BLOCK_CAP_S:
            print(f"  block cap {BLOCK_CAP_S} s reached; stopping with "
                  f"{len(rows)} fits done")
            break
        print(f"  [{i}/{min(len(todo), args.max_calls)}] "
              f"{spec['protocol']} seed={spec['seed']} ...", flush=True)
        row = _fit_one(df, spec, client, dry_run=False)
        rows.append(row)
        spent += float(row.get("metered_seconds") or 0)
        failed += row["status"] == "failed"
        store.append_row(row)
        _write_artifact(rows, spent, complete=False)
        print(f"      {row['status']}  {row.get('metered_seconds')} s  "
              f"auprc={(row.get('metrics') or {}).get('auprc')}", flush=True)

    _write_artifact(rows, spent, complete=True)
    print(f"\nB5 done: {len(rows)} fits, {failed} failed, "
          f"{spent:.1f} metered seconds.")
    return 1 if failed else 0


def _write_artifact(rows, spent, complete: bool) -> None:
    """Written after every fit (F65)."""
    ARTIFACT.write_text(json.dumps({
        "note": ("B5: sign-augmented primal QSVM on Dirac-3, ULB. Frozen grid "
                 "section 10: 12 fits, ~15 QPU s."),
        "generator": "experiments/src/run_hardware_b5.py",
        "evidence_tag": "HW",
        "block": BLOCK, "arm": ARM,
        "k_features": K_FEATURES,
        "n_variables": n_variables(K_FEATURES),
        "num_samples": NUM_SAMPLES,
        "sign_augmented": True,
        "complete": bool(complete),
        "fits": len(rows),
        "total_metered_seconds": round(spent, 2),
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
            raise SystemExit(f"{k} is not set; B5 cannot submit.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    raise SystemExit(main())
