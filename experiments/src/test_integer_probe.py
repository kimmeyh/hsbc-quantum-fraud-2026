"""The metered probe must not be able to spend seconds by accident.

F87 Task B. Criterion H: a metered block stops for explicit per-block
approval, every time. The failure this guards is a runner that submits because
someone ran it, rather than because it was approved.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "experiments" / "src" / "run_integer_probe.py"

sys.path.insert(0, str(ROOT / "experiments" / "src"))


def _src() -> str:
    return SCRIPT.read_text(encoding="utf-8")


@pytest.fixture
def probe(tmp_path, monkeypatch):
    """The runner with its ledger pointed at a scratch file.

    Every test below calls the REAL functions. None can reach the device:
    run_one is either stubbed or fails at its local import, and the
    committed ledger is never opened.
    """
    import run_integer_probe as rip
    monkeypatch.setattr(rip, "LEDGER", tmp_path / "integer_probe.json")
    return rip


def _boom(job):
    """Stand in for the device. NOTHING in this file may reach QCi.

    run_one's cost accounting is what these tests exercise, and that runs
    identically whichever way the solve ends.
    """
    raise RuntimeError("stubbed: no submission in a unit test")


def _seed(rip, *rows: dict) -> None:
    rip.LEDGER.parent.mkdir(parents=True, exist_ok=True)
    rip.LEDGER.write_text(json.dumps({"calls": list(rows)}),
                          encoding="utf-8")


def test_the_runner_exists():
    assert SCRIPT.exists()


def test_submitting_requires_an_explicit_flag():
    """Bare invocation must be a DRY RUN. A runner that meters by default is
    one bad command away from spending the allocation."""
    r = subprocess.run([sys.executable, str(SCRIPT)],
                       cwd=str(ROOT), capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-400:]
    assert "DRY RUN" in r.stdout
    assert "Nothing submitted, zero metered seconds" in r.stdout


def test_the_dry_run_flag_is_accepted():
    """The docstring advertises it; a documented flag that errors is worse
    than no flag."""
    r = subprocess.run([sys.executable, str(SCRIPT), "--dry-run"],
                       cwd=str(ROOT), capture_output=True, text=True)
    assert r.returncode == 0


def test_the_block_statement_quotes_what_criterion_h_requires():
    """Call count, and the provenance of the seconds estimate."""
    r = subprocess.run([sys.executable, str(SCRIPT)],
                       cwd=str(ROOT), capture_output=True, text=True)
    out = r.stdout
    assert "METERED BLOCK" in out
    assert "calls" in out
    assert "UNKNOWN" in out, "the seconds estimate must state its provenance"
    assert "Bounded by CALL COUNT" in out


def test_the_default_call_ceiling_is_one():
    """Smallest first, one at a time. If call 1 is expensive, call 2 does not
    run without a new approval."""
    assert 'ap.add_argument("--max-calls", type=int, default=1' in _src()


def test_every_job_is_validated_before_any_submission():
    """A bug in our own submission code must not cost allocation seconds."""
    src = _src()
    assert "problems = job.validate()" in src
    assert "REFUSING" in src


def test_an_unreadable_balance_is_never_recorded_as_zero_cost(
        probe, monkeypatch):
    """The balance delta is the authoritative cost (F47). Reporting an
    unreadable balance as zero would report a free call.

    BEHAVIORAL. The source-grep version could not fail: changing the
    `else None` to `else 0` -- the single token that encodes the
    behavior -- left all three of its assertions true, because each
    matched a neighboring line. Confirmed by mutation, PR #139 review.
    """
    monkeypatch.setattr(probe, "balance", lambda: None)
    monkeypatch.setattr(probe, "_solve", _boom)
    row = probe.run_one({"label": "unreadable"}, probe.build_job(4, 2))

    assert row["metered_seconds"] is None, (
        "an unreadable balance was recorded as a number -- a call whose "
        "cost is unknown must never read as free")
    assert "UNKNOWN" in row["cost_source"]


def test_a_readable_balance_still_records_the_delta(probe, monkeypatch):
    """The companion. Without it, an unconditional None would pass the
    test above and no call would ever record a cost at all."""
    seen = iter([1000, 987])
    monkeypatch.setattr(probe, "balance", lambda: next(seen))
    monkeypatch.setattr(probe, "_solve", _boom)
    row = probe.run_one({"label": "readable"}, probe.build_job(4, 2))

    assert row["metered_seconds"] == 13
    assert "UNKNOWN" not in row["cost_source"]


def test_an_errored_call_stops_the_block(probe, monkeypatch):
    """Call 2 does not run because call 1 failed. BEHAVIORAL: the grep
    version asserted the shape of the `if`, never that the `break`
    prevents anything."""
    calls = []

    def stub(spec, job):
        calls.append(spec["label"])
        return {"label": spec["label"], "status": "error_after_submit",
                "metered_seconds": 165, "error": "poll timeout"}

    monkeypatch.setattr(probe, "run_one", stub)
    probe.main(["--execute", "--max-calls", "6"])
    assert len(calls) == 1, (
        f"an errored call did not stop the block; it submitted {calls}")


def test_the_frozen_solve_parameters_are_not_tuned_here():
    """A sizing probe measures cost against size. Changing schedule or samples
    inside it would confound the measurement."""
    src = _src()
    assert "RELAXATION_SCHEDULE = 2" in src
    assert "NUM_SAMPLES = 8" in src
    assert "frozen" in src


def test_the_probe_sizes_fit_the_device():
    import run_integer_probe as rip
    for spec in rip.load_designs():
        job = rip.build_job(spec["n"], spec["upper_bound"])
        assert job.validate() == [], f"{spec['label']}: {job.validate()}"
        assert job.fits_device()


def test_the_probe_sizes_differ_so_a_scaling_basis_is_possible():
    """One size gives a point, not a curve. The card promises a scaling
    basis."""
    import run_integer_probe as rip
    budgets = {rip.build_job(s["n"], s["upper_bound"]).level_budget
               for s in rip.load_designs()}
    assert len(budgets) >= 2, f"all probe sizes have the same budget: {budgets}"


# ------------------- IMP-3: idempotency is a PRECONDITION, not a post-mortem

def test_the_runner_refuses_to_resubmit_a_completed_design(
        probe, monkeypatch):
    """A metered runner must not be able to spend the same seconds twice.

    Sprint 18 spent THREE calls against a two-call approval because a second
    invocation with a higher --max-calls restarted from the top. The duplicate
    cost 4 seconds; had it been the largest probe it would have cost 165.

    IMP-3 makes this a precondition: any runner that submits metered work
    refuses to re-submit a completed unit, and that is tested BEFORE the first
    approval stop rather than added after the first over-spend.
    """
    labels = [s["label"] for s in probe.load_designs()]
    _seed(probe, *[{"label": lab, "status": "ok", "metered_seconds": 4}
                   for lab in labels[:2]])

    calls = []

    def stub(spec, job):
        calls.append(spec["label"])
        return {"label": spec["label"], "status": "ok",
                "metered_seconds": 4}

    monkeypatch.setattr(probe, "run_one", stub)
    probe.main(["--execute", "--max-calls", "6"])

    assert set(calls).isdisjoint(labels[:2]), (
        f"a completed design was re-submitted: {calls}")
    assert calls, "nothing ran at all, so this proves nothing"


def test_an_unreadable_ledger_refuses_to_submit(probe, monkeypatch):
    """Fail CLOSED. A runner that cannot tell what it has already spent
    must not guess -- the allocation has no undo.

    BEHAVIORAL. The grep version asserted `return 1` within a
    200-character window of a phrase. The refusal became a SystemExit,
    which is strictly stronger, and the grep went red on the improvement.
    """
    probe.LEDGER.parent.mkdir(parents=True, exist_ok=True)
    probe.LEDGER.write_text("{ this is not json", encoding="utf-8")

    submitted = []
    monkeypatch.setattr(probe, "run_one",
                        lambda spec, job: submitted.append(spec["label"]))
    with pytest.raises(SystemExit) as exc:
        probe.main(["--execute", "--max-calls", "6"])

    assert "REFUS" in str(exc.value).upper()
    assert not submitted, "it submitted despite an unreadable ledger"


def test_a_billed_call_that_errored_blocks_a_resubmission(probe,
                                                          monkeypatch):
    """The expensive re-entry path. A call that billed and THEN failed on
    the poll must not be retried, because the seconds are already gone.

    Errors correlate with long jobs, so this is the case that costs the
    most. The first version admitted only status == "ok" into the skip
    set, so a job that cost 165 seconds and then timed out was submitted
    again. Found by the PR #139 review.
    """
    label = probe.load_designs()[0]["label"]
    _seed(probe, {"label": label, "status": "error_after_submit",
                  "metered_seconds": 165, "error": "poll timeout"})

    submitted = []

    def stub(spec, job):
        submitted.append(spec["label"])
        return {"label": spec["label"], "status": "ok", "metered_seconds": 4}

    monkeypatch.setattr(probe, "run_one", stub)
    probe.main(["--execute", "--max-calls", "6"])
    assert label not in submitted, (
        "a call that already cost 165 seconds was submitted again")


def test_a_call_that_failed_locally_is_still_retryable(probe, monkeypatch):
    """The other half. Blocking every error would strand a design on a
    typo in our own code, which costs nothing to retry. `error_local` is
    written only when the failure happened before a byte reached the
    device."""
    label = probe.load_designs()[0]["label"]
    # NO metered_seconds key. This is the case that distinguishes the
    # error_local branch from the seconds check below it: `.get()` returns
    # None, which every other path reads as "cost unknown" and blocks. Seeding
    # an explicit 0 instead made all three paths agree, so the test passed
    # under a mutation that broke every one of them.
    _seed(probe, {"label": label, "status": "error_local",
                  "error": "ImportError: no module named eqc_models"})

    submitted = []

    def stub(spec, job):
        submitted.append(spec["label"])
        return {"label": spec["label"], "status": "ok",
                "metered_seconds": 4}

    monkeypatch.setattr(probe, "run_one", stub)
    probe.main(["--execute", "--max-calls", "1"])
    assert label in submitted, (
        "a provably unbilled failure was treated as already spent")


def test_the_announced_call_count_is_the_count_that_will_be_billed(probe):
    """Criterion H requires the call count at the approval stop. An
    approval given against an inflated figure is not informed approval.

    The first version announced `--max-calls`, then skipped completed
    labels inside the loop: `--max-calls 5` announced 5 and submitted 1.
    """
    import contextlib
    import io

    labels = [s["label"] for s in probe.load_designs()]
    _seed(probe, *[{"label": lab, "status": "ok", "metered_seconds": 4}
                   for lab in labels[:-1]])

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        probe.main(["--max-calls", "5"])

    quoted = [ln for ln in buf.getvalue().splitlines()
              if ln.strip().startswith("calls")]
    assert quoted, "the announcement did not state a call count at all"
    assert quoted[0].strip().endswith(": 1"), (
        f"one design is pending, but the stop quoted {quoted[0]!r}")


def test_each_row_is_committed_before_the_next_call(probe, monkeypatch):
    """The durability boundary is PER CALL. A crash between a billed call
    and the write loses the record of money already spent -- and the next
    run, seeing no record, submits it again."""
    seen = []

    def stub(spec, job):
        try:
            prior = json.loads(probe.LEDGER.read_text(encoding="utf-8"))
            seen.append(len(prior["calls"]))
        except (OSError, ValueError):
            seen.append(0)
        return {"label": spec["label"], "status": "ok",
                "metered_seconds": 4}

    monkeypatch.setattr(probe, "run_one", stub)
    probe.main(["--execute", "--max-calls", "3"])

    assert seen == [0, 1, 2], (
        f"rows were not committed one at a time: {seen}")


def test_a_crash_mid_block_still_records_the_call_that_billed(
        probe, monkeypatch):
    """Why the commit sits in a `finally`. KeyboardInterrupt is the
    realistic case: the operator watches a long job and stops it."""
    second = probe.load_designs()[1]["label"]

    def stub(spec, job):
        if spec["label"] == second:
            raise KeyboardInterrupt
        return {"label": spec["label"], "status": "ok",
                "metered_seconds": 4}

    monkeypatch.setattr(probe, "run_one", stub)
    with pytest.raises(KeyboardInterrupt):
        probe.main(["--execute", "--max-calls", "3"])

    recorded = json.loads(probe.LEDGER.read_text(encoding="utf-8"))["calls"]
    assert len(recorded) == 1, (
        f"the completed call was lost by the interrupt: {recorded}")


# ------------------------------- IMP-4: designs are configuration, not code

def test_probe_designs_live_in_a_config_file():
    """Running one design required monkeypatching the list from a throwaway
    script. Dangerous when the selection costs metered seconds."""
    designs = ROOT / "experiments" / "probe_designs.json"
    assert designs.exists(), "probe designs are not in a config file"
    doc = json.loads(designs.read_text(encoding="utf-8"))
    assert doc["designs"], "no designs defined"
    for d in doc["designs"]:
        for field in ("label", "n", "upper_bound"):
            assert field in d, f"design {d} is missing {field}"


def test_design_labels_are_unique():
    """The ledger skips by label. Two designs sharing one would make the
    second permanently unrunnable, or the first re-runnable."""
    doc = json.loads((ROOT / "experiments" / "probe_designs.json")
                     .read_text(encoding="utf-8"))
    labels = [d["label"] for d in doc["designs"]]
    assert len(labels) == len(set(labels)), f"duplicate labels: {labels}"


def test_only_selects_exactly_one_design():
    import run_integer_probe as rip
    picked = rip.load_designs(only="probe_deep")
    assert len(picked) == 1 and picked[0]["label"] == "probe_deep"


def test_only_rejects_an_unknown_label_rather_than_running_everything():
    """A typo must not silently select the full list."""
    import run_integer_probe as rip
    with pytest.raises(SystemExit, match="no design labelled"):
        rip.load_designs(only="probe_typo")


# ------------------ a design nobody approved must not be reachable by count

def test_a_held_design_is_excluded_from_a_block_run():
    """probe_ceiling was designed and deliberately NOT run -- the revised
    estimate after round 2 put it near 181 s, above the approved envelope.

    It carried no marker, so `--max-calls 6` would have submitted the most
    expensive design in the file. The ledger skip does not help: a design
    that never ran is not "done". Found by the PR #139 review.
    """
    import run_integer_probe as rip
    labels = [d["label"] for d in rip.load_designs()]
    assert "probe_ceiling" not in labels, (
        "a held design is reachable by raising --max-calls")
    assert labels, "the hold filter removed everything"


def test_a_held_design_is_still_reachable_by_name():
    """A hold is not a deletion. `--only` remains the supported way to run
    one deliberately, which is the whole point of IMP-4."""
    import run_integer_probe as rip
    picked = rip.load_designs(only="probe_ceiling")
    assert [d["label"] for d in picked] == ["probe_ceiling"]


def test_the_hold_states_a_reason():
    """A bare flag tells the next operator nothing about whether the hold
    still applies."""
    import json
    import run_integer_probe as rip
    doc = json.loads(rip.DESIGNS_FILE.read_text(encoding="utf-8"))
    for d in doc["designs"]:
        if "hold" in d:
            assert isinstance(d["hold"], str) and len(d["hold"]) > 20, (
                f"{d['label']} is held without a usable reason: {d['hold']!r}")


def test_the_designs_are_ordered_by_variable_count_not_by_cost():
    """The ordering is by variable count, and the docstring must not promise
    more than that.

    I first wrote this test asserting "cheapest first", on the reasoning that
    cost tracks variables. The measurements refute it: probe_deep cost 71 s at
    60 variables while probe_mid_hi cost 28 s at the SAME 60, because the
    level budgets differ. Variables dominate ACROSS the probes that vary only
    in n; they do not order the file globally.

    So the guard is on the property that holds -- monotone n among the designs
    that share an upper_bound -- and the runner's docstring says "by variable
    count" rather than "smallest first".
    """
    import run_integer_probe as rip
    designs = rip.load_designs()
    by_bound: dict[int, list[int]] = {}
    for d in designs:
        by_bound.setdefault(d["upper_bound"], []).append(d["n"])
    for bound, ns in by_bound.items():
        assert ns == sorted(ns), (
            f"designs at upper_bound={bound} are not ordered by n: {ns}")

    src = SCRIPT.read_text(encoding="utf-8")
    assert "smallest first" not in src, (
        "the loader docstring promises an ordering the file does not have")


def test_a_completed_design_does_not_consume_a_call_slot(probe):
    """--max-calls means N NEW calls, not N designs considered.

    The slice used to happen before the done filter, so after a
    --max-calls 1 run, --max-calls 2 offered only ONE new design: the
    completed label ate a slot. An operator who approved two calls and got
    one would re-invoke with a higher number, which is precisely how the
    2026-09-23 over-spend happened. Found by the PR #139 review.
    """
    labels = [d["label"] for d in probe.load_designs()]
    _seed(probe, {"label": labels[0], "status": "ok", "metered_seconds": 4})

    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        probe.main(["--max-calls", "2"])
    offered = [ln.split()[1] for ln in buf.getvalue().splitlines()
               if ln.startswith("  --- ")]

    assert offered == labels[1:3], (
        f"--max-calls 2 with one design done offered {offered}; it must "
        f"offer the next two NEW designs")
