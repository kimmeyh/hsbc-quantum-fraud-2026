"""The Tuning Budget Equivalence table must include the quantum arm.

Prereg section 6 commits to publishing trials, FITS PER TRIAL and wall-clock
per arm, "reported as-is with the asymmetry acknowledged". Until Sprint 17 the
table listed the four classical studies and mentioned CVQBoost only in a
trailing footnote, so the acknowledged asymmetry had nothing to be asymmetric
with: a reader could not tell whether the quantum arm got 5 trials or 500.

The table exists to pre-empt "you under-tuned the quantum arm" as an
explanation for the H1b null. It cannot do that job without the arm in it.

Found in Manual Validation by the team lead, who pointed out that no human
reading the page could have drawn the intended comparison from it.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "experiments" / "results" / "gate_report.md"
TUNING = ROOT / "experiments" / "results" / "proxy_tuning.json"


def _table() -> str:
    if not REPORT.exists():
        pytest.skip("gate_report.md not present")
    text = REPORT.read_text(encoding="utf-8")
    start = text.index("## Tuning Budget Equivalence")
    nxt = text.find("\n## ", start + 1)
    return text[start:] if nxt == -1 else text[start:nxt]


def test_cvqboost_has_a_row_not_just_a_footnote():
    body = _table()
    row = [ln for ln in body.splitlines()
           if ln.startswith("|") and "cvqboost" in ln.lower()]
    assert row, ("the quantum arm has no ROW in the budget table; a footnote "
                 "mention is what this test exists to reject")


def test_the_cvqboost_row_carries_all_four_committed_quantities():
    """trials, fits per trial, AP and wall seconds -- prereg 6."""
    body = _table()
    row = next(ln for ln in body.splitlines()
               if ln.startswith("|") and "cvqboost" in ln.lower())
    cells = [c.strip() for c in row.strip("|").split("|")]
    assert len(cells) == 5, f"expected 5 cells, got {len(cells)}: {cells}"
    _study, trials, fits, ap, wall = cells
    assert trials.isdigit() and int(trials) > 0
    assert fits and fits not in {"-", "n/a"}
    assert re.fullmatch(r"0\.\d+", ap), ap
    assert wall.isdigit()


def test_the_figures_match_the_committed_study_record():
    """No recomputation: the row must be what proxy_tuning.json says."""
    if not TUNING.exists():
        pytest.skip("proxy_tuning.json not present")
    doc = json.loads(TUNING.read_text(encoding="utf-8"))
    wall = [t["wall_s"] for t in doc["trials"] if t.get("wall_s") is not None]

    row = next(ln for ln in _table().splitlines()
               if ln.startswith("|") and "cvqboost" in ln.lower())
    cells = [c.strip() for c in row.strip("|").split("|")]
    assert int(cells[1]) == doc["n_complete"]
    assert cells[3] == f"{doc['best_overall']['val_ap']:.4f}"
    assert int(cells[4]) == round(sum(wall))


def test_the_fits_per_trial_column_exists():
    """Committed by prereg 6 and previously buried in the footnote."""
    header = next(ln for ln in _table().splitlines()
                  if ln.startswith("| Study"))
    assert "Fits per trial" in header


def test_the_non_comparability_of_the_ap_column_is_stated():
    """The most important sentence on the page: a reader must not read the AP
    column straight across. 0.6873 vs 0.8580 is not a ranking."""
    body = _table().lower()
    assert "not comparable" in body
    assert "does not rank the arms" in body


def test_the_null_is_not_left_as_an_open_objection():
    """The asymmetry favors the classical arms, so it is a live candidate
    explanation for the null. The page must close that loop."""
    body = _table()
    assert "+0.0047" in body and "0.0028" in body
    assert "minimum detectable effect" in body.lower()


def test_the_like_for_like_comparison_is_named():
    body = _table()
    assert "H1b" in body
    assert "0.7671" in body and "0.8070" in body and "-0.0399" in body


def test_no_literal_separator_row_inside_the_table_body():
    """A |---| row inside the body renders as dashes in a data cell, not as a
    rule. The CVQBoost row is marked in its label instead."""
    body_rows = [ln for ln in _table().splitlines() if ln.startswith("|")]
    # The header separator is row index 1; any later one is a rendering bug.
    for ln in body_rows[2:]:
        cells = [c.strip() for c in ln.strip("|").split("|")]
        assert not all(set(c) <= {"-"} and c for c in cells), (
            f"literal separator row inside the table body: {ln!r}")
