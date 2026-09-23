"""verify_claim must surface the file that already answered the question.

F88 acceptance, Sprint 18 Task F. The two Sprint 17 false findings are the
test cases, and both are reproducible from committed artifacts:

  1. "QPU ARITHMETIC DOES NOT RECONCILE YET" (Sprint 17 plan). It reconciles
     exactly. SPRINT_12_SUMMARY.md records a reviewer making a version of the
     same error and how the live endpoint settled it.
  2. "A31 says 16.0, the appendix says 28.0, the artifact records neither"
     (Task D). device_resolution.json carries every figure in a per_pool
     array, and amendment A32 corrected this ON THE DAY OF SUBMISSION -- five
     days before the contradiction was reported.

The tool does not judge a claim. It answers "who has already spoken about this
figure?", which is the question neither instance asked.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "verify_claim.py"

sys.path.insert(0, str(ROOT / "scripts"))


def _run(*args: str) -> str:
    r = subprocess.run([sys.executable, str(SCRIPT), *args],
                       cwd=str(ROOT), capture_output=True, text=True)
    assert r.returncode == 0, f"exited {r.returncode}: {r.stderr[:300]}"
    return r.stdout


def test_the_script_exists():
    assert SCRIPT.exists()


# ------------------------------------------- Sprint 17 instance 1

def test_the_qpu_total_surfaces_the_sprint_that_already_settled_it():
    """SPRINT 17 INSTANCE 1. A reviewer made this error in Sprint 12 and the
    summary records the resolution. Surfacing that file is the whole job."""
    out = _run("1,141")
    assert "SPRINT_12_SUMMARY.md" in out, (
        "the file recording the same error being settled was not surfaced")
    assert "AUTHORITATIVE" in out


def test_the_qpu_total_surfaces_the_reconciliation_document():
    out = _run("1,141")
    assert "QPU_RECONCILIATION.md" in out


# ------------------------------------------- Sprint 17 instance 2

def test_the_linear_span_surfaces_the_amendment_that_corrected_it():
    """SPRINT 17 INSTANCE 2. A32 corrected A31's figure on the day of
    submission. Naming it is what would have stopped the false finding."""
    out = _run("28.0")
    assert "A32" in out, "the correcting amendment was not surfaced"
    assert "AMENDMENTS naming this figure" in out


def test_the_linear_span_surfaces_the_artifact_claimed_to_be_missing():
    """The finding asserted device_resolution.json recorded neither figure.
    It carries both, in a per_pool array below the summary block."""
    out = _run("28.0")
    assert "device_resolution.json" in out


def test_naming_a_superseded_amendment_is_flagged():
    """If the writer believes A31 is authoritative, the tool must say that a
    later amendment also names the figure."""
    out = _run("28.0", "--amendment", "A31")
    assert "A31 is not the last word" in out
    assert "A32" in out


# --------------------------------------------------- honest behaviour

def test_an_unmentioned_figure_says_nothing_has_answered_it():
    """A clean result must not read as 'your claim is correct'. Conflating
    'nobody has spoken' with 'you are right' would make this tool an instance
    of the class it exists to prevent."""
    out = _run("99999999.12345")
    assert "No tracked file mentions it" in out
    # Whitespace collapsed: the message is hard-wrapped, so a raw substring
    # search misses a phrase that spans the wrap. Match what a READER sees.
    assert "NOT that a claim about it is correct" in " ".join(out.split())


def test_the_tool_disclaims_judging_the_claim():
    out = _run("1,141")
    assert "does not judge the claim" in out


def test_authoritative_files_are_listed_before_the_others():
    """Ordering is the affordance. A flat list of sixteen files invites
    skimming; the amendment log and the sprint record come first because that
    is where both Sprint 17 answers sat."""
    out = _run("1,141")
    auth = out.index("AUTHORITATIVE")
    other = out.index("other file(s)")
    assert auth < other


def test_it_never_exits_nonzero_on_a_figure_with_no_hits():
    r = subprocess.run([sys.executable, str(SCRIPT), "zzz-no-such-figure"],
                       cwd=str(ROOT), capture_output=True, text=True)
    assert r.returncode == 0
    assert r.stdout.strip()


def test_a_regex_metacharacter_is_treated_literally():
    """Searches use -F. A figure like 1.26.4 must not be read as a pattern."""
    out = _run("1.26.4")
    assert "FIGURE: 1.26.4" in out


# ------------------------------------------------- guard the guard

def test_the_amendment_scan_actually_finds_amendments():
    """Negative assertions above would all pass on a scanner that returns
    nothing. This one fails if the scan is blind."""
    import verify_claim
    found = verify_claim.amendments_mentioning("28.0")
    assert found, "the amendment scan found nothing in a log that names 28.0"
    assert "A32" in found


def test_the_preregistration_is_listed_as_a_file_not_only_scanned():
    """The amendment log must appear in the FILE LIST, not merely be read by
    `amendments_mentioning`.

    Found by the F89 helper: dropping experiments/PREREGISTRATION.md from
    SEARCH_PATHS broke no test, because the amendment scan opens that file
    directly. So the search could stop covering the log entirely while every
    assertion still passed -- a guard with a hole exactly where it matters
    most, since the log is where both Sprint 17 answers sat.
    """
    out = _run("28.0")
    listed = out.split("AMENDMENTS naming this figure")[0]
    assert "PREREGISTRATION.md" in listed, (
        "the amendment log is not in the surfaced file list; the search no "
        "longer covers it")


def test_a_failed_search_is_not_reported_as_nothing_found(monkeypatch):
    """This script answers "who has already spoken about this figure?", and a
    wrong answer of "nobody" is the one that does damage: it invites a
    contradiction of a number some authoritative file already settled.

    A git failure used to warn on stderr and return an empty list, which the
    caller printed as "nothing has answered this yet". Found by the PR #139
    review.
    """
    import verify_claim as vc

    class Failed:
        returncode = 128
        stdout = ""
        stderr = "fatal: not a git repository"

    monkeypatch.setattr(vc.subprocess, "run", lambda *a, **k: Failed())
    rc = vc.report("0.0245")
    assert rc == 2, f"a failed search returned {rc}, not a failure code"


def test_missing_search_paths_are_not_reported_as_nothing_found(monkeypatch):
    """The other entry point to the same wrong answer: every search path
    gone, which happens when a directory is renamed."""
    import verify_claim as vc
    monkeypatch.setattr(vc, "SEARCH_PATHS", ("no/such/dir",))
    assert vc.report("0.0245") == 2


def test_a_figure_nobody_mentions_is_still_distinguishable(monkeypatch):
    """The companion. "Searched and found nothing" must remain a DIFFERENT
    outcome from "could not search" -- otherwise the fix above just moves the
    conflation instead of removing it."""
    import verify_claim as vc
    assert vc.report("0.31415926535") == 0
