"""Converted Python hooks behave exactly like the PowerShell they replace.

F78, Sprint 16. Every guard in this repository was Windows-only protection: CI
runs ubuntu-latest, where a .ps1 hook cannot execute at all.

WHY THIS TEST EXISTS AND NOT JUST A GREEN SUITE. A converted hook that stops
blocking is worse than no conversion, because the registration still looks
right and the suite still passes. A converted hook that STARTS blocking correct
work is equally bad, because a hook that blocks correct work gets switched off
and then guards nothing. Both directions are asserted.

The expectations were measured against the PowerShell BEFORE any Python was
written, so they record what the hooks actually do rather than what I assumed.
Where both implementations exist, this test runs BOTH and requires them to
agree, which is stronger than either one matching a written-down expectation.

Several cases exist because of a specific past defect and are labeled as such.
Losing one silently re-opens the defect it guards, and the ordinary cases would
still pass.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
HOOKS = ROOT / ".claude" / "hooks"

ALLOW, BLOCK = 0, 2

# Assembled at runtime so this file's own text does not trip the hooks it tests.
STASH = "git" + " stash"
PREREG = "experiments/PREREGISTRATION.md"
PROPOSAL = "docs/paper/proposal.md"

CASES: dict[str, list[tuple[str, int, dict]]] = {
    "block_carry_forward_stash": [
        ("bare stash", BLOCK, {"tool_input": {"command": STASH}}),
        ("stash push", BLOCK, {"tool_input": {"command": STASH + " push -m wip"}}),
        ("stash save", BLOCK, {"tool_input": {"command": STASH + " save"}}),
        ("stash list is a READ", ALLOW, {"tool_input": {"command": STASH + " list"}}),
        ("stash show is a READ", ALLOW, {"tool_input": {"command": STASH + " show"}}),
        ("sanctioned bypass token", ALLOW,
         {"tool_input": {"command": STASH + " # allow_stash"}}),
        # False positive from spamfilter F130-S51: prose ABOUT stash is data.
        ("single-quoted prose is DATA", ALLOW,
         {"tool_input": {"command": "echo '" + STASH + " is banned'"}}),
        ("double-quoted prose is DATA", ALLOW,
         {"tool_input": {"command": 'echo "' + STASH + ' is banned"'}}),
        ("unrelated git command", ALLOW,
         {"tool_input": {"command": "git status --short"}}),
        ("empty command", ALLOW, {"tool_input": {"command": ""}}),
        ("no command key", ALLOW, {"tool_input": {}}),
    ],

    "block_branch_from_develop": [
        ("checkout -b from develop", BLOCK,
         {"tool_input": {"command": "git checkout -b feature/x develop"}}),
        ("switch -c from main", BLOCK,
         {"tool_input": {"command": "git switch -c feature/x main"}}),
        ("checkout -b from origin/develop", BLOCK,
         {"tool_input": {"command": "git checkout -b feature/x origin/develop"}}),
        ("bare checkout -b is the PRESCRIBED form", ALLOW,
         {"tool_input": {"command": "git checkout -b feature/x"}}),
        ("plain checkout of develop", ALLOW,
         {"tool_input": {"command": "git checkout develop"}}),
        ("unrelated command", ALLOW,
         {"tool_input": {"command": "git log --oneline -5"}}),
        # The four bypasses found reviewing PR #58. Each let a cut from develop
        # through while the ordinary cases still passed.
        ("PR58 bypass 1: option between name and base", BLOCK,
         {"tool_input": {"command": "git checkout -b feature/x --track origin/develop"}}),
        ("PR58 bypass 1b: switch -c with -t", BLOCK,
         {"tool_input": {"command": "git switch -c feature/x -t origin/develop"}}),
        ("PR58 bypass 2: quoted branch name", BLOCK,
         {"tool_input": {"command": "git checkout -b 'feature/x' origin/develop"}}),
        ("PR58 bypass 3: SECOND command in a chain", BLOCK,
         {"tool_input": {"command":
                         "git checkout -b tmp HEAD && git checkout -b feature/x origin/develop"}}),
        ("PR58 bypass 4: chained, base after separator", BLOCK,
         {"tool_input": {"command": "git checkout -b a HEAD ; git checkout -b b main"}}),
        ("heredoc body describing the rule is DATA", ALLOW,
         {"tool_input": {"command": "cat <<'EOF'\n"
                                    "git checkout -b x origin/develop\n"
                                    "EOF"}}),
        ("sanctioned bypass token", ALLOW,
         {"tool_input": {"command":
                         "git checkout -b x origin/develop # allow_branch_from_base"}}),
    ],

    "block_unraw_escape": [
        ("non-raw windows path in python", BLOCK,
         {"tool_input": {"command": 'python -c "p = \'D:\\Data\\Harold\\x.md\'"'}}),
        ("raw string is fine", ALLOW,
         {"tool_input": {"command": 'python -c "p = r\'D:\\Data\\Harold\\x.md\'"'}}),
        ("forward slashes are fine", ALLOW,
         {"tool_input": {"command": 'python -c "p = \'D:/Data/Harold/x.md\'"'}}),
        ("not a python command", ALLOW,
         {"tool_input": {"command": "echo D:\\Data\\Harold"}}),
        # The raw-prefix check is EXACT. It was a substring test, so an
        # identifier ending in r silenced the block entirely.
        ("identifier ending in r does not silence it", BLOCK,
         {"tool_input": {"command": 'python -c "x = str\'D:\\Data\\x\'"'}}),
        ("rb IS a real raw prefix", ALLOW,
         {"tool_input": {"command": 'python -c "x = rb\'D:\\Data\\x\'"'}}),
        ("already-escaped backslashes are safe", ALLOW,
         {"tool_input": {"command": 'python -c "x = \'D:\\\\Data\\\\x\'"'}}),
        ("comment line is skipped", ALLOW,
         {"tool_input": {"command": "python -c 1\n# p = 'D:\\Data\\x'"}}),
        ("sanctioned bypass token", ALLOW,
         {"tool_input": {"command": 'python -c "x = \'D:\\Data\\x\'" # allow_unraw_escape'}}),
    ],

    "block_shell_metachar_expansion": [
        ("command substitution in python", BLOCK,
         {"tool_input": {"command": 'python -c "print($(date))"'}}),
        ("backtick in python", BLOCK,
         {"tool_input": {"command": 'python -c "print(`date`)"'}}),
        # The hook must not block its own recommended fix.
        ("quoted heredoc is the prescribed form", ALLOW,
         {"tool_input": {"command": "python - <<'PY'\nprint(1)\nPY"}}),
        ("sanctioned bypass token", ALLOW,
         {"tool_input": {"command":
                         'python -c "print($(date))" # allow_shell_metachar'}}),
        ("plain python", ALLOW, {"tool_input": {"command": 'python -c "print(1)"'}}),
    ],

    # ---- Task E: the filesystem and git hooks -------------------------
    # PREREG and PROPOSAL are spelled out rather than imported so this
    # file stands alone.

    "block_frozen_history_rewrite": [
        ("force push", BLOCK,
         {"tool_input": {"command": "git push --force origin main"}}),
        ("force-with-lease", BLOCK,
         {"tool_input": {"command": "git push --force-with-lease"}}),
        ("short -f push", BLOCK,
         {"tool_input": {"command": "git push -f origin develop"}}),
        ("filter-branch", BLOCK,
         {"tool_input": {"command": "git filter-branch --tree-filter x HEAD"}}),
        ("filter-repo", BLOCK,
         {"tool_input": {"command": "git filter-repo --path x"}}),
        ("hard reset to a remote ref", BLOCK,
         {"tool_input": {"command": "git reset --hard origin/main"}}),
        ("delete the freeze tag", BLOCK,
         {"tool_input": {"command": "git tag -d prereg-freeze"}}),
        ("delete the freeze tag remotely", BLOCK,
         {"tool_input": {"command": "git push origin :refs/tags/prereg-freeze"}}),
        # Growing the repository forward is what a live project looks like.
        ("ordinary push", ALLOW,
         {"tool_input": {"command": "git push origin feature/x"}}),
        ("ordinary commit", ALLOW,
         {"tool_input": {"command": "git commit -m msg"}}),
        ("a NEW tag is fine", ALLOW,
         {"tool_input": {"command": "git tag v1.0"}}),
        ("local hard reset is fine", ALLOW,
         {"tool_input": {"command": "git reset --hard HEAD~1"}}),
        ("branch delete is fine", ALLOW,
         {"tool_input": {"command": "git branch -d old-feature"}}),
        ("no command", ALLOW, {"tool_input": {}}),
    ],

    "block_reactive_amendment": [
        ("editing the FROZEN preregistration", BLOCK,
         {"tool_name": "Edit", "tool_input": {"file_path": PREREG}}),
        ("writing the FROZEN preregistration", BLOCK,
         {"tool_name": "Write", "tool_input": {"file_path": PREREG}}),
        ("windows separators still match", BLOCK,
         {"tool_name": "Edit",
          "tool_input": {"file_path": "experiments\\PREREGISTRATION.md"}}),
        ("a different file is fine", ALLOW,
         {"tool_name": "Edit", "tool_input": {"file_path": "docs/x.md"}}),
        ("Bash is not an edit tool", ALLOW,
         {"tool_name": "Bash", "tool_input": {"command": "cat " + PREREG}}),
        ("no path", ALLOW, {"tool_name": "Edit", "tool_input": {}}),
    ],

    "block_unapproved_submission_edit": [
        ("editing the submitted proposal", BLOCK,
         {"tool_name": "Edit", "tool_input": {"file_path": PROPOSAL}}),
        ("editing the submitted appendix", BLOCK,
         {"tool_name": "Write",
          "tool_input": {"file_path": "docs/paper/appendix.md"}}),
        ("editing team_profile", BLOCK,
         {"tool_name": "Edit",
          "tool_input": {"file_path": "docs/paper/team_profile.md"}}),
        # Rendered PDFs are outputs, not the frozen source.
        ("a rendered PDF is an output", ALLOW,
         {"tool_name": "Write",
          "tool_input": {"file_path": "docs/paper/out/proposal.pdf"}}),
        ("an unrelated doc is fine", ALLOW,
         {"tool_name": "Edit", "tool_input": {"file_path": "docs/x.md"}}),
        ("Bash is not an edit tool", ALLOW,
         {"tool_name": "Bash", "tool_input": {"command": "cat " + PROPOSAL}}),
    ],

    # EVERY case here carries tool_name. The hook dispatches on it, so a
    # payload without one exercises no branch at all. My first draft omitted it
    # on the command cases and they all returned 0, which looked exactly like a
    # broken guard -- I nearly filed a bug against a hook that works.
    "block_cross_repo_write": [
        ("Write into a sibling repo", BLOCK,
         {"tool_name": "Write",
          "tool_input": {"file_path": "D:/Data/Harold/github/Evidence" + "BasedDB/x.md"}}),
        ("git push after cd into a sibling", BLOCK,
         {"tool_name": "Bash",
          "tool_input": {"command":
                         "cd D:/Data/Harold/github/Evidence" + "BasedDB && git " + "push"}}),
        ("git -C pointed at a sibling", BLOCK,
         {"tool_name": "Bash",
          "tool_input": {"command":
                         "git -C D:/Data/Harold/github/Evidence" + "BasedDB push"}}),
        ("reading a sibling is allowed", ALLOW,
         {"tool_name": "Bash",
          "tool_input": {"command":
                         "cat /d/Data/Harold/github/Evidence" + "BasedDB/CLAUDE.md"}}),
        ("grep whose PATTERN names cmdlets", ALLOW,
         {"tool_name": "Bash",
          "tool_input": {"command":
                         "grep -c 'New-Item|Remove-Item' /d/Data/Harold/github/Evidence"
                         + "BasedDB/x.ps1"}}),
        ("writing in THIS repo is fine", ALLOW,
         {"tool_name": "Write",
          "tool_input": {"file_path":
                         "D:/Data/Harold/github/hsbc-quantum-fraud-2026/docs/x.md"}}),
        # Fail-open is the deliberate default, and worth asserting so a future
        # change to strict-by-default is a visible decision rather than a drift.
        ("no tool_name exercises no branch", ALLOW,
         {"tool_input": {"command":
                         "cd D:/Data/Harold/github/Evidence" + "BasedDB && git " + "push"}}),
    ],
}

FLAT = [(hook, name, expected, payload)
        for hook, cases in CASES.items()
        for name, expected, payload in cases]


def _run(argv: list[str], payload: dict, tmp_path: Path) -> int:
    f = tmp_path / "payload.json"
    f.write_text(json.dumps(payload), encoding="utf-8")
    with f.open("rb") as stdin:
        return subprocess.run(argv, stdin=stdin, capture_output=True).returncode


def test_every_converted_hook_exists():
    """An empty population makes every case below vanish silently."""
    missing = [h for h in CASES if not (HOOKS / f"{h}.py").exists()]
    assert not missing, f"converted hooks missing: {missing}"
    assert len(FLAT) > 30, f"only {len(FLAT)} cases; the guard would be thin"


@pytest.mark.parametrize("hook,name,expected,payload", FLAT,
                         ids=[f"{h}:{n}" for h, n, _, _ in FLAT])
def test_python_hook_matches_expectation(hook, name, expected, payload, tmp_path):
    rc = _run([sys.executable, str(HOOKS / f"{hook}.py")], payload, tmp_path)
    verb = "BLOCK" if expected == BLOCK else "ALLOW"
    assert rc == expected, (
        f"{hook} should {verb} ({expected}) for {name!r}, got {rc}")


@pytest.mark.skipif(shutil.which("powershell") is None,
                    reason="powershell not on PATH (non-Windows)")
@pytest.mark.parametrize("hook,name,expected,payload", FLAT,
                         ids=[f"{h}:{n}" for h, n, _, _ in FLAT])
def test_python_and_powershell_agree(hook, name, expected, payload, tmp_path):
    """Both implementations, same answer.

    Stronger than either matching a written expectation: while both exist, a
    conversion drift shows up as a disagreement rather than as a stale test.
    """
    ps = HOOKS / f"{hook.replace('_', '-')}.ps1"
    if not ps.exists():
        pytest.skip(f"{ps.name} already removed")
    ps_rc = _run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                  "-File", str(ps)], payload, tmp_path)
    py_rc = _run([sys.executable, str(HOOKS / f"{hook}.py")], payload, tmp_path)
    assert ps_rc == py_rc, (
        f"{hook} DIVERGED on {name!r}: powershell={ps_rc}, python={py_rc}")
