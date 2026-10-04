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


def test_the_reconciliation_does_not_pretend_to_decide():
    """F93's acceptance is that the evidence is assembled and the decision
    recorded. The decision is Class 3 -- allocation spend -- so a document
    that quietly picked would be taking the team lead's call."""
    text = RECON.read_text(encoding="utf-8")
    assert "## Decision" in text, "no Decision section to record the choice in"
    assert "does not pick" in text.lower() or "not yet made" in text.lower(), (
        "the reconciliation neither defers the choice nor records one")


def test_the_options_are_enumerated_with_their_costs():
    """Four options, each with what it spends. An option list without costs
    is not a decision aid for an allocation decision."""
    text = RECON.read_text(encoding="utf-8")
    for n in range(1, 5):
        assert f"Option {n}" in text, f"Option {n} is missing"
