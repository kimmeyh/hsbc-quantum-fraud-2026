"""The four SPECTRA records point at one reconciliation, and cannot drift.

F93, Sprint 20. Four records described the same hardware block and disagreed
about its size, schedule and cost: F2b (15 fits, ~450 s, no schedule stated),
F90 (schedule 3, 833 variables, ~1,236 s), F5 (3 cells x 5 seeds), and the
hardware plan SENT to QCi (30 fits, 91-136 variables, 270 s).

Nobody introduced that on purpose. Each record was written against the
knowledge of its day and none was retired when the next arrived, so the
disagreement accumulated silently until a fresh read found it. These guards
make the next accumulation visible instead.

The cost figures themselves are NOT restated here -- the cards own them, and
restating a number another file owns is the defect this repository bans. What
is asserted is that the records cross-reference the reconciliation, and that
the externally-visible figure is recorded.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "docs" / "ALL_SPRINTS_MASTER_PLAN.md"
RECON = ROOT / "docs" / "SPECTRA_BLOCK_RECONCILIATION.md"

# The records that describe this block. If a fifth appears, it belongs here.
SPECTRA_CARDS = ("F2b", "F5", "F90", "F93")


def _plan() -> str:
    if not PLAN.exists():
        pytest.skip("master plan not present")
    return PLAN.read_text(encoding="utf-8")


def test_the_reconciliation_document_exists():
    assert RECON.exists(), (
        "docs/SPECTRA_BLOCK_RECONCILIATION.md is missing. It is where the four "
        "SPECTRA records are held side by side; without it they drift apart "
        "again, which is the defect F93 exists to prevent.")


def test_every_spectra_record_points_at_the_reconciliation():
    """A record that does not reference the reconciliation is a record a
    reader can act on without seeing the other three."""
    text = _plan()
    missing = []
    for card in SPECTRA_CARDS:
        start = text.index(f"**{card}. ")
        nxt = text.find("\n**F", start + 5)
        body = text[start:nxt if nxt != -1 else len(text)]
        if "SPECTRA_BLOCK_RECONCILIATION.md" not in body:
            missing.append(card)
    assert not missing, (
        f"these SPECTRA records do not reference the reconciliation: "
        f"{missing}. Each describes the same block, so a reader who finds one "
        f"must be able to find the others.")


def test_the_reconciliation_records_what_qci_was_actually_sent():
    """The decision is constrained by an external commitment, so the
    commitment must be in the document rather than in someone's memory.

    Verified 2026-10-02 with pypdf against the sent PDF: it contains
    "Experiment 5, segment transfer (30 fits)", "270" and "91 to 136".
    """
    text = RECON.read_text(encoding="utf-8")

    # THE TABLE ROW, not the document. Asserting "270" appears somewhere was
    # vacuous: the figure is discussed in five places, so deleting it from the
    # comparison table left four hits and the guard passed on a real loss.
    # Presence is not correctness -- the same substitution this sprint has
    # already made three times elsewhere.
    row = next((ln for ln in text.splitlines()
                if ln.startswith("| **Sent hardware plan**")), None)
    assert row, (
        "the comparison table has no row for the sent hardware plan, so a "
        "reader cannot see what QCi was actually told")

    # EXACT CELLS, not substrings. Anchoring to the row was only half the fix:
    # `"270" in "2700 s"` is true, so every figure QCi was sent could be
    # inflated TENFOLD and this guard noticed nothing. Measured on PR #146 --
    # 270 to 2700 and 30 to 300 both stayed green. I diagnosed the
    # presence-is-not-correctness defect, anchored to the row, and left the
    # same defect one level down inside it.
    cells = [c.strip() for c in row.strip().strip("|").split("|")]
    assert len(cells) >= 6, (
        f"the sent-plan row has {len(cells)} cells, expected at least 6: {row}")

    fits, variables, _schedule, cost = cells[2], cells[3], cells[4], cells[5]
    assert fits == "30", (
        f"the sent plan quotes 30 fits; the row says {fits!r}")
    assert variables.replace("–", "-") == "91-136", (
        f"the sent plan quotes 91 to 136 variables; the row says "
        f"{variables!r}")
    assert cost == "**270 s**", (
        f"the sent plan quotes 270 seconds; the row says {cost!r}. That is "
        "the figure QCi holds, so a change here is externally visible.")

    assert "SENT" in text or "was sent" in text, (
        "the reconciliation does not say the figure was SENT, which is what "
        "makes it a constraint rather than one more estimate")


def test_the_reconciliation_never_picks_without_attribution():
    """F93's acceptance is that the evidence is assembled and the decision
    recorded. The decision is Class 3 -- allocation spend -- so a document
    that quietly picked would be taking the team lead's call.

    REWRITTEN (F122 (b), Sprint 21). The first version asserted that the
    phrase "does not pick" or "not yet made" appeared, which meant it went RED
    on 2026-10-03, the day the team lead actually made the decision and the
    document correctly recorded it. A guard that fails on correct progress gets
    deleted, and this repository has already paid for that four times.

    What is actually load-bearing is not that the document defers forever. It
    is that the document is in exactly ONE of two legitimate states, never a
    third where a choice appears with nobody's name on it:

      (1) OPEN      -- the choice is explicitly deferred to the team lead, or
      (2) DECIDED   -- a choice is recorded AND attributed to the team lead
                       with a date.

    The failure this prevents is state (3): a configuration silently selected
    by the document itself.
    """
    text = RECON.read_text(encoding="utf-8")
    assert "## Decision" in text, "no Decision section to record the choice in"

    # Scope the check to the Decision section's OWN opening, not the whole
    # file. The file elsewhere discusses the team lead and carries many dates
    # (the options, the corrections), so a file-wide search would find an
    # attribution no matter what the Decision section said -- which is how the
    # first attempt at this rewrite passed a mutation that stripped exactly
    # the attribution it was supposed to require.
    start = text.index("## Decision")
    nxt = text.find("\n## ", start + 1)
    section = text[start:nxt] if nxt != -1 else text[start:]
    head = section[:800]          # the decision itself, not its commentary
    low = head.lower()

    deferred = ("does not pick" in low or "not yet made" in low
                or "is the team lead's" in low)

    # A recorded decision must carry BOTH an attribution and a date, in the
    # Decision section's own opening, so a choice cannot be entered without
    # saying who made it and when.
    attributed = "team lead" in low and re.search(
        r"\b20\d{2}-\d{2}-\d{2}\b", head) is not None
    decided = attributed and re.search(
        r"\b(approved|decided|selected|chose|made|proceed)\b", low) is not None

    assert deferred or decided, (
        "the reconciliation is in neither legitimate state: it does not defer "
        "the choice to the team lead, and it does not record a decision "
        "attributed to the team lead with a date. A configuration chosen by "
        "the document itself is the Class 3 violation this guard exists for")


def test_the_options_are_enumerated_with_their_costs():
    """Four options, each with what it spends. An option list without costs
    is not a decision aid for an allocation decision.

    NOW ACTUALLY CHECKS THE COSTS (F122 (c), Sprint 21). The first version
    asserted only that the strings "Option 1" through "Option 4" appeared,
    which is not what its name or its docstring claimed. An option could lose
    its cost figure entirely and this guard stayed green -- on a document whose
    whole purpose is pricing an allocation decision.
    """
    text = RECON.read_text(encoding="utf-8")

    # A cost is a number of seconds: "270 s", "1,236 s", "about 450 s".
    seconds = re.compile(r"[\d,]+(?:\.\d+)?\s*s\b")

    for n in range(1, 5):
        marker = f"Option {n}"
        assert marker in text, f"{marker} is missing"

        # The option's own text runs from its marker to the next option
        # marker, or to the end of the Options section.
        start = text.index(marker)
        nxt = text.find(f"Option {n + 1}", start)
        body = text[start:nxt] if nxt != -1 else text[start:start + 1200]

        assert seconds.search(body), (
            f"{marker} states no cost in seconds. This document exists to "
            f"price an allocation decision; an option without its spend is "
            f"not a decision aid. Option body was: {body[:200]!r}")
