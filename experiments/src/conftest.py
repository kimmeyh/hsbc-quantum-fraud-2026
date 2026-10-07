"""The test suite may not change committed evidence (IMP-3, Sprint 22).

Every file under `experiments/results/` and `experiments/phase2/results/`
that git tracks, PLUS every untracked file there that is not ignored, is
hashed when the pytest session starts and again when it ends. If any file
changed, appeared or disappeared, the session fails and names it.

WHY A SESSION CHECK, NOT ANOTHER TEST. For several sprints
`test_score_gates.py::test_report_generates_over_the_live_store` ran
`score_gates.main()`, which writes the REAL `gate_report.md`, and never
restored it. It was invisible while `results.json` did not change between
commits, because the rewrite produced identical bytes. On 2026-10-06 B4 and B5
added 22 rows, and that test silently rewrote the evidence mid-suite: four
`test_gate_report_totals` tests failed on one run and passed on the next.

That test now restores its file, but a per-test fix protects one test. This
protects the evidence from all of them, including tests not yet written. A
test that regenerates and RESTORES leaves the bytes unchanged and passes.

HARDENED AFTER A SECURITY REVIEW (2026-10-06). The first version:
  - passed the run when git could not list the files, printing a warning --
    now the run FAILS: an integrity check that cannot run is not a pass;
  - hashed only tracked files, so `experiments/phase2/results/` (no tracked
    files yet) was protected by nothing, and a test that CREATED a file in
    either directory went unseen -- now untracked, non-ignored files are in
    the snapshot, and a new or deleted file is a change;
  - failed the run only when it would otherwise have been OK, so other
    non-failure exit codes (e.g. no tests collected) could carry a detected
    change through -- now any non-failing status becomes a failure;
  - could be switched off with `--noconftest` without a trace -- now
    `test_evidence_immutability.py` asserts this conftest actually ran.
"""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIRS = ("experiments/results", "experiments/phase2/results")

# Set by pytest_sessionstart; the liveness test reads it. If it is False when
# the suite runs, the guard was bypassed (for example with --noconftest).
GUARD_ACTIVE = False

_BEFORE: dict[str, str] | None = None
_UNCHECKED_REASON: str | None = None
_CHANGED: list[str] = []


def _evidence_files() -> list[str] | None:
    """Tracked files plus untracked, non-ignored files in the evidence dirs."""
    files: set[str] = set()
    for extra in ((), ("--others", "--exclude-standard")):
        try:
            out = subprocess.run(["git", "ls-files", *extra, "--",
                                  *EVIDENCE_DIRS],
                                 capture_output=True, text=True,
                                 cwd=str(ROOT), timeout=30)
        except Exception:                               # noqa: BLE001
            return None
        if out.returncode != 0:
            return None
        files.update(ln for ln in out.stdout.splitlines() if ln.strip())
    return sorted(files)


def _hashes(paths) -> dict[str, str]:
    result = {}
    for rel in paths:
        p = ROOT / rel
        result[rel] = (hashlib.sha256(p.read_bytes()).hexdigest()
                       if p.is_file() else "<missing>")
    return result


def pytest_sessionstart(session):
    global _BEFORE, _UNCHECKED_REASON, GUARD_ACTIVE
    GUARD_ACTIVE = True
    paths = _evidence_files()
    if paths is None:
        _UNCHECKED_REASON = ("git could not list the evidence files, so the "
                             "suite could NOT be checked for changes to "
                             "committed evidence. That is not a pass.")
        return
    _BEFORE = _hashes(paths)


def pytest_sessionfinish(session, exitstatus):
    failing = (pytest.ExitCode.TESTS_FAILED, pytest.ExitCode.INTERRUPTED,
               pytest.ExitCode.INTERNAL_ERROR, pytest.ExitCode.USAGE_ERROR)
    if _UNCHECKED_REASON:
        if session.exitstatus not in failing:
            session.exitstatus = pytest.ExitCode.TESTS_FAILED
        return
    if _BEFORE is None:
        return
    after_paths = _evidence_files()
    if after_paths is None:
        _CHANGED[:] = ["<git could not list the evidence files at session end>"]
    else:
        after = _hashes(sorted(set(_BEFORE) | set(after_paths)))
        _CHANGED[:] = [rel for rel in sorted(after)
                       if _BEFORE.get(rel, "<absent>") != after[rel]]
    if _CHANGED and session.exitstatus not in failing:
        session.exitstatus = pytest.ExitCode.TESTS_FAILED


def pytest_terminal_summary(terminalreporter):
    if _UNCHECKED_REASON:
        terminalreporter.write_sep("!", "EVIDENCE NOT CHECKED -- RUN FAILED")
        terminalreporter.write_line(_UNCHECKED_REASON)
    if _CHANGED:
        terminalreporter.write_sep(
            "!", "THE SUITE CHANGED COMMITTED EVIDENCE (IMP-3)")
        for rel in _CHANGED:
            terminalreporter.write_line(f"  changed: {rel}")
        terminalreporter.write_line(
            "A test wrote, created or deleted a file in an evidence directory "
            "and did not restore it. Restore it (`git checkout -- <file>`, or "
            "delete a created file) and fix the test to clean up in a "
            "`finally`.")
