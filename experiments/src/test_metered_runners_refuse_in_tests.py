"""No test process may spend Dirac-3 seconds. Ever.

Sprint 21, and this guard exists because I did it.

Two of my own window-guard tests invoked `run_hardware_b4.py` and
`run_hardware_b5.py` with `--max-calls 1`, then checked for "REFUSING" in the
output AFTER `subprocess.run` had already returned. Before 18:00 local they
skipped, so they looked correct. Once the team lead's 18:00 window opened the
guard correctly ALLOWED the run, and the tests submitted two real jobs at
20:57 and 21:02 local on 2026-10-05 -- with no Criterion H statement read by
any human.

Nothing was billed, by luck alone: one submission hit a malformed job body and
the other an SSL error. A correct body would have spent device seconds from a
test run against an allocation that has no undo.

`pytest.skip` placed after `subprocess.run` is the whole defect: by the time
the skip is evaluated, the spend has happened.

The tests were rewritten to use source-level checks. These guards pin the
STRUCTURAL fix, which does not depend on any test being written carefully: the
runners refuse to submit when they detect a pytest process, whatever their
arguments say.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parent
ROOT = SRC.parents[1]

RUNNERS = ("run_hardware_b4.py", "run_hardware_b5.py")


@pytest.mark.parametrize("runner", RUNNERS)
def test_the_runner_refuses_when_invoked_from_a_test(runner):
    """Invoked WITH the pytest marker in the environment, the runner must
    refuse before constructing a client or submitting anything.

    This is the one place a test is allowed to invoke a metered runner at all,
    and it is safe precisely because the refusal is what is being asserted.
    """
    env = dict(os.environ)
    env["PYTEST_CURRENT_TEST"] = "guard::test_the_runner_refuses"
    r = subprocess.run(
        [sys.executable, str(SRC / runner), "--max-calls", "1"],
        capture_output=True, text=True, cwd=str(ROOT), env=env, timeout=2400)

    assert "REFUSING" in r.stdout, (
        f"{runner} did not refuse when invoked from a test process. "
        f"stdout tail: {r.stdout[-300:]}")
    assert "test process" in r.stdout
    assert r.returncode == 5, (
        f"{runner} must exit 5 on the test-process refusal, got "
        f"{r.returncode}. A refusal that exits 0 reports success.")
    assert "SUBMITTED" not in r.stdout


@pytest.mark.parametrize("runner", RUNNERS)
def test_the_runner_never_hand_builds_a_job_body(runner):
    """Submission goes through eqc-models, as every block since B1 has.

    The first B4 and B5 runners hand-built the request with invented field
    names; QCi rejected the one that reached it ("400: Must specify one and
    only one job under the job_submission.problem_config field"). The dry run
    of that version stopped before the request was built, so nothing checked
    the one part the vendor reads. `run_hardware_b3._submit_via_eqc` already
    said why this is wrong: a hand-built body "is a reimplementation that can
    drift, which is exactly what [ADR-0002] rejects".
    """
    src = (SRC / runner).read_text(encoding="utf-8")
    code = src.split('"""', 2)[-1]          # past the module docstring
    for forbidden in ('"job_submission"', '"problem_config"',
                      '"device_config"', "submit_job("):
        assert forbidden not in code, (
            f"{runner} builds part of a job body itself ({forbidden}). Submit "
            "through the eqc-models classifier and eqc_submit.metered_fit.")
    assert "eqc_submit.metered_fit" in code
    assert "eqc_submit.offline_solver" in code, (
        "the dry run must go through the library with only the cloud solver "
        "stubbed, or it never exercises the request")


@pytest.mark.parametrize("runner", RUNNERS)
def test_the_test_process_check_precedes_the_window_check(runner):
    """Order matters. The window opens every evening; the test-process check
    does not. If the window check came first, an evening test run would reach
    the client exactly as it did on 2026-10-05."""
    src = (SRC / runner).read_text(encoding="utf-8")
    i_test = src.index("PYTEST_CURRENT_TEST")
    i_window = src.index("if not (_window_open()")
    i_client = src.index("QciClient(")
    assert i_test < i_window < i_client, (
        f"{runner}: the test-process refusal must come before the window "
        "check, which must come before client construction")


@pytest.mark.parametrize("runner", RUNNERS)
def test_no_test_file_invokes_a_runner_without_dry_run_or_the_guard_env(runner):
    """The behavioral fix above does not excuse a test that tries.

    Any test invoking a metered runner must either pass --dry-run or be the
    refusal guard in this file. Scanning for the pattern catches a new test
    reintroducing the defect, which is how it arrived the first time.
    """
    # Walk the AST rather than scanning text. The first version of this guard
    # looked 200 characters BACKWARDS for the word "subprocess" and flagged a
    # `read_text` call because the docstring above it discussed subprocesses --
    # a false positive, and exactly the unanchored-substring defect this
    # repository keeps paying for. The call graph is the fact; prose is not.
    import ast

    offenders = []
    for path in sorted(SRC.glob("test_*.py")):
        if path.name == Path(__file__).name:
            continue                       # this file asserts the refusal
        text = path.read_text(encoding="utf-8")
        if runner not in text:
            continue
        for node in ast.walk(ast.parse(text)):
            if not isinstance(node, ast.Call):
                continue
            # subprocess.run(...) / subprocess.check_output(...)
            fn = node.func
            name = (fn.attr if isinstance(fn, ast.Attribute)
                    else getattr(fn, "id", ""))
            if name not in ("run", "check_output", "Popen", "call"):
                continue
            literals = [n.value for n in ast.walk(node)
                        if isinstance(n, ast.Constant)
                        and isinstance(n.value, str)]
            if not any(runner in s for s in literals):
                continue
            if not any("--dry-run" in s for s in literals):
                offenders.append(f"{path.name}:{node.lineno}")

    assert not offenders, (
        f"test(s) invoke {runner} without --dry-run: {offenders}. A test that "
        "can reach a metered submission is one careless edit away from "
        "spending the allocation; use --dry-run or a source-level check.")
