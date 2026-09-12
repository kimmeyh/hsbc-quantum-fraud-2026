"""Every completed sprint keeps its three documents.

SPRINT_EXECUTION_WORKFLOW.md 3.2.1 states the three-doc rule "no exceptions":
every completed sprint has SPRINT_N_PLAN.md, SPRINT_N_RETROSPECTIVE.md and
SPRINT_N_SUMMARY.md. Until Sprint 12 nothing enforced it, so a missing document
was invisible -- and Sprint 12's summary was in fact missing until the
retrospective went looking.

The rule is worth enforcing because the summary is the only document written
AFTER a sprint's consequences are known. A plan records intent and a
retrospective records process; the summary is where the sprint says what it
actually established, and it is the one a later reader reaches for first.

Scope note: the CURRENT sprint is exempt from the summary requirement, because
3.2.1 has it created during Sprint N+1 planning. Only completed sprints are
checked.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SPRINTS = ROOT / "docs" / "sprints"
STATUS = ROOT / ".claude" / "sprint_status.json"


def _current_sprint() -> int | None:
    """The sprint still in flight, which owes no summary yet."""
    if not STATUS.exists():
        return None
    try:
        return int(json.loads(STATUS.read_text(encoding="utf-8"))
                   ["current_sprint"]["number"])
    except Exception:                                   # noqa: BLE001
        return None


def _sprint_numbers() -> list[int]:
    seen = set()
    for f in SPRINTS.glob("SPRINT_*_PLAN.md"):
        m = re.match(r"SPRINT_(\d+)_PLAN\.md", f.name)
        if m:
            seen.add(int(m.group(1)))
    return sorted(seen)


@pytest.mark.skipif(not SPRINTS.exists(), reason="no sprint docs directory")
def test_every_completed_sprint_has_all_three_documents():
    """Plan, retrospective and summary, for every sprint that has finished."""
    current = _current_sprint()
    missing: list[str] = []
    for n in _sprint_numbers():
        for kind in ("PLAN", "RETROSPECTIVE", "SUMMARY"):
            if kind == "SUMMARY" and n == current:
                continue                                 # written in N+1 planning
            f = SPRINTS / f"SPRINT_{n}_{kind}.md"
            if not f.exists():
                missing.append(f.name)
    assert not missing, (
        f"the three-doc rule (workflow 3.2.1, 'no exceptions') is unmet: "
        f"{missing}. A sprint's summary is the only document written after its "
        f"consequences are known; write it rather than deleting this test.")


@pytest.mark.skipif(not SPRINTS.exists(), reason="no sprint docs directory")
def test_sprint_documents_are_not_placeholders():
    """A file that exists but says nothing satisfies the letter and not the rule.

    The retrospective template ships with `[feedback]` placeholders, and its own
    exit gate requires all 16 categories filled by all 4 roles. A retrospective
    still holding placeholders has not been conducted.
    """
    thin: list[str] = []
    for f in sorted(SPRINTS.glob("SPRINT_*.md")):
        body = f.read_text(encoding="utf-8")
        if len(body.strip()) < 400:
            thin.append(f"{f.name} (only {len(body.strip())} chars)")
        if "[feedback]" in body:
            thin.append(f"{f.name} (unfilled [feedback] placeholder)")
    assert not thin, f"sprint documents present but not written: {thin}"


@pytest.mark.skipif(not STATUS.exists(), reason="no sprint_status.json")
def test_sprint_status_points_at_a_real_sprint():
    """The status file is how tooling knows which sprint is live.

    Sprint 12 ran with this file reading `phase_4_execution` and `pr: null`
    against a sprint that had already merged two PRs, and an automated reviewer
    read the stale value and called the work "Sprint 13's". A status file nobody
    updates is worse than none, because it is quoted.
    """
    st = json.loads(STATUS.read_text(encoding="utf-8"))["current_sprint"]
    n = int(st["number"])
    assert (SPRINTS / f"SPRINT_{n}_PLAN.md").exists(), (
        f"sprint_status.json names sprint {n}, which has no plan document")
    plan = st.get("plan_doc")
    if plan:
        assert (ROOT / plan).exists(), f"plan_doc {plan} does not exist"
