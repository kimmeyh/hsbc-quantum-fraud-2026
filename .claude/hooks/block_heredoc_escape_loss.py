"""PreToolUse hook: block a heredoc that will lose a backslash escape on its
way into a file. F82, Sprint 17.

THE FAILURE, which is not the one block_unraw_escape.py catches. That hook
guards Python string literals holding Windows paths. This one guards a
different mechanism with the same symptom: an UNQUOTED heredoc delimiter makes
the shell expand the body before the command sees it, so a backslash escape is
consumed in transit and what lands in the file is not what was written.

    cat > f.py <<EOF          <- unquoted: shell expands the body
    print("a\\nb")             <- the shell eats one backslash
    EOF
    # file now contains: print("a
    # b")                      <- a literal newline, and a syntax error

    cat > f.py <<'EOF'        <- quoted: body passes through verbatim
    print("a\\nb")
    EOF

THE COUNT. Nine occurrences in Sprint 16, including twice while writing the
retrospective that documented the class. Then TWICE MORE in Sprint 17 Task C,
inside five minutes, while editing a file -- the first attempt turned an
f-string's \\n into a literal newline and produced an unterminated f-string;
the second, written to avoid the first, did exactly the same thing again.

WHY A HOOK AND NOT A RULE. There has been a rule since Sprint 16. It is in
CLAUDE.md, in a retrospective, and in a card. The rule did not work, because it
depends on remembering at the moment of writing, and the failure mode is a
plausible wrong result rather than an error. The mechanical check succeeds
where the remembered rule fails. This is the same reasoning that produced
block_unraw_escape.py after five recurrences of its own class.

WHAT THIS DELIBERATELY DOES NOT BLOCK. Prose about backslashes, a quoted
heredoc (which is already correct), and a body with no escape sequence at all.
A guard that blocks correct work gets bypassed, and a bypassed guard protects
nothing.

Exit 0 = allow. Exit 2 = block, with stderr fed back to Claude.
Bypass: the literal token `allow_heredoc_escape`, for a body where shell
expansion inside an unquoted heredoc is genuinely what is wanted.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hooklib import ALLOW, block, command_of, read_payload  # noqa: E402

# An unquoted heredoc opener: <<EOF or <<-EOF, delimiter NOT in quotes.
#
# A quoted delimiter (<<'EOF' or <<"EOF") is the CORRECT form -- it passes the
# body through verbatim -- and this pattern already excludes it, because the
# trailing quote defeats the \s*$ anchor. That is load-bearing and easy to
# break, so test_allows_the_quoted_form_of_the_same_body pins it.
#
# An earlier draft also carried a separate `delim in quoted` check against a
# QUOTED_HEREDOC pattern. It was DEAD CODE: no input could reach it, because
# anything it would have caught was already excluded here. Removed after an
# injection run showed that deleting it broke no test -- which is the signature
# of a guard that cannot fire, the same class this repository keeps paying for.
# The delimiter may be followed by a REDIRECT, so the old `\s*$` anchor was
# wrong: `cat <<EOF > f.py` is at least as idiomatic as `cat > f.py <<EOF`, and
# the anchor made the first form unrecognisable, so it was allowed outright.
# Found by the PR #122 review.
UNQUOTED_HEREDOC = re.compile(
    r"<<-?\s*([A-Za-z_][A-Za-z0-9_]*)(?=\s|$|[>|&;])", re.MULTILINE)

# WHAT BASH ACTUALLY CONSUMES in an unquoted heredoc, measured rather than
# assumed (PR #122 review; re-measured here on Linux bash with every sequence
# built from chr(92) so no layer could eat the test input):
#
#   written   [n]a\nb [t]a\tb [r]a\rb [b]a\bb [0]a\0b [x41]a\x41b [$x]a\$xb [\]a\\b
#   landed    [n]a\nb [t]a\tb [r]a\rb [b]a\bb [0]a\0b [x41]a\x41b []a$xb    [\]a\b
#
# Only `\$` and `\\` change. `\n`, `\t`, `\r`, `\b`, `\0` and `\x` pass through
# COMPLETELY UNTOUCHED -- bash does not interpret them in a heredoc body at all.
#
# The first version of this pattern blocked all eight. That is a large
# false-positive surface on a guard whose own docstring says a guard that
# blocks correct work gets bypassed, and the block message told the author
# something untrue about their `\n`.
#
# The real Sprint 17 failure was the `\\` in `\\n` inside an f-string: bash ate
# one level and the intended `\n` escape became a literal newline. That is the
# `\\` case below, which is still caught.
RISKY_ESCAPE = re.compile(r"\\[\\$]|\\$")

# Writing to a FILE is what makes this dangerous. A heredoc feeding a pager or
# a diff is throwaway; one feeding a file persists the damage.
#
# Decided INDEPENDENTLY OF OPERATOR ORDER. The old pattern required `>` to
# follow cat/tee/dd with no `<` between them, so it missed `cat <<EOF > f.py`,
# `python - <<EOF > out.txt` and `tee f.py <<EOF` -- three forms that write a
# file exactly as destructively as the one form it did catch. `tee` and `dd`
# need no `>` at all, which the old comment claimed to cover and did not.
WRITES_A_FILE = re.compile(
    r">>?\s*\S"                              # any output redirect on the line
    r"|(?:^|[|&;]\s*)(?:tee|dd)\b")          # tee/dd write without needing `>`


def risky_heredocs(cmd: str) -> list[tuple[str, str]]:
    """Return (delimiter, offending_line) for each unquoted heredoc whose body
    carries an escape that will not survive."""
    lines = cmd.split("\n")
    found: list[tuple[str, str]] = []

    for i, line in enumerate(lines):
        m = UNQUOTED_HEREDOC.search(line)
        if not m:
            continue
        delim = m.group(1)
        # Only care when the heredoc is on its way into a file.
        if not WRITES_A_FILE.search(line):
            continue
        # Scan the body up to the closing delimiter.
        for body_line in lines[i + 1:]:
            if body_line.strip() == delim:
                break
            if RISKY_ESCAPE.search(body_line):
                found.append((delim, body_line.strip()))
                break
    return found


def message(hits: list[tuple[str, str]]) -> str:
    delim, sample = hits[0]
    # The escape examples are BUILT, not typed. Writing `\x` in a non-raw
    # string is a truncated-escape SyntaxError, and writing `\n` in a message
    # ABOUT `\n` silently becomes a newline. Both happened here while editing
    # this very function -- the class the hook exists to catch, inside the hook.
    bs = chr(92)
    seqs = ", ".join(f"`{bs}{c}`" for c in "ntrb0x")
    return f"""[BLOCKED] Unquoted heredoc will eat a backslash escape (F82, Sprint 17).

Heredoc delimiter: <<{delim}   (unquoted, so the shell expands the body first)
Offending line:
    {sample}

Bash consumes one level of backslash from `{bs}{bs}` and `{bs}$` before the
content reaches the file, so what lands on disk is not what you wrote. A
`{bs}{bs}n` meant as an escaped newline arrives as a LITERAL newline and breaks
the string it was in. (Measured: {seqs} pass through a heredoc untouched and
are not blocked here.)

The result is usually a plausible wrong file rather than an error, which is why
this class has now cost eleven occurrences across two sprints -- nine in
Sprint 16, two more in Sprint 17 inside five minutes, the second while trying
to avoid the first.

FIX, one keystroke:
    cat > f <<'{delim}'     <- QUOTE the delimiter; body passes through verbatim
    cat > f <<{delim}       <- what you wrote; shell expands the body

If you need the shell to expand the body, re-run with the literal token
allow_heredoc_escape in the command."""


def main() -> int:
    payload = read_payload()
    cmd = command_of(payload)
    if not cmd or not cmd.strip():
        return ALLOW
    if "allow_heredoc_escape" in cmd:
        return ALLOW

    hits = risky_heredocs(cmd)
    if hits:
        return block(message(hits))
    return ALLOW


if __name__ == "__main__":
    sys.exit(main())
