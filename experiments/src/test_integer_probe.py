"""The metered probe must not be able to spend seconds by accident.

F87 Task B. Criterion H: a metered block stops for explicit per-block
approval, every time. The failure this guards is a runner that submits because
someone ran it, rather than because it was approved.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "experiments" / "src" / "run_integer_probe.py"

sys.path.insert(0, str(ROOT / "experiments" / "src"))


def _src() -> str:
    return SCRIPT.read_text(encoding="utf-8")


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


def test_an_unreadable_balance_is_never_recorded_as_zero_cost():
    """The balance delta is the authoritative cost (F47). Reporting an
    unreadable balance as zero would report a free call."""
    src = _src()
    assert 'row["metered_seconds"] = (before - after' in src
    assert "if before is not None and after is not None" in src
    assert "UNKNOWN -- balance unreadable" in src


def test_an_errored_call_stops_the_block():
    src = _src()
    assert 'if row["status"] == "error":' in src
    assert "does not\n                  run without a new approval" in src or \
           "without a new approval" in src


def test_the_frozen_solve_parameters_are_not_tuned_here():
    """A sizing probe measures cost against size. Changing schedule or samples
    inside it would confound the measurement."""
    src = _src()
    assert "RELAXATION_SCHEDULE = 2" in src
    assert "NUM_SAMPLES = 8" in src
    assert "frozen" in src


def test_the_probe_sizes_fit_the_device():
    import run_integer_probe as rip
    for spec in rip.PROBE_SIZES:
        job = rip.build_job(spec["n"], spec["upper_bound"])
        assert job.validate() == [], f"{spec['label']}: {job.validate()}"
        assert job.fits_device()


def test_the_probe_sizes_differ_so_a_scaling_basis_is_possible():
    """One size gives a point, not a curve. The card promises a scaling
    basis."""
    import run_integer_probe as rip
    budgets = {rip.build_job(s["n"], s["upper_bound"]).level_budget
               for s in rip.PROBE_SIZES}
    assert len(budgets) >= 2, f"all probe sizes have the same budget: {budgets}"
