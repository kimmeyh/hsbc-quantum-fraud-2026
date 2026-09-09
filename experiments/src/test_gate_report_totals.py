"""The gate report's campaign total must equal what results.json holds.

score_gates.py is the file CLAUDE.md names as the verification path for every
reported number. It filtered hardware rows with `arm == "cvqboost_hw"`, which
silently dropped the 10 cvqboost_hw_mixed fits, so the generated report said
27 fits / 120.0 s while results.json held 37 / 163.0 s.

That is how the submission came to contradict itself: the appendix quoted the
true 37/163 and the proposal and team profile quoted the report's 27/120. A
reviewer found it, not us, and the tool that exists to catch exactly this class
of error was the source of it.

These tests read the artifact and the store and compare them. They do not
recompute the numbers a different way, because the point is agreement between
the two things the submission cites.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "experiments" / "results" / "results.json"
REPORT = ROOT / "experiments" / "results" / "gate_report.md"


def _rows():
    d = json.loads(RESULTS.read_text(encoding="utf-8"))
    return d if isinstance(d, list) else d["rows"]


def _metered():
    """Every row that actually consumed device seconds, by whatever arm."""
    return [r for r in _rows()
            if r.get("status") == "ok" and (r.get("metered_seconds") or 0)]


def test_report_fit_count_matches_the_store():
    n = len(_metered())
    m = re.search(r"(\d+) successful fits", REPORT.read_text(encoding="utf-8"))
    assert m, "campaign-total line missing from gate_report.md"
    assert int(m.group(1)) == n, (
        f"gate_report.md says {m.group(1)} fits, results.json holds {n}. The "
        f"arm filter in score_gates.py has probably narrowed again.")


def test_report_metered_seconds_match_the_store():
    total = sum(float(r["metered_seconds"]) for r in _metered())
    m = re.search(r"metered seconds recorded: ([\d.]+)", REPORT.read_text(encoding="utf-8"))
    assert m, "metered-seconds figure missing from gate_report.md"
    assert abs(float(m.group(1)) - total) < 0.05, (
        f"gate_report.md says {m.group(1)} s, results.json holds {total} s")


def test_every_metered_arm_appears_in_the_breakdown():
    """A new metered arm must show up, not be silently absorbed into a total."""
    arms = {r["arm"] for r in _metered()}
    line = REPORT.read_text(encoding="utf-8")
    m = re.search(r"By arm: (.+?)\.$", line, re.MULTILINE)
    assert m, "per-arm breakdown missing; it is what makes the total auditable"
    for arm in arms:
        assert arm in m.group(1), (
            f"metered arm {arm!r} is absent from the gate report's per-arm "
            f"breakdown, so its seconds are invisible in the audit trail")


def test_the_guard_would_catch_the_original_bug():
    """Guard the guard: cvqboost_hw alone must NOT satisfy the total.

    If someone re-narrows the filter, the count reverts to the single arm. This
    asserts the store genuinely holds more than one metered arm, so the tests
    above are not passing vacuously on a single-arm dataset.
    """
    arms = {r["arm"] for r in _metered()}
    assert len(arms) > 1, (
        "only one metered arm in results.json; these tests cannot detect the "
        "narrowing bug they exist to prevent")
