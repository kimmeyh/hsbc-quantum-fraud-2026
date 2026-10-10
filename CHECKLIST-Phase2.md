# Checklist: Phase 2 (if selected)

Owners: **H** = Harold (only you can do it), **C** = Claude (I do it), **H+C** = decision or review done together.

**STATUS: DORMANT until finalist notification. Provisional until the Phase 2
brief arrives, and the brief overrides this file.**

## Change policy (team lead, 2026-09-12)

**THE SIX COMMITTED EXPERIMENTS DO NOT CHANGE.** They are what proposal section
6 promises, in the order it promises them, and the submission was judged on that
commitment. Reordering or dropping one is not a checklist edit; it would be a
departure from a published commitment and needs to be recorded as one.

**Everything else here may grow.** Items may be ADDED, and committed items may be
EXPANDED with detail, sub-steps, acceptance criteria and resourcing as we learn
what Phase 2 actually requires. That is expected and is why this file is not
frozen like Phase 1.

The distinction in one line: **add and elaborate freely; do not alter the six.**

---

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
