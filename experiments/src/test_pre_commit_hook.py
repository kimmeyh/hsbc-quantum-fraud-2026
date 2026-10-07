"""The tracked pre-commit hook blocks what it says it blocks (IMP-3, Sprint 22).

Until Sprint 22 the confidentiality gate lived only in `.git/hooks/pre-commit`,
which git does not track: a fresh clone, or a new repository started from this
one, silently had no gate. It now lives in `.githooks/pre-commit` and also
enforces the CHANGELOG policy ("an entry in the SAME commit as the change"),
which failed twice when it relied on memory (F70; Sprint 22).

Each test runs the REAL hook file in a scratch git repository, so what is
asserted is git's behavior with the hook installed, not a reading of its text.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / ".githooks" / "pre-commit"

pytestmark = pytest.mark.skipif(shutil.which("git") is None,
                                reason="git is not installed")


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True,
                          text=True)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "t@example.invalid")
    _git(tmp_path, "config", "user.name", "t")
    _git(tmp_path, "config", "commit.gpgsign", "false")
    hooks = tmp_path / ".githooks"
    hooks.mkdir()
    # Copy bytes: a CRLF conversion here would break the sh shebang and make
    # every commit pass or fail for the wrong reason.
    (hooks / "pre-commit").write_bytes(HOOK.read_bytes())
    (hooks / "pre-commit").chmod(0o755)
    _git(tmp_path, "config", "core.hooksPath", ".githooks")
    return tmp_path


def _commit(repo: Path, files: dict[str, str]) -> subprocess.CompletedProcess:
    for rel, text in files.items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        _git(repo, "add", "-f", rel)
    return _git(repo, "commit", "-q", "-m", "x")


def test_hook_is_tracked_with_lf_endings():
    assert HOOK.exists(), ".githooks/pre-commit is missing"
    assert b"\r\n" not in HOOK.read_bytes(), "CRLF breaks the sh shebang"
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch",
                              ".githooks/pre-commit"], cwd=ROOT,
                             capture_output=True)
    assert tracked.returncode == 0, "the hook must be tracked by git"


def test_code_without_changelog_is_blocked(repo):
    r = _commit(repo, {"scripts/tool.py": "x = 1\n"})
    assert r.returncode != 0
    assert "CHANGELOG.md" in (r.stdout + r.stderr)


@pytest.mark.parametrize("path", ["experiments/src/mod.py",
                                  "experiments/phase2/src/mod.py",
                                  ".claude/hooks/h.py",
                                  "conftest.py",
                                  "scripts/run.sh"])
def test_every_code_area_is_covered(repo, path):
    assert _commit(repo, {path: "x = 1\n"}).returncode != 0


def test_code_with_changelog_passes(repo):
    r = _commit(repo, {"scripts/tool.py": "x = 1\n",
                       "CHANGELOG.md": "- entry\n"})
    assert r.returncode == 0, r.stdout + r.stderr


def test_docs_only_commit_needs_no_changelog(repo):
    assert _commit(repo, {"docs/note.md": "text\n"}).returncode == 0


def test_staged_env_file_is_blocked(repo):
    r = _commit(repo, {".env": "TOKEN=x\n", "CHANGELOG.md": "- entry\n"})
    assert r.returncode != 0
    assert ".env" in (r.stdout + r.stderr)
