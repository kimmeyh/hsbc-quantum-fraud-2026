"""The test suite may not change committed evidence (IMP-3, Sprint 22).

Every tracked file under `experiments/results/` and `experiments/phase2/results/`
is hashed when the pytest session starts and again when it ends. If any
changed, the session fails and names the file.

WHY A SESSION CHECK, NOT ANOTHER TEST. For several sprints
`test_score_gates.py::test_report_generates_over_the_live_store` ran
`score_gates.main()`, which writes the REAL `gate_report.md`, and never
restored it. It was invisible while `results.json` did not change between
commits, because the rewrite produced identical bytes. On 2026-10-06 B4 and B5
added 22 rows, and that test silently rewrote the evidence mid-suite: four
`test_gate_report_totals` tests failed on one run and passed on the next,
because a different test had changed the thing they check.

That test now restores its file, but a per-test fix protects one test. This
protects the evidence from all of them, including tests not yet written. It
extends `test_evidence_artifacts_current.py`, which already checks that the
report matches a regeneration; this checks that nothing in the suite left the
evidence different from how it found it.

A test that regenerates and RESTORES leaves the bytes unchanged and passes.
Only tracked files are hashed, so heartbeats, smoke outputs and other
untracked scratch files are not evidence and are not checked.

If git cannot list the files, the check says so loudly in the terminal
summary rather than passing silently: "could not check" reading as "clean"
is this repository's most-repeated defect.
"""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIRS = ("experiments/results", "experiments/phase2/results")

_BEFORE: dict[str, str] | None = None
_UNCHECKED_REASON: str | None = None
_CHANGED: list[str] = []


def _tracked_evidence() -> list[str] | None:
    try:
        out = subprocess.run(["git", "ls-files", "--", *EVIDENCE_DIRS],
                             capture_output=True, text=True, cwd=str(ROOT),
                             timeout=30)
    except Exception:                                   # noqa: BLE001
        return None
    if out.returncode != 0:
        return None
    return [ln for ln in out.stdout.splitlines() if ln.strip()]


def _hashes(paths: list[str]) -> dict[str, str]:
    result = {}
    for rel in paths:
        p = ROOT / rel
        result[rel] = (hashlib.sha256(p.read_bytes()).hexdigest()
                       if p.exists() else "<missing>")
    return result


def pytest_sessionstart(session):
    global _BEFORE, _UNCHECKED_REASON
    paths = _tracked_evidence()
    if paths is None:
        _UNCHECKED_REASON = ("git could not list the tracked evidence files, "
                             "so the suite was NOT checked for changes to "
                             "committed evidence")
        return
    _BEFORE = _hashes(paths)


def pytest_sessionfinish(session, exitstatus):
    if _BEFORE is None:
        return
    after = _hashes(list(_BEFORE))
    _CHANGED[:] = [rel for rel, h in _BEFORE.items() if after[rel] != h]
    if _CHANGED and session.exitstatus == pytest.ExitCode.OK:
        session.exitstatus = pytest.ExitCode.TESTS_FAILED


def pytest_terminal_summary(terminalreporter):
    if _UNCHECKED_REASON:
        terminalreporter.write_sep("!", "EVIDENCE NOT CHECKED")
        terminalreporter.write_line(_UNCHECKED_REASON)
    if _CHANGED:
        terminalreporter.write_sep(
            "!", "THE SUITE CHANGED COMMITTED EVIDENCE (IMP-3)")
        for rel in _CHANGED:
            terminalreporter.write_line(f"  changed: {rel}")
        terminalreporter.write_line(
            "A test wrote a tracked results file and did not restore it. "
            "Restore with `git checkout -- <file>` and fix the test to restore "
            "in a `finally`.")
