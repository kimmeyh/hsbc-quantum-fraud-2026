"""Phase 3's artifacts must exist once work has started (Sprint 17 defect).

SPRINT_CHECKLIST.md Phase 3 requires, before the first task file is touched:
a DRAFT PR (which stays draft until 7.7), one GitHub issue per task, and the
team lead's approval recorded.

NONE of the three happened in Sprint 17. The sprint ran through nine tasks,
Manual Validation and a retrospective with `pr: null`, `github_issues: []` and
`plan_approved: false`, and I repeatedly told the team lead "no PR opened,
that's your call" -- which was wrong. Opening the draft PR is Claude's job at
Phase 3; only the MERGE is the team lead's.

WHY THE EXISTING GUARD MISSED IT. verify_closeout_complete.py checked
`plan_approved is True and pr is None`. It read one stale field to decide
whether to distrust another, so a second stale field disabled it entirely --
exactly the failure its own docstring records from Sprint 16.

The fix anchors on something that cannot be stale: commits exist on the branch.
If work has happened, Phase 3's artifacts were due before it started.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / ".claude" / "hooks" / "verify_closeout_complete.py"
STATUS = ROOT / ".claude" / "sprint_status.json"

# The hook only fires on a close-out CLAIM; an empty payload exits early. The
# first proof of this fix sent "{}" and reported every case as allowed, which
# is a vacuous injection rather than a broken hook.
CLOSEOUT_CLAIM = json.dumps(
    {"last_assistant_message": "The sprint close-out is complete."})


def _run_hook() -> tuple[int, str]:
    r = subprocess.run([sys.executable, str(HOOK)], input=CLOSEOUT_CLAIM,
                       capture_output=True, text=True, cwd=str(ROOT))
    return r.returncode, r.stderr


def _status() -> dict:
    if not STATUS.exists():
        pytest.skip("sprint_status.json not present")
    return json.loads(STATUS.read_text(encoding="utf-8"))


def test_the_hook_checks_all_three_phase_3_artifacts():
    """Source-level: the checks exist and are not gated on each other."""
    src = HOOK.read_text(encoding="utf-8")
    assert "current_sprint.pr is null" in src
    assert "github_issues is empty" in src
    assert "plan_approved is not true" in src
    assert 'cur.get("plan_approved") is True and cur.get("pr") is None' not in src, (
        "the checks are gated on each other again; a second stale field "
        "disables them, which is how Sprint 17 shipped with none of the three")


def test_current_sprint_records_its_draft_pr():
    cur = _status().get("current_sprint", {})
    assert cur.get("pr") is not None, (
        "current_sprint.pr is null. Phase 3 requires a DRAFT PR created before "
        "the first task file is touched.")


def test_current_sprint_records_its_task_issues():
    cur = _status().get("current_sprint", {})
    assert cur.get("github_issues"), (
        "current_sprint.github_issues is empty. Phase 3 requires one issue "
        "per task BEFORE the first task file is touched.")


def test_plan_approval_is_recorded():
    cur = _status().get("current_sprint", {})
    assert cur.get("plan_approved") is True, (
        "plan_approved is not true. Either the plan was not approved, or the "
        "approval was never recorded -- and the second is how the PR and "
        "issue checks were silently skipped in Sprint 17.")


@pytest.mark.parametrize("field,broken", [
    ("pr", None),
    ("github_issues", []),
    ("plan_approved", False),
])
def test_the_hook_blocks_when_a_phase_3_artifact_is_missing(field, broken,
                                                            tmp_path):
    """Each omission must BLOCK a close-out claim, independently.

    Mutates the real status file and restores it, because the hook reads that
    path directly. The assertion that the mutation reached disk is the part
    that five Sprint 17 injections skipped.
    """
    orig = STATUS.read_text(encoding="utf-8")
    doc = json.loads(orig)
    doc["current_sprint"][field] = broken
    STATUS.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    try:
        on_disk = json.loads(STATUS.read_text(encoding="utf-8"))
        assert on_disk["current_sprint"][field] == broken, "mutation not on disk"
        rc, err = _run_hook()
        assert rc != 0, f"a missing {field} did not block the close-out claim"
        assert "Phase 3" in err
    finally:
        STATUS.write_text(orig, encoding="utf-8")
        assert STATUS.read_text(encoding="utf-8") == orig


def test_an_unresolvable_base_ref_does_not_disable_the_checks(tmp_path):
    """The Phase 3 checks must fire even where `develop` is not a local ref.

    `git rev-list --count develop..HEAD` exits 128 with EMPTY STDOUT when
    develop does not resolve, and hooklib.git swallows stderr. The first
    version read that as "no commits" and skipped all three checks -- which
    reproduces the exact Sprint 17 defect the checks exist to catch, in every
    environment that lacks a local develop: an actions/checkout@v4 clone
    (fetches only the PR ref), a --single-branch clone, a worktree, or a
    pruned branch.

    Found by the PR #122 code review.
    """
    repo = tmp_path / "clone"
    repo.mkdir()

    def git(*args: str):
        return subprocess.run(["git", *args], cwd=str(repo),
                              capture_output=True, text=True)

    git("init", "-b", "feature/20260919_Sprint_17")
    git("config", "user.email", "t@example.com")
    git("config", "user.name", "t")
    (repo / "f.txt").write_text("work happened\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-m", "a commit exists on this branch")

    # No develop branch here, which is the whole point.
    assert git("rev-parse", "--verify", "develop").returncode != 0

    claude = repo / ".claude"
    claude.mkdir()
    (claude / "sprint_status.json").write_text(json.dumps({
        "current_sprint": {"number": 17, "pr": None, "github_issues": [],
                           "plan_approved": False},
    }), encoding="utf-8")

    payload = json.dumps({
        "last_assistant_message": "The sprint close-out is complete.",
        "repo_override": str(repo),
        "branch_override": "feature/20260919_Sprint_17",
    })
    r = subprocess.run([sys.executable, str(HOOK)], input=payload,
                       capture_output=True, text=True, cwd=str(ROOT))

    assert r.returncode != 0, (
        "the hook allowed a close-out claim with pr null, no issues and no "
        "recorded approval, because the base ref did not resolve")
    assert "Phase 3" in r.stderr
