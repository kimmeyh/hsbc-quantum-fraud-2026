"""The status footer must be deterministic, and must never print nothing.

The failure paths matter more than the happy path. A footer that silently drops
a field is the defect this script exists to prevent: the PowerShell version it
replaces printed "Sprint 17" with NO PHASE against this repository's status
file for as long as it was used, because it expected spamfilter-multi's prose
convention and this repo writes snake_case slugs.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "status_footer.py"
WORKFLOW = ROOT / "docs" / "SPRINT_EXECUTION_WORKFLOW.md"

sys.path.insert(0, str(ROOT / "scripts"))
import status_footer as sf  # noqa: E402

# 09/20/2026 12:29pm | Sprint 17 Phase 5.0 Review & Validation
FOOTER = re.compile(
    r"^\d{2}/\d{2}/\d{4} \d{1,2}:\d{2}(?:am|pm) \| Sprint \d+ Phase \d+\.\d+ \S")


def _write(tmp_path: Path, doc) -> Path:
    p = tmp_path / "sprint_status.json"
    p.write_text(doc if isinstance(doc, str) else json.dumps(doc),
                 encoding="utf-8")
    return p


def _run(*args: str) -> str:
    r = subprocess.run([sys.executable, str(SCRIPT), *args],
                       cwd=str(ROOT), capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


# ---------------------------------------------------------------- happy path

def test_the_live_script_matches_the_required_format():
    assert FOOTER.match(_run()), _run()


def test_the_clock_is_read_every_call():
    """Never a timestamp carried forward. This is the original defect."""
    a = sf.build(datetime(2026, 9, 19, 13, 6), None)
    b = sf.build(datetime(2026, 9, 19, 14, 6), None)
    assert "1:06pm" in a and "2:06pm" in b


def test_the_SCRIPT_prints_the_current_time_not_a_baked_in_one():
    """Exercises main(), not build().

    The clock test above calls build() with an explicit datetime, so it cannot
    see a main() that passes a hardcoded date. An injection proved exactly
    that: freezing the clock inside main() broke no test. This asserts the
    subprocess output against the real clock, which is the thing a reader of
    the footer actually depends on.
    """
    now = datetime.now()
    line = _run()
    stamp = line.split(" | ")[0]
    assert stamp.startswith(f"{now.month:02d}/{now.day:02d}/{now.year}"), (
        f"script printed {stamp!r}, today is {now:%m/%d/%Y}")
    hour12 = now.hour % 12 or 12
    assert f"{hour12}:" in stamp, (
        f"script printed {stamp!r}, current hour is {hour12}")


def test_the_date_keeps_its_leading_zero_and_the_hour_drops_its_own():
    """The first version used one strftime plus a string fixup and printed
    9/20/2026, because stripping the hour's zero also stripped the month's."""
    line = sf.build(datetime(2026, 9, 5, 1, 6), None)
    assert line.startswith("09/05/2026 1:06am"), line


def test_midnight_and_noon_are_not_zero_or_twenty_four():
    assert "12:00am" in sf.build(datetime(2026, 9, 5, 0, 0), None)
    assert "12:00pm" in sf.build(datetime(2026, 9, 5, 12, 0), None)


# ------------------------------------------------------------ phase parsing

@pytest.mark.parametrize("slug,expected", [
    ("phase_5_validation", "5.0 Review & Validation"),
    ("phase_1_backlog_refinement", "1.0 Backlog Refinement"),
    ("phase_4_execution", "4.0 Execution"),
    ("phase_8_delivery_cycle", "8.0 Delivery Cycle"),
    ("phase_5_3_manual_validation", "5.3 Review & Validation"),
    ("phase_7_pr_ready", "7.0 Retrospective"),
])
def test_every_slug_this_repo_has_ever_written_parses(slug, expected):
    assert sf.phase_from_status(slug) == expected


def test_the_spamfilter_prose_form_also_parses():
    """Portability: another repo writes the phase as prose."""
    got = sf.phase_from_status("Sprint 70 Phase 5.3 MANUAL VALIDATION -- x")
    assert got == "5.3 Manual Validation"


def test_a_two_digit_phase_is_not_read_as_a_sub_phase():
    """phase_13_x is phase 13, not phase 1.3."""
    assert sf.phase_from_status("phase_13_x").startswith("13.0")


def test_an_undefined_phase_number_is_reported_not_invented():
    got = sf.phase_from_status("phase_99_whatever")
    assert "99" in got and "not in the workflow" in got


def test_phase_names_match_the_workflow_document():
    """The names are held in the script, so drift must fail a test rather than
    print a wrong name."""
    if not WORKFLOW.exists():
        pytest.skip("workflow doc not present")
    text = WORKFLOW.read_text(encoding="utf-8")
    for num, name in sf.PHASE_NAMES.items():
        assert re.search(rf"^#+ *Phase {num}: *{re.escape(name)}", text,
                         re.MULTILINE), (
            f"Phase {num} is '{name}' in the script but not in the workflow")


# ------------------------------------------------------------ failure paths

def test_a_missing_status_file_still_prints_a_usable_line(tmp_path):
    line = sf.build(datetime(2026, 9, 20, 12, 0), tmp_path / "nope.json")
    assert line and "phase unknown" in line and "12:00pm" in line


def test_no_status_file_found_at_all_still_prints(tmp_path):
    line = sf.build(datetime(2026, 9, 20, 12, 0), None)
    assert line.startswith("09/20/2026 12:00pm |")
    assert "unknown" in line


def test_a_malformed_status_file_does_not_raise(tmp_path):
    p = _write(tmp_path, "{ this is not json")
    line = sf.build(datetime(2026, 9, 20, 12, 0), p)
    assert "phase unknown" in line and str(p) in line


def test_a_status_file_with_no_phase_keeps_the_sprint_number(tmp_path):
    """The marker must NAME THE PATH to check, not just say 'phase unknown'.

    Asserting the phrase alone was vacuous: build() falls back to
    `note or 'phase unknown'`, so deleting the note assignment entirely still
    produced the phrase and broke no test. The path is the part that tells the
    reader which file to go and look at.
    """
    p = _write(tmp_path, {"current_sprint": {"number": 17, "status": ""}})
    line = sf.build(datetime(2026, 9, 20, 12, 0), p)
    assert "Sprint 17" in line
    assert "phase unknown" in line
    assert str(p) in line, "the marker does not name the file to check"


def test_a_status_file_with_an_unparseable_phase_says_so(tmp_path):
    p = _write(tmp_path, {"current_sprint": {"number": 17,
                                             "status": "something else"}})
    line = sf.build(datetime(2026, 9, 20, 12, 0), p)
    assert "Sprint 17" in line
    assert "phase unknown" in line
    assert str(p) in line, "the marker does not name the file to check"


def test_an_empty_file_does_not_raise(tmp_path):
    p = _write(tmp_path, "")
    assert "phase unknown" in sf.build(datetime(2026, 9, 20, 12, 0), p)


def test_the_script_never_exits_nonzero_on_a_broken_file(tmp_path):
    p = _write(tmp_path, "{ broken")
    r = subprocess.run([sys.executable, str(SCRIPT), "--status-path", str(p)],
                       cwd=str(ROOT), capture_output=True, text=True)
    assert r.returncode == 0
    assert r.stdout.strip(), "printed nothing"


# ----------------------------------------------------------------- overrides

def test_overrides_win_over_the_file():
    line = _run("--sprint", "99", "--phase", "2.1 Sprint Pre-Kickoff")
    assert "Sprint 99 Phase 2.1 Sprint Pre-Kickoff" in line
