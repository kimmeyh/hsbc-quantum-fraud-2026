"""The close-out hook's commit count and plan gate (F125, Sprint 22).

On 2026-10-06 the hook blocked a backlog-refinement message, demanding Sprint
22's draft PR, issues and approval before a plan existed. Two causes:

1. It counted `develop..HEAD` against a LOCAL develop last updated at Sprint
   16's merge: 105 commits where `origin/develop..HEAD` was 1.
2. Any commit read as "work started". The one real commit was Phase 8's
   refinement sweep, which the carry-forward rule puts on the new branch
   before its plan is written.

The fix counts against origin/develop first, and applies the Phase 3 checks
only once the sprint's plan document exists. Before that, commits touching
more than the planning records are flagged as task work without a plan, and a
diff that cannot be listed is flagged as unchecked -- never passed.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / ".claude" / "hooks" / "verify_closeout_complete.py"
BRANCH = "feature/20261006_Sprint_22"


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(repo), capture_output=True,
                          text=True)


def _commit(repo: Path, rel: str, msg: str) -> None:
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(msg + "\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", msg)


def _repo(tmp_path: Path, stale_local_develop: bool = True) -> Path:
    """A clone whose origin/develop is AHEAD of its local develop.

    Local develop stays at the first commit; origin/develop advances three
    commits; the sprint branch is cut from origin/develop. So
    `develop..HEAD` overcounts and `origin/develop..HEAD` is exact.
    """
    origin = tmp_path / "origin.git"
    _git(tmp_path, "init", "--bare", "-b", "develop", str(origin))
    repo = tmp_path / "clone"
    repo.mkdir()
    _git(repo, "init", "-b", "develop")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "t")
    _git(repo, "remote", "add", "origin", str(origin))
    _commit(repo, "seed.txt", "seed")
    _git(repo, "push", "origin", "develop")
    first = _git(repo, "rev-parse", "HEAD").stdout.strip()
    for i in range(3):
        _commit(repo, f"later{i}.txt", f"later {i}")
    _git(repo, "push", "origin", "develop")
    _git(repo, "fetch", "origin")
    _git(repo, "checkout", "-b", BRANCH, "origin/develop")
    if stale_local_develop:
        # AFTER leaving develop: `git branch -f` refuses to move the branch
        # that is checked out. The first version of this fixture moved it
        # while it was checked out, git silently refused, both counts came out
        # 1, and the count test passed against the OLD hook -- caught by the
        # mutation proof before commit.
        _git(repo, "branch", "-f", "develop", first)
        stale = _git(repo, "rev-list", "--count", "develop..HEAD").stdout
        exact = _git(repo, "rev-list", "--count",
                     "origin/develop..HEAD").stdout
        assert int(stale) > int(exact), (
            f"fixture is not stale: develop..HEAD={stale.strip()}, "
            f"origin/develop..HEAD={exact.strip()}")
    (repo / ".claude").mkdir()
    return repo


def _status(repo: Path) -> None:
    (repo / ".claude" / "sprint_status.json").write_text(json.dumps({
        "current_sprint": {"number": 22, "pr": None, "github_issues": [],
                           "plan_approved": False},
    }), encoding="utf-8")


def _hook(repo: Path) -> subprocess.CompletedProcess:
    payload = json.dumps({
        "last_assistant_message": "The sprint close-out is complete.",
        "repo_override": str(repo),
        "branch_override": BRANCH,
    })
    return subprocess.run([sys.executable, str(HOOK)], input=payload,
                          capture_output=True, text=True, cwd=str(ROOT),
                          timeout=120)


def test_refinement_commits_before_a_plan_owe_no_phase_3_artifacts(tmp_path):
    """The 2026-10-06 false block, reproduced: one commit touching only the
    planning records, no plan yet. No Phase 3 violation may appear."""
    repo = _repo(tmp_path)
    _status(repo)
    _commit(repo, "docs/ALL_SPRINTS_MASTER_PLAN.md", "refinement sweep")
    r = _hook(repo)
    _ran_to_completion(r)
    assert "current_sprint.pr is null" not in r.stderr
    assert "plan_approved is not true" not in r.stderr
    assert "without a plan" not in r.stderr
    assert "could not be listed" not in r.stderr


def _ran_to_completion(r) -> None:
    """Absence assertions alone pass on a hook that CRASHED: a traceback
    contains none of the strings they look for (PR #159 review). A finished
    hook exits ALLOW (0) or BLOCK (2); an uncaught exception exits 1."""
    assert r.returncode in (0, 2), (
        f"the hook did not finish (exit {r.returncode}):\n{r.stderr[-800:]}")
    assert "Traceback" not in r.stderr, r.stderr[-800:]


def test_a_local_develop_without_origin_is_diffed_not_blocked(tmp_path):
    """The count falls back to local `develop`; the no-plan file list must
    use the same ref. It used to diff origin/develop unconditionally, fail,
    and raise a false "could not be listed" block (PR #159 review)."""
    repo = _repo(tmp_path, stale_local_develop=False)
    _git(repo, "remote", "remove", "origin")
    assert _git(repo, "rev-parse", "--verify", "origin/develop").returncode != 0
    _status(repo)
    _commit(repo, "docs/ALL_SPRINTS_MASTER_PLAN.md", "refinement sweep")
    r = _hook(repo)
    _ran_to_completion(r)
    assert "could not be listed" not in r.stderr, r.stderr[-800:]
    assert "without a plan" not in r.stderr


def test_the_count_uses_origin_develop_not_a_stale_local_develop(tmp_path):
    """With a plan present, the Phase 3 violations name the TRUE count: 1
    commit ahead of origin/develop, not 5 ahead of the stale local develop."""
    repo = _repo(tmp_path)
    _status(repo)
    _commit(repo, "docs/sprints/SPRINT_22_PLAN.md", "the plan")
    r = _hook(repo)
    assert "1 commit(s) on this branch but current_sprint.pr is null" \
        in r.stderr, r.stderr[-600:]


def test_code_work_without_a_plan_is_a_violation(tmp_path):
    """No plan is not a free pass: commits that touch code with no plan are
    task work without a plan."""
    repo = _repo(tmp_path)
    _status(repo)
    _commit(repo, "experiments/src/new_module.py", "task work")
    r = _hook(repo)
    assert r.returncode != 0
    assert "task work without a plan" in r.stderr
    assert "experiments/src/new_module.py" in r.stderr


def test_an_unlistable_diff_is_flagged_not_passed(tmp_path):
    """No origin/develop to diff against: whether task work started without a
    plan could not be checked, and the hook must say so."""
    repo = tmp_path / "solo"
    repo.mkdir()
    _git(repo, "init", "-b", BRANCH)
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "t")
    (repo / ".claude").mkdir()
    _status(repo)
    _commit(repo, "experiments/src/x.py", "work, no remote")
    r = _hook(repo)
    assert r.returncode != 0
    assert "was NOT checked" in r.stderr
