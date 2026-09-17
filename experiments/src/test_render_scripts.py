"""The converted render scripts carry the per-document settings that matter.

F78, Sprint 16. These do NOT render (pandoc and xelatex are not guaranteed
present, and a render takes minutes). They assert the settings, which is where
the failures have actually been.

THE APPENDIX MARGIN IS THE WHOLE POINT. Sprint 5 retrospective improvement 4:
the appendix needs 0.9in, because at the 1in default it spills onto a fourth
page against a HARD 3-page limit. The margin lived only in an ADR paragraph, so
any rebuild that did not read the ADR produced a silently over-limit appendix.

That failure reproduced during the conversion, which is a fair demonstration
that the setting earns a test: rendering the appendix at the default produced 4
pages and 6 extra words. At 0.9in it produced 3 pages, text identical to the
committed PDF.

Verified once by hand at conversion time, on the real toolchain: all three core
documents re-rendered to byte-identical PDFs (git reported no change).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
RENDER_ALL = ROOT / "scripts" / "render_all.py"
RENDER_PDF = ROOT / "scripts" / "render_pdf.py"


def test_both_scripts_exist():
    assert RENDER_ALL.exists() and RENDER_PDF.exists()


def _settings():
    import importlib.util
    spec = importlib.util.spec_from_file_location("render_all", RENDER_ALL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_appendix_keeps_its_narrow_margin():
    """0.9in, everywhere the appendix appears.

    If this ever reads 1in, the appendix silently becomes 4 pages against a
    hard 3-page limit, and nothing else in the toolchain would notice.
    """
    mod = _settings()
    entries = [d for d in mod.CORE + mod.QCI_PACKAGE
               if d[0].endswith("appendix.md")]
    assert entries, "the appendix is not in the render list at all"
    for source, out, margin, _landscape in entries:
        assert margin == "0.9in", (
            f"{out} renders the appendix at {margin}; it must be 0.9in "
            "(Sprint 5 retro improvement 4, hard 3-page limit)")


def test_the_gate_report_is_landscape():
    """It is a wide table and portrait truncates it."""
    mod = _settings()
    entries = [d for d in mod.QCI_PACKAGE if "gate_report" in d[0]]
    assert entries, "the gate report is not in the QCi package list"
    for _source, out, _margin, landscape in entries:
        assert landscape is True, f"{out} must render landscape"


def test_core_documents_are_the_three_submitted_ones():
    mod = _settings()
    sources = {Path(d[0]).name for d in mod.CORE}
    assert sources == {"proposal.md", "appendix.md", "team_profile.md"}


def test_render_pdf_rejects_an_unknown_paper_size():
    r = subprocess.run(
        [sys.executable, str(RENDER_PDF), "--source", "x.md", "--out", "y.pdf",
         "--paper", "tabloid"], capture_output=True, text=True)
    assert r.returncode != 0
    assert "invalid choice" in (r.stderr + r.stdout).lower()


def test_render_pdf_reports_a_missing_source_clearly():
    r = subprocess.run(
        [sys.executable, str(RENDER_PDF), "--source", "does-not-exist.md",
         "--out", "y.pdf"], capture_output=True, text=True)
    assert r.returncode != 0
    assert "source not found" in (r.stderr + r.stdout).lower()


def test_page_size_table_names_tabloid():
    """TABLOID is in the table because it actually happened.

    An earlier renderer routed through Word and set PageSetup.PaperSize AFTER
    opening the document. Word did not reflow, so it emitted 11x17 pages while
    reporting plausible page counts. The size check exists to catch that.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location("render_pdf", RENDER_PDF)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.PAGE_SIZES[(792, 1224)] == "TABLOID 11x17"
    assert mod.PAGE_SIZES[(612, 792)] == "US Letter"


def test_xelatex_discovery_covers_both_operating_systems():
    """The card's point: these scripts must run where CI runs."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("render_pdf", RENDER_PDF)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert any("miktex" in c.lower() for c in mod.WINDOWS_XELATEX)
    assert any(c.startswith("/usr") for c in mod.POSIX_XELATEX)
