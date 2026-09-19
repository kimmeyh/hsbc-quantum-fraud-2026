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

# Documents allowed to render LANDSCAPE. Only non-submission artifacts belong
# here: the challenge's own documents must stay portrait, and this list is what
# keeps that distinction enforced rather than remembered.
LANDSCAPE_ALLOWED = {"DRAFT_gate_report.pdf"}

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
    """The tabloid defect. Guidelines section 5 permits A4 or US Letter only.

    Landscape is allowed ONLY for documents that are not part of the challenge
    submission. The gate report is one: it is a QCi-package artifact whose
    widest table needs a 37-character Cell column beside six numeric columns,
    and at portrait width that row wraps and the Cell text runs flush into its
    Seeds value. The submission documents stay portrait, and an unrequested
    rotation in any of them still fails here -- which is the check that caught
    the 11x17 tabloid defect.
    """
    size = _size(pdf)
    allowed = [US_LETTER, A4]
    if pdf.name in LANDSCAPE_ALLOWED:
        allowed += [US_LETTER[::-1], A4[::-1]]
    assert size in allowed, (
        f"{pdf.name} is {size[0]}x{size[1]}pt, not US Letter {US_LETTER} or A4 {A4}. "
        "11x17 (792x1224) means the renderer set the size after layout."
    )


def _page_limit_params():
    """Page-limit cases. Every document is now a hard check.

    These carried a strict xfail while F38 was open and both documents were
    knowingly over limit -- the appendix at 4 of 3, the proposal at 7 of 6.
    strict=True was chosen so the marker would FAIL the moment a document came
    back under limit, making it impossible for the exemption to outlive the
    problem. On 2026-09-11 both did: the trimmed sources render at 6 of 6 and
    3 of 3, the markers fired as designed, and they are deleted here.

    Do not reintroduce an xfail to quiet this test. Going over the limit is a
    submission-rules failure the rules call out explicitly ("submissions
    exceeding the page limit may be returned or assessed only on the first 6
    pages"), so a red line here is the correct signal, not noise.
    """
    out = []
    for name, limit in sorted(PAGE_LIMITS.items()):
        out.append(pytest.param(name, limit, id=name))
    return out


@pytest.mark.parametrize("name,limit", _page_limit_params())
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


def test_documents_state_the_true_amendment_count():
    """Every document naming the amendment count must match the preregistration.

    Sprint 8 shipped a QCi letter asserting "twelve amendments" while the
    ENCLOSED preregistration held seventeen. A letter that miscounts a document
    attached to it undercuts the accuracy it is claiming, and the error was
    caught by reading rather than by any check. Registering A18 recreated the
    same exposure immediately.

    This is the failure class F39 (the fact database) targets. Until that
    exists, the one fact most likely to drift gets its own test.
    """
    import re

    prereg = (ROOT / "experiments" / "PREREGISTRATION.md").read_text(encoding="utf-8")
    nums = sorted({int(m) for m in re.findall(r"\(A(\d+)\)", prereg)})
    assert nums == list(range(1, len(nums) + 1)), (
        f"amendment numbers are not contiguous: {nums}")
    n = len(nums)

    words = {12: "twelve", 13: "thirteen", 14: "fourteen", 15: "fifteen",
             16: "sixteen", 17: "seventeen", 18: "eighteen", 19: "nineteen",
             20: "twenty"}
    stale = {w for k, w in words.items() if k != n}

    # THE SUBMITTED DOCUMENTS ARE FROZEN AT THE COUNT THEY WERE FILED WITH.
    #
    # Until 2026-09-12 every document here had to track the CURRENT count, and
    # this test kept them honest. After filing, that requirement inverts: the
    # submitted documents are a record of what was sent, and editing one to
    # match a later amendment would falsify the record. A33 (Sprint 17) is the
    # first amendment written after the filing and is what surfaced this.
    #
    # So the expected count is per-document: frozen documents keep the filed
    # number, live documents track the log. Both halves are still enforced --
    # the guard is not weakened, it is made correct about which is which.
    FILED_AMENDMENT_COUNT = 32          # the count as filed on 2026-09-12
    FROZEN = {"docs/paper/appendix.md",
              "docs/paper/proposal.md",
              "docs/paper/team_profile.md"}

    # qci_cover.md moved to docs/qci_package/ on 2026-09-17 (private
    # correspondence, now gitignored). It is still CHECKED here: the retraction
    # must not reappear in a letter just because the letter is unpublished.
    # The exists() guard below would have skipped it silently otherwise.
    for rel in ("docs/paper/appendix.md",
                "docs/qci_package/qci_cover.md",
                "docs/QCI_EQC_MODELS_FEEDBACK.md"):
        path = ROOT / rel
        if not path.exists():
            continue
        expected = FILED_AMENDMENT_COUNT if rel in FROZEN else n
        body = path.read_text(encoding="utf-8").lower()
        stale_here = {w for k, w in words.items() if k != expected}
        for bad in stale_here:
            assert f"{bad} amendment" not in body and f"{bad} dated" not in body, (
                f"{rel} says '{bad}' amendments; expected {expected}")
        # Match the whole range phrase, not a substring: "a1 to a18" contains
        # "a1 to a1", so a naive `in` test fails on the CORRECT text.
        for found in re.findall(r"a1 to a(\d+)", body):
            assert int(found) == expected, (
                f"{rel} says 'A1 to A{found}'; expected A{expected} "
                f"({'frozen at the filed count' if rel in FROZEN else 'tracks the log'})")


def test_submission_does_not_claim_prior_paid_tier_degree3_work():
    """Prior paid-account degree-3 work belongs in the QCi letter, not here.

    Team lead, 2026-09-08: "so for qci we can state that, but for the challenge
    we do not want to claim that."

    The QCi letter is private correspondence to a vendor who already knows the
    history, and there it is the stronger and more honest framing. The proposal
    and appendix go to challenge judges, where prior privileged hardware access
    is not something we want to assert -- it invites a fairness question the
    submission should not have to answer, and the result does not depend on it.

    The submission may still refer to "a prior Dirac-3 campaign" in general
    terms, which it does. What it must not do is name the tier, the account, or
    the degree.
    """
    banned = ("degree-3", "degree 3", "paid account", "paid-account",
              "non-free", "paid tier", "paid-tier")
    for name in ("proposal.md", "appendix.md", "team_profile.md"):
        path = ROOT / "docs" / "paper" / name
        if not path.exists():
            continue
        body = path.read_text(encoding="utf-8").lower()
        for phrase in banned:
            assert phrase not in body, (
                f"{name} contains {phrase!r}; prior paid-tier work is for the "
                f"QCi letter only, not the challenge submission")
