"""F87 Task B: the integer sizing probe. METERED. Stops for approval.

Buys ONE number: seconds per fit on the Dirac-3 INTEGER path at a stated
variable count and level budget. That figure replaces the sentence in the QCi
hardware plan that currently reads "We are not quoting a cost for that block."

WHAT THIS IS NOT. It is not F25, the cardinality-constrained investigation. It
does not ask whether the integer path beats a classical control, and it draws
no performance conclusion. Scope creep into that question needs its own
approval.

THE COST IS UNKNOWN BY CONSTRUCTION, which is why the block is bounded by CALL
COUNT rather than by a quoted second figure (Criterion H). We have never run
this solver on this problem and no comparable anchor exists. Quoting a number
here would be inventing one, which is the failure the whole card exists to
prevent.

SAFETY, in order:
  1. --dry-run is the DEFAULT. Nothing is submitted without --execute.
  2. Every job is validated locally first (integer_path.validate()), so a bug
     in our own submission code cannot cost allocation seconds.
  3. The balance is read before and after; the delta is the billed cost, and
     it is recorded even if the response cannot be parsed.
  4. Calls run one at a time, smallest first. If call 1 is expensive, call 2
     does not run without a new approval.

Usage:
    python experiments/src/run_integer_probe.py --dry-run
    python experiments/src/run_integer_probe.py --execute --max-calls 1
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import store  # noqa: E402
from integer_path import IntegerJob, size_report  # noqa: E402

RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"
LEDGER = RESULTS_DIR / "integer_probe.json"

# Smallest first. The point is a SCALING BASIS, so two sizes beat one big one,
# and a cheap first call bounds the risk of the second.
PROBE_SIZES = (
    {"label": "probe_small", "n": 8, "upper_bound": 3},    # 32 levels
    {"label": "probe_mid", "n": 24, "upper_bound": 3},     # 96 levels
)

RELAXATION_SCHEDULE = 2      # frozen; never tuned inside a sizing probe
NUM_SAMPLES = 8              # frozen


def build_job(n: int, upper_bound: int, seed: int = 42) -> IntegerJob:
    """A well-conditioned integer quadratic at the requested size.

    Deliberately synthetic. The probe measures DEVICE TIME against problem
    size; using a real pool would confound the measurement with pool
    construction and would imply a performance claim this card does not make.
    """
    rng = np.random.default_rng(seed)
    a = rng.normal(size=(n, n))
    quad = (a + a.T) / 2
    quad += np.eye(n) * (np.abs(quad).sum(axis=1).max() + 1.0)   # diag-dominant
    return IntegerJob(linear=rng.normal(size=n), quadratic=quad,
                      upper_bound=np.full(n, upper_bound),
                      relaxation_schedule=RELAXATION_SCHEDULE,
                      num_samples=NUM_SAMPLES)


def balance() -> int | None:
    """Allocation seconds remaining, or None if it cannot be read.

    A balance that cannot be read is reported as None and NEVER as zero: the
    before/after delta is how the cost is established when a response cannot
    be parsed, and a silent zero would report a free call.
    """
    try:
        from qci_client import QciClient
        url = os.environ.get("QCI_API_URL")
        token = os.environ.get("QCI_TOKEN") or os.environ.get("QCI_API_KEY")
        if not (url and token):
            return None
        allocs = QciClient(url=url, api_token=token).get_allocations()
        return int(allocs["allocations"]["dirac"]["seconds"])
    except Exception:                                    # noqa: BLE001
        return None


def _load_env() -> None:
    env = Path(__file__).resolve().parents[2] / ".env"
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def announce(jobs: list[tuple[dict, IntegerJob]]) -> None:
    """The Criterion H block statement, printed before anything is submitted."""
    print("=" * 70)
    print("METERED BLOCK: Dirac-3 integer sizing probe (F87)")
    print("=" * 70)
    print(f"  calls            : {len(jobs)}")
    print("  expected seconds : UNKNOWN -- no comparable anchor exists.")
    print("                     Bounded by CALL COUNT, per Criterion H.")
    print(f"  relaxation_sched : {RELAXATION_SCHEDULE} (frozen)")
    print(f"  num_samples      : {NUM_SAMPLES} (frozen)")
    bal = balance()
    print(f"  balance before   : {bal if bal is not None else 'UNREADABLE'}")
    print()
    for spec, job in jobs:
        print(f"  --- {spec['label']} ---")
        for line in size_report(job).splitlines():
            print(f"      {line}")
    print()


def run_one(spec: dict, job: IntegerJob) -> dict:
    """Submit one job and record what it cost. Never raises."""
    from eqc_models.solvers import Dirac3IntegerCloudSolver

    before = balance()
    started = time.strftime("%Y-%m-%dT%H:%M:%S")
    row: dict = {
        "label": spec["label"], "n_variables": job.n_variables,
        "level_budget": job.level_budget,
        "relaxation_schedule": job.relaxation_schedule,
        "num_samples": job.num_samples,
        "balance_before": before, "started_utc": started,
    }
    try:
        solver = Dirac3IntegerCloudSolver()
        resp = solver.solve(job.to_model(),
                            relaxation_schedule=job.relaxation_schedule,
                            num_samples=job.num_samples)
        row["status"] = "ok"
        row["response_repr"] = repr(resp)[:600]
    except Exception as exc:                             # noqa: BLE001
        row["status"] = "error"
        row["error"] = f"{type(exc).__name__}: {exc}"[:400]

    row["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    after = balance()
    row["balance_after"] = after
    # The balance delta is the AUTHORITATIVE cost. Sprint 11's F47 established
    # this: the runner could not capture job ids, and the balance is what the
    # ledger was reconstructed from.
    row["metered_seconds"] = (before - after
                              if before is not None and after is not None
                              else None)
    row["cost_source"] = ("allocation balance before minus after"
                          if row["metered_seconds"] is not None
                          else "UNKNOWN -- balance unreadable, treat as unbilled "
                               "at your own risk")
    return row


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--execute", action="store_true",
                    help="actually submit. Without it, nothing is metered.")
    # Accepted explicitly even though it is the default, because the docstring
    # advertises it and a documented flag that errors is worse than no flag.
    ap.add_argument("--dry-run", action="store_true",
                    help="the default: validate and announce, submit nothing")
    ap.add_argument("--max-calls", type=int, default=1,
                    help="hard ceiling on submissions this run (default 1)")
    args = ap.parse_args(argv)

    _load_env()
    jobs = [(s, build_job(s["n"], s["upper_bound"])) for s in PROBE_SIZES]

    for spec, job in jobs:
        problems = job.validate()
        if problems:
            print(f"REFUSING: {spec['label']} fails local validation:")
            for p in problems:
                print(f"  - {p}")
            return 1

    announce(jobs[:args.max_calls])

    if not args.execute:
        print("DRY RUN. Nothing submitted, zero metered seconds.")
        print("Re-run with --execute after per-block approval.")
        return 0

    # ALREADY-RUN LABELS ARE SKIPPED. Without this, `--max-calls 2` after a
    # `--max-calls 1` run re-submits the first probe from the top rather than
    # resuming after it. That happened on 2026-09-23: an approved TWO-call
    # block cost THREE calls and 16 seconds instead of 12, because the runner
    # had no idea what it had already done.
    #
    # The ledger is the memory. A metered runner that cannot tell whether it
    # has already spent a second is one bad re-invocation away from spending
    # it twice, and the allocation has no undo.
    done = set()
    if LEDGER.exists():
        try:
            prior = json.loads(LEDGER.read_text(encoding="utf-8"))
            done = {c["label"] for c in prior.get("calls", [])
                    if c.get("status") == "ok"}
        except (OSError, ValueError, KeyError, TypeError):
            print("WARNING: the probe ledger is unreadable. REFUSING to "
                  "submit, because a re-run could duplicate a metered call.")
            return 1

    rows = []
    for spec, job in jobs[:args.max_calls]:
        if spec["label"] in done:
            print(f"skipping {spec['label']}: already completed "
                  "(see the ledger). Re-running it would spend seconds twice.")
            continue
        print(f"submitting {spec['label']} ...")
        row = run_one(spec, job)
        rows.append(row)
        print(f"  status={row['status']} metered={row['metered_seconds']}")
        if row["status"] == "error":
            print("  STOPPING: a call errored. The rest of the block does not "
                  "run without a new approval.")
            break

    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    existing = (json.loads(LEDGER.read_text(encoding="utf-8"))
                if LEDGER.exists() else {"calls": []})
    existing["calls"].extend(rows)
    existing["note"] = ("F87 integer sizing probe. Cost from the allocation "
                        "balance delta, per F47.")
    LEDGER.write_text(json.dumps(existing, indent=1) + "\n", encoding="utf-8")
    print(f"\nrecorded {len(rows)} call(s) in {LEDGER}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
