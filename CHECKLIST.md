# Joint Checklist

Owners: **H** = Harold (only you can do it), **C** = Claude (I do it), **H+C** =
decision or review done together. Mark items `[x]` as they complete.
`docs/requirements-matrix.md` remains the final acceptance gate.

**Restructured 2026-09-12 (F71).** This file was titled "Submission-Ready by
Sep 8, 2026" and carried eighteen unchecked boxes against work that had shipped
weeks earlier, because ticking them depended on remembering. It now runs in
three sections, newest phase first: what is live now, what Phase 2 would need,
and the completed Phase 1 record corrected to what actually happened.

---

# 1. PRE-PHASE 2 (live: 2026-09-12 to finalist notification)

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

# 2. PHASE 2 (if selected; PoC sprint begins mid-Nov 2026)

Drafted 2026-09-12 from the proposal's own commitments so that acceptance does
not start from a blank page. **Every item here is provisional** until the
Phase 2 brief arrives, and the brief overrides this list.

## Confidentiality changes on acceptance

- [ ] **H**: T&C s7 binds only on receiving sponsor problem statements,
      technical briefings, compute resources or other non-public material. From
      that point, treat all of it as confidential and keep it OUT of this public
      repository
- [ ] **H+C**: Decide where Phase 2 work lives. The public repository is a
      Phase 1 asset; Phase 2 may need a private one

## The six experiments, in the order the proposal commits to

- [ ] **C**: 1. Isolate the confound -- the 153-variable ULB cell at k=17,
      subset order 2. Zero device seconds. Pre-flight already done (F64)
- [ ] **C**: 2. Temporal validity -- IEEE-CIS rolling-origin folds supply the
      test ULB's two-day span cannot. No configuration is recommended for a
      production path until this is settled
- [ ] **H+C**: 3. Cardinality-constrained selection on Dirac-3's integer solver,
      against a time-capped MIQP, greedy, and simulated annealing. **A win
      against a certified-optimal classical solve is a result; a win against no
      control is not**
- [ ] **C**: 4. Replication under source protocol -- H1a reproduces Loke et al.
      under their split and comparator, then re-evaluates under ours
- [ ] **H+C**: 5. The gate-based arm on Amazon Braket or Classiq, against a
      matched classical baseline, **reported whatever the outcome**. The
      proposal commits to this unconditionally
- [ ] **C**: 6. Remaining hardware blocks B4 and B5 (F2b), if the allocation
      supports them

## Resourcing, per proposal section 3

- [ ] **H**: Confirm what compute the PoC sprint provides. T&C s1 promises
      "access to compute resources, tooling, and expert support" to finalists
      and s9 disclaims all warranties over it
- [ ] **H**: Dirac-3 allocation for Phase 2. 1,961 of the 3,000 granted seconds
      remain from Phase 1
- [ ] **H+C**: Latency benchmark (p50/p95/p99) against the 100-300 ms envelope,
      which Phase 1 states as a target rather than a measurement (D10)
- [ ] **H+C**: Calibration layer fitted, which Phase 1 specifies but does not
      fit (D1)

## Deliverable

- [ ] **C**: Preregister the Phase 2 protocol BEFORE any result is seen, as
      Phase 1 did. It is the thing this project does best and the reason the
      null is credible

---

# 3. CHALLENGE SUBMISSION (Phase 1, COMPLETE 2026-09-12)

Corrected 2026-09-12 to what actually happened. Eighteen items below were
delivered but never ticked; they are marked complete with the sprint that
delivered them, because a checklist that disagrees with the repository is worse
than none.

## Standing rule: Dirac-3 hardware budget (held throughout)

Every metered run required team-lead approval with the expected call count
stated in advance. Final: **61 fits, 1,141 metered seconds, zero device
failures, zero retries**.

## Stage 0 to 1: Requirements and thesis (Aug 29 to 30)

- [x] **H+C**: Four official challenge PDFs staged and verified byte-identical
      against the portal copies (2026-09-04)
- [x] **C**: Requirements matrix built, 92 rows, walked line by line at Stage 8
- [x] **H+C**: Thesis fixed: can a quantum-inspired training step beat a tuned
      GBDT on the metric a fraud team uses, under a protocol that cannot move
      after the result is seen

## Stage 2: Experiment design (Aug 30 to 31)

- [x] **C**: Preregistration v1.1 FROZEN at commit 95751b9, tag
      `prereg-freeze`. Amended 32 times, never rewritten
- [x] **C**: Gates with numeric pass criteria, fixed before any run

## Stage 3: Experiments (Sep 1 to 10)

- [x] **C**: ULB classical arms, ten seeds, stratified 60/20/20
- [x] **C**: CVQBoost proxy -- the exact classical solve of the identical
      Hamiltonian, which is what makes the hardware comparison meaningful
- [x] **C**: QFE phase-representation arm (H6) with trained-frequency GAM, GA2M
      and JOINT twins -- *delivered Sprint 9, A18/A19; measured null at -0.0115*
- [x] **C**: IEEE-CIS reduced Deotte recipe, UID excluded, leakage controls --
      *delivered Sprint 8, F3*
- [x] **C**: Temporal protocols: IEEE-CIS GroupKFold-by-month rolling origin and
      ULB temporal split -- *delivered Sprint 8*
- [x] **C**: Hardware blocks B1, G0b, B2, B3 on Dirac-3 -- *Sprints 4 and 12*
- [x] **C**: Shuffled-label control run on every fold, not merely declared

## Stages 4 to 6: Paper (Sep 4 to 11)

- [x] **C**: Outline, seven sections mapped to the rubric -- *delivered Sprint 5*
- [x] **H+C**: Outline approved
- [x] **C**: Draft with [HW]/[SIM]/[PROJ] on every number and prevalence beside
      every AUPRC
- [x] **H**: Team Capability content approved -- *Sprint 12, with the LLM-review
      disclosure added*
- [x] **C**: Domain-reviewer pass and revision
- [x] **C**: Quantum-reviewer pass -- *three external LLM reviews, Sprint 12;
      they found three FALSE published claims, all withdrawn (A26, A27)*
- [x] **C**: Rubric-scoring pass -- *F55 found two required sections missing
      entirely, together 35% of the Phase 1 weight*
- [x] **H**: Independent read-through as the reviewer

## Stages 7 to 8: Finalize and submit (Sep 11 to 12)

- [x] **C**: Every number in the paper verified against `results.json` --
      *Sprint 13 Task A; found nine defects the suite caught none of*
- [x] **C**: Pre-publication confidentiality scan -- *0 HIGH; the one REVIEW is
      the required contact block*
- [x] **C**: Reproducibility repository public -- *F37, Sprint 12, verified
      anonymously*
- [x] **C**: Compliance walk of every requirements-matrix row -- *Sprint 13
      Task B; six rows contradicted the shipped documents*
- [x] **H**: Final PDFs approved: 6 / 3 / 1 pages, US Letter, 10.0pt
- [x] **H**: **SUBMITTED via the portal 2026-09-12**, three days early. Receipt
      and the four now-answered A5 unknowns in
      `docs/submission/SUBMISSION_RECEIPT.md`
