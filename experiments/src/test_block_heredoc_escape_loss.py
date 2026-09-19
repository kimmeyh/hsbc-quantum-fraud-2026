"""Guard tests for .claude/hooks/block_heredoc_escape_loss.py (F82, Sprint 17).

The two BLOCK cases are the two real failures from Sprint 17 Task C, five
minutes apart, the second written specifically to avoid the first.

A NOTE ON WRITING THESE TESTS. The first attempt at this test file was itself
an instance of the bug: the harness was built with an unquoted heredoc, so the
shell ate the backslash in the test INPUT and the hook was handed a string
containing a real newline rather than the two characters it was meant to see.
The test reported the hook as broken when the hook was correct. That is the
class exactly -- a plausible wrong result, not an error -- and it is why the
inputs below are built with explicit chr(92) rather than typed as literals
that any layer could consume.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / ".claude" / "hooks" / "block_heredoc_escape_loss.py"

BS = chr(92)  # a single backslash, immune to any layer that eats escapes.
ALLOW, BLOCK = 0, 2


def run_hook(command: str) -> int:
    payload = json.dumps({"tool_name": "Bash",
                          "tool_input": {"command": command}})
    r = subprocess.run([sys.executable, str(HOOK)], input=payload,
                       capture_output=True, text=True, cwd=str(ROOT))
    return r.returncode


def test_hook_exists():
    assert HOOK.exists(), f"hook missing: {HOOK}"


def test_blocks_real_sprint_17_failure_one():
    """An f-string's \\n inside an unquoted heredoc. Produced an unterminated
    f-string in scripts/render_all.py."""
    cmd = ("cat > x.py <<PYEOF\n"
           'new = "    print(f' + BS + '"' + BS + BS + 'nFAILED' + BS + '")"\n'
           "PYEOF")
    assert run_hook(cmd) == BLOCK


def test_blocks_real_sprint_17_failure_two():
    """The retry, written to avoid the first, which failed the same way."""
    cmd = ("cat > fix.py <<PYEOF\n"
           'block = ("    print(f' + BS + '"' + BS + BS + 'nMISSING' + BS + '")")\n'
           "PYEOF")
    assert run_hook(cmd) == BLOCK


def test_allows_the_quoted_form_of_the_same_body():
    """Quoting the delimiter is the fix. The identical body must pass."""
    cmd = ("cat > x.py <<'PYEOF'\n"
           'new = "    print(f' + BS + '"' + BS + BS + 'nFAILED' + BS + '")"\n'
           "PYEOF")
    assert run_hook(cmd) == ALLOW


def test_allows_prose_about_backslashes():
    """A guard that blocks correct work gets bypassed."""
    cmd = ("cat > notes.md <<'EOF'\n"
           "Use a backslash before n to write a newline.\n"
           "EOF")
    assert run_hook(cmd) == ALLOW


def test_allows_unquoted_heredoc_with_no_escapes():
    cmd = "cat > f.txt <<EOF\nplain text, nothing to eat\nEOF"
    assert run_hook(cmd) == ALLOW


def test_allows_heredoc_not_writing_a_file():
    """A heredoc feeding a pager is throwaway; only a file persists damage."""
    cmd = "grep foo <<EOF\na" + BS + "nb\nEOF"
    assert run_hook(cmd) == ALLOW


def test_bypass_token_allows():
    """The bypass must change the outcome on a command that WOULD be blocked.

    The first version of this test used a body the hook allows anyway, so it
    passed whether or not the bypass was honored -- proven vacuous by an
    injection that disabled the bypass and broke no test. The body below is
    byte-for-byte the one in test_blocks_real_sprint_17_failure_one, so the
    only difference between blocked and allowed is the token itself.
    """
    body = ('new = "    print(f' + BS + '"' + BS + BS + 'nFAILED' + BS + '")"\n')
    blocked = "cat > x.py <<PYEOF\n" + body + "PYEOF"
    # The token goes on its OWN line. Put after the opener as a trailing
    # comment it defeats the opener pattern's end-of-line anchor, so the
    # command is allowed because no heredoc was recognized at all -- a second
    # way this test managed to pass without the bypass doing anything.
    allowed = "# allow_heredoc_escape\ncat > x.py <<PYEOF\n" + body + "PYEOF"

    assert run_hook(blocked) == BLOCK, "precondition: this body must block"
    assert run_hook(allowed) == ALLOW, "the bypass token must allow it"


def test_fails_open_on_malformed_payload():
    """Every hook in this repository fails open. A hook that raises on an
    unexpected payload blocks every subsequent tool call."""
    r = subprocess.run([sys.executable, str(HOOK)], input="not json",
                       capture_output=True, text=True, cwd=str(ROOT))
    assert r.returncode == ALLOW


def test_fails_open_on_empty_payload():
    r = subprocess.run([sys.executable, str(HOOK)], input="",
                       capture_output=True, text=True, cwd=str(ROOT))
    assert r.returncode == ALLOW
