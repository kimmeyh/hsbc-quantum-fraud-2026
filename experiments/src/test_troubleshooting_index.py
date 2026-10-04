"""Every pointer in the troubleshooting index must resolve.

IMP-2, Sprint 20. `docs/TROUBLESHOOTING.md` is a symptom index: each entry is
a symptom, a cause, and a pointer to where the authoritative answer lives. It
deliberately does NOT restate what another file owns, because restating a
number another file owns is the defect CLAUDE.md bans.

That design makes the pointers load-bearing. An index whose targets have moved
is worse than no index: it sends the reader somewhere, confidently, and wastes
the very lookup the document exists to save. A renamed or deleted file is
exactly the drift that happens between sprints -- Sprint 20 itself saw
`CHECKLIST-Phase2-pre.md` deleted mid-sprint by another session.

So this guard is cheap and mechanical, and it is the only thing standing
between a stale pointer and a reader who trusts it.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs" / "TROUBLESHOOTING.md"

# A backtick-quoted thing that looks like a file in this repository.
FILE_REF = re.compile(r"`([A-Za-z0-9_./\\-]+\.(?:md|py|json))`")

# Where a bare filename might legitimately live.
# docs/sprints was missing, so a legitimate pointer there read as broken.
# And a pointer containing ".." resolved outside the repository entirely.
# Both make the guard inaccurate rather than silent. Found by a PR #146
# review agent.
SEARCH_ROOTS = (".", "docs", "docs/sprints", "experiments/src", "scripts",
                ".claude/hooks")


def _resolve(ref: str) -> bool:
    """Does this pointer name a real file INSIDE the repository?

    A pointer containing ".." used to resolve, escaping the repository -- so
    `../README.md` passed. A pointer that only works from one directory is not
    a pointer a reader can follow.
    """
    if ".." in Path(ref).parts:
        return False
    for root in SEARCH_ROOTS:
        candidate = (ROOT / root / ref).resolve()
        try:
            candidate.relative_to(ROOT.resolve())
        except ValueError:
            continue
        if candidate.exists():
            return True
    return False


def test_the_index_exists():
    assert DOC.exists(), (
        "docs/TROUBLESHOOTING.md is missing. SPRINT_RETROSPECTIVE.md category "
        "9 points at it, and the capability pre-flight in SPRINT_PLANNING.md "
        "names it as the first thing to read.")


def test_every_pointer_resolves():
    """The pointers are the whole value. A stale one is worse than none."""
    text = DOC.read_text(encoding="utf-8")
    refs = sorted(set(FILE_REF.findall(text)))
    assert refs, "the index contains no file pointers at all"

    missing = [r for r in refs if not _resolve(r)]
    assert not missing, (
        f"these pointers in docs/TROUBLESHOOTING.md do not resolve: "
        f"{missing}. An index that sends the reader to a file that has moved "
        "wastes the lookup it exists to save. Update the pointer or remove "
        "the entry.")


def test_the_index_does_not_restate_what_it_points_at():
    """It is an index, not a second copy.

    The failure mode this prevents is the document growing into a parallel
    source of truth that drifts from the files it points at -- which is how a
    number restated in two places goes wrong, and CLAUDE.md bans it.

    A heuristic: an index entry is a few lines. A section running past ~45
    lines has stopped pointing and started explaining, and whatever it is
    explaining should live in the file that owns it.
    """
    text = DOC.read_text(encoding="utf-8")
    sections = re.split(r"^## ", text, flags=re.M)[1:]
    bloated = []
    for s in sections:
        title = s.splitlines()[0].strip()
        n = len([ln for ln in s.splitlines() if ln.strip()])
        # 80, not 45. The old threshold sat six lines above the largest
        # section, so it was a tripwire that would fire on the next ordinary
        # edit -- and a guard that fails on correct work gets deleted. It
        # measures LENGTH, which is a proxy for restatement rather than a
        # detector of it, so it earns a wide margin.
        if n > 80:
            bloated.append(f"{title} ({n} lines)")
    assert not bloated, (
        f"these sections have grown past pointing into explaining: {bloated}. "
        "Move the explanation into the file that owns the subject and leave a "
        "pointer. This document is an index.")


def test_the_retrospective_template_points_here():
    """Category 9 asked for a troubleshooting note from Sprint 2 and nothing
    existed, so nine retrospectives' findings had nowhere to go. The template
    must name the document now that it exists, or the same gap reopens."""
    # ASSERT, do not skip. This file is TRACKED, so its absence means it was
    # DELETED -- a defect, not an unavailable fixture. This module's own
    # docstring cites a tracked checklist deleted mid-sprint by another
    # session, which is exactly the drift it was written for. Found by a
    # PR #146 review agent.
    tmpl = ROOT / "docs" / "SPRINT_RETROSPECTIVE.md"
    assert tmpl.exists(), (
        "docs/SPRINT_RETROSPECTIVE.md is missing. It is tracked, so this is a "
        "deletion rather than a reason to skip.")
    assert "TROUBLESHOOTING.md" in tmpl.read_text(encoding="utf-8"), (
        "the retrospective template no longer points at "
        "docs/TROUBLESHOOTING.md, so category-9 findings have nowhere to land "
        "again")


def test_the_preflight_rule_points_here():
    """IMP-2's whole mechanism is that the pre-flight names this document as
    the first thing to read. Without that reference the index is optional,
    and an optional lookup is the one that does not happen."""
    # Same reasoning as above: tracked, so absence is a deletion.
    planning = ROOT / "docs" / "SPRINT_PLANNING.md"
    assert planning.exists(), (
        "docs/SPRINT_PLANNING.md is missing. It is tracked, so this is a "
        "deletion rather than a reason to skip.")
    text = planning.read_text(encoding="utf-8")
    assert "TROUBLESHOOTING.md" in text, (
        "the capability pre-flight no longer names docs/TROUBLESHOOTING.md")
    for pattern in ("HARDWARE_REQUEST_", "_RECONCILIATION.md", "RESULTS_MEMO"):
        assert pattern in text, (
            f"the pre-flight no longer names {pattern}, one of the four "
            "patterns IMP-2 specified instead of a directory sweep")
