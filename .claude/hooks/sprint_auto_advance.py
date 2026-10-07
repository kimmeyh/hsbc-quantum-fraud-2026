"""Stop hook: do not end a turn mid-sprint with a question or an unkept promise.

PORTED from spamfilter-multi `.claude/hooks/sprint-auto-advance.ps1`
(2026-09-17, Sprint 16). The team lead asked for this hook to be transferred
here and it had not been; this is that transfer, in Python rather than
PowerShell because F78 is converting this repository's hooks for Linux CI.

Established there 2026-04-20 during Sprint 36 after a model was observed
violating the Phase Auto-Advance Rule even though the rule lives in CLAUDE.md.
Documentation-only control proved insufficient; a forcing function was required.
Fifteen sprints of this repository's history say the same thing: a rule in a
document decays, a rule with a failing check does not.

ENFORCEMENT WINDOW. Between Phase 3.7 plan approval and the START of Manual
Validation. Outside it, ending a turn is correct: before approval the sprint
questions are still being asked, and from Manual Validation onward the work is
team-lead-driven.

WHAT IT BLOCKS
  - a closing question (permission-asking inside the auto-advance window)
  - a closing COMMITMENT: an announced next action that the turn does not take

WHAT IT ALLOWS
  - any of the named criteria in docs/SPRINT_STOPPING_CRITERIA.md
  - Manual Validation handover
  - a metered Dirac-3 run awaiting approval (Criterion H)
  - a genuine external blocker
  - anything outside the enforcement window

THE COMMITMENT PATTERNS ARE WIDER HERE THAN IN THE SOURCE, and that difference
is the reason this port is not a copy. Checked against the three real failures
in this repository:

    "Continuing with Task C."                     Sprint 15
    "Continuing to Task B, extending the hook."   Sprint 16
    "Continuing with the Task E conversions."     Sprint 16

The source's patterns match NONE of them: they require "I'll continue" or
"proceeding to", and a bare participle opening ("Continuing with X.") slips
through all four. Verified by running its regexes against those exact strings
before porting. The source encountered the same class in its Sprint 61 (IMP-1,
three occurrences) and wrote patterns for the shapes IT had seen.

Bypass: the literal token `allow_stop_hook_bypass` in the branch name.
Fails OPEN on anything unparseable: a Stop hook that errors would block every
turn, which is far worse than missing one announcement.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hooklib  # noqa: E402

SPRINT_BRANCH = re.compile(r"feature/\d+_Sprint_(\d+)", re.IGNORECASE)

# Phase 5.3 onward: the window's upper bound.
PAST_VALIDATION = {
    "phase_5_validation", "phase_5_3_manual_validation", "phase_6_push",
    "phase_7_retrospective", "phase_8_delivery_cycle", "complete", "closed",
}

QUESTION_SHAPED = [
    re.compile(r"(?i)\bshould i\b"),
    re.compile(r"(?i)\bwould you like\b"),
    re.compile(r"(?i)\bdo you want\b"),
    re.compile(r"(?i)\blet me know\b"),
    re.compile(r"(?i)\bshall i\b"),
    re.compile(r"(?i)\bor (wait|defer|skip)\b"),
    re.compile(r"(?i)\bplease (confirm|advise)\b"),
]

# A turn ending on a future commitment is the same violation as asking
# permission: the announced action never ran.
COMMITMENT = [
    # From the source hook, kept as-is.
    re.compile(r"(?i)\b(i|we)('ll| will)( now| next)? (start|begin|proceed|do|run|"
               r"build|create|update|fix|implement|write|execute|extract|wire|add|"
               r"move on|continue|tackle|pick up)\b[^.!?]*[.!]\s*$"),
    re.compile(r"(?i)\bnext[,:]? (i|we)[^.!?]*[.!]\s*$"),
    re.compile(r"(?i)\b(proceeding|moving) (to|on to)\b[^.!?]*[.!]\s*$"),
    re.compile(r"(?i)\bnow (executing|starting|beginning|building|running|"
               r"implementing)\b[^.!?]*[.!]\s*$"),
    # ADDED HERE. A bare participle opening is the shape this repository
    # actually produced three times, and the four patterns above miss it.
    re.compile(r"(?i)(?:^|[.!?]\s+)(continuing|proceeding|starting|beginning|"
               r"moving|converting|running|writing)\b[^.!?]*[.!]\s*$"),
    re.compile(r"(?i)\bon to\s+(task|phase)\b[^.!?]*[.!]\s*$"),
]

LEGITIMATE = [
    re.compile(r"(?i)manual validation"),
    re.compile(r"(?i)stopping criteri"),
    re.compile(r"(?i)criterion\s+h\b"),
    re.compile(r"(?i)\bmetered\b[^.]{0,80}\bapprov"),
    re.compile(r"(?i)all (sprint )?tasks (complete|done|finished)"),
    re.compile(r"(?i)sprint (is )?complete"),
    re.compile(r"(?i)\bblocked (on|by|waiting for)\b"),
    re.compile(r"(?i)\bcannot proceed without\b"),
    re.compile(r"(?i)\bneeds? your (decision|approval|input|call)\b"),
    re.compile(r"(?i)\bawaiting (your )?(approval|decision|review)\b"),
]

MESSAGE = """[BLOCKED] The turn is ending inside the auto-advance window.

Found in the closing message:

    {found}

Workflow invariant 1: between Phase 3.7 approval and Manual Validation, the
ONLY thing that ends a turn is arriving at Manual Validation. Not a completed
task, not a completed phase, not a progress report.

If the next task is executable, EXECUTE IT IN THIS TURN. Either the work is in
the turn, or the sentence announcing it does not belong in the turn.

This rule is fifteen sprints old and was violated three times in two sprints
(Sprint 15 Task C, Sprint 16 Tasks B and E) while living only in documents.

LEGITIMATE endings, all of which suppress this block:
  - Manual Validation handover with the recommended steps
  - a named criterion from docs/SPRINT_STOPPING_CRITERIA.md
  - a metered Dirac-3 run awaiting approval (Criterion H)
  - a genuine external blocker, stated as one

Context length is NOT a stopping reason."""


def _status(root: Path) -> dict:
    try:
        raw = (root / ".claude" / "sprint_status.json").read_text(
            encoding="utf-8")
        return json.loads(raw).get("current_sprint", {})
    except Exception:                                    # noqa: BLE001
        return {}


def _root(payload: dict) -> Path:
    """Payload cwd wins, as in the source hook; else the usual resolution."""
    cwd = str(payload.get("cwd") or "")
    if cwd and Path(cwd).exists():
        return Path(cwd)
    return hooklib.repo_root()


def _branch(payload: dict, root: Path) -> str:
    """Test-only override, ported from the source hook.

    `branch_override` lets cases simulate any branch deterministically. Real
    Stop payloads never carry it. Without this the branch gate needs a real git
    repository, so every BLOCK case in a temp directory exits 0 at Gate 1 and
    the suite goes green while testing nothing.
    """
    override = str(payload.get("branch_override") or "").strip()
    if override:
        return override
    rc, out = hooklib.git("rev-parse", "--abbrev-ref", "HEAD", cwd=root)
    return out.strip() if rc == 0 else ""


# ---- the status footer must be GENERATED, not typed (IMP-2, Sprint 21) ------
#
# CLAUDE.md: "Generate it with the script every time. Never assemble it by
# hand, and never carry a timestamp forward from an earlier message." A rule
# in a document, and it failed four times in Sprint 21 (1:14am, 1:41am,
# 3:22pm, 3:31pm, all typed; the script read otherwise). This hook already
# runs on every turn, so the check extends it rather than adding a hook.
#
# The check: if the reply ENDS with a footer-shaped line, some
# `status_footer.py` run in the SAME turn must have printed exactly that line.
# It runs before every sprint gate, because footers end replies everywhere.

FOOTER = re.compile(r"^\d{2}/\d{2}/\d{4} \d{1,2}:\d{2}[ap]m \| .+$")

FOOTER_MESSAGE = (
    "The closing footer line was typed, not generated: no status_footer.py run "
    "in this turn printed it.\n  found: {found}\n"
    "Run the venv interpreter on scripts/status_footer.py and end the reply "
    "with its exact output (CLAUDE.md: generate it, never type it).")


def _footer_line(message: str) -> str | None:
    lines = [ln.strip() for ln in message.splitlines() if ln.strip()]
    if lines and FOOTER.match(lines[-1]):
        return lines[-1]
    return None


def _generated_this_turn(transcript_path: str, footer: str) -> bool | None:
    """True if a status_footer.py run since the last user message printed
    `footer`; False if none did; None if the transcript cannot be read.

    Format verified against a real transcript 2026-10-06: the call is a
    `tool_use` block in an assistant entry, its output a `tool_result` string
    in the next user entry, linked by id.
    """
    try:
        entries = [json.loads(ln) for ln in
                   Path(transcript_path).read_text(encoding="utf-8")
                   .splitlines()[-3000:] if ln.strip()]
    except Exception:                                   # noqa: BLE001
        return None

    def blocks(e):
        c = (e.get("message") or {}).get("content")
        return c if isinstance(c, list) else []

    def is_user_turn(e):
        if e.get("type") != "user":
            return False
        c = (e.get("message") or {}).get("content")
        if isinstance(c, str):
            return True
        return not any(isinstance(b, dict) and b.get("type") == "tool_result"
                       for b in (c or []))

    start = 0
    for i, e in enumerate(entries):
        if is_user_turn(e):
            start = i
    turn = entries[start:]

    footer_ids = {b.get("id") for e in turn if e.get("type") == "assistant"
                  for b in blocks(e)
                  if isinstance(b, dict) and b.get("type") == "tool_use"
                  and "status_footer" in json.dumps(b.get("input", {}))}
    for e in turn:
        for b in blocks(e):
            if not (isinstance(b, dict) and b.get("type") == "tool_result"
                    and b.get("tool_use_id") in footer_ids):
                continue
            c = b.get("content")
            text = c if isinstance(c, str) else " ".join(
                x.get("text", "") for x in (c or []) if isinstance(x, dict))
            if footer in (ln.strip() for ln in text.splitlines()):
                return True
    return False


def _check_footer(payload: dict) -> int | None:
    """hooklib.block(...) when a typed footer is found, else None."""
    message = str(payload.get("last_assistant_message") or "")
    footer = _footer_line(message)
    if footer is None:
        return None
    ok = _generated_this_turn(str(payload.get("transcript_path") or ""), footer)
    if ok is False:
        return hooklib.block(FOOTER_MESSAGE.format(found=footer))
    # None: the transcript could not be read. Fail OPEN, like the rest of this
    # hook -- an unreadable transcript must not block every turn.
    return None


def main() -> int:
    payload = hooklib.read_payload()

    # Never re-block an already-blocked stop; that wedges the session.
    if payload.get("stop_hook_active"):
        return hooklib.ALLOW

    typed_footer = _check_footer(payload)
    if typed_footer is not None:
        return typed_footer

    root = _root(payload)
    branch = _branch(payload, root)
    if "allow_stop_hook_bypass" in branch:
        return hooklib.ALLOW

    # Gate 1a: only on a sprint branch.
    m = SPRINT_BRANCH.search(branch)
    if not m:
        return hooklib.ALLOW
    sprint_num = m.group(1)

    # Gate 1b: a plan must exist (Phase 3+).
    if not (root / "docs" / "sprints" /
            f"SPRINT_{sprint_num}_PLAN.md").exists():
        return hooklib.ALLOW

    status = _status(root)

    # Gate 1b2: not yet approved means asking is still correct.
    if status.get("plan_approved") is not True:
        return hooklib.ALLOW

    # Gate 1c: at or past Manual Validation, ending the turn is correct.
    if str(status.get("status", "")) in PAST_VALIDATION:
        return hooklib.ALLOW

    message = str(payload.get("last_assistant_message") or "").strip()
    if not message:
        return hooklib.ALLOW

    # Gate 3: a legitimate stopping signal anywhere in the message.
    if any(p.search(message) for p in LEGITIMATE):
        return hooklib.ALLOW

    # Gate 2: question or commitment, tail-anchored so mid-turn narration
    # followed by real work does not trip it.
    tail = message[-400:]
    if message.rstrip().endswith("?"):
        return hooklib.block(MESSAGE.format(found=message.rstrip()[-160:]))

    for pattern in QUESTION_SHAPED + COMMITMENT:
        hit = pattern.search(tail)
        if hit:
            return hooklib.block(MESSAGE.format(found=hit.group(0)[:160]))

    return hooklib.ALLOW


if __name__ == "__main__":
    sys.exit(main())
