"""PreToolUse hook blocking shell metacharacters that bash expands BEFORE
python runs. F48, Sprint 11 retrospective improvement 4.

Converted from PowerShell 2026-09-17 (F78, Sprint 16).

The sibling hook block_unraw_escape catches Windows path escapes in non-raw
PYTHON strings. It does not catch SHELL metacharacters, and those are worse: in
Sprint 11 backticks inside a Python string were expanded as command
substitution, bash executed a source file as shell, and the backticked filenames
were SILENTLY DELETED from a master-plan line. The command reported success and
the damage was visible only on inspection. A crash would have been kinder.

Exit 0 = allow. Exit 2 = block, with stderr fed back to Claude.
Bypass: the literal token `allow_shell_metachar`.

TWO BEHAVIORS PRESERVED FROM THE ORIGINAL, both of which exist because the first
version blocked correct commands within minutes of being written:

1. A SINGLE-QUOTED heredoc is exempt. It suppresses every expansion and is the
   fix this hook recommends, so without the exemption the hook blocks its own
   advice.

2. PER-LINE anchoring, not per-command, and python must sit at a COMMAND
   POSITION. Testing the whole command blocked a multi-line block whose last
   line ran python (flagging backticks in an unrelated earlier echo) and a
   command with no python at all, because the word appeared inside echoed prose.
   A hook that blocks a sentence mentioning python is a hook that gets switched
   off, and then it guards nothing.
"""
from __future__ import annotations

import json
import re
import sys

ALLOW, BLOCK = 0, 2

QUOTED_HEREDOC = re.compile(r"<<\s*'[A-Za-z_][A-Za-z0-9_]*'")

# python at a command position: line start, or after a separator or open paren,
# optionally behind a path such as .venv/Scripts/ or /usr/bin/.
INVOKES = re.compile(
    r"(?:^|[;&|(]|&&|\|\|)\s*(?:[^\s;&|()]*[/\\])?python[0-9.]*(?:\.exe)?(?:\s|$)")

EXPANSIONS = (
    (re.compile(r"`[^`]+`"), "`...` command substitution"),
    (re.compile(r"\$\([^)]*\)"), "$(...) command substitution"),
    (re.compile(r"\$\{[^}]*\}"), "${...} parameter expansion"),
)


def read_command() -> str | None:
    """Fail OPEN on anything malformed, matching the PowerShell original."""
    try:
        raw = sys.stdin.read()
    except Exception:                                    # noqa: BLE001
        return None
    if not raw or not raw.strip():
        return None
    try:
        payload = json.loads(raw)
    except Exception:                                    # noqa: BLE001
        return None
    if not isinstance(payload, dict):
        return None
    ti = payload.get("tool_input")
    if isinstance(ti, dict) and ti.get("command"):
        return str(ti["command"])
    if payload.get("command"):
        return str(payload["command"])
    return None


def message(sample: str) -> str:
    return f"""[BLOCKED] Shell metacharacter in a python command; bash expands it BEFORE
python runs (F48, Sprint 11 retrospective improvement 4).

Found:
    {sample}

Why this is blocked and not merely warned: in Sprint 11 backticks inside a
Python string were expanded as command substitution. Bash executed a source
file as shell and SILENTLY DELETED the backticked filenames from a master-plan
line. The command reported success and the damage was only visible on
inspection. A crash would have been kinder than a plausible-looking wrong
result.

FIX, in order of preference:

  1. Write the script to a .py file and run it. Best for anything non-trivial,
     and it makes the script reviewable and re-runnable.

  2. Use a SINGLE-QUOTED heredoc, which suppresses every expansion:

         python - <<'PYEOF'
         ...your code...
         PYEOF

     The quotes around PYEOF are the whole point. Without them bash expands
     the body.

  3. Escape it for the shell, if the expansion is genuinely intended.

If the expansion IS deliberate, re-run with the literal token
allow_shell_metachar in the command."""


def main() -> int:
    cmd = read_command()
    if not cmd or not cmd.strip():
        return ALLOW
    if "allow_shell_metachar" in cmd:
        return ALLOW
    if QUOTED_HEREDOC.search(cmd):
        return ALLOW

    bad: list[str] = []
    for line in cmd.split("\n"):
        if line.strip().startswith("#"):
            continue
        if not INVOKES.search(line):
            continue
        for pattern, label in EXPANSIONS:
            if pattern.search(line):
                bad.append(label)

    if not bad:
        return ALLOW

    seen: list[str] = []
    for item in bad:
        if item not in seen:
            seen.append(item)
    sys.stderr.write(message("\n    ".join(seen[:3])) + "\n")
    return BLOCK


if __name__ == "__main__":
    sys.exit(main())
