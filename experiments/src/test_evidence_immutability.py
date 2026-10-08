"""The session-level evidence guard (IMP-3) works, tested by BEHAVIOR.

The guard is the repository-root `conftest.py`. These tests load a private
copy of it, drive its hooks with a stand-in session, and point it at scratch
git repositories, so no test touches real evidence.

WHY BEHAVIOR, NOT SOURCE TEXT (second security review, 2026-10-07, finding
3). The first version asserted that `session.exitstatus =
pytest.ExitCode.TESTS_FAILED` appeared in the source. It appeared twice, once
in a different branch, so deleting the change-detection branch left the test
green: the "substring that appears twice" defect CLAUDE.md names. Every test
below was proven red by breaking the branch it covers.
"""
from __future__ import annotations

import hashlib
import importlib.util
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
CONFTEST = REPO / "conftest.py"
OK = pytest.ExitCode.OK
FAILED = pytest.ExitCode.TESTS_FAILED

needs_git = pytest.mark.skipif(shutil.which("git") is None,
                               reason="git is not installed")


class _Session:
    def __init__(self, status=OK):
        self.exitstatus = status


@pytest.fixture
def guard():
    """A fresh, private copy of the guard module: its globals are its own,
    so the live session's guard is untouched."""
    spec = importlib.util.spec_from_file_location("_guard_copy", CONFTEST)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def scratch(tmp_path, guard):
    """A scratch git repository holding the anchor file, with the guard
    pointed at it."""
    def git(*a):
        subprocess.run(["git", "-C", str(tmp_path), *a], check=True,
                       capture_output=True)
    git("init", "-q")
    git("config", "user.email", "t@example.invalid")
    git("config", "user.name", "t")
    git("config", "commit.gpgsign", "false")
    (tmp_path / ".gitignore").write_text("*.npz\n", encoding="utf-8")
    res = tmp_path / "experiments" / "results"
    res.mkdir(parents=True)
    (res / "results.json").write_text("{}", encoding="utf-8")
    (tmp_path / "experiments" / "phase2" / "results").mkdir(parents=True)
    git("add", "-A")
    git("commit", "-q", "-m", "x")
    guard.ROOT = tmp_path
    return tmp_path


# ---- where it lives -------------------------------------------------------

def test_the_guard_is_at_the_repository_root():
    """Beside pytest.ini it is an initial conftest for every invocation, so
    pytest_sessionstart always runs (finding 1)."""
    assert CONFTEST.exists(), "the root conftest.py (evidence guard) is gone"
    assert (REPO / "pytest.ini").exists()
    assert not (REPO / "experiments" / "src" / "conftest.py").exists(), (
        "a conftest under experiments/src is not initial for "
        "`pytest experiments -k x`; the guard must stay at the root")


def test_it_covers_both_phases_evidence(guard):
    assert set(guard.EVIDENCE_DIRS) == {"experiments/results",
                                        "experiments/phase2/results"}


def test_the_guard_ran_this_session(request):
    """`--noconftest` skips the guard; this test then fails. Locally it
    only catches a bypass when selected; CI's clean-tree step catches the
    rest."""
    live = [p for p in request.config.pluginmanager.get_plugins()
            if getattr(p, "__file__", None)
            and Path(p.__file__).resolve() == CONFTEST]
    assert live, ("the evidence guard is not loaded this session (was "
                  "--noconftest passed?). Committed evidence was not "
                  "protected.")
    assert live[0].GUARD_ACTIVE and live[0]._BEFORE is not None


# ---- what fails the session -----------------------------------------------

def _finish(guard, before, after, status=OK):
    guard._BEFORE = before
    guard._evidence_files = lambda: sorted(after)
    guard._hashes = lambda paths: {p: after.get(p, "<missing>") for p in paths}
    s = _Session(status)
    guard.pytest_sessionfinish(s, status)
    return s


def test_a_changed_file_fails_the_session(guard):
    s = _finish(guard, {"a.json": "1"}, {"a.json": "2"})
    assert s.exitstatus == FAILED
    assert guard._CHANGED == ["a.json"]


def test_an_unchanged_tree_passes(guard):
    s = _finish(guard, {"a.json": "1"}, {"a.json": "1"})
    assert s.exitstatus == OK and guard._CHANGED == []


def test_a_created_file_fails_the_session(guard):
    s = _finish(guard, {"a.json": "1"}, {"a.json": "1", "new.json": "9"})
    assert s.exitstatus == FAILED and guard._CHANGED == ["new.json"]


def test_a_change_overrides_any_non_failing_exit_status(guard):
    s = _finish(guard, {"a.json": "1"}, {"a.json": "2"},
                status=pytest.ExitCode.NO_TESTS_COLLECTED)
    assert s.exitstatus == FAILED


def test_a_change_is_also_written_to_stderr(guard, capsys):
    """Shown even under --no-summary (finding 11)."""
    _finish(guard, {"a.json": "1"}, {"a.json": "2"})
    assert "a.json" in capsys.readouterr().err


def test_no_snapshot_fails_the_session(guard):
    """The finding-1 path: sessionstart never ran for the guard."""
    guard._BEFORE = None
    s = _Session()
    guard.pytest_sessionfinish(s, OK)
    assert s.exitstatus == FAILED
    assert "no snapshot" in guard._UNCHECKED_REASON


def test_git_unavailable_at_start_fails_the_session(guard):
    guard._evidence_files = lambda: None
    s = _Session()
    guard.pytest_sessionstart(s)
    guard.pytest_sessionfinish(s, OK)
    assert s.exitstatus == FAILED


def test_a_listing_without_the_anchor_fails_the_session(guard):
    """A wrong tree or index lists files that are not ours (finding 6)."""
    guard._evidence_files = lambda: ["experiments/results/other.json"]
    s = _Session()
    guard.pytest_sessionstart(s)
    guard.pytest_sessionfinish(s, OK)
    assert s.exitstatus == FAILED
    assert "results.json" in guard._UNCHECKED_REASON


# ---- what it sees, on a real git repository -------------------------------

@needs_git
def test_a_name_git_would_quote_is_listed(scratch, guard):
    """Without -z, git prints this name C-quoted and the guard hashed a path
    that does not exist (finding 5)."""
    (scratch / "experiments" / "results" / "café.json").write_text(
        "x", encoding="utf-8")
    assert "experiments/results/café.json" in guard._evidence_files()


@needs_git
def test_a_nested_gitignore_cannot_hide_a_new_file(scratch, guard):
    """Only the root .gitignore decides what is out of scope (finding 8)."""
    res = scratch / "experiments" / "results"
    (res / ".gitignore").write_text("*\n", encoding="utf-8")
    (res / "new.json").write_text("x", encoding="utf-8")
    assert "experiments/results/new.json" in guard._evidence_files()


@needs_git
def test_root_ignored_files_stay_out_of_scope(scratch, guard):
    (scratch / "experiments" / "results" / "pool.npz").write_bytes(b"x")
    assert "experiments/results/pool.npz" not in guard._evidence_files()


@needs_git
def test_an_inherited_git_dir_does_not_redirect_it(scratch, guard,
                                                   monkeypatch, tmp_path_factory):
    """Launched from a git hook, GIT_DIR points elsewhere (finding 6)."""
    monkeypatch.setenv("GIT_DIR", str(tmp_path_factory.mktemp("elsewhere")))
    assert "experiments/results/results.json" in guard._evidence_files()


@needs_git
def test_evidence_already_modified_at_start_is_named(scratch, guard):
    """The baseline is the disk; a file a killed run left modified is
    reported, not silently adopted (finding 4)."""
    (scratch / "experiments" / "results" / "results.json").write_text(
        "{changed}", encoding="utf-8")
    assert guard._dirty_at_start() == ["experiments/results/results.json"]


def test_a_symlink_is_hashed_as_its_target_path(tmp_path, guard):
    """Replacing a file with a link to identical bytes is a change
    (finding 9)."""
    real = tmp_path / "real.json"
    real.write_text("same", encoding="utf-8")
    link = tmp_path / "link.json"
    try:
        os.symlink(real, link)
    except (OSError, NotImplementedError):
        pytest.skip("this machine cannot create symlinks")
    guard.ROOT = tmp_path
    h = guard._hashes(["link.json"])["link.json"]
    assert h.startswith("link:")
    assert h != hashlib.sha256(b"same").hexdigest()


def test_a_case_only_rename_is_a_change(tmp_path, guard):
    """On a case-insensitive disk the old name still opens the renamed file
    (finding 10). On a case-sensitive one it is simply missing. Either way
    the hash must differ from the content's."""
    (tmp_path / "Gate_Report.md").write_text("x", encoding="utf-8")
    guard.ROOT = tmp_path
    h = guard._hashes(["gate_report.md"])["gate_report.md"]
    assert h in ("<name case changed>", "<missing>")
