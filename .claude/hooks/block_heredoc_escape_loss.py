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
UNQUOTED_HEREDOC = re.compile(r"<<-?\s*([A-Za-z_][A-Za-z0-9_]*)\s*$", re.MULTILINE)

# Escape sequences the shell will consume or transform inside an unquoted
# heredoc. \n \t \r \b \0 \x are the ones that silently become something else;
# \\ and \$ are consumed one level.
RISKY_ESCAPE = re.compile(r"\\[ntrb0xuU\\$`]")

# Writing to a FILE is what makes this dangerous. A heredoc feeding a pager or
# a diff is throwaway; one feeding a file persists the damage.
WRITES_A_FILE = re.compile(r"(?:^|[|&;]\s*)(?:cat|tee|dd)\b[^<]*>|>\s*\S+\s*<<")


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
    return f"""[BLOCKED] Unquoted heredoc will eat a backslash escape (F82, Sprint 17).

Heredoc delimiter: <<{delim}   (unquoted, so the shell expands the body first)
Offending line:
    {sample}

The shell consumes one level of backslash before the content reaches the file,
so what lands on disk is not what you wrote. The result is usually a plausible
wrong file rather than an error, which is why this class has now cost eleven
occurrences across two sprints -- nine in Sprint 16, two more in Sprint 17
inside five minutes, the second while trying to avoid the first.

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
