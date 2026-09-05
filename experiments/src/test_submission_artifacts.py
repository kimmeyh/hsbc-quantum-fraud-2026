"""Tests over the SUBMISSION ARTIFACTS themselves, not the code that makes them.

Sprint 5 retrospective, improvements 1-3. Every defect these cover actually
shipped and was caught by a human asking a question, never by a check:

- Nine PDFs rendered 11x17 TABLOID for days. `check-page-limits.py` reported
  "within limits" the whole time because it read page counts from reflowed Word
  output. Verification that measures the wrong artifact is worse than none.
- The appendix silently became 4 pages against a hard 3-page limit mid-edit; the
  page check reported "3 of 3" from a stale PDF.
- The team profile shipped without the lead contact details and affiliation that
  guidelines section 4.1 requires, while the requirement sat marked TODO in
  requirements-matrix.md. A TODO does not enforce itself.
- The QCi cover kept the corrected-away "exactly uniform" claim after an edit
  script asserted on a bad anchor and silently rolled back every edit in the
  batch.

These tests read the RENDERED PDFs. They are skipped when the PDFs are absent
(a fresh clone has not rendered yet), so they never block unrelated work.
"""
from __future__ import annotations

from pathlib import Path

import pytest

pypdf = pytest.importorskip("pypdf")
from pypdf import PdfReader  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "paper" / "out"

US_LETTER = (612, 792)
A4 = (595, 842)

# Hard limits from Phase 1 Submission Guidelines sections 4.3, 4.4 and 5.
PAGE_LIMITS = {
    "proposal.pdf": 6,
    "appendix.pdf": 3,
    "team_profile.pdf": 1,
}

# Phrasings corrected during review. If one reappears in a rendered PDF, an
# edit was lost or a stale file was published.
RETIRED_CLAIMS = [
    "exactly uniform",
    "L1 distance from uniform of 0.000000",
    "quantum optimization is necessary",
    "Contact details supplied through the submission portal",
]

# Guidelines 4.1: team name, lead contact details, affiliation.
TEAM_PROFILE_REQUIRED = [
    "Harold",
    "kimmeyharold@aol.com",
    "216-357-9227",
    "linkedin.com/in/haroldkimmey",
    "independent researcher",
]


def _pdfs(subdir: str = "") -> list[Path]:
    base = OUT / subdir if subdir else OUT
    return sorted(base.glob("*.pdf")) if base.is_dir() else []


def _text(path: Path) -> str:
    return " ".join(page.extract_text() or "" for page in PdfReader(str(path)).pages)


def _size(path: Path) -> tuple[int, int]:
    box = PdfReader(str(path)).pages[0].mediabox
    return round(float(box.width)), round(float(box.height))


ALL_PDFS = _pdfs() + _pdfs("qci_package")


@pytest.mark.skipif(not ALL_PDFS, reason="no rendered PDFs; run scripts/render-pdf.ps1")
@pytest.mark.parametrize("pdf", ALL_PDFS, ids=lambda p: p.name)
def test_page_size_is_letter_or_a4(pdf: Path) -> None:
    """The tabloid defect. Guidelines section 5 permits A4 or US Letter only."""
    size = _size(pdf)
    assert size in (US_LETTER, A4), (
        f"{pdf.name} is {size[0]}x{size[1]}pt, not US Letter {US_LETTER} or A4 {A4}. "
        "11x17 (792x1224) means the renderer set the size after layout."
    )


@pytest.mark.parametrize("name,limit", sorted(PAGE_LIMITS.items()))
def test_page_count_within_limit(name: str, limit: int) -> None:
    """Read the count from the PDF, never from a tool that reflows it."""
    pdf = OUT / name
    if not pdf.exists():
        pytest.skip(f"{name} not rendered")
    n = len(PdfReader(str(pdf)).pages)
    assert n <= limit, (
        f"{name} is {n} pages against a hard limit of {limit}. Over-limit "
        "submissions may be returned or assessed on the first pages only."
    )


@pytest.mark.skipif(not ALL_PDFS, reason="no rendered PDFs; run scripts/render-pdf.ps1")
@pytest.mark.parametrize("pdf", ALL_PDFS, ids=lambda p: p.name)
def test_no_retired_claims(pdf: Path) -> None:
    """A corrected claim reappearing means a lost edit or a stale render.

    PREREGISTRATION.md is exempt by design: it is FROZEN and its original
    wording is part of the record, so its rendered form may retain phrasing the
    submission documents have moved past.
    """
    if "preregistration" in pdf.name.lower():
        pytest.skip("frozen preregistration keeps its original wording")
    text = _text(pdf)
    found = [c for c in RETIRED_CLAIMS if c in text]
    assert not found, f"{pdf.name} still contains retired claim(s): {found}"


def test_team_profile_has_required_fields() -> None:
    """Guidelines 4.1 requires lead contact details and affiliation."""
    pdf = OUT / "team_profile.pdf"
    if not pdf.exists():
        pytest.skip("team_profile.pdf not rendered")
    text = _text(pdf)
    missing = [f for f in TEAM_PROFILE_REQUIRED if f not in text]
    assert not missing, (
        f"team_profile.pdf is missing guidelines 4.1 element(s): {missing}. "
        "An email broken by LaTeX hyphenation also fails here, which is correct: "
        "a hyphenated address does not copy-paste."
    )


def test_proposal_covers_every_required_section() -> None:
    """Guidelines 4.3 lists seven required concept-proposal elements."""
    pdf = OUT / "proposal.pdf"
    if not pdf.exists():
        pytest.skip("proposal.pdf not rendered")
    text = _text(pdf).lower()
    required = {
        "problem framing": "problem framing",
        "technical approach": "technical approach",
        "feasibility/resources": "feasibility",
        "expected impact": "impact",
        "validation plan": "validation",
        "hybrid integration": "hybrid",
        "team capability": "team capability",
    }
    missing = [label for label, probe in required.items() if probe not in text]
    assert not missing, f"proposal.pdf does not visibly cover: {missing}"
