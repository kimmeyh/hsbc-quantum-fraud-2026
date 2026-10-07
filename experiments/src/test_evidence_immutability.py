"""The session-level evidence guard (IMP-3) stays wired.

`conftest.py` hashes every tracked results file at session start and end and
fails the run if any changed. Its behavior was proven red on 2026-10-06 with a
probe test that appended to gate_report.md without restoring it (exit 1, the
file named) and a probe that restored in a `finally` (exit 0). A behavioral
probe cannot live in the suite permanently -- it would have to change the
evidence it protects -- so these guards pin the wiring instead: if the
conftest disappears, stops covering a directory, or stops failing the
session, they go red.
"""
from __future__ import annotations

import ast
from pathlib import Path

CONFTEST = Path(__file__).resolve().parent / "conftest.py"


def test_the_conftest_exists_beside_the_tests():
    """pytest only applies a conftest in or above the test directory."""
    assert CONFTEST.exists(), (
        "experiments/src/conftest.py is gone; the suite no longer checks "
        "whether it changed committed evidence")


def test_it_covers_both_phases_evidence():
    src = CONFTEST.read_text(encoding="utf-8")
    assert '"experiments/results"' in src
    assert '"experiments/phase2/results"' in src, (
        "Phase 2 evidence must be protected too (docs/PHASE_SEPARATION.md)")


def test_it_implements_the_three_session_hooks():
    tree = ast.parse(CONFTEST.read_text(encoding="utf-8"))
    names = {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}
    for hook in ("pytest_sessionstart", "pytest_sessionfinish",
                 "pytest_terminal_summary"):
        assert hook in names, f"conftest no longer defines {hook}"


def test_a_change_fails_the_session():
    """The line that turns a detected change into a failing exit code."""
    src = CONFTEST.read_text(encoding="utf-8")
    assert "session.exitstatus = pytest.ExitCode.TESTS_FAILED" in src, (
        "the conftest reports changes but no longer fails the run, which is "
        "a check that cannot fail")


def test_the_guard_actually_ran_this_session():
    """A bypass must not be silent (security review, 2026-10-06).

    `pytest --noconftest` skips the conftest entirely: no hashing, no check,
    and nothing in the output says so. pytest_sessionstart sets GUARD_ACTIVE;
    if this suite runs without it, this test fails.
    """
    import conftest
    assert conftest.GUARD_ACTIVE, (
        "the evidence guard did not run this session (was --noconftest "
        "passed?). Committed evidence was not protected.")


def test_new_files_in_evidence_dirs_are_covered():
    """Untracked, non-ignored files are part of the snapshot, so a test that
    CREATES a file in an evidence directory is caught, and the Phase 2
    directory -- with no tracked files yet -- is protected by more than a
    name."""
    src = CONFTEST.read_text(encoding="utf-8")
    assert '"--others", "--exclude-standard"' in src


def test_an_unchecked_run_says_so_rather_than_passing_silently():
    src = CONFTEST.read_text(encoding="utf-8")
    assert "EVIDENCE NOT CHECKED" in src, (
        "if git cannot list the files, the run must say the check did not "
        "happen; 'could not check' must never read as 'clean'")
