"""Generation requirements for the QCi post-submission documents (F86).

WHY THIS EXISTS (Sprint 17 improvement 7, team lead). Every PDF in the QCi
package originates in a markdown or text source, and those sources now carry
wording requirements that were established AFTER the challenge submission. They
came from the team lead reading the rendered documents, and each one corrects a
statement that was wrong or would have read badly to QCi.

A requirement established by review and recorded only in a review comment is a
requirement that survives exactly as long as someone remembers it. These are
the requirements, enforced.

The team lead's framing: all generated PDFs originate with .md files, and
anything that generates an .md file has requirements around its generation.
The rendered document is still reviewed, because it is what the reader sees --
this does not replace that.

SCOPE. The QCi package sources only. It does NOT cover docs/paper/* or
PREREGISTRATION.md, which are frozen records of the 2026-09-12 filing and have
their own guards.
"""
from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
FEEDBACK = ROOT / "docs" / "QCI_EQC_MODELS_FEEDBACK.md"
HARDWARE = ROOT / "docs" / "HARDWARE_PLAN_PHASE_2.md"
MEMO = ROOT / "docs" / "qci_package" / "Phase 1 - QCi memo.txt"

SUBMISSION_DATE = "2026-09-12"


def _read(p: Path) -> str:
    """Source text with whitespace COLLAPSED.

    These documents are hard-wrapped at ~76 columns, so a required phrase such
    as "approved by me after reviewing the plan" spans a line break and a raw
    substring search misses it. The first version of these tests reported two
    documents as non-compliant when both were correct -- a wrong result that
    looked exactly like a real finding, which is the class this repository
    keeps paying for. Collapsing whitespace matches what a READER sees rather
    than where the wrap happens to fall.
    """
    if not p.exists():
        pytest.skip(f"{p.name} not present")
    return " ".join(p.read_text(encoding="utf-8").split())


# --------------------------------------------------------------- all sources

@pytest.mark.parametrize("path", [FEEDBACK, HARDWARE], ids=lambda p: p.name)
def test_every_source_states_the_date_its_content_is_current_to(path: Path):
    """A QCi reader must be able to tell what the document knew and when."""
    assert f"current to {SUBMISSION_DATE}" in _read(path), (
        f"{path.name} does not state the date its content is current to")


@pytest.mark.parametrize("path", [FEEDBACK, HARDWARE, MEMO],
                         ids=lambda p: p.name)
def test_no_source_claims_qci_saw_an_earlier_draft(path: Path):
    """QCi never received a draft of any of these (team lead, Sprint 17).

    Phrasing that implies otherwise -- "an earlier draft of this document
    described" -- tells the reader they missed something they never had.
    """
    text = _read(path).lower()
    for phrase in ("earlier draft of this document",
                   "an earlier draft described",
                   "as we said previously",
                   "in our last update"):
        assert phrase not in text, (
            f"{path.name} implies QCi saw an earlier version: {phrase!r}")


# ------------------------------------------------------- eqc_models feedback

def test_feedback_does_not_claim_we_were_unaware_of_the_tier_ceiling():
    """Team lead, Sprint 17: the free-tier ceiling was known to him
    personally from prior work. The finding stands on what the DOCUMENTATION
    states, not on what we did or did not know.

    No need to say he knew; the requirement is to avoid asserting we did not.
    """
    text = _read(FEEDBACK).lower()
    for phrase in ("we had sized our experiment against that number",
                   "after the experiment had been designed",
                   "we did not know",
                   "we were unaware"):
        assert phrase not in text, (
            f"the feedback claims we were unaware of the ceiling: {phrase!r}")


def test_feedback_scopes_its_scaling_statement_to_the_time():
    """"could make at the time", not "can currently make": the campaign is
    over and the limits it describes are historical."""
    assert "could make at the time was bounded" in _read(FEEDBACK)


def test_feedback_does_not_overstate_the_cost_of_the_ceiling():
    """"would have saved time", not "would have saved us a redesign"."""
    text = _read(FEEDBACK)
    assert "saved us a redesign" not in text
    assert "would have saved time" in text


def test_feedback_does_not_lecture_qci_about_their_api_contract():
    """The repr() sentence was removed: the suggested fix stands on its own,
    and telling a vendor what they should not rely on is not our place."""
    assert "not a contract" not in _read(FEEDBACK)


def test_the_833_finding_states_its_conclusion_in_one_sentence():
    """The paragraph was misread as "we should have limited to 200 learners",
    which inverts it: the 833-variable arm is the campaign's ONLY positive
    result at scale. The one-sentence summary must carry both halves --
    the device picked a subset, and that subset won.
    """
    text = _read(FEEDBACK)
    assert "In one sentence:" in text, (
        "the 833-variable finding has no one-sentence summary")
    start = text.index("In one sentence:")
    summary = text[start:start + 600]
    assert "+0.0256" in summary, (
        "the summary does not say the sparsified result WON; without the gain "
        "it reads as a limitation")
    assert "ten of ten seeds" in summary


def test_feedback_reports_the_full_campaign_not_the_free_tier_subset():
    text = _read(FEEDBACK)
    assert "61 metered fits" in text
    assert "1,141.0 s" in text or "1,141" in text


# -------------------------------------------------------------- hardware plan

def test_hardware_plan_carries_the_team_leads_protocol_wording():
    """Replaced verbatim at his instruction, Sprint 17. The recovery clause is
    the operative part: a dropped connection must not cost a repeat run."""
    text = _read(HARDWARE)
    assert "approved by me after reviewing the plan" in text
    assert "computer goes down" in text
    assert "no need for repeat runs" in text


def test_hardware_plan_drops_the_retry_rule_bullet():
    """Removed at the team lead's instruction."""
    assert "retries at most twice" not in _read(HARDWARE)


def test_hardware_plan_closing_sentence_is_the_short_form():
    text = _read(HARDWARE)
    assert "makes the fidelity comparison meaningful" in text
    assert "even if nothing else survived" not in text


# ---------------------------------------------------------------------- memo

def test_the_memo_asks_for_nothing_but_thoughts():
    """The 30,000-second request was the PREVIOUS letter. Re-asking inside a
    thank-you would undercut both."""
    text = _read(MEMO).lower()
    for phrase in ("30,000", "we request", "please grant", "we are asking for"):
        assert phrase not in text, f"the memo contains an ask: {phrase!r}"


def test_the_memo_states_the_submission_date_the_receipt_records():
    assert SUBMISSION_DATE in _read(MEMO)


def test_the_memo_reports_the_allocation_position():
    """1,039 drawn of 3,000, 1,961 remaining. The subtraction 3000-1141 is
    wrong in both directions; see docs/QPU_RECONCILIATION.md."""
    text = _read(MEMO)
    assert "1,039" in text and "1,961" in text
    assert "1,859" not in text, (
        "the memo quotes 1,859, which is grant minus CAMPAIGN total -- wrong "
        "in both directions (see QPU_RECONCILIATION.md)")
