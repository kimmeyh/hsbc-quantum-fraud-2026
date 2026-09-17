"""PreToolUse hook blocking Python string literals holding a Windows path
escape outside a raw string. Sprint 10 retrospective improvement 1.

Converted from PowerShell 2026-09-17 (F78, Sprint 16).

This failure has recurred five-plus times across sprints, twice in Sprint 10
alone, and twice more since the PowerShell version was written. The shape is
always the same: a Python snippet contains a Windows path in a normal quoted
string,

    p = 'D:\\Data\\Harold\\...'

Python reads \\D as an invalid escape and \\b, \\x, \\n as real control
characters, so this either warns, crashes, or -- worst -- silently produces the
wrong value. In Sprint 10 a \\b inside a path became a backspace and wrote a
file to the wrong directory; the JSON looked fine.

A rule against it already existed and did not work, because it depends on
remembering at the moment of writing. The mechanical check succeeds where the
remembered rule fails.

Exit 0 = allow. Exit 2 = block, with stderr fed back to Claude.
Bypass: the literal token `allow_unraw_escape`, for the rare case where the
escape is deliberate.

Only inspects commands that invoke python, so shell strings and prose are
untouched.

ONE FIX PRESERVED FROM THE ORIGINAL, with its own test case: the raw-prefix
check is an EXACT match on valid Python prefixes. It was a substring test over
a [A-Za-z]* capture, so an adjacent identifier ending in r -- str'...',
dir'...', ptr'...' -- silenced the block entirely.
"""
from __future__ import annotations

import json
import re
import sys

ALLOW, BLOCK = 0, 2

# A command that actually invokes python, not merely mentions it.
PYTHON_INVOCATION = re.compile(r"(?:^|[\s;&|(])python[0-9.]*(?:\.exe)?(?:\s|$)")

# prefix + quote + body + same quote.
LITERAL = re.compile(r"(?P<prefix>[A-Za-z]*)(?P<q>['\"])(?P<body>[^'\"]*)(?P=q)")

# Valid Python raw-string prefixes ONLY. Anything else abutting a quote is an
# identifier, not a prefix.
RAW_PREFIX = re.compile(r"^(?:r|rb|br|rf|fr)$", re.IGNORECASE)

# A drive-letter path whose backslash is followed by a letter, i.e. a real
# escape sequence rather than an already-escaped separator.
WINDOWS_PATH = re.compile(r"[A-Za-z]:\\[A-Za-z]")


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


def offenders(cmd: str) -> list[str]:
    found: list[str] = []
    for line in cmd.split("\n"):
        if line.strip().startswith("#"):
            continue
        for m in LITERAL.finditer(line):
            if RAW_PREFIX.match(m.group("prefix")):
                continue
            # A doubled backslash is already escaped and is not the defect.
            probe = m.group("body").replace("\\\\", "")
            if WINDOWS_PATH.search(probe):
                found.append(m.group(0))
    return found


def message(sample: str) -> str:
    return f"""[BLOCKED] Python string with an unescaped Windows path (Sprint 10 retro item 1).

Found:
    {sample}

Python reads \\D, \\H, \\U as invalid escapes and \\b, \\x, \\n as real control
characters, so this either warns, crashes, or -- worst -- silently produces the
wrong value. In Sprint 10 a \\b inside a path became a backspace and wrote a
file to the wrong directory; the JSON looked fine.

FIX, one keystroke either way:
    r'D:\\Data\\Harold\\...'      <- raw string, preferred
    'D:/Data/Harold/...'       <- forward slashes work on Windows

If the escape is genuinely intended, re-run with the literal token
allow_unraw_escape in the command."""


def main() -> int:
    cmd = read_command()
    if not cmd or not cmd.strip():
        return ALLOW
    if "allow_unraw_escape" in cmd:
        return ALLOW
    if not PYTHON_INVOCATION.search(cmd):
        return ALLOW

    bad = offenders(cmd)
    if bad:
        sys.stderr.write(message("\n    ".join(bad[:3])) + "\n")
        return BLOCK
    return ALLOW


if __name__ == "__main__":
    sys.exit(main())
