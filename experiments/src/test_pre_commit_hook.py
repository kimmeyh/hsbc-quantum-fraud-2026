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


CHANGELOG_MSG = "changes code but not CHANGELOG.md"


def test_code_without_changelog_is_blocked(repo):
    r = _commit(repo, {"scripts/tool.py": "x = 1\n"})
    assert r.returncode != 0
    assert CHANGELOG_MSG in (r.stdout + r.stderr)


# Each path matches exactly ONE alternative of the hook's pattern, so dropping
# any alternative turns its case red (PR #159 review: every case used to end
# in .py, so the other alternatives were untested). The message is asserted,
# so a hook that fails for another reason does not pass.
@pytest.mark.parametrize("path", ["experiments/src/mod.py",
                                  "conftest.py",
                                  "scripts/run.sh",
                                  ".claude/hooks/h.sh",
                                  ".githooks/post-merge"])
def test_every_code_area_is_covered(repo, path):
    r = _commit(repo, {path: "x = 1\n"})
    assert r.returncode != 0
    assert CHANGELOG_MSG in (r.stdout + r.stderr), (
        "blocked, but not by the CHANGELOG check")


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


# ---- confidentiality: the whole staged diff is scanned ---------------------

SECRET = "ZZQSECRETWORDZZQ"
# Enough lines that one added line keeps git's rename similarity above 50%.
BODY = "".join(f"plain line {i}\n" for i in range(20))


@pytest.fixture
def secret_repo(repo):
    """The pattern file is local and untracked, as in a real clone."""
    (repo / ".secrets-patterns.txt").write_text(SECRET + "\n",
                                                encoding="utf-8")
    assert _commit(repo, {"notes.md": BODY}).returncode == 0
    return repo


def _blocked_for_secret(r) -> bool:
    return (r.returncode != 0
            and "confidential patterns" in (r.stdout + r.stderr))


def test_a_new_file_with_a_secret_is_blocked(secret_repo):
    assert _blocked_for_secret(_commit(secret_repo, {"new.md": SECRET + "\n"}))


def test_a_renamed_and_edited_file_with_a_secret_is_blocked(secret_repo):
    """A file list built with --diff-filter=ACM omitted renames (PR #159
    review, reproduced: R075 notes.md -> moved.md committed a secret)."""
    _git(secret_repo, "mv", "notes.md", "moved.md")
    (secret_repo / "moved.md").write_text(BODY + SECRET + "\n",
                                          encoding="utf-8")
    _git(secret_repo, "add", "moved.md")
    status = _git(secret_repo, "diff", "--cached", "--name-status").stdout
    assert status.startswith("R"), f"not staged as a rename: {status!r}"
    assert _blocked_for_secret(_git(secret_repo, "commit", "-q", "-m", "x"))


def test_a_file_name_with_a_space_is_scanned(secret_repo):
    """xargs split the name, and 2>/dev/null hid the miss (PR #159 review)."""
    assert _blocked_for_secret(_commit(secret_repo,
                                       {"my notes.md": SECRET + "\n"}))


def test_clean_text_passes_the_secret_scan(secret_repo):
    assert _commit(secret_repo, {"more.md": "nothing here\n"}).returncode == 0
