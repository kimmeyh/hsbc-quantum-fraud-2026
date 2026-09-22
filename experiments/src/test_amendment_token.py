"""The amendment approval token is SINGLE-USE (Sprint 17 improvement 5).

`.claude/.amendment-verified` disables block_reactive_amendment while it
exists. A token left behind after the amendment it authorized turns that guard
off for every later edit, silently, because a disabled guard looks exactly like
a passing one.

That happened in Sprint 17: the token written for A33 stayed on disk, and three
hook-parity tests went red because the hook could no longer block anything.
Deleting it was a remembered step. These tests pin the mechanical replacement.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / ".claude" / "hooks" / "block_reactive_amendment.py"
TOKEN = ROOT / ".claude" / ".amendment-verified"
PREREG = "experiments/PREREGISTRATION.md"

ALLOW, BLOCK = 0, 2


def _edit_payload() -> str:
    return json.dumps({"tool_name": "Edit",
                       "tool_input": {"file_path": PREREG}})


def _run() -> int:
    r = subprocess.run([sys.executable, str(HOOK)], input=_edit_payload(),
                       capture_output=True, text=True, cwd=str(ROOT))
    return r.returncode


def test_the_hook_exists():
    assert HOOK.exists()


def test_editing_the_frozen_prereg_blocks_without_a_token():
    assert not TOKEN.exists(), (
        f"{TOKEN} is present; a stale token disables this guard entirely")
    assert _run() == BLOCK


def test_the_token_allows_exactly_one_edit_then_is_consumed():
    """The whole point: approval means ONE verified amendment, not 'amendments
    are allowed from now on'."""
    assert not TOKEN.exists(), "precondition: no token on disk"
    TOKEN.write_text("test token", encoding="utf-8")
    try:
        assert TOKEN.exists(), "precondition: token written"
        assert _run() == ALLOW, "the token must allow the edit it authorizes"
        assert not TOKEN.exists(), (
            "the token was NOT consumed; the guard is still disabled")
        assert _run() == BLOCK, "the next edit must block again"
    finally:
        if TOKEN.exists():
            TOKEN.unlink()


def test_no_token_is_committed_to_the_repository():
    """A token in git would disable the guard on every clone."""
    r = subprocess.run(["git", "ls-files", ".claude/.amendment-verified"],
                       cwd=str(ROOT), capture_output=True, text=True)
    assert not r.stdout.strip(), (
        "the approval token is tracked in git; it must never be committed")
