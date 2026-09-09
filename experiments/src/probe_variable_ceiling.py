"""F46 step 2: does the paid allocation lift the 100-variable ceiling?

ONE metered call, approved by the team lead 2026-09-09 under Criterion H.

A12 records a free-tier ceiling of 100 continuous degree-2 variables, established
when F32's 312-variable job was refused SERVER-SIDE with HTTP 400 and zero
metered spend. The account now shows `dirac: {seconds: 3000, paid: true}`, and
`paid` is what the free tier was not -- so the ceiling has to be re-tested rather
than assumed either way.

THE PROBE. k=15 at schedule 2 is 15 + 15*12/2 = 105 variables: five above the
ceiling, the smallest configuration that can distinguish the two worlds. Cost is
asymmetric and that is the point:

  refused  -> HTTP 400 before billing, ZERO metered seconds, A12 confirmed
  accepted -> a real fit, 4-5 metered seconds, A12 needs an amendment

Both outcomes are decisive and the failure case is free.

Mirrors run_hardware.run_cell's call pattern exactly, including its sizing-error
branch: a variable-limit refusal must NOT be retried (F18 disposition 5), because
retrying a deterministic refusal only wastes attempts.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import data          # noqa: E402
import qubo_proxy as qp   # noqa: E402
import store         # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[2]
OUT = REPO / "experiments" / "results" / "variable_ceiling_probe.json"

K = 15                # -> 105 variables at schedule 2
SCHEDULE = 2
SEED = 42
CEILING = 100         # the A12 free-tier limit under test


def _load_env() -> None:
    p = REPO / ".env"
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def _billed(resp) -> float | None:
    m = re.search(r"'device_usage_s':\s*([0-9.]+)", repr(resp))
    return float(m.group(1)) if m else None


def main() -> int:
    _load_env()
    if not (os.environ.get("QCI_API_URL") and os.environ.get("QCI_TOKEN")):
        print("QCI_API_URL and QCI_TOKEN must both be set (ADR-0011).")
        return 2

    n_vars = K + K * (K - 3) // 2
    assert n_vars == 105, f"expected 105 variables, computed {n_vars}"
    print(f"probe: k={K}, schedule {SCHEDULE} -> {n_vars} variables "
          f"(ceiling under test: {CEILING})")
    print("ONE metered call, approved under Criterion H. Expected 0s if refused, "
          "4-5s if accepted.\n")

    df = data.load_ulb().drop_duplicates().reset_index(drop=True)
    split = data.stratified_split(df, SEED)
    cols = data.top_k_features(split.X_train, split.y_train, K, seed=SEED)
    Xtr = split.X_train[cols].to_numpy()
    y_pm1 = (split.y_train.to_numpy() == 1).astype(int) * 2 - 1

    from eqc_models.ml.classifierqboost import QBoostClassifier

    cfg = dict(lambda_coef=qp.LAMBDA_MULT * len(y_pm1),
               weak_cls_schedule=SCHEDULE, weak_cls_type="dct",
               weak_cls_params={}, weak_cls_strategy="sequential", **qp.FIXED)

    # Heartbeat BEFORE the call, so a crash or a lost tool result still leaves a
    # record that the submission was attempted. The first attempt died with no
    # artifact, which made "was the approved call spent?" unanswerable from the
    # repository -- only the allocation balance settled it (it was not).
    hb = OUT.with_name("variable_ceiling_probe_attempt.json")
    store.atomic_write_json(hb, {
        "note": "submission attempted; overwritten by the result on completion",
        "n_variables": n_vars, "k": K, "schedule": SCHEDULE,
        "attempted_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    })
    print(f"heartbeat written: {hb.name}")
    print("submitting (queue wait is normal; a fit bills 4-5s once it runs)...", flush=True)

    started = time.strftime("%Y-%m-%dT%H:%M:%S")
    t0 = time.perf_counter()
    resp, err, refused = None, None, False
    try:
        clf = QBoostClassifier(api_url=os.environ["QCI_API_URL"],
                               api_token=os.environ["QCI_TOKEN"], **cfg)
        resp = clf.fit(Xtr, y_pm1)          # THE one metered call
    except Exception as e:                  # noqa: BLE001
        err = f"{type(e).__name__}: {str(e)[:500]}"
        low = str(e).lower()
        refused = ("number of variables" in low
                   or ("variable" in low and "limit" in low)
                   or "free-tier" in low or "free tier" in low)
        # Sizing refusals are deterministic: no retry (F18 disposition 5).

    elapsed = round(time.perf_counter() - t0, 2)
    billed = _billed(resp) if resp is not None else 0.0

    out = {
        "note": ("F46 step 2: one metered probe at 105 continuous degree-2 variables, "
                 "five above the A12 free-tier ceiling of 100. Team-lead approved "
                 "under Criterion H, 2026-09-09."),
        "generator": "experiments/src/probe_variable_ceiling.py",
        "evidence_tag": "HW",
        "arm": "cvqboost_hw_ceiling_probe",
        "dataset": "ulb",
        "k_features": K,
        "schedule": SCHEDULE,
        "n_variables": n_vars,
        "ceiling_under_test": CEILING,
        "seed": SEED,
        "status": "ok" if resp is not None else "refused" if refused else "failed",
        "ceiling_lifted": bool(resp is not None),
        "error": err,
        "metered_seconds": billed,
        "wall_clock_sec": elapsed,
        "timestamps": {"started": started,
                       "finished": time.strftime("%Y-%m-%dT%H:%M:%S")},
        "raw_response_repr": repr(resp)[:2000] if resp is not None else None,
    }
    store.atomic_write_json(OUT, out)

    print(f"status          : {out['status']}")
    print(f"ceiling lifted  : {out['ceiling_lifted']}")
    print(f"metered seconds : {billed}")
    print(f"wall clock      : {elapsed}s")
    if err:
        print(f"error           : {err[:300]}")
    print(f"\nwritten: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
