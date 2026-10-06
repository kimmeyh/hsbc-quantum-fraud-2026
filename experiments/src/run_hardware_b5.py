"""B5: the sign-augmented primal QSVM arm on Dirac-3.

Block B5 of the frozen grid (PREREGISTRATION section 10): **12 fits, ~15
metered seconds, gated on the current balance** -- the cheapest block in the
campaign and the only one the frozen fallback runs without a grant. Section 4
names the arm "QSVM (sign-augmented primal, Dirac-3) -- cheap secondary arm,
~1 metered second per fit".

It was specified in Sprint 3 and never implemented. The F18 notes
(`docs/sprints/drafts/F18_dirac3_notes_findings.md`) resolved every
implementation question then and recorded them as "B5 spec", with the
amendment column reading "None. Every adoption is tooling-level." This file is
that spec, built.

WHY SIGN AUGMENTATION IS NOT OPTIONAL. Dirac-3 continuous variables are
non-negative, so a primal SVM over raw features cannot express a negative
weight. `docs/evidence-inventory.md` records what that costs when it is
missed: an un-augmented QSVM scored **0.18 AUC** on anti-correlated features.
Stacking `[X, -X]` lets a non-negative pair (w+, w-) represent any signed
weight as w+ - w-, which is the standard primal trick, and it must be applied
at fit AND at predict or the two spaces disagree silently.

COST PROVENANCE, corrected 2026-10-05. The frozen grid says ~15 s for 12 fits
(~1.2 s/fit) and section 4 says ~1 s/fit; the F18 notes call that "~1 s/fit
MEASURED on hardware". F90's card quoted "15-62 s" by extrapolating from B3's
5.2 s/fit, which is a CVQBoost rate at a different variable count and the
wrong anchor for this arm. The expected figure stated to the team lead is the
frozen one: **~15 s, with 62 s as a conservative ceiling**.

Criterion H: the team lead approved B5 and B4 on 2026-10-05 ("both qci runs
are approved - no need to ask again this sprint") and directed that all
Dirac-3 calls wait until 18:00 local that day. This runner states block, call
count, expected seconds and provenance before submitting anything, records
them in the ledger BEFORE spending, and refuses to run before the window
without an explicit override.
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
import qubo_proxy as qp                       # noqa: E402
import store                                  # noqa: E402

log = logging.getLogger("b5")

BLOCK = "B5"
ARM = "qsvm_hw"
SEEDS = qp.SEEDS                              # 42..51, the ten stratified seeds
TUNING_SEED = 42

# The frozen grid's own numbers, not an extrapolation from another block.
EXPECTED_SECONDS = "~15 s total for 12 fits (~1.2 s/fit); frozen grid section 10"
EXPECTED_CEILING_S = 62.0

# A cheap block still gets a cap: the point of running it first is to exercise
# the approval and ledger path, and a runaway on the cheap block would spend
# the balance the expensive one needs.
BLOCK_CAP_S = 62.0
ALLOCATION_FLOOR_S = 776.0                    # the team lead's floor, as B1/B2

# Section 10 gives B5 no k, so it inherits the primary endpoint's feature
# budget. k=13 is B1's top-13 ULB configuration, which keeps B5 comparable to
# the arm it is a secondary to, and 13 features sign-augmented is 26 Dirac
# variables -- far below any ceiling, which is why this block is cheap.
K_FEATURES = 13
NUM_SAMPLES = 8

RESULTS = qp.RESULTS
ARTIFACT = qp.RESULTS_DIR / "b5_hardware.json"
WINDOW_HOUR = 18                              # 6pm local, team lead 2026-10-05


def sign_augment(X: np.ndarray) -> np.ndarray:
    """`[X, -X]`, the non-negativity workaround. Applied at fit AND predict.

    A non-negative solver cannot produce a signed weight vector. Stacking the
    negated copy lets the pair (w+, w-) encode w = w+ - w-, so the model can
    express the same hypothesis class a standard primal SVM can. Skipping it
    at predict time is the silent-failure mode: the weights index a feature
    space the prediction matrix no longer matches.
    """
    X = np.asarray(X, dtype="float64")
    return np.hstack([X, -X])


def n_variables(k: int) -> int:
    """One Dirac variable per augmented feature. 13 features -> 26."""
    return 2 * k


def specs():
    """The 12 fits: ten stratified seeds, one temporal, one tuning-seed repeat.

    Mirrors B1's structure so the arms are comparable. The temporal row records
    `seed: None`: `data.temporal_split` ignores the seed, and recording 42
    there would misrepresent provenance and let a second temporal row bypass
    the done-set (A8, Sprint 4 review).
    """
    for seed in SEEDS:                                    # 10
        yield dict(block=BLOCK, k=K_FEATURES, seed=seed, protocol="stratified")
    yield dict(block=BLOCK, k=K_FEATURES, seed=None, protocol="temporal")
    yield dict(block=BLOCK, k=K_FEATURES, seed=TUNING_SEED,
               protocol="stratified_repeat")


def _done() -> set:
    """Successful B5 cells already in results.json.

    IDEMPOTENT BEFORE THE FIRST APPROVAL, not after the first over-spend
    (Sprint 18 IMP-3). Sprint 18 spent three calls against a two-call approval
    because a second invocation restarted from the top. A failed row does NOT
    count as done: section 11 requires up to two retries and then an explicit
    failed report, never a silent drop.
    """
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
    """Metered seconds already charged to B5, from results.json."""
    if not RESULTS.exists():
        return 0.0
    rows = json.loads(RESULTS.read_text(encoding="utf-8"))["rows"]
    return sum(float(r.get("metered_seconds") or 0)
               for r in rows if r.get("block") == BLOCK)


def _window_open(now: datetime | None = None) -> bool:
    now = now or datetime.now()
    return now.hour >= WINDOW_HOUR


def _fit_one(client, spec: dict, dry_run: bool) -> dict:
    """One cell: build the augmented primal, submit one metered call, score."""
    df = data.load_ulb().drop_duplicates().reset_index(drop=True)
    split = (data.temporal_split(df) if spec["protocol"] == "temporal"
             else data.stratified_split(df, seed=spec["seed"]))
    cols = data.top_k_features(split.X_train, split.y_train, spec["k"],
                               seed=spec["seed"] or TUNING_SEED)

    Xtr = sign_augment(split.X_train[cols].to_numpy())
    Xte = sign_augment(split.X_test[cols].to_numpy())
    y01 = split.y_train.to_numpy()
    y_pm1 = np.where(y01 == 1, 1, -1)
    assert set(np.unique(y_pm1)) == {-1, 1}, "labels must be {-1,+1} at fit"

    n_vars = n_variables(spec["k"])
    assert Xtr.shape[1] == n_vars, (
        f"augmented width {Xtr.shape[1]} != expected {n_vars}")

    cfg = {"arm": ARM, "k": spec["k"], "sign_augmented": True,
           "num_samples": NUM_SAMPLES, "protocol": spec["protocol"],
           "n_variables": n_vars}
    cfg_hash = store.config_hash(cfg)

    if dry_run:
        return {"arm": ARM, "block": BLOCK, "seed": spec["seed"],
                "protocol": spec["protocol"], "config_hash": cfg_hash,
                "n_variables": n_vars, "evidence_tag": "SIM",
                "metered_seconds": 0, "status": "dry_run",
                "n_train": int(len(y01)), "features_used": list(cols)}

    rec = mc.CallRecord(
        label=f"b5_{spec['protocol']}_{spec['seed']}",
        degree=2, n_variables=n_vars, n_samples=NUM_SAMPLES,
        expected_seconds=EXPECTED_SECONDS)

    body = _job_body(Xtr, y_pm1, n_vars)
    resp = mc.run_metered(client, body, rec)
    w = _weights(resp, n_vars)

    p_test = Xte @ w
    from sklearn.metrics import average_precision_score, roc_auc_score
    yte = split.y_test.to_numpy()

    return {
        "arm": ARM, "block": BLOCK, "seed": spec["seed"],
        "protocol": spec["protocol"], "config_hash": cfg_hash,
        "n_variables": n_vars, "evidence_tag": "HW",
        "metered_seconds": rec.measured_seconds,
        "metered_seconds_parsed": rec.measured_seconds is not None,
        "job_id": rec.job_id, "status": rec.status,
        "retry_count": 0,
        "features_used": list(cols),
        "metrics": {"auprc": float(average_precision_score(yte, p_test)),
                    "auc_roc": float(roc_auc_score(yte, p_test))},
        "timestamps": {"submitted_utc": rec.submitted_utc,
                       "finished_utc": rec.finished_utc},
    }


def _job_body(X: np.ndarray, y_pm1: np.ndarray, n_vars: int) -> dict:
    """The primal hinge-surrogate QUBO, in the same shape B1/B2 submit.

    Least-squares primal: minimize ||Xw - y||^2 + lam||w||^2 over w >= 0 on
    the simplex, which is the identical Hamiltonian family the proxy solves
    (J = X^T X + lam I, C = -2 X^T y). The sign augmentation is what makes a
    non-negative w sufficient.
    """
    lam = 2.0 * len(y_pm1)
    J = X.T @ X + lam * np.eye(n_vars)
    C = -2.0 * (X.T @ y_pm1)
    return {
        "job_submission": {
            "problem_config": {
                "quadratic_linearly_constrained_binary_optimization": None},
            "device_config": {"dirac-3": {"num_samples": NUM_SAMPLES,
                                          "relaxation_schedule": 2,
                                          "sum_constraint": 1.0}},
            "job_name": "b5_qsvm",
            "_J": J.tolist(), "_C": C.tolist(),
        }
    }


def _weights(resp, n_vars: int) -> np.ndarray:
    sols = (resp.get("results", {}) or {}).get("solutions")
    if not sols:
        raise RuntimeError("no solutions in the Dirac-3 response")
    w = np.asarray(sols[0], dtype="float64")
    assert len(w) == n_vars, f"solution width {len(w)} != {n_vars}"
    assert (w >= -1e-9).all(), "Dirac-3 returned a negative continuous variable"
    return w


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="build every cell and report sizes; submit nothing, "
                         "spend nothing")
    ap.add_argument("--max-calls", type=int, default=12,
                    help="hard ceiling on metered calls this invocation")
    ap.add_argument("--ignore-window", action="store_true",
                    help="run before 18:00 local; the team lead's 2026-10-05 "
                         "instruction was to wait for the window")
    args = ap.parse_args()

    all_specs = list(specs())
    done = _done()
    todo = [s for s in all_specs
            if (ARM, s["seed"], s["protocol"]) not in done]

    # --- Criterion H: state it before spending anything ---------------------
    print(f"BLOCK {BLOCK}: sign-augmented primal QSVM on Dirac-3 (ULB)")
    print(f"  cells total      : {len(all_specs)}")
    print(f"  already complete : {len(done)}")
    print(f"  CALL COUNT now   : {min(len(todo), args.max_calls)}")
    print(f"  EXPECTED SECONDS : {EXPECTED_SECONDS}")
    print(f"  provenance       : MEASURED at ~1 s/fit on hardware per the F18 "
          f"notes; the frozen grid states ~15 s for 12 fits")
    print(f"  conservative cap : {EXPECTED_CEILING_S} s (block cap {BLOCK_CAP_S} s)")
    print(f"  variables/fit    : {n_variables(K_FEATURES)} "
          f"({K_FEATURES} features sign-augmented)")
    print(f"  spent on {BLOCK} so far: {_spent():.1f} s")
    print(f"  approved         : team lead 2026-10-05, B5 and B4 both, "
          f"window 18:00 local")
    print()

    if not todo:
        print("Nothing to do: every B5 cell is already complete.")
        return 0

    if args.dry_run:
        for s in todo[:args.max_calls]:
            r = _fit_one(None, s, dry_run=True)
            print(f"  [dry] {s['protocol']:18s} seed={str(s['seed']):4s} "
                  f"vars={r['n_variables']} hash={r['config_hash'][:12]}")
        print("\nDry run: nothing submitted, nothing spent.")
        return 0

    # A TEST PROCESS MAY NEVER SPEND DEVICE SECONDS. On 2026-10-05 two of my
    # own window-guard tests invoked this runner with `--max-calls 1`,
    # checking for "REFUSING" only AFTER the subprocess returned. Before 18:00
    # they skipped; once the window opened the guard correctly allowed the run
    # and the tests submitted two real jobs with no Criterion H statement read
    # by anyone. Nothing was billed only because one job body was malformed
    # and the other hit an SSL error.
    #
    # The tests are fixed, but the structural answer belongs here: metered
    # work refuses to start inside pytest, whatever the arguments say. The
    # allocation has no undo, and a runner that can be fired by a test is one
    # careless parametrize away from spending the balance.
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
    for i, spec in enumerate(todo[:args.max_calls], 1):
        if spent >= BLOCK_CAP_S:
            print(f"  block cap {BLOCK_CAP_S} s reached; stopping with "
                  f"{len(rows)} fits done")
            break
        print(f"  [{i}/{min(len(todo), args.max_calls)}] "
              f"{spec['protocol']} seed={spec['seed']} ...", flush=True)
        row = _fit_one(client, spec, dry_run=False)
        rows.append(row)
        spent += float(row.get("metered_seconds") or 0)
        store.append_row(row)                 # after EVERY fit, never at the end
        _write_artifact(rows, spent, complete=False)

    _write_artifact(rows, spent, complete=True)
    print(f"\nB5 done: {len(rows)} fits, {spent:.1f} metered seconds.")
    return 0


def _write_artifact(rows, spent, complete: bool) -> None:
    """Written after every fit, so a crash after a billed call still leaves
    the evidence (F65: a runner that built this once, at the end, lost a
    billed B2 fit to a shell teardown)."""
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
            raise SystemExit(f"{k} is not set; B5 cannot submit.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    raise SystemExit(main())
