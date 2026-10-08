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
import re
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
# branch_override IS REQUIRED, not optional. Without it the hook falls back to
# `git branch --show-current`, which returns EMPTY on a detached HEAD -- and
# actions/checkout leaves CI detached. The hook's first gate is "sprint feature
# branch only", so it returned ALLOW before reaching any artifact check, and
# every test here asserting a block failed on Linux while passing on Windows.
#
# The branch name must match SPRINT_BRANCH and carry the sprint number in
# sprint_status.json, or the hook exits on the stale-state path instead.
# Mirrors SPRINT_BRANCH in .claude/hooks/verify_closeout_complete.py. A copy,
# so a drift in either is visible: the test below asserts the pinned branch
# still satisfies it.
SPRINT_BRANCH_IN_HOOK = re.compile(r"^feature/\d+_Sprint_(\d+)")


def _claim() -> str:
    number = json.loads(STATUS.read_text(encoding="utf-8"))[
        "current_sprint"]["number"]
    return json.dumps({
        "last_assistant_message": "The sprint close-out is complete.",
        "branch_override": f"feature/20260922_Sprint_{number}",
    })


def _status() -> dict:
    if not STATUS.exists():
        pytest.skip("sprint_status.json not present")
    return json.loads(STATUS.read_text(encoding="utf-8"))


# Ordered, so "has this sprint reached Phase 3?" is a comparison rather than a
# set membership test that a new slug would silently fall out of.
PHASE_ORDER = (
    "phase_1_backlog_refinement",
    "phase_2_pre_kickoff",
    "phase_3_planning",
    "phase_4_execution",
    "phase_5_validation",
    "phase_5_3_manual_validation",
    "phase_6_push",
    "phase_7_retrospective",
    "phase_8_delivery_cycle",
    "complete",
    "closed",
)


def _reached_phase_3() -> bool:
    """Has this sprint reached the phase that CREATES the Phase 3 artifacts?

    THE DEFECT THIS EXISTS FOR. The three artifact tests below asserted that a
    draft PR, task issues and a recorded approval exist -- unconditionally.
    In a Phase 1 or Phase 2 planning window none of them exists yet, because
    the plan being written is what creates them, so all three failed on
    correct behavior. Measured 2026-10-02: six tests red in a planning window,
    all green the moment Phase 3 completed, with no code change.

    A suite that is expected to be red for days at a time is a suite nobody
    reads, and this repository has already paid for CI red on every commit of
    a sprint.

    An UNKNOWN phase returns True, deliberately: a slug this list does not
    know must not silently disable the checks. That is the failure mode these
    tests exist to catch, and it is how Sprint 17 shipped with none of the
    three artifacts recorded.
    """
    status = str(_status().get("current_sprint", {}).get("status") or "")
    if status not in PHASE_ORDER:
        return True
    return PHASE_ORDER.index(status) >= PHASE_ORDER.index("phase_3_planning")


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
    if not _reached_phase_3():
        pytest.skip("sprint has not reached Phase 3; the PR does not exist yet")
    cur = _status().get("current_sprint", {})
    assert cur.get("pr") is not None, (
        "current_sprint.pr is null. Phase 3 requires a DRAFT PR created before "
        "the first task file is touched.")


def test_current_sprint_records_its_task_issues():
    if not _reached_phase_3():
        pytest.skip("sprint has not reached Phase 3; issues do not exist yet")
    cur = _status().get("current_sprint", {})
    assert cur.get("github_issues"), (
        "current_sprint.github_issues is empty. Phase 3 requires one issue "
        "per task BEFORE the first task file is touched.")


def test_plan_approval_is_recorded():
    if not _reached_phase_3():
        pytest.skip("sprint has not reached Phase 3; no plan to approve yet")
    cur = _status().get("current_sprint", {})
    assert cur.get("plan_approved") is True, (
        "plan_approved is not true. Either the plan was not approved, or the "
        "approval was never recorded -- and the second is how the PR and "
        "issue checks were silently skipped in Sprint 17.")


# The text the hook writes for each omission. Asserted per field, so a block
# raised for some OTHER reason cannot pass as this field's block.
_ARTIFACT_MESSAGE = {
    "pr": "current_sprint.pr is null",
    "github_issues": "current_sprint.github_issues is empty",
    "plan_approved": "plan_approved is not true",
}


@pytest.mark.parametrize("field,broken", [
    ("pr", None),
    ("github_issues", []),
    ("plan_approved", False),
])
def test_the_hook_blocks_when_a_phase_3_artifact_is_missing(field, broken,
                                                            tmp_path):
    """Each omission must BLOCK a close-out claim, independently.

    HERMETIC since the Sprint 22 Pass 1 sweep. The first version mutated the
    REAL status file and ran the hook against the real repository, so its
    answer depended on the live sprint. Since F125 the hook owes no Phase 3
    artifacts before the sprint's plan exists, so in every backlog-refinement
    window all three cases went red on correct behavior (2026-10-07, Sprint 23
    Phase 1). A scratch repository with a plan and one commit is the state
    these checks exist for, whatever phase the real sprint is in.
    """
    repo = tmp_path / "clone"
    repo.mkdir()

    def git(*args: str):
        return subprocess.run(["git", *args], cwd=str(repo),
                              capture_output=True, text=True)

    git("init", "-b", "feature/20260919_Sprint_17")
    git("config", "user.email", "t@example.com")
    git("config", "user.name", "t")
    (repo / "docs" / "sprints").mkdir(parents=True)
    (repo / "docs" / "sprints" / "SPRINT_17_PLAN.md").write_text(
        "# plan\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-m", "a commit exists on this branch")

    current = {"number": 17, "pr": 1, "github_issues": [1],
               "plan_approved": True}
    current[field] = broken
    claude = repo / ".claude"
    claude.mkdir()
    (claude / "sprint_status.json").write_text(
        json.dumps({"current_sprint": current}), encoding="utf-8")

    payload = json.dumps({
        "last_assistant_message": "The sprint close-out is complete.",
        "repo_override": str(repo),
        "branch_override": "feature/20260919_Sprint_17",
    })
    r = subprocess.run([sys.executable, str(HOOK)], input=payload,
                       capture_output=True, text=True, cwd=str(ROOT))

    assert r.returncode != 0, (
        f"a missing {field} did not block the close-out claim")
    assert _ARTIFACT_MESSAGE[field] in r.stderr, r.stderr
    for other, text in _ARTIFACT_MESSAGE.items():
        if other != field:
            assert text not in r.stderr, (
                f"{other} is present but was reported missing")


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
    # Sprint 17 HAD a written plan; its failure was nine tasks run under it
    # with no PR, no issues and no approval. Since F125 (Sprint 22) the Phase
    # 3 checks apply once the plan exists, so the fixture carries one -- as
    # the real Sprint 17 did. Without it, this repository is in the no-plan
    # branch, which test_closeout_plan_gate.py covers.
    (repo / "docs" / "sprints").mkdir(parents=True)
    (repo / "docs" / "sprints" / "SPRINT_17_PLAN.md").write_text(
        "# plan\n", encoding="utf-8")
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


def test_the_hook_tests_do_not_depend_on_the_checked_out_branch():
    """These tests must give the same answer on a detached HEAD.

    THE DEFECT THIS EXISTS FOR. The payload omitted `branch_override`, so the
    hook fell back to `git branch --show-current`. That returns a name in a
    normal clone and EMPTY on a detached HEAD, which is what
    actions/checkout leaves behind. The hook's first gate is "sprint feature
    branch only", so on CI it returned ALLOW before reaching any artifact
    check, and three tests asserting a block failed on Linux while passing on
    Windows -- for every commit of this sprint.

    Verified by running the pre-fix file in a detached worktree: 3 failed.
    """
    # BEHAVIORAL, not a source grep: the payload the hook actually receives
    # must name a branch. A grep on this file matched the phrase inside this
    # docstring, which is its own small lesson about presence-checking.
    payload = json.loads(_claim())
    assert payload.get("branch_override"), (
        "the hook payload does not pin the branch, so these tests depend on "
        "how the repository happens to be checked out")
    assert SPRINT_BRANCH_IN_HOOK.match(payload["branch_override"]), (
        f"{payload['branch_override']!r} does not match the pattern the hook "
        "requires, so the hook would exit before any artifact check")

    number = json.loads(STATUS.read_text(encoding="utf-8"))[
        "current_sprint"]["number"]
    assert str(number) in payload["branch_override"], (
        "the pinned branch names a different sprint than the status file, "
        "so the hook takes its stale-state path instead")

def test_a_failing_git_does_not_silently_skip_the_phase_3_checks():
    """A count we could not get is not a count of zero.

    THE DEFECT THIS EXISTS FOR, found by a PR #146 review agent. hooklib.git
    returns (1, "") on ANY exception including a timeout, so _count returned
    None, `work_started` became False, and all three Phase 3 checks were
    skipped WITH NO VIOLATION RECORDED -- reproducing the Sprint 17 failure
    (nine tasks, a full retrospective, pr: null) silently.

    Measured: with git healthy the Sprint 17 state gave 3 violations; with
    rev-list stubbed to fail it gave 0 and an EMPTY list. Nothing in the
    output said the count had failed. The explicit timeout=2 added during the
    same review made it MORE reachable, since 2s is realistic on a cold or
    large repository.

    test_an_unresolvable_base_ref_does_not_disable_the_checks covers develop
    not resolving. It does not cover git itself failing, which is why the
    suite was green on this.
    """
    import importlib.util

    spec = importlib.util.spec_from_file_location("closeout_gitfail", HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    real = mod.hooklib.git

    def failing_rev_list(*args, **kwargs):
        if args and args[0] == "rev-list":
            return 1, ""
        return real(*args, **kwargs)

    mod.hooklib.git = failing_rev_list
    try:
        violations = mod.collect_violations(ROOT, 20)
    finally:
        mod.hooklib.git = real

    assert any("DID NOT RUN" in v for v in violations), (
        "git failed and the Phase 3 checks were skipped with no violation. "
        f"That is 'could not check' reading as 'clean'. Violations: "
        f"{violations}")
