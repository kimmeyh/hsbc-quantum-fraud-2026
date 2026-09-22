"""Emit the status footer line, deterministically.

    09/20/2026 12:28pm | Sprint 17 Phase 5.0 Review And Validation

WHY A SCRIPT AND NOT A TYPED LINE. On 2026-09-19 a hand-assembled footer
reported a timestamp an hour stale, copied forward from an earlier message in
the same conversation. The sprint number and phase in that same line were
correct, because they came from a file that was actually read. The one field
filled from memory was the one that was wrong. Every field here is read at call
time or it is reported as unknown.

WHY PYTHON AND NOT THE EXISTING POWERSHELL. Two reasons, both measured rather
than assumed:

  1. The PowerShell script at ~/.claude/scripts/status-footer.ps1 expects the
     status field to read "Sprint 70 Phase 5.3 MANUAL VALIDATION", which is
     spamfilter-multi's convention. THIS repository writes snake_case slugs
     ("phase_5_validation"). The regex does not match, so the phase is silently
     dropped and the footer prints "Sprint 17" with no phase at all. A footer
     that quietly loses a field is the same class of defect as the stale
     timestamp it was written to prevent.
  2. F78 (Sprint 16) converted every hook and script in this repository from
     PowerShell to Python, because CI runs ubuntu-latest and a .ps1 cannot run
     there. Adding a new PowerShell dependency would reintroduce exactly what
     that sprint removed.

FAILURE BEHAVIOR, which matters more than the happy path. This never raises and
never prints nothing. A missing, malformed or phase-less status file yields the
date and time plus an honest marker naming the path to check. A footer with an
unknown phase is strictly better than no footer, because the reader can see
that the phase is unknown rather than assuming the last one they saw.

Usage:
    python scripts/status_footer.py
    python scripts/status_footer.py --phase "5.3 Manual Validation"
    python scripts/status_footer.py --sprint 18
    python scripts/status_footer.py --status-path /path/to/sprint_status.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# The authoritative phase names, from docs/SPRINT_EXECUTION_WORKFLOW.md.
# Held here rather than parsed from the document on every call: the workflow is
# prose with headings, and a parser over prose is a second thing that can break
# silently. test_status_footer.py asserts these against the document, so drift
# fails a test instead of printing a wrong name.
PHASE_NAMES = {
    1: "Backlog Refinement",
    2: "Sprint Pre-Kickoff",
    3: "Kickoff & Planning",
    4: "Execution",
    5: "Review & Validation",
    6: "Push & Finalize PR",
    7: "Retrospective",
    8: "Delivery Cycle",
}

# "phase_5_validation" -> (5, None); "phase_5_3_manual_validation" -> (5, 3).
# Anchored at the start: prose later in the field must never be mistaken for
# the phase. A sub-phase is only recognised when the digit group is followed by
# another underscore-word, so "phase_13_x" reads as phase 13, not 1.3.
SLUG = re.compile(r"^phase_(\d+)(?:_(\d+))?(?:_|$)")

# The spamfilter-multi form, accepted so this script is portable to a repo that
# writes "Sprint 70 Phase 5.3 MANUAL VALIDATION -- ...".
PROSE = re.compile(r"(?i)^\s*(?:sprint\s+\d+\s+)?phase\s+(\d+)(?:\.(\d+))?\s+([^.\-(]+)")


def find_status_file(start: Path | None = None) -> Path | None:
    """Walk up from `start` looking for .claude/sprint_status.json."""
    here = (start or Path.cwd()).resolve()
    for d in [here, *here.parents]:
        candidate = d / ".claude" / "sprint_status.json"
        if candidate.is_file():
            return candidate
    return None


def phase_from_status(status: str) -> str | None:
    """Render a status field as 'n.n Name', or None if it carries no phase."""
    if not status:
        return None

    m = SLUG.match(status.strip())
    if m:
        major = int(m.group(1))
        minor = int(m.group(2)) if m.group(2) else 0
        name = PHASE_NAMES.get(major)
        if name is None:
            # A phase number the workflow does not define. Report the number
            # rather than inventing a name for it.
            return f"{major}.{minor} (phase {major} not in the workflow)"
        return f"{major}.{minor} {name}"

    m = PROSE.match(status.strip())
    if m:
        major = int(m.group(1))
        minor = int(m.group(2)) if m.group(2) else 0
        name = m.group(3).strip()
        if name.isupper():
            name = name.title()
        return f"{major}.{minor} {name}"

    return None


def build(now: datetime, status_path: Path | None,
          sprint: str | None = None, phase: str | None = None) -> str:
    """The footer line. Never raises."""
    # Built field by field rather than with one strftime and a string fixup.
    # The DATE keeps its leading zero (09/20/2026) and the HOUR drops its own
    # (1:06pm, not 01:06pm), so a blanket replace of " 0" or "^0" corrupts one
    # to fix the other -- which it did on the first run, printing 9/20/2026.
    #
    # %-d and %-I would do this natively but are not portable to Windows, so
    # the hour is computed directly. Nothing here is culture-sensitive: a
    # locale-aware %p renders EMPTY on some non-US machines and a locale-aware
    # date separator can become '.', silently producing a different format.
    hour12 = now.hour % 12 or 12
    meridiem = "am" if now.hour < 12 else "pm"
    stamp = (f"{now.month:02d}/{now.day:02d}/{now.year} "
             f"{hour12}:{now.minute:02d}{meridiem}")

    read_sprint, read_phase = None, None
    note = None

    if status_path is None:
        note = "phase unknown -- no .claude/sprint_status.json found"
    else:
        try:
            doc = json.loads(status_path.read_text(encoding="utf-8"))
            cur = doc.get("current_sprint") or {}
            if cur.get("number") is not None:
                read_sprint = str(cur["number"])
            read_phase = phase_from_status(str(cur.get("status") or ""))
            if read_phase is None:
                note = f"phase unknown -- check {status_path}"
        except (OSError, ValueError, TypeError, AttributeError):
            note = f"phase unknown -- check {status_path}"

    sprint = sprint or read_sprint
    phase = phase or read_phase

    if sprint and phase:
        return f"{stamp} | Sprint {sprint} Phase {phase}"
    # AN EXPLICITLY SUPPLIED PHASE IS NEVER DISCARDED. The first version fell
    # straight through to the last line when no sprint was found, so
    # `--phase "5.3 Manual Validation"` outside a sprint repo printed "phase
    # unknown" -- reintroducing the exact silent phase drop this script exists
    # to replace. Found by the PR #122 review.
    if phase:
        # The note says "phase unknown", which is now false -- the caller
        # supplied it. Report only what IS unknown here.
        why = ""
        if note:
            why = note.split("--", 1)[1].strip() if "--" in note else ""
        return f"{stamp} | Phase {phase} (sprint unknown{f' -- {why}' if why else ''})"
    if sprint:
        return f"{stamp} | Sprint {sprint} {note or 'phase unknown'}"
    return f"{stamp} | {note or 'sprint and phase unknown'}"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sprint", default=None, help="override the sprint number")
    ap.add_argument("--phase", default=None,
                    help='override the phase, as "n.n Name"')
    ap.add_argument("--status-path", default=None,
                    help="path to sprint_status.json (tests override this)")
    args = ap.parse_args(argv)

    path = (Path(args.status_path) if args.status_path
            else find_status_file())
    print(build(datetime.now(), path, args.sprint, args.phase))
    return 0


if __name__ == "__main__":
    sys.exit(main())
