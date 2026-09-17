"""The turn-end guard fires on a promise and stays silent on a real handover.

Team lead, 2026-09-17, after the third occurrence: "Do not end turns until you
are ready for Manual Validation (that is the only thing that ends turns). Update
everything necessary to ensure this is how it handles sprint execution after
sprint plan approval."

The rule itself is fifteen sprints old (workflow invariant 1). What was missing
was a check at the moment of the violation. Three of the BLOCK cases below are
the exact closing sentences from the three real failures.

The ALLOW cases matter as much: a Stop hook that blocks a legitimate handover
wedges the session at the one moment the team lead is waiting.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / ".claude" / "hooks" / "sprint_auto_advance.py"

ALLOW, BLOCK = 0, 2
EXEC = "phase_4_execution"
OTHER = "phase_7_retrospective"

CASES = [
    # --- the three real failures, verbatim --------------------------------
    ("Sprint 15 Task C, verbatim", BLOCK, EXEC,
     "Seven of eight issues are closed.\n\nContinuing with Task C."),
    ("Sprint 16 Task B, verbatim", BLOCK, EXEC,
     "Task A is committed and pushed. Continuing to Task B, extending "
     "verify-closeout-complete to check the current sprint's retrospective."),
    ("Sprint 16 Task E, verbatim", BLOCK, EXEC,
     "578 tests green. Continuing with the Task E conversions."),

    # --- other shapes of the same promise ---------------------------------
    ("I will start next", BLOCK, EXEC, "Done. I will start Task F now."),
    ("next I'll", BLOCK, EXEC, "Committed. Next, I'll convert the scripts."),
    ("moving on to", BLOCK, EXEC, "All green. Moving on to Task G."),
    ("on to task", BLOCK, EXEC, "Task D complete. On to Task E."),
    ("proceeding with", BLOCK, EXEC, "Pushed. Proceeding with the conversion."),

    # --- legitimate turn endings ------------------------------------------
    ("manual validation handover", ALLOW, EXEC,
     "All tasks complete. Here are the recommended Manual Validation steps:\n"
     "1. Read the document\n2. Check the disclaimer"),
    ("metered run awaiting approval", ALLOW, EXEC,
     "The next block is a metered Dirac-3 run: 12 fits, about 60 device "
     "seconds. Criterion H applies, so this needs explicit approval."),
    ("named stopping criterion", ALLOW, EXEC,
     "Stopping here: this meets the stopping criteria in "
     "SPRINT_STOPPING_CRITERIA.md, specifically a decision-class item."),
    ("genuine blocker", ALLOW, EXEC,
     "I am blocked: the dataset is not present and cannot be regenerated "
     "without the team lead's Kaggle credentials."),
    ("needs your decision", ALLOW, EXEC,
     "Two options and they differ materially. This needs your decision "
     "before I pick one."),

    # --- outside the window the hook must not fire ------------------------
    ("promise during retrospective phase", ALLOW, OTHER,
     "Continuing with Task E."),
    # NOTE: this one is covered by its own test below, because it varies
    # plan_approved rather than the phase string. Leaving it here with
    # plan_approved=True asserted the opposite of its own name.

    # --- descriptions of completed work are not promises ------------------
    ("past tense is fine", ALLOW, EXEC,
     "I continued with Task C and converted all four hooks. 77 tests pass."),
    ("empty message", ALLOW, EXEC, ""),
]


def _run(status: str, message: str, tmp_path: Path, active: bool = False,
         approved: bool = True) -> int:
    """Run the hook against a fake sprint_status by pointing the repo root at a copy."""
    fake = tmp_path / "repo"
    (fake / ".claude").mkdir(parents=True, exist_ok=True)
    (fake / ".git").mkdir(exist_ok=True)
    (fake / "docs" / "sprints").mkdir(parents=True, exist_ok=True)
    (fake / "docs" / "sprints" / "SPRINT_16_PLAN.md").write_text("plan", encoding="utf-8")
    (fake / ".claude" / "sprint_status.json").write_text(
        json.dumps({"current_sprint": {"number": 16, "status": status,
                                       "plan_approved": approved}}),
        encoding="utf-8")

    payload = {"last_assistant_message": message, "stop_hook_active": active,
               "cwd": str(fake),
               # branch_override is the source hook's test seam: without it the
               # branch gate needs a real git repo, every BLOCK case exits 0 at
               # Gate 1, and the suite goes green while testing nothing.
               "branch_override": "feature/20260916_Sprint_16"}
    pf = tmp_path / "payload.json"
    pf.write_text(json.dumps(payload), encoding="utf-8")

    env = {**dict(__import__("os").environ), "CLAUDE_PROJECT_DIR": str(fake)}
    with pf.open("rb") as stdin:
        return subprocess.run([sys.executable, str(HOOK)], stdin=stdin,
                              capture_output=True, env=env).returncode


def test_the_hook_exists():
    assert HOOK.exists(), "the turn-end guard is missing"


@pytest.mark.parametrize("name,expected,status,message", CASES,
                         ids=[c[0] for c in CASES])
def test_turn_end_guard(name, expected, status, message, tmp_path):
    rc = _run(status, message, tmp_path)
    verb = "BLOCK" if expected == BLOCK else "ALLOW"
    assert rc == expected, f"expected {verb} ({expected}) for {name!r}, got {rc}"


def test_never_reblocks_an_active_stop(tmp_path):
    """Re-blocking an already-blocked stop would wedge the session."""
    rc = _run(EXEC, "Continuing with Task E.", tmp_path, active=True)
    assert rc == ALLOW, "stop_hook_active must suppress the block"


def test_fails_open_when_status_is_unreadable(tmp_path):
    """A Stop hook that errors ends every turn with a spurious block."""
    fake = tmp_path / "repo"
    (fake / ".claude").mkdir(parents=True)
    (fake / ".git").mkdir()
    (fake / "docs" / "sprints").mkdir(parents=True)
    (fake / "docs" / "sprints" / "SPRINT_16_PLAN.md").write_text("plan", encoding="utf-8")
    (fake / ".claude" / "sprint_status.json").write_text("{ not json",
                                                         encoding="utf-8")
    pf = tmp_path / "p.json"
    pf.write_text(json.dumps({"last_assistant_message": "Continuing with Task E.",
                              "cwd": str(fake),
                              "branch_override": "feature/20260916_Sprint_16"}),
                  encoding="utf-8")
    env = {**dict(__import__("os").environ), "CLAUDE_PROJECT_DIR": str(fake)}
    with pf.open("rb") as stdin:
        rc = subprocess.run([sys.executable, str(HOOK)], stdin=stdin,
                            capture_output=True, env=env).returncode
    assert rc == ALLOW


def test_silent_before_plan_approval(tmp_path):
    """Gate 1b2: before approval, asking and announcing are both correct.

    This case was in the parametrized list and PASSED for the wrong reason: the
    helper hardcoded plan_approved=True, so a case named "before approval" was
    testing an approved sprint. It only surfaced once the hook started working.
    """
    rc = _run(EXEC, "Continuing to Task B.", tmp_path, approved=False)
    assert rc == ALLOW, "before approval the hook must not fire"
