# Sprint 6 Summary: The Diverse Pool

Archival record (three-doc rule). Date: Sep 5, 2026. Branch
`feature/20260905_Sprint_6` (carried forward from Sprint 5's head); PR #36.
Sources: SPRINT_6_PLAN.md, SPRINT_6_RETROSPECTIVE.md, git history, PR #36.

## Objective

Test whether the CVQBoost optimizer does useful work on a pool that is not
degenerate, and prepare Sprint 7 and 8 work in parallel. Scope: F31, F3 prep,
F23, F24, F32. Four concurrent tracks.

## Delivered

1. **F31, the central result.** A mixed pool of four learner families (dct, lda,
   lg, knn; 312 learners) over ten seeds moves the optimum genuinely off
   uniform: L1 distance 0.127 against the frozen pool's 8.0e-08, largest weight
   1.24x uniform against 1.0000000, solved-minus-uniform +0.0076 on 10 of 10
   seeds against +0.0022.
2. **Two controls that make it credible.** Sprint 5's apparent gain was
   tie-breaking; this one is not. Rounding solved scores to two decimals leaves
   FEWER distinct values than uniform produces (96 against 123) yet still scores
   0.7693 against 0.7607, so the advantage cannot come from finer tie-breaking.
   And shrinking weights from uniform toward the optimum traces a monotone AP
   curve, which sampling noise does not produce.
3. **F32, 10 metered fits, 43.0 device seconds** of a 40-50 s approval, zero
   failures, all billing parsed. Hardware minus proxy -0.0007, weight cosine
   0.977 to 0.983. Operating points now computed from PERSISTED hardware
   predictions: recall 0.271 / 0.509 / 0.839 at the 0.05 / 0.1 / 0.5% budgets
   [HW], closing the external-review finding that aggregate AP similarity does
   not establish the top-k equivalence an alert budget depends on.
4. **F3 prep** (agent): IEEE-CIS loader, preregistered feature pass, rolling
   origin splitter with a no-temporal-leakage invariant. 590,540 rows, 3.499%
   prevalence, checksums verified. +38 tests. No arm run.
5. **F23 prep** (agent): the Fourier Wall phase recipe as a fitted train-only
   transformer with an anti-leakage test that fails if test statistics reach the
   fitted parameters; all three twin families pre-flighted; ADR-0013.
6. **F24 prep** (agent): in-segment machinery with a matched random-segment
   control and the >=50-positive floor enforced in code; 3 cells frozen; the
   ADR-0003 provenance proof run (staged files match the FourierWall2-era
   originals byte for byte); B4 request drafted.
7. **Amendments A11 and A12**, both registered before their work was used.

## The two errors we corrected in our own claims

**"The binding constraint was our own budget rather than a device ceiling."**
False. Submitting a 312-variable job returned HTTP 400 server-side: the free
tier refuses any continuous degree-2 job above 100 variables. Our frozen pool is
91 variables, sitting under that ceiling by accident rather than design, which
is why no earlier run met it. A reviewer with QCi access could have falsified
the sentence in one API call. Corrected in the proposal; registered as A12 with
the verbatim message; zero metered seconds established it.

**The spend guard's own arithmetic.** Two defects in one sprint. A cap was set
at 60 s when 50 s was approved, which would have let the code authorize spend
the team lead had not granted. And the pre-call projection added `_spent()`
(reading results.json) to the in-memory rows `append_row` had already written
there, double-counting every fit: the block halted at a reported 50.0 s when
25.0 s had been spent, losing four approved seeds. Both found by reading rather
than by a test, which is why F34 was registered.

## What the result does and does not say

It says the optimizer has real work to do on a heterogeneous pool, with the
mechanism measured rather than asserted. It does NOT say the quantum arm won:
+0.0076 is well below the preregistered 0.0268 MDE. And one fact cuts against
the convenient reading, recorded in the proposal in the same breath as the
finding: the mixed pool's absolute AUPRC is 0.7565, BELOW the frozen pool's
0.7681. Diversity bought the optimizer headroom, not accuracy. Loke et al. reach
above 0.8 with a heterogeneous pool, so the remaining gap is learner quality and
tuning, which is exactly what F33 tests in Sprint 7.

## Estimated vs actual

Best of the project on authored work. The capability pre-flight cut F31 from an
estimated 6-10 h to 180 m and ran close to it. Agent tracks came in at roughly
0.2-0.3 of estimate, consistent with Sprint 4's research agent, so agent tasks
should be estimated at about a third of main-loop work. F32 overran badly
against 90 m because it failed three times before succeeding -- a schema defect,
a device refusal and the spend bug -- none of which was in the estimate. Metered
work needs a contingency multiplier that authored work does not.

## Key decisions

- Section 3 rewritten to the two-part finding (team lead approved the Class 2
  evidence-claim change).
- ADR-0013 accepted: REPLACE rather than augment for the raw column under phase
  encoding (k<=6 free tier, k<=8 device), and keep the statsmodels/sklearn twin
  substitutes with the caveat disclosed.
- B4 NOT approved, deferred on sequencing rather than science, with the
  reasoning and re-present conditions recorded at the top of the request itself.
- QCi cover rewritten to lead with the commercial case: what 30,000 QPU seconds
  returns to QCi, what we want beyond the challenge, then the science.
- Sprint 7 takes F33, Sprint 8 takes F3; the roadmap was renumbered rather than
  treating them as competing for one sprint.

## Retrospective improvements applied

Suite 50 -> 115 across the sprint. `-u` for background python recorded in the
Windows guide with the failure it caused; `test_row_schema.py` asserts every row
carries the fields its consumers index; `check_free_tier_size` refuses an
oversized job locally so the device never has to; `scripts/page-fill-report.py`
diagnoses whether an over-limit document has a length problem or a page-break
problem, which two sprints of prose-trimming failed to distinguish.
