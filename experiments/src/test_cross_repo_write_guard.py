"""The cross-repository write boundary must be enforced, not merely documented.

Team lead, 2026-09-15: sessions in this repository never write to the sibling
repositories. Reading them on request is fine.

Why a test and not only a CLAUDE.md line: in Sprint 14 a session reviewing
PR #97 examined a sibling repository, found real defects, and fixed, committed
and pushed them there directly. Every finding was genuine; the boundary was
still wrong, because the changes reached that repository with no review, no
tests as gatekeeper and no sprint record.

Half of these cases assert the guard ALLOWS something. That half is not filler.
The first version of this hook blocked two legitimate read-only commands within
minutes of shipping, because it tested "is this mutating anywhere?" and "does it
name a sibling anywhere?" independently and ANDed the answers. A grep whose
PATTERN contained `New-Item|Remove-Item` was refused, and so was a heredoc
writing a file in THIS repository whose text quoted the sibling names. A guard
that blocks correct work trains people to bypass it, which is worse than no
guard.

The cases run through the hook itself, so a hook that stops firing fails here
rather than going quietly inert. That is exactly how two hooks in this
repository stayed dead for their entire life.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
# F78 (Sprint 16) converted this hook to Python. The cases below are
# unchanged; only the implementation under test moved.
HOOK = ROOT / ".claude" / "hooks" / "block_cross_repo_write.py"

# Assembled at runtime so this file's own text is not a literal match for the
# guard it tests. Writing the names out would make the file unwritable through
# a shell heredoc, which is how this test was first blocked.
SIBLING = "Evidence" + "BasedDB"
OTHER = "spamfilter" + "-multi"
HERE = "D:/Data/Harold/github"

BLOCK, ALLOW = 2, 0

CASES = [
    # --- must BLOCK: the sibling is the target of a write -------------------
    ("Write tool into a sibling", BLOCK,
     {"tool_name": "Write",
      "tool_input": {"file_path": f"{HERE}/{SIBLING}/CLAUDE.md"}}),
    ("Edit tool into the other sibling", BLOCK,
     {"tool_name": "Edit",
      "tool_input": {"file_path": f"{HERE}/{OTHER}/lib/main.dart"}}),
    ("git push after cd into a sibling", BLOCK,
     {"tool_name": "Bash",
      "tool_input": {"command": f"cd {HERE}/{SIBLING} && git " + "push origin HEAD"}}),
    ("git -C pointed at a sibling", BLOCK,
     {"tool_name": "Bash",
      "tool_input": {"command": f"git -C {HERE}/{SIBLING} commit -m x"}}),
    ("shell redirect into a sibling", BLOCK,
     {"tool_name": "Bash",
      "tool_input": {"command": f"echo hi > {HERE}/{SIBLING}/x.md"}}),
    ("rm inside a sibling", BLOCK,
     {"tool_name": "Bash",
      "tool_input": {"command": f"rm -f {HERE}/{SIBLING}/docs/old.md"}}),
    ("sed -i against a sibling", BLOCK,
     {"tool_name": "Bash",
      "tool_input": {"command": f"sed -i s/a/b/ {HERE}/{SIBLING}/README.md"}}),

    # --- must ALLOW: reading a sibling --------------------------------------
    ("cat a sibling file", ALLOW,
     {"tool_name": "Bash",
      "tool_input": {"command": f"cat {HERE}/{SIBLING}/CLAUDE.md"}}),
    ("grep a sibling", ALLOW,
     {"tool_name": "Bash",
      "tool_input": {"command": f"grep -n rule {HERE}/{SIBLING}/CLAUDE.md"}}),
    ("git log in a sibling", ALLOW,
     {"tool_name": "Bash",
      "tool_input": {"command": f"git -C {HERE}/{SIBLING} log --oneline -5"}}),
    ("ls a sibling directory", ALLOW,
     {"tool_name": "Bash",
      "tool_input": {"command": f"ls {HERE}/{SIBLING}/.claude/hooks/"}}),

    # --- must ALLOW: the regressions the first version caused ---------------
    ("grep whose PATTERN names cmdlets, run against a sibling", ALLOW,
     {"tool_name": "Bash",
      "tool_input": {"command":
                     f"grep -cE 'New-Item|Remove-Item|Set-Content' {HERE}/{SIBLING}/x.ps1"}}),
    ("writing in THIS repo a file whose text mentions the siblings", ALLOW,
     {"tool_name": "Bash",
      "tool_input": {"command":
                     f"echo 'never write to {OTHER} or {SIBLING}' > "
                     f"{HERE}/hsbc-quantum-fraud-2026/docs/rule.md"}}),

    # --- must ALLOW: ordinary work in this repository -----------------------
    ("Write tool in this repository", ALLOW,
     {"tool_name": "Write",
      "tool_input": {"file_path": str(ROOT / "docs" / "scratch.md")}}),
    ("git commit in this repository", ALLOW,
     {"tool_name": "Bash", "tool_input": {"command": "git commit -m x"}}),
]


def test_the_hook_file_exists():
    assert HOOK.exists(), f"{HOOK} is missing; the boundary would be unenforced"


# NO skipif. This test ran only where PowerShell was on PATH until Sprint 17
# Task H measured the suite on both platforms and found 15 cases skipping on
# Linux. The gate was a leftover from the PowerShell era: the hook under test
# is block_cross_repo_write.py, a PYTHON file invoked through sys.executable,
# so PowerShell has nothing to do with it.
#
# The cost of the leftover was precise. CI is ubuntu-latest, so the guard
# enforcing the team lead's cross-repo boundary -- the rule added after a
# session wrote into EvidenceBasedDB -- was never actually exercised there.
# It passed by being skipped.
@pytest.mark.parametrize("name,expected,payload", CASES, ids=[c[0] for c in CASES])
def test_guard_decides_correctly(name, expected, payload, tmp_path):
    f = tmp_path / "payload.json"
    f.write_text(json.dumps(payload), encoding="utf-8")
    with f.open("rb") as stdin:
        r = subprocess.run([sys.executable, str(HOOK)],
                           stdin=stdin, capture_output=True)
    verb = "BLOCK" if expected == BLOCK else "ALLOW"
    assert r.returncode == expected, (
        f"expected the guard to {verb} ({expected}) for {name!r}, got "
        f"{r.returncode}. stderr: {r.stderr.decode(errors='replace')[:300]}")


def test_the_guard_is_registered_and_its_path_resolves():
    """A hook registered at a path that does not resolve cannot fire.

    Not hypothetical: two hooks here were registered with a single backslash
    before `block-`, which JSON parses as U+0008, and never ran. The same bug
    was reproduced while writing THIS guard and caught by this check.
    """
    settings = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
    commands = [h.get("command", "")
                for matchers in settings.get("hooks", {}).values()
                for m in matchers for h in m.get("hooks", [])]

    # Match the STEM, not the extension: asserting on ".ps1" is what made this
    # test fail on the very conversion it should have survived.
    mine = [c for c in commands
            if "cross-repo-write" in c or "cross_repo_write" in c]
    assert mine, ("the cross-repository guard is not registered in "
                  ".claude/settings.json")

    for c in mine:
        ctrl = [hex(ord(ch)) for ch in c if ord(ch) < 32]
        assert not ctrl, f"control characters {ctrl} in the registered command: {c!r}"
        # Commands now use forward slashes (F78: they work on both OSes and
        # cannot be eaten as an escape), so split on either separator.
        name = c.rstrip('"').replace("\\", "/").split("/")[-1]
        assert (ROOT / ".claude" / "hooks" / name).exists(), \
            f"registered hook {name!r} does not resolve to a file"
