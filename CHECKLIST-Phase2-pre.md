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
- [x] **C**: F67 -- the pool-mechanism guard runs on a fresh clone (Sprint 14).
      Three storage options were measured rather than argued: full pools
      2.38 MB, needed arrays 1.42 MB, int8 signs 0.83 MB. The fixture is
      lossless because every H_tr holds only -1 and +1, asserted at build time

## Phase 2 preparation (no metered spend, no commitment)

- [x] **C**: F39 -- ADR-0014 written and ACCEPTED (Sprint 14), early-innovation
      status with a 20-paper checkpoint. Scope corrected during review: the
      glossary is use case ONE, not the boundary
- [x] **C**: F72 -- ADR-0015 written and ACCEPTED (Sprint 14). Restructured in
      review: a paper is a SOURCE OF ASSERTIONS rather than a record
- [ ] **C**: F77 -- BUILD the Evidence Based DB. Repository created 2026-09-14
      at `github.com/kimmeyh/EvidenceBasedDB` (private) and seeded; Sprint 1 is
      planned there. The work happens in that repository, not this one
- [ ] **C**: F73 -- the submission explained at an 8th-grade level. Sequenced
      AFTER F77 so its contents can be validated against the store
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
