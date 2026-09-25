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


# The memo was dropped from this list on 2026-09-25 when it was sent; the
# two documents below are still editable and still go to QCi.
@pytest.mark.parametrize("path", [FEEDBACK, HARDWARE],
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


# ------------------- the memo agrees with the plan it travels with (F92, S19)
#
# Sprint 19, approved by the team lead 2026-09-24. The memo was written before
# the Sprint 18 integer probes and the F91 attribution, and six passages came
# to contradict the hardware plan in the same envelope. Each removed claim is
# pinned below. These run only where the memo exists: it is gitignored as
# private correspondence, so they SKIP in CI and protect this workstation only.


# ------------------ Task D findings, team lead dispositions 2026-09-24 (F92)

# ---------------------------------------------------------------------------
# THE MEMO GUARDS WERE RETIRED ON 2026-09-25, WHEN THE MEMO WAS SENT.
#
# Thirteen guards pinned wording in `Phase 1 - QCi memo.txt`: the allocation
# position, the attribution rather than the confound, the integer cost no
# longer refused, the fidelity figure scoped to its arm. They did their job --
# every one of them was written because a stale claim had survived a revision
# round -- and they are now pointed at a draft that no longer exists.
#
# A sent artifact is evidence, not a test fixture. This repository already
# applies that rule to the three SUBMITTED PDFs, which are documents of record
# for the 2026-09-12 filing and are guarded against REBUILD rather than for
# content. The sent email is the same class: it is preserved as
# `Request and Results ... activities.htm` with its `_files` sidecar, and as
# `Phase 1 - QCi memo AS SENT 2026-09-25.md` for readability.
#
# What remains under test is the HARDWARE PLAN, which is still editable and
# still goes to QCi. If a future memo is drafted, it gets its own guards --
# reusing these would pin the new draft to the old one's wording.
# ---------------------------------------------------------------------------


def test_three_experiments_cost_zero_device_seconds_everywhere():
    """Experiments 1, 2 and 4 run on the proxy; 3, 5 and 6 are metered. The
    plan and the memo both said FOUR, against their own list and against the
    submitted proposal's "experiments 1, 2 and 4 (zero device seconds)".

    The memo half was retired on 2026-09-25 when the memo was sent; only the
    hardware plan is still editable, so only it still needs guarding."""
    text = _read(HARDWARE).lower()
    assert "four of the six" not in text, "the plan says four of six"
    assert "four cost zero" not in text, "the plan says four cost zero"
    assert "Three of the six cost zero device seconds" in _read(HARDWARE)


def test_the_plan_states_the_shrink_it_can_compute():
    """2,000 + 20,000..40,000 against 9,000 is 2.4x to 4.7x, not 3x to 5x.
    Derived, so the guard fails if either end of the stated range moves."""
    text = _read(HARDWARE)
    assert "three to five" not in text
    low, high = 9000, 9000
    lo_ratio = (2000 + 20000) / low
    hi_ratio = (2000 + 40000) / high
    assert f"{lo_ratio:.1f} to {hi_ratio:.1f}" in text, (
        f"the plan does not state the shrink as {lo_ratio:.1f} to {hi_ratio:.1f}")


def test_the_plan_does_not_date_every_cost_to_phase_1():
    """The integer costs were measured 2026-09-23, after the filing."""
    text = _read(HARDWARE)
    assert "measured on your hardware during Phase 1**" not in text
    assert "integer sizing calls of 2026-09-23" in text


def test_the_per_size_table_accounts_for_all_61_fits():
    """The table's rows sum to 45; the footnote names the other 16. Summed
    from the table itself, so adding a row without fixing the note fails."""
    import re
    text = _read(HARDWARE)
    section = text[text.index("## Measured per-fit cost"):]
    section = section[:section.index("Cost tracks problem size")]
    rows = [int(n) for n in re.findall(r"\| (\d+) fits", section)]
    assert sum(rows) == 45, f"table rows sum to {sum(rows)}, note says 45"
    assert "three sizes that recur, 45 fits. The other 16" in section
    assert sum(rows) + 16 == 61


def test_the_ask_covers_now_through_phase_2():
    """9,000 s covers everything from now to the end of Phase 2, INCLUDING
    what the memo runs from the 1,681 s already held (team lead, 2026-09-25).
    "For Phase 2" read as the Phase 2 period only, so experiment 5 looked
    counted twice: once before Phase 2 in the memo, once inside the total."""
    text = _read(HARDWARE)
    assert "9,000 Dirac-3 seconds from now through the end of Phase 2" in text
    assert "9,000 Dirac-3 seconds for Phase 2." not in text
