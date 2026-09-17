"""Every registered hook must actually resolve to a file on disk.

F68. Two hooks were registered in `.claude/settings.json` and NEVER RAN. The
file held `\\hooks\\block-...` with a single backslash before `b`, which JSON
parses as U+0008 BACKSPACE, so the path resolved to `hooks<BS>lock-...`. That
file does not exist, and Claude Code skips a hook whose file is missing without
saying anything.

Broken since the commit that created them. The Sprint 13 retrospective recorded
that the Class 4 submission-edit hook "worked exactly as designed"; it had never
executed once, and every submission-document edit that sprint was unguarded. The
process held because the team lead approved each change in conversation, not
because anything enforced it.

WHY THIS IS THE RIGHT GUARD. The defect is invisible from the inside: a hook
that never fires looks exactly like a hook that fires and permits. Nothing in
the edit's behaviour distinguishes them, so no amount of care while editing
would have caught it. What separates the two cases is whether the registered
path exists, which is a fact about the filesystem and is cheap to assert.

This is also the F48 defect class -- a silent escape corruption -- living in the
file that registers the guard against it.

Verified by injection: reverting one registration to the single-backslash form
fails `test_every_registered_hook_path_resolves` with the offending name, and
`test_no_hook_command_contains_a_control_character` names the control character.
Restoring the doubled backslash passes both.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SETTINGS = ROOT / ".claude" / "settings.json"


def _hook_commands() -> list[tuple[str, str]]:
    """(matcher, command) for every registered PreToolUse hook."""
    if not SETTINGS.exists():
        return []
    cfg = json.loads(SETTINGS.read_text(encoding="utf-8"))
    out: list[tuple[str, str]] = []
    for group in cfg.get("hooks", {}).get("PreToolUse", []):
        matcher = group.get("matcher", "<none>")
        for hook in group.get("hooks", []):
            cmd = hook.get("command")
            if cmd:
                out.append((matcher, cmd))
    return out


def _script_path(command: str) -> Path | None:
    """The -File argument of a hook command, resolved against the repo root.

    Separators are NORMALISED to forward slashes after substitution. The hook
    commands are PowerShell invocations and carry Windows backslashes, which a
    POSIX filesystem reads as literal filename characters rather than
    separators -- so `Path(tail).exists()` is unconditionally False on Linux and
    macOS.

    Found by Copilot on PR #94. CI runs ubuntu-latest, so the first version of
    this guard would have turned CI red for exactly the fresh-clone audience the
    sprint was written to serve: a test asserting that hooks resolve, failing
    because it could not resolve them itself.
    """
    marker = "-File "
    if marker not in command:
        return None
    tail = command.split(marker, 1)[1].strip().strip('"')
    tail = tail.replace("${CLAUDE_PROJECT_DIR}", str(ROOT))
    return Path(tail.replace("\\", "/"))


@pytest.mark.skipif(not SETTINGS.exists(), reason="no .claude/settings.json")
def test_every_registered_hook_path_resolves():
    """A hook whose file is missing is skipped silently, so it must exist."""
    missing: list[str] = []
    for matcher, cmd in _hook_commands():
        path = _script_path(cmd)
        if path is None:
            continue                      # not a -File invocation; nothing to check
        if not path.exists():
            missing.append(f"{matcher}: {path}")
    assert not missing, (
        "these hooks are registered but their files do not exist, so Claude Code "
        f"skips them WITHOUT ERROR: {missing}. Two hooks were dead this way from "
        "the moment they were written, and a retrospective recorded one of them "
        "as working.")


@pytest.mark.skipif(not SETTINGS.exists(), reason="no .claude/settings.json")
def test_no_hook_command_contains_a_control_character():
    """The specific corruption that killed two hooks, caught at its cause.

    `\\b` in a JSON string is a backspace, not a path separator. The path still
    LOOKS right in an editor that renders the control character as nothing,
    which is why the previous test checks existence and this one checks the
    cause: they fail for different reasons and a reader needs the second to
    understand the first.
    """
    bad: list[str] = []
    for matcher, cmd in _hook_commands():
        for ch in cmd:
            if ord(ch) < 32:
                bad.append(f"{matcher}: U+{ord(ch):04X} in {cmd!r}")
                break
    assert not bad, (
        "a hook command contains a control character, which means a backslash "
        f"escape was consumed by the JSON parser: {bad}. In the raw file a "
        "Windows path separator must be a DOUBLED backslash.")


@pytest.mark.skipif(not SETTINGS.exists(), reason="no .claude/settings.json")
def test_the_submission_and_amendment_guards_are_registered():
    """The two guards over frozen artifacts must be present, not merely valid.

    The tests above would pass a settings file with no hooks at all. These two
    protect the submitted documents and the frozen preregistration, and their
    absence is what the repository would least notice.
    """
    commands = " ".join(c for _, c in _hook_commands())
    # Stems rather than extensions: F78 (Sprint 16) converted every hook from
    # .ps1 to .py, and an assertion naming the extension would have to be
    # edited by the very change it is meant to survive. This test FAILED on the
    # conversion, which is correct -- it noticed. Matching the stem means it
    # keeps guarding through a future rename too.
    for guard, variants in {
        "the submitted-document guard": ("unapproved-submission-edit",
                                         "unapproved_submission_edit"),
        "the frozen-preregistration guard": ("reactive-amendment",
                                             "reactive_amendment"),
    }.items():
        assert any(v in commands for v in variants), (
            f"{guard} is not registered in .claude/settings.json (looked for "
            f"{variants}). It guards an artifact that has already been "
            "submitted or frozen.")
