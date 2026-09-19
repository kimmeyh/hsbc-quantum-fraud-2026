"""PreToolUse hook blocking `git stash` (carry-forward protection).

Converted from PowerShell 2026-09-17 (F78, Sprint 16). The PowerShell original
was ported 2026-09-02 from spamfilter-multi per the Sprint 2 retro disposition,
and enforces workflow 6.6 and ADR-0004: NEVER stash to carry forward; create the
branch, then COMMIT.

Exit 0 = allow. Exit 2 = block, with stderr fed back to Claude.
Bypass: the literal token `allow_stash` in the command (team-lead-sanctioned).

Matches INVOCATIONS, not text: heredoc bodies and quoted spans are stripped
before matching, so documentation ABOUT stash does not trip it. That behavior
came from a real false positive (spamfilter F130-S51) and is preserved here,
with test cases asserting it in both directions.

Why this runs on Python: CI is ubuntu-latest, where a .ps1 hook cannot execute
at all, so every guard in this repository was Windows-only protection.
"""
from __future__ import annotations

import json
import re
import sys

ALLOW, BLOCK = 0, 2

MESSAGE = """[BLOCKED] git stash is disallowed (workflow 6.6 carry-forward rule; ADR-0004).

Use the DETERMINISTIC flow instead:
  1. Create the next branch:  git checkout -b <next-branch>
  2. COMMIT the uncommitted files on that branch -- the working tree follows
     a checkout -b; stashing is never needed for carry-forward.

Recovery for a mis-cut branch is cherry-pick, never stash. If the team lead
has sanctioned a genuine non-carry-forward stash, re-run with the literal
token allow_stash in the command."""


def read_command() -> str | None:
    """Fail OPEN on anything malformed, matching the PowerShell original.

    A hook that crashes on an unexpected payload blocks every subsequent tool
    call, which is a worse failure than missing one stash.
    """
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


def strip_data_regions(cmd: str) -> str:
    """Remove heredocs and quoted spans so prose about stash is not an invocation."""
    scan = cmd
    # Heredoc: <<'TOKEN' ... TOKEN  (quoted or not, optional leading dash)
    scan = re.sub(r"<<-?\s*['\"]?([A-Za-z_][A-Za-z0-9_]*)['\"]?.*?^\s*\1\s*$",
                  " ", scan, flags=re.S | re.M)
    scan = re.sub(r"@'.*?'@", " ", scan, flags=re.S)     # PowerShell here-string
    scan = re.sub(r"'[^']*'", " ", scan)
    scan = re.sub(r'"[^"]*"', " ", scan)
    return scan


def main() -> int:
    cmd = read_command()
    if not cmd or not cmd.strip():
        return ALLOW

    if "allow_stash" in cmd:
        return ALLOW

    scan = strip_data_regions(cmd)

    # `stash list` and `stash show` are reads and change nothing.
    if re.search(r"git\s+stash\s+(list|show)\b", scan):
        return ALLOW

    if re.search(r"git\s+stash\b", scan):
        sys.stderr.write(MESSAGE + "\n")
        return BLOCK

    return ALLOW


if __name__ == "__main__":
    sys.exit(main())
