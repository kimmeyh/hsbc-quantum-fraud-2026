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
def test_an_unreadable_state_exits_nonzero(ci, monkeypatch, why, patch):
    """Every way of NOT knowing must exit non-zero. This is the whole point:
    a run that cannot read CI must not report it green."""
    if patch == "which":
        monkeypatch.setattr(ci.shutil, "which", lambda name: None)
    else:
        monkeypatch.setattr(ci, "_require_gh", lambda: None)
        monkeypatch.setattr(ci, "_run",
                            lambda args, timeout=60: (0, "not json", ""))
    rc = ci.main(["--sha", "HEAD"])
    assert rc == ci.UNKNOWN, f"{why} did not exit UNKNOWN"


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


def test_the_hook_allows_a_closeout_when_ci_is_green():
    """The companion. Without it, blocking unconditionally would satisfy all
    three tests above and the gate would be useless."""
    rc, err = _hook_with_ci(
        '    return [{"name": "CI", "status": "completed", '
        '"conclusion": "success", "headSha": sha, "url": ""}]')
    assert rc == 0, f"a green close-out was blocked: {err[-400:]}"


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
