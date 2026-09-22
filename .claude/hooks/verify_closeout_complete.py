"""Stop hook: a claim of close-out completion must survive contact with the
artifacts.

Converted from PowerShell 2026-09-17 (F78, Sprint 16), including the
retrospective fix from Task B.

Fires when the closing message CLAIMS the sprint or close-out is complete, then
checks machine-readable artifacts that can contradict it. It does not check
whether the work was good; it checks whether the claim is true.

This hook has already caught a real violation in this sprint: `plan_approved`
was true while `current_sprint.pr` was null, and a second stale field
(`github_issues` empty while ten issues existed) surfaced only because the block
prompted an artifact walk.

Gates, in order:
  1. sprint feature branch only
  2. the message actually claims completion, and is not hedged by a mid-sprint
     signal ("Task C is blocked", "still executing")
  3. artifacts contradict the claim

Fails OPEN on anything unparseable. A Stop hook that errors blocks every turn.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hooklib  # noqa: E402

SPRINT_BRANCH = re.compile(r"^feature/\d+_Sprint_(\d+)")

CLAIM = [
    re.compile(r"(?i)\b(the\s+)?(sprint|phase\s*[78]|close[- ]?out|post[- ]?merge)\s+"
               r"(work\s+|process\s+)?(is|was)\s+(now\s+)?(fully\s+|genuinely\s+)?"
               r"(complete|closed|done|finished)\b"),
    re.compile(r"(?i)\bclose[- ]?out\b[^.\n]{0,40}\b(is|was)\s+(now\s+)?"
               r"(complete|done|finished)\b"),
    re.compile(r"(?i)\ball\s+(the\s+)?(post[- ]?merge|checklist|close[- ]?out)\s+"
               r"(items|steps)\b[^.\n]{0,40}\b(are\s+)?(now\s+)?(complete|done)\b"),
    re.compile(r"(?i)\bready\s+for\s+(the\s+)?next\s+sprint\b"),
    re.compile(r"(?i)\bsprint\s+\d+\s+is\s+(fully\s+)?(closed|complete)\b"),
]

# A claim hedged by one of these is not a claim of completion.
MID_SPRINT = [
    re.compile(r"(?i)\b(task|tier|sub[- ]?task)\s+\w+\b[^.\n]{0,40}"
               r"\b(blocked|in progress|not started|remaining|pending)\b"),
    re.compile(r"(?i)\bstopping criterion\s*\d"),
    re.compile(r"(?i)\b(is|remains)\s+blocked\b"),
    re.compile(r"(?i)\bstill\s+(executing|in\s+flight|running)\b"),
]

TEMPLATE = """[BLOCKED by verify-closeout-complete hook]

The final message claims close-out completion, but these artifacts contradict it:

{violations}

Open docs/SPRINT_CHECKLIST.md, walk the close-out section line by line, and fix
each violation. Verify by CHECKING the artifact, not by recalling. Do not
re-assert completion until every item is verified done.

Bypass (only if a violation is genuinely not applicable): rename the branch to
include allow_stop_hook_bypass, or state explicitly which item does not apply
and why."""


def _last_message(payload: dict) -> str:
    if payload.get("last_assistant_message"):
        return str(payload["last_assistant_message"])
    msgs = payload.get("messages")
    if isinstance(msgs, list):
        for m in reversed(msgs):
            if isinstance(m, dict) and m.get("role") == "assistant":
                return str(m.get("content") or "")
    return ""


def _root(payload: dict) -> Path:
    for key in ("repo_override", "cwd"):
        v = str(payload.get(key) or "")
        if v and Path(v).exists():
            return Path(v)
    return hooklib.repo_root()


def _branch(payload: dict, root: Path) -> str:
    override = str(payload.get("branch_override") or "").strip()
    if override:
        return override
    rc, out = hooklib.git("branch", "--show-current", cwd=root)
    return out.strip() if rc == 0 else ""


def collect_violations(root: Path, sprint_num: int) -> list[str]:
    violations: list[str] = []

    status_path = root / ".claude" / "sprint_status.json"
    status = None
    if not status_path.exists():
        violations.append(".claude/sprint_status.json is MISSING.")
    else:
        try:
            status = json.loads(status_path.read_text(encoding="utf-8"))
            cur = status.get("current_sprint", {})
            num = cur.get("number")
            if num is not None and int(num) != sprint_num:
                violations.append(
                    f".claude/sprint_status.json current_sprint.number is {num} "
                    f"but the branch is Sprint {sprint_num} -- stale state file "
                    "misleads the next session.")
        except Exception:                                # noqa: BLE001
            violations.append(".claude/sprint_status.json is not valid JSON.")

    if status:
        cur = status.get("current_sprint", {})

        # THE PHASE 3 ARTIFACTS ARE CHECKED AGAINST THE WORK, NOT AGAINST EACH
        # OTHER (Sprint 17). The original check was
        # `plan_approved is True and pr is None`, which reads one stale field
        # to decide whether to distrust another. In Sprint 17 plan_approved was
        # never set to true, so the condition never fired, and the sprint ran
        # to Manual Validation with NO draft PR, NO task issues and no recorded
        # approval. The guard was defeated by exactly the second-stale-field
        # failure its own docstring describes from Sprint 16.
        #
        # The fix is to anchor on something that cannot be stale: commits
        # exist on this branch. If work has happened, Phase 3's artifacts were
        # due before it started.
        rc_commits, commits_out = hooklib.git(
            "rev-list", "--count", f"develop..HEAD", cwd=root)
        work_started = rc_commits == 0 and commits_out.strip().isdigit() \
            and int(commits_out.strip()) > 0

        if work_started:
            if cur.get("pr") is None:
                violations.append(
                    f"{commits_out.strip()} commit(s) on this branch but "
                    "current_sprint.pr is null -- SPRINT_CHECKLIST.md Phase 3 "
                    "requires a DRAFT PR created before the first task file is "
                    "touched (it stays draft until 7.7).")
            if not cur.get("github_issues"):
                violations.append(
                    f"{commits_out.strip()} commit(s) on this branch but "
                    "current_sprint.github_issues is empty -- "
                    "SPRINT_CHECKLIST.md Phase 3 requires one issue per task "
                    "BEFORE the first task file is touched.")
            if cur.get("plan_approved") is not True:
                violations.append(
                    f"{commits_out.strip()} commit(s) on this branch but "
                    "plan_approved is not true -- SPRINT_CHECKLIST.md Phase 3 "
                    "requires explicit team-lead approval, recorded. Either "
                    "the plan was not approved, or the approval was never "
                    "written down. Both are violations; the second is how the "
                    "PR and issue checks above were silently skipped in "
                    "Sprint 17.")

    rc, out = hooklib.git("status", "--porcelain", "--", "0*", cwd=root)
    if rc == 0 and out.strip():
        names = ", ".join(line[2:].strip() for line in out.splitlines() if line.strip())
        violations.append(
            f"Uncommitted team-lead 0* working file(s): {names}. Commit with a "
            "neutral message (never read them).")

    # Three-doc rule for the PREVIOUS sprint. Task B fix: the retrospective is
    # demanded independently. The original asked for the summary only, and only
    # when the retrospective already existed, so a missing retrospective
    # triggered nothing at all.
    prev = sprint_num - 1
    if prev > 0:
        sprints = root / "docs" / "sprints"
        if (sprints / f"SPRINT_{prev}_PLAN.md").exists():
            if not (sprints / f"SPRINT_{prev}_RETROSPECTIVE.md").exists():
                violations.append(
                    f"docs/sprints/SPRINT_{prev}_RETROSPECTIVE.md is missing "
                    "(three-doc rule, workflow 3.2.1). Phase 7 is an exit gate: "
                    "a sprint does not close without its retrospective.")
            if not (sprints / f"SPRINT_{prev}_SUMMARY.md").exists():
                violations.append(
                    f"docs/sprints/SPRINT_{prev}_SUMMARY.md is missing "
                    "(three-doc rule, workflow 3.2.1).")

    # Open sprint issues -- POST-MERGE precondition only.
    #
    # RESTORED 2026-09-19. The PowerShell had this fifth check and the Sprint 16
    # conversion dropped it silently, which the PR #120 review caught. Without
    # it, a close-out could be certified complete with every task issue still
    # open, and nothing would object.
    #
    # It is post-merge ONLY because `Closes #N` does not fire on a
    # feature->develop merge (workflow 2.3), so the issues must be closed by
    # hand and the only moment that is checkable is after the merge lands.
    rc, out = hooklib.git("rev-parse", "--abbrev-ref", "HEAD", cwd=root)
    branch_now = out.strip() if rc == 0 else ""
    if branch_now:
        try:
            pr = subprocess.run(
                ["gh", "pr", "list", "--head", branch_now, "--state", "all",
                 "--json", "state,mergedAt"],
                cwd=str(root), capture_output=True, text=True, timeout=20)
            merged = pr.returncode == 0 and any(
                p.get("state") == "MERGED" or p.get("mergedAt")
                for p in json.loads(pr.stdout or "[]"))
            if merged:
                iss = subprocess.run(
                    ["gh", "issue", "list", "--label", "sprint", "--state",
                     "open", "--json", "number"],
                    cwd=str(root), capture_output=True, text=True, timeout=20)
                if iss.returncode == 0 and iss.stdout:
                    nums = [f"#{i['number']}" for i in json.loads(iss.stdout)]
                    if nums:
                        violations.append(
                            "Sprint PR MERGED but sprint-labeled issues still "
                            f"OPEN: {', '.join(nums)} ('Closes #N' does not fire "
                            "on feature->develop merges; close manually, "
                            "workflow 2.3).")
        except Exception:                                # noqa: BLE001
            # gh missing, offline, or rate-limited. Fail open on THIS check
            # only: the other four still ran, and a hook that blocks every
            # close-out because GitHub is unreachable would be bypassed.
            pass

    return violations


def main() -> int:
    payload = hooklib.read_payload()
    if payload.get("stop_hook_active"):
        return hooklib.ALLOW

    message = _last_message(payload)
    if not message:
        return hooklib.ALLOW

    root = _root(payload)
    branch = _branch(payload, root)
    if not branch or "allow_stop_hook_bypass" in branch:
        return hooklib.ALLOW

    m = SPRINT_BRANCH.match(branch)
    if not m:
        return hooklib.ALLOW
    sprint_num = int(m.group(1))

    if not any(p.search(message) for p in CLAIM):
        return hooklib.ALLOW
    if any(p.search(message) for p in MID_SPRINT):
        return hooklib.ALLOW

    violations = collect_violations(root, sprint_num)
    if not violations:
        return hooklib.ALLOW

    return hooklib.block(TEMPLATE.format(
        violations="\n".join(f"  - {v}" for v in violations)))


if __name__ == "__main__":
    sys.exit(main())
