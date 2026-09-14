"""The CHANGELOG must not fall far behind the commits it describes.

F70. The file's own policy says entries are written in the SAME commit as the
change they describe. That policy held for six days and then silently stopped:
CHANGELOG.md ran from 2026-08-29 to 2026-09-04 and then nothing, while Sprints 7
through 13 delivered the whole hardware campaign, three external reviews, the
public-repository flip and the submission. Eight days were missing and nothing
noticed, because a same-commit policy depends on remembering at the moment of
committing.

WHAT THIS CHECKS, AND WHAT IT DELIBERATELY DOES NOT. It does not require an
entry for every day -- that would fail on any quiet weekend and a noisy rule gets
deleted. It requires that the newest entry is not absurdly stale relative to the
newest commit, which is the state that actually went unnoticed for eight days.

THE THRESHOLD WAS SET BY INJECTION, NOT BY JUDGEMENT, AND THE FIRST VALUE WAS
WRONG. It was written as 14 days on the reasoning that a fortnight is generous.
Injecting the real lapse -- deleting 2026-09-05 through 09-12 -- left the guard
GREEN, because the gap that went unnoticed for seven sprints is only eight days
wide. A guard that passes on the exact defect it was written for asserts
nothing, which is the vacuous-guard failure the injection standard exists to
catch, and it was caught here only because the injection was actually run.

The threshold is now 5 days: comfortably wider than this project's roughly daily
sprint rhythm, and narrower than the eight-day lapse that motivated the test.

Verified by injection: removing 2026-09-05 through 09-12 fails with the measured
gap; restoring them passes.
"""
from __future__ import annotations

import re
import subprocess
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CHANGELOG = ROOT / "CHANGELOG.md"

# Days between the newest commit and the newest CHANGELOG entry before this
# fails. Must be SMALLER than the eight-day lapse that motivated the test, or
# the guard passes on its own defect -- which it did at 14. See the module
# docstring.
MAX_LAG_DAYS = 5

_DATE = re.compile(r"^### (\d{4})-(\d{2})-(\d{2})\s*$", re.M)


def _newest_entry() -> date | None:
    if not CHANGELOG.exists():
        return None
    found = [date(int(y), int(m), int(d))
             for y, m, d in _DATE.findall(CHANGELOG.read_text(encoding="utf-8"))]
    return max(found) if found else None


def _newest_commit() -> date | None:
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cd", "--date=short"],
            cwd=ROOT, capture_output=True, text=True, timeout=30)
    except Exception:                                    # noqa: BLE001
        return None
    raw = out.stdout.strip()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
        return None
    y, m, d = raw.split("-")
    return date(int(y), int(m), int(d))


@pytest.mark.skipif(not CHANGELOG.exists(), reason="no CHANGELOG.md")
def test_the_changelog_is_not_badly_stale():
    """The newest entry must be within MAX_LAG_DAYS of the newest commit."""
    entry = _newest_entry()
    assert entry is not None, (
        "CHANGELOG.md holds no `### YYYY-MM-DD` entry at all")

    commit = _newest_commit()
    if commit is None:
        pytest.skip("git log unavailable (shallow clone or no git)")

    lag = (commit - entry).days
    assert lag <= MAX_LAG_DAYS, (
        f"the newest CHANGELOG entry is {entry} but the newest commit is "
        f"{commit}, a gap of {lag} days. Workflow 8.1.1 reconciles the "
        f"CHANGELOG before backlog refinement, every delivery cycle. The lapse "
        f"this guard exists for ran to eight days across seven sprints and cost "
        f"about ninety minutes to reconstruct.")


@pytest.mark.skipif(not CHANGELOG.exists(), reason="no CHANGELOG.md")
def test_changelog_entries_are_in_newest_first_order():
    """The file's stated format is newest first; out-of-order entries hide gaps.

    A date inserted in the wrong place reads as present while sitting where
    nobody looks, which is how a missing day survives a skim.
    """
    text = CHANGELOG.read_text(encoding="utf-8")
    dates = [date(int(y), int(m), int(d)) for y, m, d in _DATE.findall(text)]
    if len(dates) < 2:
        pytest.skip("fewer than two dated entries")
    out_of_order = [(a, b) for a, b in zip(dates, dates[1:]) if a < b]
    assert not out_of_order, (
        f"CHANGELOG entries are not newest-first: {out_of_order}")
