"""CI status is checked, and "could not check" never reads as green.

Sprint 18 ran RED on every commit from the first push to the last, and the
failure surfaced only when a monitor was armed on the PR during a review round
that had already finished. Two failures, not one:

  1. Three tests could not fail locally. They sent a Stop hook a payload with
     no `branch_override`, so the hook read the live branch name -- a name in
     a normal clone, EMPTY on the detached HEAD that actions/checkout leaves
     behind. The hook's first gate is "sprint feature branch only", so on CI
     it returned ALLOW before reaching any artifact check.
  2. A red check sat on the PR through an entire review round without being
     opened. The reviews were read; the check status was not.

`scripts/check_ci_status.py` answers the second. These tests pin the property
that makes it worth having: every path that cannot determine the state returns
non-zero, because the defect class this repository keeps paying for is a check
that reports success when it checked nothing.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check_ci_status.py"
HOOK = ROOT / ".claude" / "hooks" / "verify_closeout_complete.py"
STATUS = ROOT / ".claude" / "sprint_status.json"

sys.path.insert(0, str(ROOT / "scripts"))


@pytest.fixture
def ci():
    import check_ci_status
    return check_ci_status


def _runs(status: str, conclusion: str | None, name: str = "CI") -> list[dict]:
    return [{"name": name, "status": status, "conclusion": conclusion,
             "headSha": "deadbee", "url": "http://example/run"}]


def test_the_checker_exists():
    assert SCRIPT.exists()


def test_a_completed_success_is_the_only_pass(ci, monkeypatch):
    monkeypatch.setattr(ci, "runs_for",
                        lambda sha: _runs("completed", "success"))
    rc, _lines = ci.evaluate("deadbee")
    assert rc == ci.OK


def test_a_failing_run_is_reported_as_failed(ci, monkeypatch):
    monkeypatch.setattr(ci, "runs_for",
                        lambda sha: _runs("completed", "failure"))
    rc, lines = ci.evaluate("deadbee")
    assert rc == ci.FAILED
    assert any("RED" in ln for ln in lines)
    assert any("http://example/run" in ln for ln in lines), (
        "the failure does not link the run, so it cannot be opened")


def test_a_run_still_in_progress_is_not_a_pass(ci, monkeypatch):
    """A queued run reads exactly like a passing one if you only check for
    the absence of failures."""
    monkeypatch.setattr(ci, "runs_for",
                        lambda sha: _runs("in_progress", None))
    rc, _lines = ci.evaluate("deadbee")
    assert rc == ci.PENDING
    assert rc != ci.OK


def test_no_run_at_all_is_not_a_pass(ci, monkeypatch):
    """The commit may not have been pushed. Nothing was checked."""
    monkeypatch.setattr(ci, "runs_for", lambda sha: [])
    with pytest.raises(ci.Undetermined):
        ci.evaluate("deadbee")


def test_a_mixed_result_takes_the_failure(ci, monkeypatch):
    """One green run does not excuse a red one."""
    monkeypatch.setattr(ci, "runs_for", lambda sha: (
        _runs("completed", "success", "lint")
        + _runs("completed", "failure", "tests")))
    rc, _lines = ci.evaluate("deadbee")
    assert rc == ci.FAILED


def test_skipped_and_neutral_do_not_count_as_failures(ci, monkeypatch):
    """The companion. Treating every non-success conclusion as red would make
    the guard fire on correct behavior, which is how guards get deleted."""
    monkeypatch.setattr(ci, "runs_for", lambda sha: (
        _runs("completed", "skipped", "optional")
        + _runs("completed", "success", "tests")))
    rc, _lines = ci.evaluate("deadbee")
    assert rc == ci.OK


@pytest.mark.parametrize("why,patch", [
    ("gh is not installed", "which"),
    ("gh returns unparseable json", "json"),
])
def test_an_unreadable_state_exits_nonzero(ci, monkeypatch, why, patch,
                                           capsys):
    """Every way of NOT knowing must exit non-zero. This is the whole point:
    a run that cannot read CI must not report it green.

    THE MESSAGE IS ASSERTED, not just the code. Both params previously checked
    only `rc == UNKNOWN`, which ANY Undetermined satisfies -- so neither test
    could tell its own path from the other's, and in the json case the stubbed
    _run also feeds head_sha, so it could have been passing for a reason it
    does not name. Found by the PR #141 review.
    """
    if patch == "which":
        monkeypatch.setattr(ci.shutil, "which", lambda name: None)
        expect = "not on PATH"
    else:
        monkeypatch.setattr(ci, "_require_gh", lambda: None)
        monkeypatch.setattr(ci, "head_sha", lambda ref: "deadbee")
        monkeypatch.setattr(ci, "_run",
                            lambda args, timeout=60: (0, "not json", ""))
        expect = "unparseable"
    rc = ci.main(["--sha", "HEAD"])
    assert rc == ci.UNKNOWN, f"{why} did not exit UNKNOWN"
    out = capsys.readouterr().out
    assert expect in out, (
        f"{why} exited UNKNOWN but said nothing about it: {out!r}")


def test_the_exit_codes_are_distinct(ci):
    """A caller must be able to tell "red" from "cannot tell" from "still
    running" -- collapsing them is how one becomes the other."""
    codes = {ci.OK, ci.FAILED, ci.UNKNOWN, ci.PENDING}
    assert len(codes) == 4
    assert ci.OK == 0 and ci.FAILED != 0 and ci.UNKNOWN != 0 and ci.PENDING != 0


# ------------------------------------------- the hook refuses a red close-out

def _claim() -> str:
    number = json.loads(STATUS.read_text(encoding="utf-8"))[
        "current_sprint"]["number"]
    return json.dumps({
        "last_assistant_message": "The sprint close-out is complete.",
        "branch_override": f"feature/20260922_Sprint_{number}",
    })


def _hook_with_ci(monkeypatched_source: str) -> tuple[int, str]:
    """Run the hook with the CI checker stubbed to a fixed state.

    Mutates the checker on disk and restores it, asserting the restore. The
    hook runs in a subprocess and imports the checker by path, so a
    monkeypatch in this process would not reach it.
    """
    orig = SCRIPT.read_text(encoding="utf-8")
    stub = orig.replace(
        '    """Workflow runs whose head commit is exactly this sha."""',
        '    """Workflow runs whose head commit is exactly this sha."""\n'
        + monkeypatched_source, 1)
    assert stub != orig, "the stub did not apply; this test would prove nothing"
    SCRIPT.write_text(stub, encoding="utf-8")
    try:
        assert monkeypatched_source.strip() in SCRIPT.read_text(
            encoding="utf-8"), "the mutation is not on disk"
        r = subprocess.run([sys.executable, str(HOOK)], input=_claim(),
                           capture_output=True, text=True, cwd=str(ROOT))
        return r.returncode, r.stderr
    finally:
        SCRIPT.write_text(orig, encoding="utf-8")
        assert SCRIPT.read_text(encoding="utf-8") == orig, "RESTORE FAILED"


def test_the_hook_blocks_a_closeout_claim_when_ci_is_red():
    """The defect this exists for: Sprint 18 shipped a full review round
    under a red check, and nothing objected."""
    rc, err = _hook_with_ci(
        '    return [{"name": "CI", "status": "completed", '
        '"conclusion": "failure", "headSha": sha, "url": "http://x"}]')
    assert rc != 0, "a close-out claim passed over a RED check"
    assert "CI is RED" in err


def test_the_hook_blocks_while_ci_is_still_running():
    rc, err = _hook_with_ci(
        '    return [{"name": "CI", "status": "in_progress", '
        '"conclusion": None, "headSha": sha, "url": ""}]')
    assert rc != 0, "a close-out claim passed while CI was still running"
    assert "still RUNNING" in err


def test_the_hook_blocks_when_ci_cannot_be_determined():
    """Unlike the open-issues check beside it, this one does NOT fail open.
    That check asks a question whose answer is usually "nothing to do"; this
    one exists because the answer went unread."""
    rc, err = _hook_with_ci(
        '    raise Undetermined("simulated: gh unavailable")')
    assert rc != 0, "a close-out claim passed with CI status unknown"
    assert "could not be determined" in err


def test_the_hook_raises_no_ci_violation_when_ci_is_green():
    """The companion. Without it, blocking unconditionally would satisfy all
    three tests above and the gate would be useless.

    IT ASSERTS THE ABSENCE OF A CI COMPLAINT, NOT A CLEAN EXIT. The first
    version asserted `rc == 0`, which requires EVERY other violation to be
    empty too -- the Phase 3 artifacts, the three-doc rule, and a live
    `gh pr list` network call. So it went red whenever the sprint was mid-flight
    or GitHub was slow, for reasons having nothing to do with the CI gate it
    names. Measured 2026-10-02 as one of six planning-window failures (F97).

    What this test owns is one claim: a GREEN CI produces no CI violation.
    """
    rc, err = _hook_with_ci(
        '    return [{"name": "CI", "status": "completed", '
        '"conclusion": "success", "headSha": sha, "url": ""}]')

    for phrase in ("CI is RED", "still RUNNING", "could not be determined",
                   "could not be imported", "A guard that errors"):
        assert phrase not in err, (
            f"green CI still produced a CI violation ({phrase!r}): "
            f"{err[-400:]}")

    # And the hook must not have crashed: rc is 0 (allow) or 2 (block on some
    # OTHER violation), never a traceback.
    assert rc in (0, 2), f"the hook errored rather than deciding: {err[-400:]}"


def test_the_early_checkpoint_waits_before_looking(ci, monkeypatch):
    """--after exists so a just-created PR has time to FAIL.

    The 3.3.2 checkpoint runs about five minutes after the draft PR opens.
    Checking sooner is worse than not checking: with no workflow run yet, the
    answer is "cannot determine", which a reader skims as "nothing wrong".
    The delay is the mechanism, not a convenience.
    """
    slept = []
    monkeypatch.setattr(ci.time, "sleep", lambda s: slept.append(s))
    monkeypatch.setattr(ci, "head_sha", lambda ref: "deadbee")
    monkeypatch.setattr(ci, "runs_for",
                        lambda sha: _runs("completed", "success"))

    assert ci.main(["--after", "300"]) == ci.OK
    assert slept == [300], f"it did not wait before looking: {slept}"


def test_no_delay_is_requested_by_default(ci, monkeypatch):
    """The 7.0 checkpoint must NOT wait -- the retrospective proceeds while
    CI finishes, and a watcher reports later."""
    slept = []
    monkeypatch.setattr(ci.time, "sleep", lambda s: slept.append(s))
    monkeypatch.setattr(ci, "head_sha", lambda ref: "deadbee")
    monkeypatch.setattr(ci, "runs_for",
                        lambda sha: _runs("completed", "success"))

    ci.main([])
    assert slept == [], f"the default invocation blocked for {slept}"

def test_every_run_skipped_is_not_a_pass(ci, monkeypatch):
    """A commit whose every job was skipped read no test result at all.

    THE DEFECT THIS EXISTS FOR. The pass condition was the ABSENCE of
    failures, so a lone completed/skipped run returned exit 0 and printed
    "CI is green". Reachable in practice: a workflow gated behind a path
    filter, or a push with paths-ignore, completes with every job skipped.

    test_skipped_and_neutral_do_not_count_as_failures pairs skipped WITH a
    success, so it could not catch this -- a companion test that made the
    surrounding guard look covered. Found by the PR #141 review.
    """
    monkeypatch.setattr(ci, "runs_for",
                        lambda sha: _runs("completed", "skipped"))
    with pytest.raises(ci.Undetermined):
        ci.evaluate("deadbee")


def test_a_success_beside_a_skip_is_still_a_pass(ci, monkeypatch):
    """The companion. Requiring EVERY run to succeed would break every
    repository that gates a job behind a path filter."""
    monkeypatch.setattr(ci, "runs_for", lambda sha: (
        _runs("completed", "skipped", "optional")
        + _runs("completed", "success", "tests")))
    rc, _lines = ci.evaluate("deadbee")
    assert rc == ci.OK

# ------------------- F98: the budget, and the order the checks run in

def test_the_hook_timeout_budget_covers_its_own_subprocess_calls():
    """A Stop hook killed at its timeout produces NO exit code, so it cannot
    BLOCK -- a timeout fails OPEN whatever the hook would have decided.
    Measured 2026-10-02 with a hook that slept past its budget.

    So the sum of internal subprocess timeouts must fit the configured
    budget. It did not: 20 + 20 + 60 + 60 = 160s against a 20s budget, where
    a single hanging `gh pr list` exceeded it alone.
    """
    import json as _json

    settings = _json.loads(
        (ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))

    budget = None
    def walk(o):
        nonlocal budget
        if isinstance(o, dict):
            cmd = str(o.get("command", ""))
            if "verify_closeout_complete" in cmd and "timeout" in o:
                budget = int(o["timeout"])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(settings)
    assert budget, "no timeout configured for verify_closeout_complete"

    hook_src = HOOK.read_text(encoding="utf-8")
    hook_timeouts = [int(m) for m in re.findall(r"timeout=(\d+)\)", hook_src)]
    assert hook_timeouts, "no subprocess timeouts found in the hook"

    # EVERY subprocess call must pass an explicit timeout, because a DEFAULT
    # is invisible to this regex -- which is exactly how 75 of 98 seconds
    # hid from the first version of this guard. hooklib.git defaults to 15s.
    implicit = [s for s in re.findall(r"hooklib\.git\(([^)]*)\)", hook_src)
                if "timeout=" not in s]
    assert not implicit, (
        f"{len(implicit)} hooklib.git call(s) rely on the default timeout, "
        f"which this guard cannot see and therefore cannot budget for: "
        f"{implicit}. Pass an explicit timeout=.")

    checker_src = SCRIPT.read_text(encoding="utf-8")
    m = re.search(r"def _run\(args: list\[str\], timeout: int = (\d+)\)",
                  checker_src)
    assert m, "check_ci_status._run default timeout not found"
    ci_default = int(m.group(1))

    # THREE calls go through _run, not two: head_sha, _require_gh and
    # runs_for. The first version counted two and so did the hook comment, so
    # this guard passed on the same undercount it existed to catch. Two PR
    # #146 reviewers found it independently.
    worst = sum(hook_timeouts) + 3 * ci_default
    assert worst <= budget, (
        f"worst-case internal timeouts total {worst}s against a {budget}s "
        f"hook budget. A killed hook cannot block, so exceeding the budget "
        f"silently disables every check.")


def test_the_ci_check_runs_before_the_gh_dependent_issues_check():
    """ORDER IS LOAD-BEARING. The issues check fails OPEN (`except Exception:
    pass`); the CI check deliberately fails CLOSED. With the fail-open check
    first, one hanging `gh pr list` could consume the whole budget and kill
    the hook before the fail-closed guard ran -- defeating it precisely when
    GitHub is slow, which is when it matters.

    ANCHORED ON THE CALLS, NOT THE COMMENTS (F122 (a), Sprint 21). The first
    version of this test used `src.index("# CI on the HEAD commit.")`, so
    renaming a comment failed it with zero code change, and moving the code
    while leaving the comments in place passed it. It asserted the order of
    two strings nothing executes.
    """
    src = HOOK.read_text(encoding="utf-8")

    # The fail-CLOSED CI evaluation: the call that returns a verdict.
    i_ci = src.index("ci.evaluate(")

    # The fail-OPEN issues check: the `gh pr list` subprocess that can hang.
    i_issues = src.index('"gh", "pr", "list"')

    assert i_ci < i_issues, (
        "the gh-dependent issues check runs BEFORE the CI check again; a hang "
        "there kills the hook before the fail-closed CI guard executes. "
        f"ci.evaluate( at {i_ci}, gh pr list at {i_issues}")

    # And neither anchor may silently vanish: if the code is restructured so
    # one of these calls no longer exists, .index() raises ValueError above
    # rather than passing, which is the fail-safe direction. Assert the counts
    # so a SECOND call site cannot appear and make the ordering ambiguous.
    assert src.count("ci.evaluate(") == 1, (
        "more than one ci.evaluate( call site; the ordering assertion above "
        "pins only the first and is no longer unambiguous")
    assert src.count('"gh", "pr", "list"') == 1, (
        "more than one `gh pr list` call site; same ambiguity")

@pytest.mark.parametrize("payload,why", [
    ('{"message": "Not Found"}', "a gh error body: a dict, not a list"),
    ("null", "gh returned null"),
    ('["a", "b"]', "a list of strings, not of run objects"),
    ("5", "a bare number"),
])
def test_a_wrong_shaped_gh_response_is_UNDETERMINED_not_FAILED(
        ci, monkeypatch, payload, why):
    """json.loads succeeding does not mean the SHAPE is right.

    A gh error body is valid JSON, so `r.get("headSha")` raised AttributeError
    or TypeError -- which main() does not catch, so the script died with a
    traceback and exit 1. By this script's own table 1 means "at least one
    check FAILED", so "gh handed back the wrong shape" was reported as CI RED
    and the "nothing was checked" message never printed.

    It failed closed, which is why this is not critical, but with the wrong
    code and the wrong explanation -- and the four distinct exit codes exist
    precisely so a caller can tell red from cannot-tell. Found by a PR #146
    review agent.
    """
    monkeypatch.setattr(ci, "_require_gh", lambda: None)
    monkeypatch.setattr(ci, "_run",
                        lambda args, timeout=3: (0, payload, ""))
    with pytest.raises(ci.Undetermined):
        ci.runs_for("deadbee")


def test_a_correctly_shaped_response_still_parses(ci, monkeypatch):
    """The companion. Rejecting every payload would satisfy the test above
    and the checker would never read CI at all."""
    monkeypatch.setattr(ci, "_require_gh", lambda: None)
    monkeypatch.setattr(ci, "_run", lambda args, timeout=3: (
        0, '[{"headSha": "deadbee", "status": "completed", '
           '"conclusion": "success", "name": "CI", "url": ""}]', ""))
    runs = ci.runs_for("deadbee")
    assert len(runs) == 1 and runs[0]["conclusion"] == "success"
