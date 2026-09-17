"""The venv interpreter is written down in ONE place.

F78 Task H, Sprint 16, with IMP-4 from the Sprint 15 retrospective.

The interpreter path was spelled out in 21 places across 16 files, and it is not
discoverable from the environment: a bare `python` on the development machine is
a different interpreter from the project's. I got it wrong myself in Sprint 15,
reported nine test modules as failing for a missing `sklearn`, and the
dependency was installed all along. The wrong interpreter produces a plausible
wrong answer rather than an error.

`docs/ENVIRONMENT.md` is now the single place both the Windows and the Linux
interpreter are written down.

WHAT THIS TEST ALLOWS, deliberately, because a rule that forbids the string
outright would be wrong:

  - `docs/ENVIRONMENT.md` itself, which has to state the paths
  - `docs/WINDOWS_POWERSHELL_GUIDE.md`, which is explicitly the Windows document
    and correctly gives Windows paths; it cross-references ENVIRONMENT.md for
    the Linux ones
  - prose DESCRIBING the problem (the sprint plan, the CHANGELOG entry, a
    converted script's docstring explaining what it removed)
  - the retired .ps1 files, which are not the live implementation

What it forbids is a new INSTRUCTION telling a reader to run that path, in a
file that is not one of the above.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

INTERPRETER = re.compile(r"\.venv[\\/]{1,2}Scripts[\\/]{1,2}python")

# Files permitted to contain the literal path, each for a stated reason.
ALLOWED = {
    "docs/ENVIRONMENT.md": "the single source of truth; it must state the paths",
    "docs/WINDOWS_POWERSHELL_GUIDE.md": "the Windows-specific guide",
    # ALL_SPRINTS_MASTER_PLAN.md had an allowance until the F78 card was
    # pruned at close-out. The test below caught the dead permission, which
    # is what it is for: an allowance for a file that no longer needs one
    # makes the list read as larger than it is.
    "docs/sprints/SPRINT_16_PLAN.md": "the plan describes the problem",
    "CHANGELOG.md": "the entry describes the problem",
    "scripts/render_pdf.py": "docstring explains the path it removed",
    "scripts/render-pdf.ps1": "retired, not the live implementation",
    "scripts/render-all.ps1": "retired, not the live implementation",
}


def _tracked() -> list[str]:
    r = subprocess.run(["git", "ls-files"], cwd=ROOT,
                       capture_output=True, text=True, timeout=30)
    return r.stdout.splitlines() if r.returncode == 0 else []


FILES = _tracked()


def test_the_environment_doc_exists():
    doc = ROOT / "docs" / "ENVIRONMENT.md"
    assert doc.exists(), "docs/ENVIRONMENT.md is the single source of truth"
    text = doc.read_text(encoding="utf-8")
    # It must give BOTH, or it is a Windows document wearing another name.
    assert "Scripts" in text and "bin/python" in text, (
        "ENVIRONMENT.md must give the Windows AND the Linux interpreter")


def test_the_file_list_is_not_empty():
    assert len(FILES) > 50, f"only {len(FILES)} tracked files; guard would be vacuous"


def test_no_new_hardcoded_interpreter_paths():
    offenders = []
    for rel in FILES:
        if rel in ALLOWED:
            continue
        p = ROOT / rel
        if not p.is_file() or p.suffix.lower() not in {
                ".md", ".py", ".ps1", ".yml", ".yaml", ".txt", ".json"}:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            if INTERPRETER.search(line):
                offenders.append(f"  {rel}:{lineno}  {line.strip()[:90]}")

    assert not offenders, (
        "hardcoded venv interpreter paths outside the permitted files:\n"
        + "\n".join(offenders)
        + "\n\nReference docs/ENVIRONMENT.md instead. The interpreter differs "
          "per OS and is not discoverable from the environment; a bare `python` "
          "is usually the wrong one and fails like a broken checkout.")


@pytest.mark.parametrize("rel,reason", sorted(ALLOWED.items()))
def test_every_allowance_is_still_used(rel, reason):
    """An allowance for a file that no longer needs it is dead permission.

    If a file stops containing the path, its entry should go, or the next
    person reads the list as larger than it is.
    """
    p = ROOT / rel
    if not p.exists():
        pytest.skip(f"{rel} no longer exists")
    text = p.read_text(encoding="utf-8")
    assert INTERPRETER.search(text), (
        f"{rel} is allowed to contain the interpreter path ({reason}) but no "
        "longer does. Remove its entry from ALLOWED.")
