"""Update `.claude/sprint_status.json` without hand-editing it.

Converted from PowerShell 2026-09-17 (F78, Sprint 16).

Hand-editing that file is how it went stale twice: Sprint 12 ran with
`phase_4_execution` and `pr: null` against a sprint that had already merged two
PRs, and an automated reviewer quoted the stale value. Sprint 16 had
`plan_approved: true` with `pr: null` and an empty `github_issues` while ten
issues existed, caught by the close-out hook rather than by inspection.

Usage:
    python scripts/update_sprint_status.py --set status=phase_6_push
    python scripts/update_sprint_status.py --set pr=120 --set plan_approved=true
    python scripts/update_sprint_status.py --set last_completed_sprint.number=15
    python scripts/update_sprint_status.py --new-sprint 17 \\
        --name "The Next Thing" --branch feature/20260918_Sprint_17 \\
        --plan-doc docs/sprints/SPRINT_17_PLAN.md

Values are typed: `true`/`false` become booleans, `null` becomes null, digits
become integers, everything else stays a string. A bare key targets
`current_sprint`; a dotted key names its section.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

STATUS = Path(__file__).resolve().parents[1] / ".claude" / "sprint_status.json"


def typed(value: str):
    low = value.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    if low == "null":
        return None
    if value.isdigit():
        return int(value)
    return value


def apply_set(doc: dict, assignment: str) -> str:
    if "=" not in assignment:
        raise SystemExit(f"--set needs key=value, got {assignment!r}")
    key, raw = assignment.split("=", 1)
    key = key.strip()

    section_name = "current_sprint"
    if "." in key:
        section_name, key = key.split(".", 1)

    if section_name not in doc:
        raise SystemExit(
            f"Unknown section {section_name!r} in {assignment!r}. "
            f"Sections: {', '.join(doc)}")

    section = doc[section_name]
    if not isinstance(section, dict):
        raise SystemExit(f"Section {section_name!r} is not an object")

    # An UNKNOWN KEY IS A HARD ERROR, never a silent add. Carried from the
    # PowerShell original, whose header stated it explicitly, and dropped by
    # mistake in the Sprint 16 conversion. Found by Copilot on PR #120.
    #
    # Why this matters more than catching a typo: `--set stauts=phase_6_push`
    # returned 0, created a bogus `stauts` field, and left the REAL status
    # stale. That is precisely the went-stale-twice failure this tool exists to
    # prevent, so a silent add makes the tool an instance of its own problem.
    if key not in section:
        raise SystemExit(
            f"Unknown key {key!r} in section {section_name!r} ({assignment!r}). "
            f"Known keys: {', '.join(sorted(section))}")

    before = section[key]
    section[key] = typed(raw)
    return f"  {section_name}.{key}: {before!r} -> {section[key]!r}"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE",
                    help="assign a field; repeatable")
    ap.add_argument("--new-sprint", type=int, default=0,
                    help="roll to this sprint number")
    ap.add_argument("--name", default="")
    ap.add_argument("--branch", default="")
    ap.add_argument("--plan-doc", default="")
    ap.add_argument("--path", default=str(STATUS),
                    help="status file (tests override this)")
    args = ap.parse_args(argv)

    path = Path(args.path)
    if not path.exists():
        raise SystemExit(f"{path} does not exist")

    doc = json.loads(path.read_text(encoding="utf-8"))
    changes: list[str] = []

    if args.new_sprint > 0:
        cur = doc.get("current_sprint", {})
        doc["last_completed_sprint"] = {
            "number": cur.get("number"),
            "merged_pr": cur.get("pr"),
            "main_merge_pr": None,
            # Deliberately False: the triad is not complete until the
            # retrospective and summary exist, and claiming otherwise here is
            # what let Sprint 15 merge without a retrospective.
            "docs_triad_complete": False,
        }
        doc["current_sprint"] = {
            "number": args.new_sprint,
            "name": args.name,
            "branch": args.branch,
            "status": "phase_1_backlog_refinement",
            "plan_doc": args.plan_doc,
            "pr": None,
            "plan_approved": False,
            "github_issues": [],
        }
        changes.append(f"  rolled to sprint {args.new_sprint} "
                       f"(previous: {doc['last_completed_sprint']['number']})")

    for assignment in args.set:
        changes.append(apply_set(doc, assignment))

    if not changes:
        print("nothing to do; pass --set or --new-sprint")
        return 0

    # The original stamped this on every write, and the conversion dropped it.
    # Found while verifying Copilot's finding against the retired script, so it
    # is a SECOND regression from the same conversion. A status file nobody can
    # date is one nobody can tell is stale, which is the failure that put
    # `phase_4_execution` against a sprint with two merged PRs.
    doc["updated"] = date.today().isoformat()

    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")

    # Re-read and re-parse rather than trusting the write.
    json.loads(path.read_text(encoding="utf-8"))

    print(f"{path}:")
    for line in changes:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
