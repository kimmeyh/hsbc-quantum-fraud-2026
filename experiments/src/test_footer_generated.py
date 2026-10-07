"""The status footer must be GENERATED in the turn that shows it (IMP-2).

Sprint 21 retrospective. CLAUDE.md: "Generate it with the script every time.
Never assemble it by hand, and never carry a timestamp forward from an earlier
message." The rule failed four times in Sprint 21 -- 1:14am, 1:41am, 3:22pm
and 3:31pm were typed while the script read otherwise. The every-turn Stop
hook `sprint_auto_advance.py` now refuses a reply that ends with a footer line
no `status_footer.py` run printed in the same turn.

The transcript format these fixtures use was read off a real session
transcript on 2026-10-06: the call is a `tool_use` block in an assistant
entry, its output a `tool_result` string in the next user entry, linked by id.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / ".claude" / "hooks" / "sprint_auto_advance.py"
ALLOW, BLOCK = 0, 2

FOOTER = "10/06/2026 4:56pm | Sprint 21 Phase 7.0 Retrospective"


def user(text: str) -> dict:
    return {"type": "user", "message": {"role": "user", "content": text}}


def call(tool_id: str, command: str) -> dict:
    return {"type": "assistant", "message": {"role": "assistant", "content": [
        {"type": "tool_use", "id": tool_id, "name": "Bash",
         "input": {"command": command}}]}}


def result(tool_id: str, output: str) -> dict:
    return {"type": "user", "message": {"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": tool_id, "content": output}]}}


def run(tmp_path: Path, entries: list[dict], message: str,
        stop_hook_active: bool = False) -> subprocess.CompletedProcess:
    transcript = tmp_path / "t.jsonl"
    transcript.write_text("\n".join(json.dumps(e) for e in entries) + "\n",
                          encoding="utf-8")
    payload = {"last_assistant_message": message,
               "transcript_path": str(transcript),
               "stop_hook_active": stop_hook_active,
               # Off any sprint branch, so only the footer check can block.
               "branch_override": "main"}
    return subprocess.run([sys.executable, str(HOOK)],
                          input=json.dumps(payload), capture_output=True,
                          text=True, cwd=str(ROOT), timeout=60)


GEN = "<venv python> scripts/status_footer.py"


def test_a_typed_footer_is_blocked(tmp_path):
    """The Sprint 21 failure: a footer with no generating run behind it."""
    r = run(tmp_path, [user("retro please")], f"Done.\n\n{FOOTER}")
    assert r.returncode == BLOCK
    assert "typed, not generated" in r.stderr


def test_a_footer_generated_this_turn_is_allowed(tmp_path):
    entries = [user("retro please"), call("t1", GEN), result("t1", FOOTER)]
    r = run(tmp_path, entries, f"Done.\n\n{FOOTER}")
    assert r.returncode == ALLOW, r.stderr


def test_a_footer_carried_forward_from_an_earlier_turn_is_blocked(tmp_path):
    """'Never carry a timestamp forward from an earlier message' -- the
    generating run must be in THIS turn, after the latest user message."""
    entries = [user("first"), call("t1", GEN), result("t1", FOOTER),
               user("second question")]
    r = run(tmp_path, entries, f"Answer.\n\n{FOOTER}")
    assert r.returncode == BLOCK


def test_a_footer_echoed_by_another_command_is_blocked(tmp_path):
    """Printing the line some other way is still typing it."""
    entries = [user("retro please"), call("t1", f"echo '{FOOTER}'"),
               result("t1", FOOTER)]
    r = run(tmp_path, entries, f"Done.\n\n{FOOTER}")
    assert r.returncode == BLOCK


def test_a_footer_that_differs_from_the_generated_one_is_blocked(tmp_path):
    """The 3:31pm case: the script ran and printed 3:20pm, and the reply
    showed a different, hand-typed time."""
    entries = [user("q"), call("t1", GEN),
               result("t1", FOOTER.replace("4:56pm", "4:55pm"))]
    r = run(tmp_path, entries, f"Done.\n\n{FOOTER}")
    assert r.returncode == BLOCK


def test_a_reply_without_a_footer_is_untouched(tmp_path):
    r = run(tmp_path, [user("q")], "A plain answer with no footer.")
    assert r.returncode == ALLOW


def test_an_unreadable_transcript_fails_open(tmp_path):
    """Like the rest of this hook: a Stop hook that errors would block every
    turn, which is worse than missing one typed footer."""
    payload = {"last_assistant_message": f"Done.\n\n{FOOTER}",
               "transcript_path": str(tmp_path / "missing.jsonl"),
               "branch_override": "main"}
    r = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(payload),
                       capture_output=True, text=True, cwd=str(ROOT),
                       timeout=60)
    assert r.returncode == ALLOW


def test_an_already_blocked_stop_is_not_reblocked(tmp_path):
    """Re-blocking an active stop wedges the session."""
    r = run(tmp_path, [user("q")], f"Done.\n\n{FOOTER}",
            stop_hook_active=True)
    assert r.returncode == ALLOW


def test_the_check_runs_before_the_branch_bypass():
    """No override in the commit that creates the guard (CLAUDE.md, Sprint
    17): the footer check sits ahead of the `allow_stop_hook_bypass` gate."""
    src = HOOK.read_text(encoding="utf-8")
    body = src[src.index("def main()"):]
    assert body.index("_check_footer(payload)") < body.index(
        "allow_stop_hook_bypass")
