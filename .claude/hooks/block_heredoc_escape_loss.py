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

# A QUOTED heredoc: <<'EOF' or <<"EOF". The shell passes the body verbatim, so
# bash is innocent -- and that is exactly why this was excluded as "already
# correct". It is not correct for a SECOND mechanism: the body reaches PYTHON,
# which interprets the escape itself whenever the string literal is not raw.
# Same symptom, different layer. Sprint 20 hit this five times.
QUOTED_HEREDOC = re.compile(
    r"""<<-?\s*(?:'([A-Za-z_][A-Za-z0-9_]*)'|"([A-Za-z_][A-Za-z0-9_]*)")""",
    re.MULTILINE)

# A PYTHON string literal that is NOT raw, carrying an escape Python will
# interpret. Built from chr(92) so no layer can eat the pattern itself -- the
# same precaution the message() function below already takes, for the same
# reason.
#
# The r-prefix exclusion is the whole point: r"a\nb" is safe because Python
# leaves it alone, and blocking it would make the hook fire on correct work.
_BS = chr(92)                          # built, so no layer can eat it

# ONLY the r-prefix is safe. A BYTES literal interprets escapes exactly as a
# str does -- b"a\x00b" puts a real NUL byte in the file, which is precisely
# the Sprint 20 case that corrupted a test file. Excluding `b` here made the
# hook miss its own worst instance; only `rb`/`br` are exempt.
# MATCH THE PREFIX FORWARD, do not exclude it with lookbehinds.
#
# The first version used two negative lookbehinds and had two holes, both
# found independently by Copilot and two review agents on PR #146:
#
#   rf"a\nb"        RAW and therefore safe, but BLOCKED -- the character
#                   before the quote is `f`, so neither lookbehind fired.
#                   (fr"" happened to work, which made the bug look absent.)
#   r"it's a\nb"    RAW and safe, but BLOCKED -- `['\"]` anchored on the
#                   apostrophe INSIDE the literal, a fresh start past the
#                   prefix.
#
# Both are false positives on correct work, and the block message tells the
# author to "make the literal RAW" -- advice that did not clear the block.
# This hook's own docstring says a guard that blocks correct work gets
# bypassed, so a false positive here is not cosmetic.
#
# Matching the prefix forward fixes both at once: capture whatever prefix
# letters precede the quote, then decide. Any prefix containing r or R is raw
# and exempt, whatever else it contains and in whatever order.
_PREFIXED_STRING = re.compile(
    r"(?<![A-Za-z0-9_])"               # prefix starts a token
    r"([A-Za-z]{0,3})"                 # the prefix letters, if any
    r"(['\"])"                         # the opening quote, captured
    r"((?:(?!\2).)*?)"                 # content, up to the SAME quote
    + _BS + _BS + r"[ntr0x]"           # the escape Python will interpret
)


def has_python_escape(line: str) -> bool:
    """Does this line hold a Python escape Python itself will interpret?

    True only for a NON-RAW literal. A prefix containing r or R is raw --
    `r`, `rb`, `br`, `rf`, `fr`, and every case variant -- and Python leaves
    its escapes alone, so blocking it would fire on correct work.
    """
    for m in _PREFIXED_STRING.finditer(line):
        if "r" not in m.group(1).lower():
            return True
    return False


# Kept as a module attribute: the tests and the earlier message text refer to
# it, and it still answers "could this line hold an interpreted escape?" for
# the non-prefixed case.
PY_ESCAPE_IN_NON_RAW = _PREFIXED_STRING

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


def risky_quoted_heredocs(cmd: str) -> list[tuple[str, str]]:
    """Return (delimiter, offending_line) for each QUOTED heredoc whose body
    carries a Python escape inside a non-raw string literal.

    The shell will not touch it. Python will. Writing `"a{bs}nb"` in a
    replacement string, an assertion message or a file being generated puts a
    real newline where the two characters were intended -- and in a string
    being matched against a file, the match then silently fails.

    Deliberately NOT blocked: a raw literal (`r"a{bs}nb"`), which is the
    correct form and must stay cheap to write; prose; and a body with no
    escape at all. A guard that blocks correct work gets bypassed.
    """.replace("{bs}", chr(92))
    lines = cmd.split("\n")
    found: list[tuple[str, str]] = []

    for i, line in enumerate(lines):
        m = QUOTED_HEREDOC.search(line)
        if not m:
            continue
        delim = m.group(1) or m.group(2)
        if not WRITES_A_FILE.search(line) and "python" not in line.lower():
            # A quoted heredoc feeding a pager is throwaway. One feeding
            # python is not: the escape damage lands wherever that script
            # writes, which is how all five Sprint 20 cases happened.
            continue
        for body_line in lines[i + 1:]:
            if body_line.strip() == delim:
                break
            if has_python_escape(body_line):
                found.append((delim, body_line.strip()))
                break
    return found


def quoted_message(hits: list[tuple[str, str]]) -> str:
    delim, sample = hits[0]
    bs = chr(92)
    seqs = ", ".join(f"`{bs}{c}`" for c in "ntr0x")
    return f"""[BLOCKED] A quoted heredoc will let PYTHON eat a backslash escape.

Heredoc delimiter: <<'{delim}'   (quoted, so the SHELL is innocent)
Offending line:
    {sample}

WHY THIS IS BLOCKED EVEN THOUGH THE QUOTING IS RIGHT. Quoting stops bash from
expanding the body, which is why this hook used to skip quoted heredocs
entirely. It does not stop PYTHON. The body arrives verbatim, Python reads a
NON-RAW string literal, and interprets {seqs} itself. What lands in the file is
not what you wrote -- and when the string is a match target, the match then
fails silently.

Sprint 20 hit this FIVE times in one sprint, all in correctly quoted heredocs.
One wrote a literal NUL byte into a test file and corrupted it. Another
produced an unterminated string literal. Two more made a .replace() target
that could never match, so the edit reported success and changed nothing.

FIX, in order of preference:

  1. Use the Edit or Write tool. No shell, no heredoc, no escape layer. This is
     the right answer for anything non-trivial and it is what finally worked
     every time this sprint.

  2. Make the literal RAW: r"a{bs}nb" instead of "a{bs}nb". Python then leaves
     it alone. This hook does not block raw literals.

  3. BUILD the sequence: chr(92) + "n". Verbose, but no layer can eat it, and
     it is what this hook's own message() function does for exactly this
     reason.

If the escape IS meant to be interpreted, re-run with the literal token
allow_heredoc_escape."""


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

    # The quoted case, added Sprint 20 after five occurrences the unquoted
    # check could not see.
    quoted = risky_quoted_heredocs(cmd)
    if quoted:
        return block(quoted_message(quoted))

    return ALLOW


if __name__ == "__main__":
    sys.exit(main())
