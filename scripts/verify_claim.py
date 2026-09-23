"""Before asserting a contradiction, find out who has already answered it.

F88, Sprint 18 Task F. Twice in Sprint 17 a "finding" was written down that
was an incomplete reading of an artifact, and both times the correct answer
was already recorded in a file that had not been opened:

  1. The Sprint 17 plan asserted in bold that the QPU arithmetic "DOES NOT
     RECONCILE". It reconciles exactly. `billed_s` was counted while 24 of 25
     paid rows carry `measured_seconds` instead. A reviewer made a version of
     the same error in Sprint 12 and `SPRINT_12_SUMMARY.md` records how it was
     settled.
  2. Task D reported A31 (16.0) and the appendix (28.0) contradicting each
     other on the linear-term span, and claimed the artifact recorded neither.
     `device_resolution.json` carries every figure in a `per_pool` array;
     only the summary block had been read. Amendment A32 had already corrected
     this ON THE DAY OF SUBMISSION.

WHY A SEARCH AND NOT A RULE. The retrospective first proposed "grep the
summaries before writing any such claim". The team lead declined it: a step
that fires on every claim is a tax that prevents nothing structurally, and it
is better to get it right the first time. The difference here is that this
takes one command and returns the specific files that mention the figure,
including the amendment log -- so "has this already been answered?" stops being
a memory exercise.

WHAT IT DOES NOT DO. It does not judge whether a claim is true. It reports
where a figure appears so the writer reads those files first. A clean result
means nothing else mentions the figure, NOT that the claim is correct.

Usage:
    python scripts/verify_claim.py 1,141
    python scripts/verify_claim.py 28.0 --amendment A31
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Searched in priority order. The amendment log and the sprint record are
# FIRST because that is where both Sprint 17 answers already sat.
# `docs` already covers docs/sprints recursively, so listing both was
# REDUNDANT: dropping docs/sprints changed no result, which an injection
# proved by staying green. Redundant entries make a search look broader than
# it is, and the ranking below -- not this tuple -- is what puts the sprint
# record in front of the reader.
SEARCH_PATHS = (
    "experiments/PREREGISTRATION.md",
    "experiments/results",
    "docs",
    "CHANGELOG.md",
)

# A file that resolves a question, as opposed to one that merely repeats a
# figure. Hits here are reported first and loudest.
AUTHORITATIVE = (
    "PREREGISTRATION.md",
    "_SUMMARY.md",
    "_RETROSPECTIVE.md",
    "QPU_RECONCILIATION.md",
)


class SearchFailed(RuntimeError):
    """The search could not run. NOT the same as finding nothing.

    This script answers "who has already spoken about this figure?", and a
    wrong answer of "nobody" is the one that does damage: it invites a
    contradiction of a number some authoritative file already settled. The
    first version returned an empty list when git failed and when no search
    path existed, so a broken search was indistinguishable from a clean one.
    Found by the PR #139 review.
    """


def _git_grep(pattern: str, paths: tuple[str, ...]) -> list[str]:
    existing = [p for p in paths if (ROOT / p).exists()]
    if not existing:
        raise SearchFailed(
            "none of the search paths exists: " + ", ".join(paths))
    r = subprocess.run(
        ["git", "grep", "-l", "-F", "--", pattern, *existing],
        cwd=str(ROOT), capture_output=True, text=True)
    # git grep exits 1 when nothing matches, which is not an error here.
    if r.returncode not in (0, 1):
        raise SearchFailed(
            f"git grep exited {r.returncode}: {r.stderr.strip()[:200]}")
    return sorted({ln.strip() for ln in r.stdout.splitlines() if ln.strip()})


def amendments_mentioning(figure: str) -> list[str]:
    """Amendment IDs whose log entry contains the figure.

    Instance 2 would have been stopped here: A32 names the corrected span.
    """
    prereg = ROOT / "experiments" / "PREREGISTRATION.md"
    if not prereg.exists():
        return []
    found = []
    for line in prereg.read_text(encoding="utf-8").splitlines():
        if figure in line:
            for m in re.finditer(r"\(A(\d+)\)", line):
                found.append(f"A{m.group(1)}")
    return sorted(set(found), key=lambda a: int(a[1:]))


def report(figure: str, amendment: str | None = None) -> int:
    print(f"FIGURE: {figure}")
    print("=" * 66)

    try:
        files = _git_grep(figure, SEARCH_PATHS)
    except SearchFailed as exc:
        print(f"  THE SEARCH DID NOT RUN: {exc}")
        print()
        print("  This is NOT a result. Nothing was checked, so nothing can be")
        print("  concluded about who has already spoken about this figure.")
        return 2
    amends = amendments_mentioning(figure)

    if not files:
        print("  No tracked file mentions it.")
        print()
        print("  That means nothing has answered this yet -- NOT that a claim")
        print("  about it is correct.")
        return 0

    authoritative = [f for f in files
                     if any(a in f for a in AUTHORITATIVE)]
    other = [f for f in files if f not in authoritative]

    if authoritative:
        print(f"  {len(authoritative)} AUTHORITATIVE file(s) mention it.")
        print("  Read these BEFORE asserting a contradiction:")
        for f in authoritative:
            print(f"    {f}")
    if other:
        print(f"\n  {len(other)} other file(s):")
        for f in other:
            print(f"    {f}")

    if amends:
        print(f"\n  AMENDMENTS naming this figure: {', '.join(amends)}")
        print("  An amendment that names your figure has probably already")
        print("  settled it. A32 did exactly that in Sprint 17, on the day of")
        print("  submission, for a contradiction reported five days later.")

    if amendment:
        rest = [a for a in amends if a != amendment]
        if rest:
            print(f"\n  {amendment} is not the last word: {', '.join(rest)} "
                  "also name this figure.")

    print()
    print("  This tool does not judge the claim. It reports who has already")
    print("  spoken about the figure so those files are read first.")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("figure", help="the figure or phrase, e.g. 1,141 or 28.0")
    ap.add_argument("--amendment", default=None,
                    help="an amendment you believe is authoritative, e.g. A31")
    args = ap.parse_args(argv)
    return report(args.figure, args.amendment)


if __name__ == "__main__":
    sys.exit(main())
