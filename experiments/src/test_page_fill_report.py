"""Regression tests for scripts/page-fill-report.py.

WHY THESE EXIST. The tool originally counted extracted CHARACTERS per page and
called a page underfilled when it held fewer than 85% of the median. That
instrument produced a false positive that cost a full card (F36): it reported
appendix pages 1 and 3 as underfilled at 71% and 65% of median, and a pandoc Lua
filter was built to float the tables and reclaim the supposed waste. Direct
measurement then showed every page of that document filling its text block. The
pages were full; the tool was wrong.

The cause is that character count is not a measure of space when pages differ in
composition. A table spends a lot of vertical space on few characters; prose
spends little. A table-heavy page therefore always "underfills" a prose-heavy
page by character count, whether or not any space is actually free.

test_table_page_is_not_underfilled is the direct regression: it is the exact
shape that fooled the old tool.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "page-fill-report.py"


def _load():
    spec = importlib.util.spec_from_file_location("page_fill_report", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class FakePage:
    """Minimal stand-in exposing the extract_text(visitor_text=...) contract.

    `runs` is a list of (text, y) at the baselines a real render would place.
    """

    def __init__(self, runs):
        self._runs = runs

    def extract_text(self, visitor_text=None):
        if visitor_text is not None:
            for text, y in self._runs:
                visitor_text(text, None, [0, 0, 0, 0, 0, y], None, 0)
        return " ".join(t for t, _ in self._runs)


def _body(top, bottom, step=12.0, text="line of body text"):
    """Text runs from `top` down to `bottom` at normal leading."""
    runs = []
    y = top
    while y >= bottom:
        runs.append((text, y))
        y -= step
    return runs


def test_full_page_reports_no_free_space():
    mod = _load()
    page = FakePage(_body(0.0, -680.0))
    top, bottom = mod.text_extent(page)
    assert top == pytest.approx(0.0)
    assert bottom == pytest.approx(-680.0, abs=12.0)


def test_folio_is_excluded_from_the_text_block():
    """The page number sits far below the body and is not content.

    Without this exclusion the folio is the deepest baseline on EVERY page, so
    every page reports zero free space -- including a nearly empty final page,
    which is the one case the tool exists to flag.
    """
    mod = _load()
    page = FakePage(_body(0.0, -200.0) + [("3", -685.0)])
    top, bottom = mod.text_extent(page)
    assert bottom > -685.0, "folio must not count as the bottom of the text"
    assert bottom == pytest.approx(-200.0, abs=12.0)


def test_table_page_is_not_underfilled_despite_few_characters():
    """The exact false positive that cost card F36.

    A page of table cells extracts far fewer characters than a page of prose of
    the SAME height. Under character counting the table page looked 35% short.
    Measured as extent, both pages are full and neither has reclaimable space.
    """
    mod = _load()
    prose = FakePage(_body(0.0, -680.0, text="a full line of ordinary prose text " * 3))
    table = FakePage(_body(0.0, -680.0, text="A 30 0.83"))

    prose_top, prose_bottom = mod.text_extent(prose)
    table_top, table_bottom = mod.text_extent(table)

    # Same vertical extent: neither page has space the other lacks.
    assert table_bottom == pytest.approx(prose_bottom, abs=12.0)
    assert table_top == pytest.approx(prose_top, abs=12.0)

    # And the character counts differ sharply, which is what misled the old
    # tool. This asserts the premise of the bug, so the test documents WHY
    # extent is measured instead of characters.
    assert len(table.extract_text()) < len(prose.extract_text()) / 2


def test_short_page_is_detected_as_underfilled():
    """The tool must still catch a page that genuinely ends early."""
    mod = _load()
    short = FakePage(_body(0.0, -300.0) + [("2", -685.0)])
    full = FakePage(_body(0.0, -680.0) + [("3", -685.0)])

    _, short_bottom = mod.text_extent(short)
    _, full_bottom = mod.text_extent(full)

    free = short_bottom - full_bottom
    assert free > mod.UNDERFILL_SLACK_PT, (
        "a page ending 380pt early must register as underfilled")


def test_a_real_trailing_element_is_not_mistaken_for_a_folio():
    """Regression: the first folio rule dropped content, not just page numbers.

    It removed whatever run sat lowest when the gap above it exceeded
    FOLIO_GAP_PT. A page number has that shape -- and so does a section heading
    opening at the foot of a page, a short final paragraph after a table, or a
    lone caption. Dropping one makes the page look FULLER than it is, hiding
    reclaimable space: the same class of error as the character counting this
    module was rewritten to remove.
    """
    mod = _load()
    page = FakePage(_body(0.0, -600.0) + [("Appendix C. Reproduction", -645.0)])
    _, bottom = mod.text_extent(page)
    assert bottom == pytest.approx(-645.0), (
        "a heading below a gap is content, not a folio")


def test_folio_is_still_dropped_when_a_trailing_heading_is_present():
    """The narrower rule must not lose its original purpose."""
    mod = _load()
    page = FakePage(_body(0.0, -600.0)
                    + [("Appendix C. Reproduction", -645.0), ("3", -685.0)])
    _, bottom = mod.text_extent(page)
    assert bottom == pytest.approx(-645.0), "folio dropped, heading kept"


def test_roman_numeral_folio_is_recognised():
    """Front matter numbers pages i, ii, iii."""
    mod = _load()
    page = FakePage(_body(0.0, -600.0) + [("iv", -685.0)])
    _, bottom = mod.text_extent(page)
    assert bottom == pytest.approx(-600.0)
