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
  4. Calls run one at a time, in variable-count order within a level budget.
     If call 1 is expensive, call 2 does not run without a new approval.
  5. A design carrying a `hold` is reachable only by name, never by raising
     --max-calls.

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

DESIGNS_FILE = Path(__file__).resolve().parents[1] / "probe_designs.json"


def load_designs(only: str | None = None) -> tuple[dict, ...]:
    """Probe designs, from a config file rather than a module constant.

    IMP-4 (Sprint 18 retrospective). These were hardcoded here, so running ONE
    design meant monkeypatching the list from a throwaway script -- acceptable
    for a careful operator, dangerous when the selection costs metered
    seconds. A file can be edited, reviewed and diffed before the approval
    stop, and `--only` makes single-design runs a supported path instead of an
    improvisation.

    Ordered by VARIABLE COUNT, which Sprint 18 measured as the cost driver, so
    the file is also ordered cheapest-first and a surprise at a small size
    stops the block before a large one.

    A design carrying a `hold` is excluded from a block run and reachable only
    by naming it with `--only`. probe_ceiling is held: it was designed and
    deliberately NOT run, at a revised estimate near 181 s above the approved
    envelope, and it carried no marker -- so `--max-calls 6` would have
    submitted the most expensive design in the file, which no one approved.
    The ledger skip does not help, because a design that never ran is not
    "done". Found by the PR #139 review.
    """
    doc = json.loads(DESIGNS_FILE.read_text(encoding="utf-8"))
    designs = tuple(doc["designs"])
    if only:
        picked = tuple(d for d in designs if d["label"] == only)
        if not picked:
            raise SystemExit(
                f"no design labelled {only!r} in {DESIGNS_FILE.name}. "
                f"Available: {', '.join(d['label'] for d in designs)}")
        return picked

    held = [d for d in designs if d.get("hold")]
    for d in held:
        print(f"HELD, not in this block: {d['label']} -- {d['hold']}")
    return tuple(d for d in designs if not d.get("hold"))


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


def append_to_ledger(row: dict) -> None:
    """Commit ONE row immediately, atomically.

    The durability boundary must be PER CALL, not per run. The first version
    accumulated rows in memory and wrote once after the loop, so a crash or a
    Ctrl-C between a billed call and that write lost the record of money
    already spent -- and the next run, seeing no record, would re-submit it.
    That is the double-spend the ledger exists to prevent, arriving through
    the back door.

    The write goes through a temp file and an atomic replace, so a torn write
    cannot leave invalid JSON. store.py already established this idiom here;
    the metered runner has strictly more to lose and was not using it.

    Found by the PR #139 review.
    """
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    try:
        existing = json.loads(LEDGER.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        existing = {"calls": []}
    existing.setdefault("calls", []).append(row)
    existing["note"] = ("F87 integer sizing probe. Cost from the allocation "
                        "balance delta, per F47.")
    tmp = LEDGER.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(existing, indent=1) + "\n", encoding="utf-8")
    tmp.replace(LEDGER)


def completed_labels() -> tuple[set, dict]:
    """(labels not to re-run, labels that are BLOCKED with the reason).

    A call that billed and then failed on the poll is the expensive re-entry
    path, and errors correlate with long jobs. The first version admitted only
    status == "ok" into the skip set, so a job that cost 165 seconds and then
    timed out was re-submitted on the next run.

    "It errored and I cannot tell whether it billed" must also block. That is
    the state that must never read as safe to retry.
    """
    if not LEDGER.exists():
        return set(), {}
    try:
        prior = json.loads(LEDGER.read_text(encoding="utf-8"))
        calls = prior.get("calls", [])
    except (OSError, ValueError, KeyError, TypeError):
        raise SystemExit(
            "REFUSING to submit: the probe ledger is unreadable, so a re-run "
            "could duplicate a metered call.")

    done, blocked = set(), {}
    for c in calls:
        label = c.get("label")
        if not label:
            continue
        if c.get("status") == "ok":
            done.add(label)
            continue
        if c.get("status") == "error_local":
            continue          # provably unbilled; safe to retry
        secs = c.get("metered_seconds")
        if secs is None or secs > 0:
            cost = (f"{secs} second(s)" if secs is not None
                    else "an UNKNOWN number of seconds")
            blocked[label] = (
                f"a prior call errored AFTER costing {cost}. Re-submitting "
                "would spend them again. Check the QCi job list, then remove "
                "that row from the ledger if it is genuinely unbilled.")
            done.add(label)
    return done, blocked


def _solve(job: IntegerJob, model):
    """THE SUBMISSION. Every metered second this repository spends on the
    integer path passes through this function.

    It exists as a named function so a test can replace it. Before, the only
    way to exercise run_one's cost accounting was to let the solver construct
    and fail, which made the tests depend on QCI_TOKEN being absent -- and on
    this machine it is present, so two tests silently made a live API call.
    A test that needs credentials to stay offline is not offline.

    The import is deliberately inside: importing the vendor solver is local
    setup, and a failure here must still be classified as post-submit, since
    by the time it runs the caller has already committed to submitting.
    """
    from eqc_models.solvers import Dirac3IntegerCloudSolver
    return Dirac3IntegerCloudSolver().solve(
        model,
        relaxation_schedule=job.relaxation_schedule,
        num_samples=job.num_samples)


def run_one(spec: dict, job: IntegerJob) -> dict:
    """Submit one job and record what it cost. Never raises on Exception.

    THE STATUS SAYS WHETHER MONEY COULD HAVE BEEN SPENT, because the resume
    logic depends on it:

        error_local        submission never attempted; provably 0 s
        error_after_submit the device may have billed before the failure

    The first version recorded both as "error".
    """
    before = balance()
    started = time.strftime("%Y-%m-%dT%H:%M:%S")
    row: dict = {
        "label": spec["label"], "n_variables": job.n_variables,
        "level_budget": job.level_budget,
        "relaxation_schedule": job.relaxation_schedule,
        "num_samples": job.num_samples,
        "balance_before": before, "started_utc": started,
    }
    # LOCAL setup in its own block: anything failing here happened before a
    # byte reached QCi, so it is provably unbilled and safe to retry.
    try:
        model = job.to_model()
    except Exception as exc:                             # noqa: BLE001
        row["status"] = "error_local"
        row["error"] = f"{type(exc).__name__}: {exc}"[:400]
        row["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        row["balance_after"] = before
        row["metered_seconds"] = 0
        row["cost_source"] = "no submission was attempted"
        return row

    try:
        resp = _solve(job, model)
        row["status"] = "ok"
        row["response_repr"] = repr(resp)[:600]
    except Exception as exc:                             # noqa: BLE001
        row["status"] = "error_after_submit"   # MAY have billed
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
    ap.add_argument("--only", default=None, metavar="LABEL",
                    help="run exactly one design by label. A supported path "
                         "rather than an edit to the design list.")
    args = ap.parse_args(argv)

    _load_env()
    jobs = [(s, build_job(s["n"], s["upper_bound"]))
            for s in load_designs(args.only)]

    for spec, job in jobs:
        problems = job.validate()
        if problems:
            print(f"REFUSING: {spec['label']} fails local validation:")
            for p in problems:
                print(f"  - {p}")
            return 1

    # THE LEDGER IS READ BEFORE THE ANNOUNCE, so the count quoted at the
    # approval stop is the count that will actually be billed. The first
    # version sliced by --max-calls and announced the slice length, then
    # skipped completed labels inside the loop -- so `--max-calls 5` announced
    # "calls: 5" and submitted 1. Criterion H requires stating the call count,
    # and an approval given against an inflated figure is not informed.
    done, blocked = completed_labels()
    for label, why in blocked.items():
        print(f"REFUSING {label}: {why}")
    if blocked:
        print()
    for spec, _job in jobs:
        if spec["label"] in done and spec["label"] not in blocked:
            print(f"skipping {spec['label']}: already completed. Re-running "
                  "it would spend those seconds twice.")

    block = [(s, j) for s, j in jobs if s["label"] not in done][:args.max_calls]

    # An EMPTY block still announces and still reports the dry run. Returning
    # early here skipped both, so a bare invocation with everything already
    # recorded printed no confirmation that nothing was submitted -- the one
    # line an operator reads to know a command was safe. Criterion H's block
    # statement is not conditional on the block being non-empty.
    announce(block)

    if not args.execute:
        print("DRY RUN. Nothing submitted, zero metered seconds.")
        return 0

    if not block:
        print()
        print("NOTHING TO SUBMIT. Every selected design is already recorded.")
        return 0
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
    submitted = 0
    for spec, job in block:
        print(f"submitting {spec['label']} ...")
        row = None
        try:
            row = run_one(spec, job)
        finally:
            # COMMIT BEFORE THE NEXT CALL, always. A crash or Ctrl-C between a
            # billed call and the write used to lose the record of what was
            # spent, and the next run would re-submit it.
            if row is not None:
                append_to_ledger(row)
                submitted += 1
        print(f"  status={row['status']} metered={row['metered_seconds']}")
        if row["status"] != "ok":
            print(f"  STOPPING: {row['label']} returned {row['status']}. The "
                  "rest of the block does not run without a new approval.")
            if row["status"] == "error_after_submit":
                print("  NOTE: this call MAY have billed. The ledger records "
                      "it and a re-run will refuse to submit it again.")
            break

    print(f"\nrecorded {submitted} call(s) in {LEDGER}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
