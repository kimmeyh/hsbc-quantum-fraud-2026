"""PreToolUse hook blocking a carry-forward branch cut from develop/main.

Converted from PowerShell 2026-09-17 (F78, Sprint 16). Enforces the OTHER half
of workflow 6.6: the next sprint branch is cut FROM THE CURRENT FEATURE BRANCH,
never from develop after the merge.

Written 2026-09-08 after Claude cut feature/20260909_Sprint_10 with
`git checkout -b feature/20260909_Sprint_10 origin/develop` during the Sprint 9
close-out. No commits were lost that time, because the merge had already carried
everything and the uncommitted work followed the checkout, so the violation was
invisible in the outcome and was caught only by re-reading 6.6. That is exactly
the failure a hook should catch: the rule's stated harm does not appear every
time it is broken, so a clean result is not evidence the flow was right.

    ALLOWED (the prescribed flow):   git checkout -b feature/<date>_Sprint_<N+1>
    BLOCKED (what went wrong):       git checkout -b <name> origin/develop

A bare `checkout -b` inherits HEAD, which on a just-merged feature branch is the
correct start point. Only an EXPLICIT develop/main start point is blocked.

Exit 0 = allow. Exit 2 = block, with stderr fed back to Claude.
Bypass: the literal token `allow_branch_from_base` (team-lead-sanctioned), for
genuinely new work off develop that is not a sprint carry-forward.

FOUR BYPASSES were found reviewing PR #58 and each is preserved here with a test
case, because a conversion that loses them silently re-opens all four:
  1. an option between the name and the base, so `--track origin/develop` and
     `switch -c -t` sailed through while cutting from develop
  2. quoting the branch name, because quote-stripping ran BEFORE the match and
     ate the operand
  3. only the FIRST match was inspected, so the second command in a chain was
     never seen
  4. the operand pattern swallowed the `&&` separator, merging a chained case
     into one match

So: strip heredoc BODIES only, split on command separators, match per segment,
and strip quotes at the operand level. Quoted spans are NOT blanked wholesale
here, because a quoted branch name is an operand this hook has to read.
"""
from __future__ import annotations

import json
import re
import sys

ALLOW, BLOCK = 0, 2

BASE_PATTERN = re.compile(r"^(?:[A-Za-z0-9_.-]+/)?(?:develop|main|master)$")
INVOCATION = re.compile(
    r"(?:git\s+checkout\s+(?:-b|-B)|git\s+switch\s+(?:-c|-C))((?:\s+\S+)+)")
SEPARATORS = re.compile(r"\s*(?:&&|\|\||;|\||\r?\n)\s*")


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


def strip_heredoc_bodies(cmd: str) -> str:
    """Remove heredoc bodies ONLY.

    A commit message or document describing the rule must not trip the hook.
    Quoted spans survive, because bypass 2 was caused by blanking them.
    """
    out = re.sub(r"<<-?\s*['\"]?([A-Za-z_][A-Za-z0-9_]*)['\"]?.*?^\s*\1\s*$",
                 " ", cmd, flags=re.S | re.M)
    return re.sub(r"@'.*?'@", " ", out, flags=re.S)


def message(new_branch: str, base: str) -> str:
    return f"""[BLOCKED] Carry-forward branch cut from '{base}' (workflow 6.6; ADR-0004).

6.6 is explicit: on merge notification, create the next sprint branch FROM THE
CURRENT FEATURE BRANCH, and "never branch from develop after the merge".

Use:
  git checkout -b {new_branch}
  (bare -- no start point; the working tree and HEAD both follow)

WHY THIS IS BLOCKED EVEN WHEN IT SEEMS TO WORK: cutting from develop drops any
uncommitted work and any feature-branch commit the merge did not carry. When
the merge HAS carried everything, the result looks identical to the correct
flow, so a clean git status is not evidence the cut was right. That is how
this slipped through at the Sprint 9 close-out.

Recovery for a branch already mis-cut is cherry-pick onto a correctly-cut
branch, never stash.

If this is genuinely new work off {base} and NOT a sprint carry-forward, re-run
with the literal token allow_branch_from_base in the command."""


def main() -> int:
    cmd = read_command()
    if not cmd or not cmd.strip():
        return ALLOW

    if "allow_branch_from_base" in cmd:
        return ALLOW

    for segment in SEPARATORS.split(strip_heredoc_bodies(cmd)):
        m = INVOCATION.search(segment)
        if not m:
            continue

        operands = m.group(1).strip().split()
        positional = []
        for token in operands:
            if token.startswith("-"):
                continue                                  # bypass 1
            cleaned = token.strip("\"'")                  # bypass 2
            if cleaned:
                positional.append(cleaned)

        if len(positional) < 2:
            continue

        new_branch, base = positional[0], positional[1]
        if BASE_PATTERN.match(base):
            sys.stderr.write(message(new_branch, base) + "\n")
            return BLOCK

    return ALLOW


if __name__ == "__main__":
    sys.exit(main())
