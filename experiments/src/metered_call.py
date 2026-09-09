"""Every Dirac-3 call: id captured at submission, cost measured, nothing lost.

F47. The F46 probe spent an approved metered call and its job id was never
captured, so its runtime is permanently unrecoverable and its cost is known only
from the allocation balance. Under Criterion H that is the worst failure mode:
the safe response to "did the approved call run?" is not to re-run, which stalls
the sprint.

WHAT THE SPIKE FOUND. `QciClient.process_job` already does the right things --
reads the allocation balance before, extracts the job id from `submit_job`, logs
it, polls, reads the balance after, returns results. We simply never captured
any of it. So this module drives `process_job` directly rather than wrapping or
monkeypatching anything.

FOUR GUARANTEES:

  1. the job id reaches disk BEFORE the wait begins, so a kill, timeout or lost
     connection leaves a recoverable handle rather than an unanswerable question
  2. cost is the allocation balance before minus after -- authoritative, and
     immune to the response-format change that broke the repr scrape when the
     account moved to the paid tier
  3. the log is appended and flushed line by line, so partial output survives
  4. the ledger records INTENT before the call and outcome after, so an
     interrupted call is visibly interrupted rather than absent

Nothing here submits without an explicit call. Reading the ledger, replaying a
job id, and estimating cost are all free.
"""
from __future__ import annotations

import datetime
import json
import math
import pathlib
import time
from dataclasses import asdict, dataclass, field

RESULTS = pathlib.Path(__file__).resolve().parents[1] / "results"
LEDGER = RESULTS / "qpu_cost_ledger.json"
LOG_DIR = RESULTS / "call_logs"


def _utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


@dataclass
class CallRecord:
    """One metered call, from intent to outcome."""
    label: str
    degree: int
    n_variables: int
    n_samples: int
    expected_seconds: str            # what Criterion H approval was given against
    submitted_utc: str | None = None
    job_id: str | None = None
    status: str = "intent"           # intent -> submitted -> ok | failed | refused
    balance_before: int | None = None
    balance_after: int | None = None
    measured_seconds: float | None = None
    runtime_sum_s: float | None = None
    per_sample_s: float | None = None
    error: str | None = None
    finished_utc: str | None = None
    tier: str = "paid"
    notes: list[str] = field(default_factory=list)


class UnbufferedLog:
    """Append-and-flush per line. A killed process keeps everything written."""

    def __init__(self, path: pathlib.Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self._path = path

    def write(self, line: str) -> None:
        with self._path.open("a", encoding="utf-8") as fh:
            fh.write(f"{_utc()}  {line}\n")
            fh.flush()

    @property
    def path(self) -> pathlib.Path:
        return self._path


def load_ledger() -> dict:
    if LEDGER.exists():
        return json.loads(LEDGER.read_text(encoding="utf-8"))
    return {"note": "measured QPU cost per Dirac-3 call", "calls": []}


def append_ledger(record: CallRecord) -> None:
    """Write the record immediately. Called at intent AND at outcome.

    Rewrites the matching entry rather than appending twice, keyed on the
    submitted timestamp plus label, so an interrupted call leaves one row
    showing where it stopped.
    """
    led = load_ledger()
    calls = led.setdefault("calls", [])
    key = (record.label, record.submitted_utc)
    for i, c in enumerate(calls):
        if (c.get("label"), c.get("submitted_utc")) == key and record.submitted_utc:
            calls[i] = asdict(record)
            break
    else:
        calls.append(asdict(record))
    LEDGER.write_text(json.dumps(led, indent=2) + "\n", encoding="utf-8")


def balance(client) -> int:
    return int(client.get_allocations()["allocations"]["dirac"]["seconds"])


def run_metered(client, job_body: dict, record: CallRecord,
                poll_s: float = 5.0, log: UnbufferedLog | None = None) -> dict:
    """Submit, capture the id, wait, measure the cost. One metered call.

    The caller is responsible for having stated call count and expected seconds
    to the team lead and obtained approval (Criterion H). This records what was
    approved alongside what happened, so the two can be compared afterwards.
    """
    log = log or UnbufferedLog(
        LOG_DIR / f"{record.label}_{time.strftime('%Y%m%dT%H%M%S')}.log")

    record.submitted_utc = _utc()
    record.balance_before = balance(client)
    log.write(f"INTENT label={record.label} vars={record.n_variables} "
              f"degree={record.degree} samples={record.n_samples} "
              f"expected={record.expected_seconds} balance={record.balance_before}")
    append_ledger(record)                     # on disk BEFORE anything is spent

    try:
        submit = client.submit_job(job_body=job_body)
        record.job_id = submit.get("job_id")
        record.status = "submitted"
        log.write(f"SUBMITTED job_id={record.job_id}")
        append_ledger(record)                 # the handle is now recoverable
    except Exception as e:                    # noqa: BLE001
        record.status = "failed"
        record.error = f"{type(e).__name__}: {str(e)[:400]}"
        record.finished_utc = _utc()
        low = str(e).lower()
        if "variable" in low and "limit" in low:
            record.status = "refused"
            record.notes.append("server-side sizing refusal; no spend")
        log.write(f"SUBMIT FAILED {record.error}")
        append_ledger(record)
        raise

    try:
        # Poll on status NAMES rather than importing the library's enum: the
        # import path is not stable (`from qci_client import enum` fails), and
        # a hardcoded set survives the constants moving.
        final = {"COMPLETED", "ERRORED", "CANCELLED", "FAILED"}
        status = None
        while True:
            latest = client.get_job_status(job_id=record.job_id)["status"]
            if latest != status:
                status = latest
                log.write(f"STATUS {status}")
            if str(status).upper() in final:
                break
            time.sleep(poll_s)
        if str(status).upper() != "COMPLETED":
            raise RuntimeError(f"job {record.job_id} finished as {status}")

        results = client.get_job_results(job_id=record.job_id)
        record.status = "ok"
    except Exception as e:                    # noqa: BLE001
        record.status = "failed"
        record.error = f"{type(e).__name__}: {str(e)[:400]}"
        log.write(f"WAIT FAILED {record.error} -- job_id={record.job_id} is still "
                  f"valid; retrieve with job_query.py rather than re-running")
        record.finished_utc = _utc()
        raise
    finally:
        # Measure THEN write. An earlier version appended inside the except
        # block, before this ran, so a failed call recorded no cost at all --
        # reproducing the F46 problem on the one path where it matters most.
        record.balance_after = balance(client)
        if record.balance_before is not None:
            record.measured_seconds = float(record.balance_before - record.balance_after)
        log.write(f"BALANCE after={record.balance_after} "
                  f"cost={record.measured_seconds}")
        append_ledger(record)

    # Device metrics: the billed quantity is ceil(sum(runtime)), validated in
    # qpu_cost_model. Recorded so the estimator improves with every call.
    try:
        import qpu_cost_model as qcm
        jc = qcm.cost_from_metrics(record.job_id,
                                   client.get_job_metrics(job_id=record.job_id))
        if jc:
            record.runtime_sum_s = round(jc.runtime_sum_s, 4)
            record.per_sample_s = round(jc.per_sample_s, 4)
            derived = math.ceil(jc.runtime_sum_s)
            if record.measured_seconds is not None and derived != record.measured_seconds:
                record.notes.append(
                    f"ceil(sum(runtime))={derived} differs from balance delta "
                    f"{record.measured_seconds}; balance is authoritative")
    except Exception as e:                    # noqa: BLE001
        record.notes.append(f"metrics unavailable: {type(e).__name__}")

    record.finished_utc = _utc()
    log.write(f"DONE status={record.status} cost={record.measured_seconds}s "
              f"runtime_sum={record.runtime_sum_s}")
    append_ledger(record)
    return results


def candidate_ids_at(random_field: str, counter_start: int, submitted_epoch: int,
                     n_calls: int, window_s: int = 2) -> list[str]:
    """Candidate job ids from a known random field, counter and TIMESTAMP.

    Job ids are MongoDB ObjectIds: 4-byte timestamp, 5-byte per-generator
    random, 3-byte counter.

    WHAT IS AND IS NOT RECOVERABLE, measured against the 27-job campaign:

      - the random field IS constant within one client process (all 27 share
        08442f441b), so it transfers across a block
      - the counter increases but is NOT contiguous: 33 counter values for 27
        jobs, six gaps of 2, because the server draws ids for other objects
        (the polynomial file uploads) from the same sequence
      - the TIMESTAMP changes per job -- those 27 span 47 minutes -- so it
        cannot be held constant across a block

    An earlier version of this function held the whole 18-character head fixed,
    which assumed a constant timestamp, and produced 26 wrong ids out of 27. The
    test caught it against real data.

    CONSEQUENCE: this is a forensic aid, not a recovery mechanism. It is useful
    when the submission SECOND is known -- from an unbuffered log that recorded
    the moment but lost the id, which is exactly what F47's logging now
    guarantees. Without a timestamp the search is a time window times a
    non-contiguous counter range, thousands of candidates each costing an API
    call, and the right answer is that the id is gone.

    Verify every candidate with job_query before believing it.
    """
    if len(random_field) != 10:
        raise ValueError(f"random field must be 5 bytes of hex: {random_field!r}")
    out = []
    for ts in range(submitted_epoch - window_s, submitted_epoch + window_s + 1):
        for c in range(counter_start, counter_start + n_calls + max(4, n_calls // 2)):
            out.append(f"{ts:08x}{random_field}{c:06x}")
    return out


def split_object_id(job_id: str) -> dict:
    """Decompose an id into its parts, for logging and forensics."""
    if len(job_id) != 24:
        raise ValueError(f"not an ObjectId: {job_id!r}")
    try:
        return {"epoch": int(job_id[:8], 16),
                "random_field": job_id[8:18],
                "counter": int(job_id[18:], 16)}
    except ValueError as e:
        raise ValueError(f"not an ObjectId: {job_id!r}") from e
