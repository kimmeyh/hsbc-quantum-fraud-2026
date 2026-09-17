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

Scope note: the CURRENT sprint is exempt from BOTH the summary and the
retrospective, because 3.2.1 binds every "completed sprint" and the one in
flight has neither yet -- the retrospective lands at Phase 7, the summary during
N+1 planning. Only the plan is owed while a sprint is live.

That exemption was too narrow when first written (summary only), and this guard
fired against Sprint 13's own plan document the moment it was created. Fixed and
verified by injection: with the current sprint set to 13, removing COMPLETED
Sprint 11's retrospective still fails with
`assert not ['SPRINT_11_RETROSPECTIVE.md']`, and restoring it passes. The
exemption covers the live sprint only, not the rule.
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
            # 3.2.1 binds every COMPLETED sprint. The sprint in flight has a
            # plan and owes the other two at its own close-out: the
            # retrospective at Phase 7, the summary during N+1 planning.
            # Demanding either mid-sprint fails the moment a plan is written,
            # which is how this guard first fired against Sprint 13's own plan.
            if n == current and kind in ("SUMMARY", "RETROSPECTIVE"):
                continue
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


# ---------------------------------------------------------------------------
# Close-out gate (F79, Sprint 16). The exemption above is correct at PLAN time
# and wrong at MERGE time, and nothing revoked it.
# ---------------------------------------------------------------------------

CLOSEOUT_STATUSES = {
    "phase_7_retrospective",
    "phase_8_delivery_cycle",
    "complete",
    "closed",
}


def _sprint_is_evidently_complete(n: int) -> tuple[bool, str]:
    """Is sprint n finished, judged on EVIDENCE rather than on a status field?

    IMP-1, Sprint 15 retrospective. The exemption above follows
    `sprint_status.json`, which is mutable and is rolled by hand. Writing the
    Sprint 16 plan BEFORE rolling that field made Sprint 16 look completed: the
    guard demanded documents that cannot exist yet, while the real gap --
    Sprint 15's missing retrospective -- stayed hidden behind the stale
    exemption. The field was wrong in both directions at once.

    A sprint is complete when a LATER sprint has a plan. That is the one signal
    nobody can forget to update, because the next sprint cannot start without
    it. A sprint whose successor is planned is over, whatever any field says.
    """
    later = [m for m in _sprint_numbers() if m > n]
    if later:
        return True, f"sprint {min(later)} already has a plan"
    return False, "no later sprint is planned"


@pytest.mark.skipif(not SPRINTS.exists(), reason="no sprint docs directory")
def test_a_superseded_sprint_has_its_retrospective():
    """A sprint whose successor is planned owes its retrospective NOW.

    THE FAILURE THIS EXISTS FOR. Sprint 15 merged to develop and then to main
    with no retrospective. Phase 7 is an exit gate in the workflow and the
    three-doc rule is stated "no exceptions", and neither stopped it, because
    the guard above exempts the live sprint and nothing revoked that exemption
    at merge.

    This assertion is deliberately SEPARATE from the one above rather than a
    change to it. The exemption is correct while a sprint is live: an earlier
    version of that guard fired against Sprint 13's own plan the moment it was
    written, which is exactly the false positive that trains people to delete a
    test.

    So: silent at plan time, loud once the next sprint is planned.
    """
    missing = []
    for n in _sprint_numbers():
        complete, why = _sprint_is_evidently_complete(n)
        if not complete:
            continue
        f = SPRINTS / f"SPRINT_{n}_RETROSPECTIVE.md"
        if not f.exists():
            missing.append(f"{f.name} ({why})")

    assert not missing, (
        "a sprint that has been superseded still owes its retrospective: "
        f"{missing}. Phase 7 is an exit gate; a sprint does not close without "
        "it. Write the retrospective rather than deleting this test -- Sprint "
        "15 merged to develop AND to main without one, which is what this "
        "guard exists to prevent.")


@pytest.mark.skipif(not STATUS.exists(), reason="no sprint_status.json")
def test_the_live_sprint_is_not_asked_for_documents_it_cannot_have():
    """The other half of the acceptance, and it has to be asserted.

    A gate that fires at plan time is worse than no gate, because it blocks
    correct work and trains bypass. The live sprint owes a plan and nothing
    else, and this test fails if that ever stops being true.
    """
    st = json.loads(STATUS.read_text(encoding="utf-8"))["current_sprint"]
    n = int(st["number"])
    complete, _ = _sprint_is_evidently_complete(n)
    assert not complete, (
        f"sprint {n} is named as current but a later sprint already has a "
        "plan. Roll sprint_status.json: the live sprint must be the newest "
        "one, or the exemption protects the wrong sprint.")
