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
    """1,039 drawn of 3,000 in Phase 1, plus 280 on the Sprint 18 integer
    probe, leaving 1,681.

    The subtraction 3000-1141 is wrong in both directions; see
    docs/QPU_RECONCILIATION.md. This test asserted 1,961 until the probe ran
    and spent against it -- a figure that was right when written and went
    stale the moment the allocation moved.

    IT THEN WENT STALE THE SAME WAY. This docstring said "plus 16 ... leaving
    1,945" after round 2 had spent 264 more, while the assertion below it
    already read 1,681. A docstring carrying a number is a second copy of it,
    and this one recorded the lesson about stale figures in the same breath as
    repeating the mistake. Found by Copilot on PR #139.
    """
    text = _read(MEMO)
    assert "1,039" in text and "1,681" in text
    assert "1,859" not in text, (
        "the memo quotes 1,859, which is grant minus CAMPAIGN total -- wrong "
        "in both directions (see QPU_RECONCILIATION.md)")


# ------------------------------- the integer cost, measured (F87, Sprint 18)

def test_the_hardware_plan_no_longer_refuses_to_quote_a_cost():
    """The sentence F87 exists to remove.

    "We are not quoting a cost for that block" was correct with no measurement
    behind it and was the weakest sentence in a package whose argument is that
    our estimates are measured rather than projected. A two-point probe
    replaced it on 2026-09-23.
    """
    text = _read(HARDWARE)
    for phrase in ("we will not quote a number",
                   "UNKNOWN, and we will not quote",
                   "no comparable anchor exists"):
        assert phrase not in text, (
            f"the hardware plan still refuses to quote a cost: {phrase!r}")


def test_the_hardware_plan_carries_the_measured_integer_figures():
    """Five measured points, not the discarded two-point line."""
    text = _read(HARDWARE)
    for probe in ("| 8 | 32 | 4 |", "| 150 | 600 | 165 |", "| 60 | 840 | 71 |"):
        assert probe in text, f"missing measured row: {probe}"


def test_the_hardware_plan_states_that_cost_tracks_variables():
    """THE FINDING. The ceiling is expressed in levels, so sizing a block on
    levels is the natural mistake -- and the one we made first."""
    text = _read(HARDWARE)
    # _read collapses whitespace, so this matches across the line wrap.
    assert "cost tracks the VARIABLE COUNT, not the level budget" in text
    assert "controlled pair" in text


def test_the_hardware_plan_does_not_quote_a_high_variable_ceiling_figure():
    """probe_ceiling was designed and NOT run, so no figure exists for a
    high-variable job at the ceiling. Quoting one would extrapolate past our
    own data.

    The team lead removed the standalone "What we will not quote" section on
    2026-09-23, so this now tests the REQUIREMENT rather than the heading:
    the per-run table must say the omission is deliberate, and the discarded
    round-1 line must not read as current.
    """
    text = _read(HARDWARE)
    assert "deliberately NOT extrapolated" in text, (
        "the plan does not say the ceiling figure was withheld on purpose")
    assert "past our own data" in text
    assert "We first fitted" in text, (
        "the falsified round-1 extrapolation is presented as current")


def test_the_discarded_fit_is_reported_as_discarded():
    """Round 1's line was falsified by round 2 at 1.6x and 4.1x. The document
    says so rather than quietly dropping it, because QCi may have read the
    earlier figure."""
    text = _read(HARDWARE)
    assert "4.1x" in text, "the falsification is not quantified"
    assert "indicative rather than as a formula" in text, (
        "the two-factor fit is presented as more certain than it is")


def test_the_level_budget_distinction_is_explained_to_qci():
    """`sum(upper_bound + 1)`, not the variable count. Not obvious from the
    documentation, and we got it wrong before the probe ran."""
    text = _read(HARDWARE)
    assert "LEVEL BUDGET" in text or "level budget" in text
    assert "upper_bound + 1" in text


def test_the_memo_reports_the_probe_as_done_and_the_balance_as_spent():
    text = _read(MEMO)
    assert "1,681" in text, "the memo does not carry the post-probe balance"
    for stale in ("1,961", "1,945"):
        assert stale not in text, (
            f"the memo still quotes {stale}; the figures must be internally "
            "consistent")


def test_the_memo_states_the_variables_not_levels_finding():
    text = _read(MEMO)
    assert "COST TRACKS THE VARIABLE COUNT, NOT THE LEVEL BUDGET" in text
    assert "4.1x" in text, "the memo does not own the mispricing"


# ------------------------------------- the Phase 2 ask (team lead, 2026-09-23)

def test_the_hardware_plan_states_the_phase_2_ask_up_front():
    """The team lead's instruction: the overall cost and the per-run cost must
    both appear, and the ask must be near the top rather than buried."""
    text = _read(HARDWARE)
    assert "The ask, up front" in text
    assert "9,000" in text, "the total request is not stated"
    head = text[:text.index("Allocation position")]
    assert "9,000" in head, "the ask is not up front"

    # THE SUBTRACTION, not the phrasing. This guard pinned the literal
    # "7,500" and so could not tell a deliberate round-up from an arithmetic
    # error. 9,000 - 1,681 = 7,319, and the ask is 7,500 BY CHOICE: a figure
    # stated to the second implies a precision the estimate does not have.
    #
    # So the rule is not "the subtraction must be exact". It is: the exact
    # remainder must appear, the asked figure must be >= it (never asking for
    # less than the plan needs), the gap must be small, and the rounding must
    # be stated in words. An unexplained 7,500 fails on the last clause.
    import re
    held = int(re.search(r"We hold ([\d,]+) of", text).group(1).replace(",", ""))
    remainder = 9000 - held
    additional = int(
        re.search(r"additional request of\s+\*\*([\d,]+) seconds",
                  text).group(1).replace(",", ""))

    # The remainder must appear IN THE SENTENCE that does the subtraction,
    # not merely somewhere in the document. A drift in the held figure was
    # otherwise invisible: changing 1,681 to 1,500 makes the remainder equal
    # the rounded ask, and a document-wide search still found the stale 7,319
    # elsewhere on the page.
    ask_sentence = text[text.index("The ask, up front"):
                        text.index("Allocation position")]
    assert f"leaving {remainder:,}" in ask_sentence, (
        f"9,000 - {held:,} = {remainder:,}, which the ask sentence does not "
        "state; a reader cannot check the ask against what we hold")
    assert additional >= remainder, (
        f"the ask of {additional:,} is BELOW the {remainder:,} the plan "
        "needs")
    assert additional - remainder < 500, (
        f"the ask rounds {remainder:,} up to {additional:,}; that is not a "
        "rounding")
    if additional != remainder:
        assert "round" in text[:text.index("Allocation position")].lower(), (
            f"the ask states {additional:,} rather than the exact "
            f"{remainder:,} and never says it is rounded")


def test_the_ask_separates_its_two_buffers():
    """Estimation contingency and discovery buffer cover DIFFERENT risks.
    Collapsing them into one round number hides what is being asked for."""
    text = _read(HARDWARE)
    assert "Estimation contingency" in text
    assert "Discovery buffer" in text
    assert "4,324" in text, "the measured-rate subtotal is not shown"

    # THE BUFFERS COMPOUND, and the table must say so. Presented as two
    # parallel percentages of the 4,324 subtotal, the column sums to 8,216
    # against a stated 9,000: 40% of the subtotal is 1,730, but the table
    # shows 2,594, which is 40% of the POST-contingency 6,486. A reviewer
    # checking the arithmetic concludes the ask is padded. Found by the PR
    # #139 review.
    assert "4,324 x 1.5 x 1.4" in text, (
        "the table does not show how the buffers compose")
    assert "6,486" in text, "the running total between buffers is not shown"
    # Each buffer row shows its INCREMENT; the running total sits between
    # them. Re-derived here so the table cannot drift from its own basis.
    assert round(4324 * 0.5) == 2162, "the contingency increment"
    assert round(4324 * 1.5) == 6486, "the running total"
    assert round(4324 * 1.5 * 0.4) == 2594, "the discovery increment"
    for figure in ("2,162", "6,486", "2,594"):
        assert figure in text, f"{figure} is missing from the ask table"


def test_the_estimation_contingency_is_justified_by_our_own_error():
    """50% is calibrated, not conventional: the opening two-point integer
    estimate was wrong by 4.1x."""
    text = _read(HARDWARE)
    i = text.index("50% estimation contingency")
    assert "4.1x" in text[i:i + 400], (
        "the contingency does not cite the error that calibrates it")


def test_the_discovery_buffer_says_what_it_is_for():
    """Not slack. It buys the ability to follow an unplanned finding without
    stopping to re-ask -- and Phase 1's best result was exactly that."""
    text = _read(HARDWARE)
    i = text.index("40% discovery buffer")
    window = text[i:i + 600]
    assert "was not in any plan we wrote" in window
    assert "re-ask" in window


def test_the_per_run_costs_are_measured_not_fitted():
    """Both experiment-3 rates are probe measurements, so the expensive half
    of the ask rests on data rather than on the discarded line."""
    text = _read(HARDWARE)
    assert "71 s (measured)" in text and "165 s (measured)" in text
    assert "| 1,420 |" in text and "| 1,650 |" in text


def test_the_ask_is_reconciled_against_the_original_sponsorship_request():
    """A request that shrinks by 3-5x needs an explanation (team lead).

    The original sponsorship request estimated 2,000 seconds for the
    preregistered runs plus 20,000-40,000 for the full grid, both marked TBD.
    Asking for 9,000 without reference to that would look like either a
    different project or a quiet climbdown. It is neither: the proxy absorbs
    four of six experiments, the null narrowed the grid, and measured costs
    came in below the estimate that sized the original ask.
    """
    text = _read(HARDWARE)
    assert "well below what we originally told you" in text, (
        "the plan does not reconcile the new ask against the original request")
    assert "20,000 to 40,000" in text, (
        "the original estimate is not quoted, so the reader cannot check the "
        "comparison")
    for reason in ("classical proxy absorbs", "null result narrowed",
                   "Measured costs came in below"):
        assert reason in text, f"the reduction is unexplained: {reason!r}"
    assert "reduction in ambition" in text, (
        "the plan does not say the shrink is evidence-driven")
