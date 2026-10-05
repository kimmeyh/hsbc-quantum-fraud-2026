"""The F100 pilot sizes every lane and names the dominant one.

Sprint 21 Task D. Sprint 9 improvement 2 requires the dominant runtime term to
be NAMED with its measurement, because Sprint 9 sized the twins and the GBDTs
from real fits, missed the CVQBoost pool build entirely, and came in 47x over.

These guards pin that the pilot measures each lane SEPARATELY (a single total
cannot name a dominant term), that it covers all five lanes F100's card lists,
and that its recorded result stays consistent with the document interpreting
it.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parent
ROOT = SRC.parents[1]
sys.path.insert(0, str(SRC))

RESULT = ROOT / "experiments" / "results" / "f100_lane_pilot.json"
DOC = ROOT / "docs" / "F100_LANE_PILOT.md"

# F100's card: "LogReg, GAM, GA2M, HGB and an order-matched JOINT twin".
REQUIRED_LANES = {"logreg", "gam_additive", "ga2m", "hgb", "joint_twin"}


def _result():
    if not RESULT.exists():
        pytest.skip(f"{RESULT.name} not present; run f100_lane_pilot.py")
    return json.loads(RESULT.read_text(encoding="utf-8"))


def test_the_pilot_covers_every_lane_f100_promises():
    """A bar missing a lane is not a complete bar, and the JOINT twin is the
    one that decides how a win reads: omitting it is how the Fourier Wall
    paper shows a fake quantum win (docs/references.md)."""
    r = _result()
    got = {l["lane"] for l in r["lanes"]}
    assert REQUIRED_LANES <= got, (
        f"the pilot is missing lane(s): {sorted(REQUIRED_LANES - got)}")


def test_every_lane_is_timed_individually():
    """One total cannot name a dominant term. This is the whole mechanism."""
    r = _result()
    for lane in r["lanes"]:
        assert "elapsed_s" in lane, f"{lane['lane']} carries no timing"
        assert isinstance(lane["elapsed_s"], (int, float))


def test_the_dominant_lane_is_named_and_is_really_the_slowest():
    r = _result()
    ok = [l for l in r["lanes"] if l["status"] == "ok"]
    if not ok:
        pytest.skip("no successful lanes recorded")
    assert r["dominant_lane"] is not None, (
        "Sprint 9 improvement 2: the dominant term must be NAMED")
    slowest = max(ok, key=lambda l: l["elapsed_s"])
    assert r["dominant_lane"] == slowest["lane"], (
        f"recorded dominant lane {r['dominant_lane']!r} is not the slowest "
        f"({slowest['lane']!r} at {slowest['elapsed_s']}s). A dominant term "
        "that is not actually dominant is worse than none.")
    assert r["dominant_seconds"] == slowest["elapsed_s"]


def test_the_projection_follows_from_the_measurement():
    """The 15-cell figure must be derived, not typed. Sprint 17 improvement 1:
    a total typed into a document is a guess that looks like an estimate."""
    r = _result()
    expected = round(r["total_seconds_one_cell"] * 15, 1)
    assert abs(r["projection_15_cells_sec"] - expected) < 0.2, (
        f"the projection {r['projection_15_cells_sec']} does not equal "
        f"15 x {r['total_seconds_one_cell']} = {expected}")


def test_the_pilot_spends_no_metered_seconds():
    r = _result()
    assert r["metered_seconds"] == 0
    assert r["evidence_tag"] == "SIM", (
        "every lane is classical; tagging this HW would misreport provenance")


def test_the_document_does_not_overclaim_about_the_device():
    """The pilot's CVQBoost comparator is the classical PROXY, not Dirac-3.
    The document must say so, because 'HGB beats CVQBoost' read as a device
    result would be a claim promoted past its evidence tag."""
    if not DOC.exists():
        pytest.skip("F100_LANE_PILOT.md not present")
    text = DOC.read_text(encoding="utf-8")
    low = text.lower()
    assert "proj" in low, "the proxy's evidence tag must appear"
    assert "nothing about dirac-3" in low or "not a result about dirac" in low, (
        "the document must state explicitly that this says nothing about the "
        "device; every figure in it is classical")
    assert "nothing about h5" in low or "not in-segment" in low, (
        "these are OVERALL metrics; the document must not let them read as "
        "the in-segment claim")


def test_the_documented_dominant_lane_matches_the_recorded_one():
    """The document interprets the result file; if they disagree, one of them
    is stale and a reader cannot tell which."""
    r = _result()
    if not DOC.exists():
        pytest.skip("F100_LANE_PILOT.md not present")
    text = DOC.read_text(encoding="utf-8")
    assert r["dominant_lane"].replace("_", "") in text.lower().replace(
            "_", "").replace(" ", ""), (
        f"the document does not name {r['dominant_lane']!r} as dominant")
