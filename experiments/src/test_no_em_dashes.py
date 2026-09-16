"""Formal documents contain no em dashes.

`docs/QUALITY_STANDARDS.md` line 19 states the rule plainly: "No contractions in
formal docs; no emoji; bracketed markers ([OK], [FAIL], [WARNING]) where a status
glyph is needed; no em dashes."

The rule held for ADRs 0008 through 0013, which contain zero between them. Then
ADR-0014 introduced eight and ADR-0015 six, because the rule lived only in a
standards document that nobody reads while writing.

Found by Copilot on PR #94, not by us. That is the whole argument for this file:
a documented rule with no mechanism behind it is a rule that decays the moment
attention moves elsewhere, and this project has replaced several such rules with
tests for exactly that reason.

SCOPE. Formal documents only: ADRs, the standards themselves, the sprint process
docs, and the submitted papers. Deliberately NOT the whole repository --
CHANGELOG entries quote external material, sprint retrospectives record the team
lead's words verbatim, and rewriting a quotation to satisfy a house style would
be worse than the style violation.

Verified by injection: adding a single em dash to any covered file fails this
test naming the file and a line number; removing it passes.
"""
from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
EM_DASH = chr(8212)

# Directories whose markdown is "formal" in the sense QUALITY_STANDARDS means.
COVERED_DIRS = (
    ROOT / "docs" / "adr",
    ROOT / "docs" / "paper",
)

# Individual formal documents outside those directories.
COVERED_FILES = (
    ROOT / "docs" / "QUALITY_STANDARDS.md",
    ROOT / "docs" / "SPRINT_EXECUTION_WORKFLOW.md",
    ROOT / "docs" / "SPRINT_PROCESS.md",
    ROOT / "docs" / "SPRINT_PLANNING.md",
    # CLAUDE.md STATES the no-em-dash rule and was not itself checked for it
    # until 2026-09-15. A rule document exempt from its own rule is the same
    # shape as a guard that cannot fail.
    ROOT / "CLAUDE.md",
    ROOT / "README.md",
)


def _covered() -> list[Path]:
    files: list[Path] = []
    for d in COVERED_DIRS:
        if d.exists():
            files.extend(sorted(d.glob("*.md")))
    files.extend(f for f in COVERED_FILES if f.exists())
    return files


@pytest.mark.parametrize("path", _covered(), ids=lambda p: p.name)
def test_formal_documents_contain_no_em_dashes(path: Path):
    """QUALITY_STANDARDS line 19. One offender fails with its line number."""
    offenders: list[str] = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if EM_DASH in line:
            offenders.append(f"line {i}: {line.strip()[:90]}")
    assert not offenders, (
        f"{path.name} contains em dashes, which docs/QUALITY_STANDARDS.md line 19 "
        f"prohibits in formal documents: {offenders[:5]}"
        f"{' ...and more' if len(offenders) > 5 else ''}. "
        f"Use ' -- ' instead. ADRs 0008 to 0013 hold zero between them; 0014 and "
        f"0015 introduced fourteen before Copilot caught it on PR #94.")
