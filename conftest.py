"""The test suite may not change committed evidence (IMP-3, Sprint 22).

Every file under `experiments/results/` and `experiments/phase2/results/`
that git tracks, PLUS every untracked file there that the root `.gitignore`
does not ignore, is hashed when the pytest session starts and again when it
ends. If any file changed, appeared, disappeared or changed the case of its
name, the session fails and names it.

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

WHY AT THE REPOSITORY ROOT. pytest calls `pytest_sessionstart` only for an
"initial" conftest: one in or above a path on the command line. In
`experiments/src/` the guard was not initial for `pytest experiments -k x`
or `pytest . -k x`; it loaded during collection, took no snapshot, and
returned silently (second security review, 2026-10-07, finding 1). Beside
`pytest.ini` it is initial for every invocation inside the repository, and a
session that ends with no snapshot now FAILS.

HARDENED AFTER TWO SECURITY REVIEWS (2026-10-06 and 2026-10-07):
  - git unable to list the files, or a listing without `results.json`
    (a wrong repository, index or root): the run FAILS. An integrity check
    that cannot run, or ran against the wrong tree, is not a pass. Inherited
    `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE` and `GIT_OBJECT_DIRECTORY`
    are removed before git runs;
  - untracked, non-ignored files are in the snapshot, judged by the ROOT
    `.gitignore` only, so a test cannot hide a new file by writing a nested
    `.gitignore`, and the scope does not vary with a machine's own excludes;
  - file names are read with `-z` as UTF-8, so names git would quote are
    hashed, not recorded as missing;
  - a symlink is hashed as its target path, not its target's bytes;
  - a case-only rename is a change, even on a case-insensitive disk;
  - any non-failing exit status becomes a failure when a change is found;
  - the failure is also written to stderr from `pytest_sessionfinish`, so it
    shows under `--no-summary`;
  - evidence that was ALREADY modified when the run started is named in a
    warning: the snapshot is the disk, not the commit, so a run killed before
    a test restored its file would otherwise make the next run's baseline.

KNOWN LIMITS, covered by CI rather than here. CI's "Test run must leave the
tree clean" step (`.github/workflows/ci.yml`) runs `git status --porcelain`
after pytest exits, which no pytest flag can skip. It covers what a session
hook cannot: `--noconftest` (locally, `test_the_guard_ran_this_session`
fails only when it is selected), writes that land after the session ends
(a detached process, a thread, an `atexit` handler), and a run killed
mid-test. Ignored files (pools, predictions, smoke and dry-run outputs) are
out of scope by design.
"""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
EVIDENCE_DIRS = ("experiments/results", "experiments/phase2/results")
ANCHOR = "experiments/results/results.json"
_GIT_ENV_DROP = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE",
                 "GIT_OBJECT_DIRECTORY")
FAILING = (pytest.ExitCode.TESTS_FAILED, pytest.ExitCode.INTERRUPTED,
           pytest.ExitCode.INTERNAL_ERROR, pytest.ExitCode.USAGE_ERROR)

# Set by pytest_sessionstart; the liveness test reads it. If it is False when
# the suite runs, the guard was bypassed (for example with --noconftest).
GUARD_ACTIVE = False

_BEFORE: dict[str, str] | None = None
_UNCHECKED_REASON: str | None = None
_CHANGED: list[str] = []
_DIRTY_AT_START: list[str] = []


def _git(*args: str) -> str | None:
    """stdout of a git command in ROOT, or None if git could not run."""
    env = {k: v for k, v in os.environ.items() if k not in _GIT_ENV_DROP}
    try:
        out = subprocess.run(["git", "-C", str(ROOT), *args],
                             capture_output=True, env=env, timeout=30)
    except Exception:                                   # noqa: BLE001
        return None
    if out.returncode != 0:
        return None
    return out.stdout.decode("utf-8", errors="surrogateescape")


def _evidence_files() -> list[str] | None:
    """Tracked files plus untracked files the root .gitignore does not
    ignore, in the evidence dirs. NUL-separated, so no name is quoted."""
    files: set[str] = set()
    for extra in ((), ("--others", "--exclude-from=.gitignore")):
        out = _git("ls-files", "-z", *extra, "--", *EVIDENCE_DIRS)
        if out is None:
            return None
        files.update(n for n in out.split("\0") if n)
    return sorted(files)


def _dirty_at_start() -> list[str]:
    """Evidence paths already modified, added or deleted at session start.
    With -z, a rename or copy entry is followed by its ORIGINAL path as a
    separate field, which is skipped."""
    out = _git("status", "--porcelain", "-z", "--untracked-files=all", "--",
               *EVIDENCE_DIRS)
    fields = iter((out or "").split("\0"))
    dirty = []
    for entry in fields:
        if len(entry) < 4:
            continue
        dirty.append(entry[3:])
        if entry[0] in "RC":
            next(fields, None)
    return sorted(dirty)


def _case_mismatch(p: Path, listings: dict[Path, set[str]]) -> bool:
    """True if `p` exists but its directory holds it under a name that
    differs only in case (a case-insensitive disk opens it anyway)."""
    parent = p.parent
    if parent not in listings:
        try:
            listings[parent] = set(os.listdir(parent))
        except OSError:
            listings[parent] = set()
    return p.name not in listings[parent]


def _hashes(paths) -> dict[str, str]:
    result: dict[str, str] = {}
    listings: dict[Path, set[str]] = {}
    for rel in paths:
        p = ROOT / rel
        if p.is_symlink():
            result[rel] = "link:" + os.readlink(p)
        elif not p.is_file():
            result[rel] = "<missing>"
        elif _case_mismatch(p, listings):
            result[rel] = "<name case changed>"
        else:
            result[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
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
    if ANCHOR not in paths:
        _UNCHECKED_REASON = (f"git listed {len(paths)} evidence files without "
                             f"{ANCHOR}, so it was looking at the wrong tree "
                             "or index. The suite was NOT checked. That is "
                             "not a pass.")
        return
    _DIRTY_AT_START[:] = _dirty_at_start()
    _BEFORE = _hashes(paths)


def _fail(session) -> None:
    if session.exitstatus not in FAILING:
        session.exitstatus = pytest.ExitCode.TESTS_FAILED


def pytest_sessionfinish(session, exitstatus):
    global _UNCHECKED_REASON
    if _BEFORE is None and not _UNCHECKED_REASON:
        _UNCHECKED_REASON = ("the evidence guard took no snapshot: "
                             "pytest_sessionstart never ran for it. The suite "
                             "was NOT checked. That is not a pass.")
    if _UNCHECKED_REASON:
        _fail(session)
        sys.stderr.write(f"\nEVIDENCE NOT CHECKED -- RUN FAILED: "
                         f"{_UNCHECKED_REASON}\n")
        return
    after_paths = _evidence_files()
    if after_paths is None:
        _CHANGED[:] = ["<git could not list the evidence files at session end>"]
    else:
        after = _hashes(sorted(set(_BEFORE) | set(after_paths)))
        _CHANGED[:] = [rel for rel in sorted(after)
                       if _BEFORE.get(rel, "<absent>") != after[rel]]
    if _CHANGED:
        _fail(session)
        sys.stderr.write("\nTHE SUITE CHANGED COMMITTED EVIDENCE (IMP-3): "
                         + ", ".join(_CHANGED[:10]) + "\n")


def pytest_terminal_summary(terminalreporter):
    if _DIRTY_AT_START:
        terminalreporter.write_sep(
            "!", "EVIDENCE WAS ALREADY MODIFIED WHEN THIS RUN STARTED")
        for rel in _DIRTY_AT_START[:20]:
            terminalreporter.write_line(f"  modified before the run: {rel}")
        terminalreporter.write_line(
            "This run compared against those modified files, not the commit. "
            "If no metered run or deliberate edit explains them, a killed "
            "test may have left them: `git diff -- experiments/results`.")
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
