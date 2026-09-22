"""Guard tests for .claude/hooks/block_heredoc_escape_loss.py (F82, Sprint 17).

The BLOCK cases are the real Sprint 17 Task C failures and the three write
forms the PR #122 review found unguarded.

A NOTE ON WRITING THESE TESTS. The first attempt was itself an instance of the
bug: the harness was built with an unquoted heredoc, so the shell ate the
backslash in the test INPUT and the hook was handed a string containing no
escape at all. The test reported the hook as broken when the hook was correct.
Every input below is built with chr(92) for that reason.

WHAT BASH ACTUALLY EATS, measured on Linux bash for the PR #122 review rather
than assumed:

    written   [n]a\\nb [t]a\\tb [r]a\\rb [b]a\\bb [$x]a\\$xb [\\]a\\\\b
    landed    [n]a\\nb [t]a\\tb [r]a\\rb [b]a\\bb []a$xb     [\\]a\\b

Only `\\$` and `\\\\` change. A lone `\\n` passes through UNTOUCHED, so the
first version of this guard blocked eight sequences bash never consumes --
false-positive surface on a hook whose own docstring says a guard that blocks
correct work gets bypassed.
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

# THE REAL SPRINT 17 SHAPE: a doubled backslash inside an f-string. Bash eats
# one level, so the intended \n escape lands as a literal newline and the
# string breaks. This is what the hook is for.
BAD_BODY = 'new = "    print(f' + BS + '"' + BS + BS + 'nFAILED' + BS + '")"'


def run_hook(command: str) -> int:
    payload = json.dumps({"tool_name": "Bash",
                          "tool_input": {"command": command}})
    r = subprocess.run([sys.executable, str(HOOK)], input=payload,
                       capture_output=True, text=True, cwd=str(ROOT))
    return r.returncode


def test_hook_exists():
    assert HOOK.exists(), f"hook missing: {HOOK}"


# ------------------------------------------------------------- must BLOCK

def test_blocks_real_sprint_17_failure_one():
    """The f-string that produced an unterminated f-string in render_all.py."""
    assert run_hook("cat > x.py <<PYEOF\n" + BAD_BODY + "\nPYEOF") == BLOCK


def test_blocks_real_sprint_17_failure_two():
    """The retry, written to avoid the first, which failed the same way."""
    body = 'block = ("    print(f' + BS + '"' + BS + BS + 'nMISSING' + BS + '")")'
    assert run_hook("cat > fix.py <<PYEOF\n" + body + "\nPYEOF") == BLOCK


def test_blocks_a_redirect_placed_after_the_heredoc_opener():
    """`cat <<EOF > f.py` is at least as idiomatic as `cat > f.py <<EOF`.

    The original opener pattern anchored the delimiter to end-of-line, so a
    trailing redirect made the heredoc unrecognisable and the command was
    allowed outright. Found by the PR #122 review.
    """
    assert run_hook("cat <<EOF > f.py\n" + BAD_BODY + "\nEOF") == BLOCK


def test_blocks_a_script_generating_a_file_through_a_redirect():
    assert run_hook("python - <<EOF > out.txt\n" + BAD_BODY + "\nEOF") == BLOCK


def test_blocks_tee_which_writes_without_any_redirect():
    """`tee f.py <<EOF` writes a file and carries no `>` at all.

    The original WRITES_A_FILE required a `>` after cat/tee/dd, so the tee and
    dd branches were unreachable for their idiomatic form -- dead code of the
    same class this file's hook had already removed once.
    """
    assert run_hook("tee f.py <<EOF\n" + BAD_BODY + "\nEOF") == BLOCK


def test_blocks_an_appending_redirect():
    assert run_hook("cat >> f.py <<EOF\n" + BAD_BODY + "\nEOF") == BLOCK


# -------------------------------------------------------------- must ALLOW

def test_allows_the_quoted_form_of_the_same_body():
    """Quoting the delimiter is the fix. The identical body must pass."""
    assert run_hook("cat > x.py <<'PYEOF'\n" + BAD_BODY + "\nPYEOF") == ALLOW


def test_allows_a_lone_backslash_n_because_bash_does_not_eat_it():
    """Measured, not assumed. Blocking this is a false positive, and every
    false positive trains the author toward the bypass token."""
    body = 'print("a' + BS + 'nb")'
    assert run_hook("cat > f.py <<EOF\n" + body + "\nEOF") == ALLOW


def test_allows_cat_when_no_file_is_written():
    """Guards against an over-broad WRITES_A_FILE.

    A mutation replacing the whole pattern with r"cat" survived the original
    test set, because the only ALLOW case exercising it used grep. That
    mutation would fire on `concatenate`, `allocate` and `truncate`. Found by
    the PR #122 review.
    """
    assert run_hook("cat notes.md | grep foo") == ALLOW


def test_allows_prose_about_backslashes():
    cmd = ("cat > notes.md <<'EOF'\n"
           "Use a backslash before n to write a newline.\n"
           "EOF")
    assert run_hook(cmd) == ALLOW


def test_allows_unquoted_heredoc_with_no_escapes():
    assert run_hook("cat > f.txt <<EOF\nplain text, nothing to eat\nEOF") == ALLOW


def test_allows_heredoc_not_writing_a_file():
    """A heredoc feeding a pager is throwaway; only a file persists damage."""
    assert run_hook("grep foo <<EOF\n" + BAD_BODY + "\nEOF") == ALLOW


def test_bypass_token_allows():
    """The bypass must change the outcome on a command that WOULD be blocked.

    The first version used a body the hook allows anyway, so it passed whether
    or not the bypass was honored. The body below is byte-for-byte the one in
    the BLOCK cases, so the token is the only variable. The token goes on its
    OWN line: as a trailing comment it defeats the opener pattern, which is a
    second way this test managed to pass without the bypass doing anything.
    """
    blocked = "cat > x.py <<PYEOF\n" + BAD_BODY + "\nPYEOF"
    allowed = "# allow_heredoc_escape\n" + blocked

    assert run_hook(blocked) == BLOCK, "precondition: this body must block"
    assert run_hook(allowed) == ALLOW, "the bypass token must allow it"


# ---------------------------------------------------------------- fail open

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


def test_the_hook_module_has_no_unescaped_literal_in_its_message():
    """The message function builds its escape examples with chr(92).

    Writing `\\x` in a non-raw string is a truncated-escape SyntaxError, and
    writing `\\n` in a message ABOUT newlines silently becomes one. Both
    happened while editing that function -- the class this hook exists to
    catch, inside the hook. A syntax error here would make the hook fail open
    on every call, which reads exactly like a passing guard.
    """
    src = HOOK.read_text(encoding="utf-8")
    assert "bs = chr(92)" in src
    # And it must actually import and run.
    assert run_hook("cat > f.txt <<EOF\nplain\nEOF") == ALLOW
