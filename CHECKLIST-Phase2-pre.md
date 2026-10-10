# Checklist: Pre-Phase 2 (LIVE)

Owners: **H** = Harold (only you can do it), **C** = Claude (I do it), **H+C** = decision or review done together.

**STATUS: LIVE. Update this file as work progresses.**

Covers 2026-09-12 to finalist notification, expected **mid-November 2026**
(Guidelines s2). Phase 2 begins at the same milestone, so there is no gap
between hearing and starting.

**Nothing here is time-bound.** Thirteen sprints of estimating against a
deadline built a habit; there is no date behind this list. Schedule on value.

**Nothing here may touch the submitted documents.** They are a record now.

Phase 1 is closed: `CHECKLIST-Phase1.md`. If selected: `CHECKLIST-Phase2.md`.

---

Phase 1 is submitted. Finalist notification and the Phase 2 PoC sprint both
land **mid-November 2026** (Guidelines s2), so there is no gap between hearing
and starting. **Nothing here is time-bound**, and nothing here may touch the
submitted documents.

## Standing constraints during the wait

- [x] **C**: The three submission documents are a RECORD, not a draft. A hook
      refuses edits without recorded approval
- [x] **C**: History is never rewritten and `prereg-freeze` never moves. Two
      commits are cited in judged PDFs that cannot be corrected. A hook refuses
      force-pushes and tag moves
- [ ] **H+C**: Any new experiment is dated post-submission and reported as such,
      never folded back into the submitted claims

## Repository durability

- [x] **C**: README rebuilt for a public reader: what was submitted, how to
      retrieve it as submitted, how to reproduce, what cannot be reproduced
- [x] **C**: Reproduce steps EXECUTED against a fresh clone, not drafted
- [x] **C**: CHANGELOG backfilled and wired into the delivery cycle (8.1.1)
- [ ] **C**: F67 -- the pool-mechanism guard is the suite's only skip and is
      inert on a fresh clone. Needs a decision: pools in the repository, or a
      committed fixture?

## Phase 2 preparation (no metered spend, no commitment)

- [ ] **C**: F39 -- fact-database investigation and ADR. Design only, starts
      off-repository
- [ ] **C**: F72 -- reference-paper library proposal. Design only, gated on
      F39's storage decision
- [ ] **H+C**: F64 -- the k=17 order-2 cell is Phase 2 experiment 1. Pre-flight
      is done and recorded; the run itself waits for acceptance
- [ ] **H**: Optional -- gate-based groundwork on a free platform (PennyLane or
      Qiskit both port to Braket). Self-funded, `[SIM]` until it runs on
      hardware, and NOT part of the Phase 1 record

## If notification arrives

- [ ] **H**: Record the outcome and the date in `docs/submission/`
- [ ] **H+C**: If selected, open the Phase 2 section below and plan properly
      (F13). If not selected, the repository stands as the public record of a
      null reported honestly

---
