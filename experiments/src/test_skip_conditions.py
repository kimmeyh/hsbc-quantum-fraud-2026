"""A skip condition must still be about something this repository uses.

THE DEFECT THIS PREVENTS (Sprint 17, F83). `test_cross_repo_write_guard.py`
skipped 15 of its 17 cases with "powershell not on PATH", but the hook under
test is `block_cross_repo_write.py` -- a PYTHON file invoked through
`sys.executable`. PowerShell had nothing to do with it. The condition was a
leftover from before F78 converted every hook from PowerShell to Python.

The cost was precise and invisible: CI runs ubuntu-latest, so the guard
enforcing the team-lead's cross-repository boundary -- the rule added after a
session wrote into EvidenceBasedDB -- never ran in CI at all. It passed by
being skipped. The boundary was enforced on one workstation and nowhere else.

A skip is the one test outcome that looks like success while proving nothing,
so a skip condition that no longer means anything is worse than a failing test.

This scans the suite for that shape mechanically, rather than relying on
someone re-reading every skipif.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parent
ROOT = SRC.parents[1]

# Dependencies this repository RETIRED. A skip gated on one of these is
# suspect: nothing here should need it any more.
#
# PowerShell was removed by F78 (Sprint 16) because CI runs ubuntu-latest and
# a .ps1 guard could never execute there.
RETIRED = ("powershell", "pwsh", ".ps1")

# Tests that legitimately reference a retired dependency, with the reason.
# Keeping this list SHORT is the point; an entry is a claim that the skip is
# still meaningful, and it has to be justified here.
PERMITTED = {
    # Compares each Python hook against its PowerShell predecessor where one
    # still exists. It needs PowerShell BY CONSTRUCTION, and it also skips per
    # hook with "<name>.ps1 already removed" once the predecessor is gone, so
    # it reports honestly on both axes.
    "test_hook_parity.py",
    # This file names the retired tokens in order to scan for them.
    "test_skip_conditions.py",
}


def _test_files() -> list[Path]:
    return sorted(p for p in SRC.glob("test_*.py"))


def _skip_sources(path: Path) -> list[str]:
    """Every skipif/skip decorator and call, as source text.

    Parsed from the AST rather than grepped: a regex over lines reads the word
    "skipif" inside a docstring as a decorator, which is how a comment
    explaining a removed skip would be flagged as the skip itself.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:  # pragma: no cover - a broken file fails elsewhere
        return []

    found: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Call, ast.Attribute)):
            continue
        text = ast.unparse(node)
        if re.search(r"\bskipif\b|\bpytest\.skip\b", text):
            found.append(text)
    return found


@pytest.mark.parametrize("path", _test_files(), ids=lambda p: p.name)
def test_no_skip_is_gated_on_a_retired_dependency(path: Path):
    if path.name in PERMITTED:
        pytest.skip(f"{path.name} is permitted to reference a retired tool")

    offenders = []
    for src in _skip_sources(path):
        low = src.lower()
        for token in RETIRED:
            if token in low:
                offenders.append(f"{token!r} in: {src[:160]}")

    assert not offenders, (
        f"{path.name} gates a skip on a RETIRED dependency:\n  "
        + "\n  ".join(offenders)
        + "\n\nF78 removed PowerShell from this repository. A skip gated on it "
          "never fires where CI runs, so the test silently does not run at "
          "all. If the dependency is genuinely still needed, add the file to "
          "PERMITTED with the reason.")


def test_the_permitted_list_does_not_rot():
    """Every PERMITTED entry must still exist and still reference a retired
    token. An entry for a file that no longer needs one is an exemption
    nobody is checking."""
    for name in sorted(PERMITTED):
        p = SRC / name
        assert p.exists(), f"PERMITTED names {name}, which does not exist"
        low = p.read_text(encoding="utf-8").lower()
        assert any(t in low for t in RETIRED), (
            f"{name} is PERMITTED to reference a retired dependency but no "
            "longer does; remove it from the list")


def test_the_cross_repo_guard_is_not_skipped_anywhere():
    """The specific regression. This guard enforces the team-lead's
    cross-repository boundary and must run on every platform."""
    p = SRC / "test_cross_repo_write_guard.py"
    if not p.exists():
        pytest.skip("cross-repo guard test absent")
    for src in _skip_sources(p):
        assert "skipif" not in src.lower(), (
            "test_cross_repo_write_guard.py has a skipif again; this guard "
            "must run on every platform, including CI")
