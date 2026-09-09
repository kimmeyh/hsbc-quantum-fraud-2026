"""Every runner that writes an evidence file must have a test that READS it.

Sprint 9 improvement 1, and it is enforced here rather than left as advice.

WHY. Six tests of run_h6.py passed while the arm was measuring the wrong thing.
The defect was not in any code path: two of three classical twins never
received the representation under test, so the classical bar was not the bar
the preregistration specifies. The code ran, the numbers were plausible, and
7h 42m of compute had to be discarded. A second defect the same sprint -- a
spline basis refitted on test data -- was caught only because it eventually
crashed, having been silently wrong for two full runs before that.

Guarding the code caught neither. Guarding the ARTIFACT would have caught both.

So this module asserts a PROPERTY OF THE TEST SUITE: for every runner writing
an evidence file, some test somewhere opens that file and asserts something
about its contents. It does not check that the assertion is a good one -- that
is a judgment no test can make -- only that the artifact is looked at, because
in both Sprint 9 failures nothing looked at it.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parent

# A runner is exempt only with a reason, and the reason is reviewed like code.
EXEMPT: dict[str, str] = {}


def _evidence_files() -> dict[str, list[str]]:
    """{runner filename: [evidence json it writes]}.

    Covers the three write idioms this repo actually uses. A runner that
    invents a fourth will not be seen here, so the convention is part of the
    guard -- and widening it is cheaper than the alternative, which is a guard
    that reads as reassurance while exempting whole classes of writer.
    """
    out: dict[str, list[str]] = {}
    for f in sorted(SRC.glob("run_*.py")):
        text = f.read_text(encoding="utf-8", errors="ignore")
        # Three idioms in this repo: OUT/CHECKPOINT module constants, the
        # RESULTS constant (run_classical), and store.append_row, which writes
        # to the shared results.json. The first version of this guard matched
        # only the first idiom and so silently exempted every append_row
        # writer -- a guard that quietly covers less than it claims is worse
        # than none, because it reads as reassurance.
        names = re.findall(r'^(?:OUT|CHECKPOINT|RESULTS)\s*=.*?/ "([\w.]+\.json)"',
                           text, re.M)
        if "append_row(" in text and "results.json" not in names:
            names.append("results.json")
        # SMOKE_OUT is deliberately excluded: smoke output is not evidence.
        if names:
            out[f.name] = names
    return out


def _tests_reading(name: str) -> list[str]:
    """Test modules that open the named results file."""
    hits = []
    for t in sorted(SRC.glob("test_*.py")):
        if t.name == Path(__file__).name:
            continue
        if name in t.read_text(encoding="utf-8", errors="ignore"):
            hits.append(t.name)
    return hits


def test_at_least_one_runner_writes_evidence():
    """Guard the guard: a broken discovery regex must not pass vacuously."""
    found = _evidence_files()
    assert found, (
        "no runner evidence files discovered; the OUT/CHECKPOINT pattern in "
        "_evidence_files() has probably drifted from the runners")


@pytest.mark.parametrize("runner", sorted(_evidence_files()))
def test_runner_evidence_file_is_read_by_some_test(runner):
    """Some test must open this runner's committed output.

    Not "the code is correct" -- that is what the runner's own tests are for.
    This asserts that the ARTIFACT is inspected, which is the check that was
    missing when a completed 20-cell run had to be thrown away.
    """
    if runner in EXEMPT:
        pytest.skip(f"{runner}: {EXEMPT[runner]}")

    files = _evidence_files()[runner]
    unread = [f for f in files if not _tests_reading(f)]
    assert not unread, (
        f"{runner} writes {unread} and no test reads any of them. A test of "
        f"the CODE passed in Sprint 9 while the experiment was wrong; the test "
        f"that caught it reads the shipped results file. Add one that opens "
        f"the artifact and asserts a property the preregistration requires, or "
        f"add {runner} to EXEMPT with a reason.")
