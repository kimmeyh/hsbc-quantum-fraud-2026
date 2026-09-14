# Checklist: Phase 1 Challenge Submission (CLOSED)

Owners: **H** = Harold (only you can do it), **C** = Claude (I do it), **H+C** = decision or review done together.

**STATUS: CLOSED 2026-09-12. THIS FILE IS NO LONGER UPDATED.**

Phase 1 was submitted on 2026-09-12, three days before the deadline, and judged
as filed. This file is the record of what was done, corrected to actuals rather
than left as the original plan.

**Do not tick, add or reword items here.** If something about Phase 1 turns out
to be wrong, the correction belongs in an amendment or a sprint document, not in
a retroactive edit to a closed checklist. A record that keeps changing is not a
record.

Live work lives in `CHECKLIST-Phase2-pre.md`. If selected, Phase 2 work lives in
`CHECKLIST-Phase2.md`.

---

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
