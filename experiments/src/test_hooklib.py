"""The shared cross-OS hook helper behaves the same on Windows and Linux.

F78, Sprint 16. `hooklib` exists so that thirteen hooks do not each carry their
own platform branch, which is the outcome the card names as the thing to avoid
because it drifts invisibly.

These tests run on whatever OS the suite runs on, which is the point: CI is
ubuntu-latest and the hooks have never executed there.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
HOOKLIB = ROOT / ".claude" / "hooks" / "hooklib.py"


def _load():
    spec = importlib.util.spec_from_file_location("hooklib", HOOKLIB)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def hooklib():
    assert HOOKLIB.exists(), f"{HOOKLIB} is missing; every converted hook imports it"
    return _load()


def test_repo_root_finds_this_repository(hooklib):
    assert (hooklib.repo_root() / ".git").exists()


def test_repo_root_works_without_the_env_var(hooklib, monkeypatch):
    """The env var is authoritative when set, but must not be REQUIRED.

    A hook that only works when CLAUDE_PROJECT_DIR is present fails in exactly
    the environments where nobody is watching.
    """
    monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
    mod = _load()
    assert (mod.repo_root() / ".git").exists()


def test_repo_file_joins_for_this_os(hooklib):
    assert hooklib.repo_file("docs", "sprints").is_dir()


@pytest.mark.parametrize("raw,expected", [
    ("\\a\\b", "/a/b"),
    ("a\\b/c", "a/b/c"),
    ("D:\\Data\\x", "D:/Data/x"),
    ("already/posix", "already/posix"),
    ("", ""),
])
def test_normalize_is_separator_agnostic(hooklib, raw, expected):
    """A path check that matches the wrong separator silently never fires.

    Not hypothetical: a Sprint 14 test left Windows separators after
    substitution, so a check was always False on POSIX and CI went red on four
    consecutive commits.
    """
    assert hooklib.normalize(raw) == expected


@pytest.mark.parametrize("payload,expected", [
    ({"tool_input": {"command": "git status"}}, "git status"),
    ({"command": "top level"}, "top level"),
    ({"tool_input": {}}, ""),
    ({}, ""),
])
def test_command_of(hooklib, payload, expected):
    assert hooklib.command_of(payload) == expected


@pytest.mark.parametrize("payload,expected", [
    ({"tool_input": {"file_path": "x.md"}}, "x.md"),
    ({"tool_input": {"notebook_path": "n.ipynb"}}, "n.ipynb"),
    ({"tool_input": {}}, ""),
    ({}, ""),
])
def test_file_path_of(hooklib, payload, expected):
    assert hooklib.file_path_of(payload) == expected


@pytest.mark.parametrize("stdin_text", ["", "   ", "not json", "[1,2,3]", "null"])
def test_read_payload_fails_open(stdin_text, tmp_path):
    """Malformed input must yield an empty dict, never an exception.

    A hook that raises on an unexpected payload blocks EVERY subsequent tool
    call until someone notices. Missing one violation is recoverable; a wedged
    session is not. Run in a subprocess because it reads real stdin.
    """
    script = tmp_path / "probe.py"
    script.write_text(
        "import sys\n"
        f"sys.path.insert(0, {str(HOOKLIB.parent)!r})\n"
        "import hooklib\n"
        "p = hooklib.read_payload()\n"
        "assert isinstance(p, dict), type(p)\n"
        "print('ok')\n",
        encoding="utf-8")
    r = subprocess.run([sys.executable, str(script)], input=stdin_text,
                       capture_output=True, text=True)
    assert r.returncode == 0, f"read_payload raised on {stdin_text!r}: {r.stderr[:200]}"


def test_git_never_raises(hooklib):
    rc, out = hooklib.git("rev-parse", "--abbrev-ref", "HEAD")
    assert rc == 0 and out.strip()
    rc2, _ = hooklib.git("definitely-not-a-git-subcommand")
    assert rc2 != 0


def test_block_returns_the_blocking_code(hooklib, capsys):
    rc = hooklib.block("test message")
    assert rc == hooklib.BLOCK == 2
    assert "test message" in capsys.readouterr().err


def test_no_converted_hook_carries_its_own_platform_branch():
    """The card's stated anti-goal, asserted rather than trusted.

    Thirteen scattered `if platform.system()` branches drift, and the drift is
    invisible because each copy looks right on its author's machine.
    """
    offenders = []
    for f in sorted((ROOT / ".claude" / "hooks").glob("*.py")):
        if f.name == "hooklib.py":
            continue
        text = f.read_text(encoding="utf-8")
        for marker in ("platform.system", "sys.platform", "os.name =="):
            if marker in text:
                offenders.append(f"{f.name}: {marker}")
    assert not offenders, (
        "converted hooks must get OS differences from hooklib, not their own "
        f"branches: {offenders}")
