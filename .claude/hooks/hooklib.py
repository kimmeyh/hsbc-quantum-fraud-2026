"""Shared cross-OS helper for this repository's hooks. F78, Sprint 16.

WHY ONE MODULE RATHER THAN THIRTEEN PLATFORM BRANCHES. The F78 card names the
outcome to avoid: `if platform.system()` scattered across every hook. Thirteen
copies of a decision drift, and the drift is invisible because each copy looks
correct on the machine its author was using. One module is one place to fix and
one place to test.

WHAT IS ACTUALLY OS-SPECIFIC, measured rather than assumed. Grepping the five
remaining hooks for OS calls returns exactly four needs:

    payload reading   stdin JSON, identical everywhere
    repo root         CLAUDE_PROJECT_DIR, else walk up for .git
    path joining      pathlib, identical everywhere
    git invocation    subprocess, identical everywhere

Almost nothing. The portability problem was never the logic; it was that the
files were written in a language Linux does not run. CI is ubuntu-latest, so
every .ps1 guard in this repository has been Windows-only protection.

The one genuine difference is path SEPARATORS, and pathlib already handles it.
This module exists so that stays true in one place.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ALLOW = 0
BLOCK = 2


def read_payload() -> dict:
    """Parse the hook payload from stdin, failing OPEN on anything malformed.

    Every hook in this repository fails open, and that is deliberate: a hook
    that raises on an unexpected payload shape blocks EVERY subsequent tool
    call until someone notices. Missing one violation is recoverable; a wedged
    session is not.
    """
    try:
        raw = sys.stdin.read()
    except Exception:                                    # noqa: BLE001
        return {}
    if not raw or not raw.strip():
        return {}
    try:
        payload = json.loads(raw)
    except Exception:                                    # noqa: BLE001
        return {}
    return payload if isinstance(payload, dict) else {}


def command_of(payload: dict) -> str:
    """The shell command a Bash/PowerShell tool call is about to run."""
    ti = payload.get("tool_input")
    if isinstance(ti, dict) and ti.get("command"):
        return str(ti["command"])
    if payload.get("command"):
        return str(payload["command"])
    return ""


def file_path_of(payload: dict) -> str:
    """The target of an Edit/Write/NotebookEdit tool call."""
    ti = payload.get("tool_input")
    if isinstance(ti, dict):
        for key in ("file_path", "notebook_path", "path"):
            if ti.get(key):
                return str(ti[key])
    return ""


def tool_name(payload: dict) -> str:
    return str(payload.get("tool_name") or "")


def repo_root() -> Path:
    """The repository root, on any OS.

    CLAUDE_PROJECT_DIR is set by the harness and is authoritative when present.
    Otherwise walk up from this file looking for .git, which works from a hook
    invoked with any working directory.

    Deliberately does NOT shell out to `git rev-parse`: hooks run on every tool
    call and a subprocess per call is a real cost, and a hook that depends on
    git being on PATH fails in exactly the environments where it matters most.
    """
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        p = Path(env)
        if p.exists():
            return p.resolve()

    here = Path(__file__).resolve()
    for candidate in [here.parent, *here.parents]:
        if (candidate / ".git").exists():
            return candidate
    return here.parent.parent.parent


def repo_file(*parts: str) -> Path:
    """A path inside the repository, joined the way the current OS spells it."""
    return repo_root().joinpath(*parts)


def git(*args: str, cwd: Path | None = None, timeout: int = 15) -> tuple[int, str]:
    """Run git and return (returncode, stdout).

    Never raises. A hook that crashes because git is missing or slow is worse
    than a hook that declines to check.
    """
    try:
        r = subprocess.run(["git", *args], cwd=str(cwd or repo_root()),
                           capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout
    except Exception:                                    # noqa: BLE001
        return 1, ""


def block(message: str) -> int:
    """Emit a block message on stderr and return the blocking exit code."""
    sys.stderr.write(message.rstrip() + "\n")
    return BLOCK


def normalize(path_text: str) -> str:
    """Compare paths without caring about separator style.

    Windows hands back backslashes and POSIX forward slashes, and a hook that
    matches on the wrong one silently never fires. That is not hypothetical:
    a Sprint 14 test left Windows separators after substitution, so a path
    check was always False on POSIX and CI went red on four commits.
    """
    return path_text.replace("\\", "/")
