# Sprint 8 Summary: The Second Dataset

**Dates**: 2026-09-06 to 2026-09-07 (~1.5 days)
**PR**: #47 (feature/20260906_Sprint_8 -> develop), then #49 (develop -> main)
**Cards**: #43, #44, #45, #46 (F3 Tasks A-D), #48 (F36)
**Metered Dirac-3 seconds spent: ZERO.** Every result is `[SIM]`.

## What shipped

**F3: IEEE-CIS under its preregistered protocol.** 590,540 transactions, 3
exact duplicates removed, 3.5% prevalence, GroupKFold-by-month rolling origin,
reduced Deotte recipe, UID excluded. Four tasks:

- **Task A** (#43): protocol compliance. Deduplication added to the IEEE loader
  with the count reported; the section 4 item 4 controls (time-consistency
  filter, adversarial validation) implemented as train-fold-only functions with
  seven known-answer tests. Replacing `permutation_importance` with a
  rank-based top-feature check cut about three CPU-hours to 46 seconds.
- **Task B** (#44): classical arms, rolling origin. LightGBM 0.5739, XGBoost
  0.5028, CatBoost 0.4795. Shuffled-label control collapses on every fold.
- **Task C** (#45): CVQBoost proxy arms. 0.0571 tuned / 0.0523 frozen at the
  six features the A12 ceiling permits.
- **Task D** (#46): H3 regime dose-response ladder. 12 cells, scoreable under
  the preregistered 3-cell rule.

## The findings, including the ones that cost us

**The matched-feature control is the most valuable thing built this sprint.**
CVQBoost's 0.0571 against a classical 0.5739 reads as a hardware failure until
the control is run: the same LightGBM given the SAME six features falls from
0.5424 to 0.0734. Every model is starved there, and the quantum arm attains 85%
of that constrained ceiling.

**The H3 ladder answers the ceiling question against our own interest.**
Lifting k from 5 to 17 does NOT close the gap: slope -0.006 AUPRC per feature.
Lifting the ceiling raises CVQBoost 2.8x and the GBDT 3.6x. The 100-variable
limit bounds absolute performance without being why the arm trails.

This **contradicts a claim made mid-sprint**, after Task C, that the ceiling was
the binding constraint. The contradiction is recorded rather than smoothed.

**Three findings that complicate our results** (`docs/reviews/f3-ieee-findings.md`):
the adversarial control never converged, hitting its 20-round cap on every fold;
our protocol run (0.574) sits below the published leakage-free band (0.64-0.67)
while our own random-split check reached 0.861; and AUPRC is not comparable
across datasets, so 0.5739 at 3.5% prevalence is a 16x lift against ULB's 490x.

**The preregistered compound falsification criterion is now stated** (appendix
B.1). Section 2 committed that the theory is unsupported if H1b fails AND the H3
slope is not positive AND H5 does not transfer. Two are now measured and both
went against the theory; H5 is unrun. The criterion has not fired -- but it has
not been survived either. The submission had been silent on this.

## A card that failed

**F36 (#48) is closed FAILED on its own acceptance criteria.** A pandoc Lua
filter was built to reclaim appendix page space that was never wasted. The
premise came from `page-fill-report.py` counting extracted CHARACTERS, which
makes any table-heavy page look short; measured as vertical extent, every page
already filled its text block with zero free space. Criterion 6 also caught that
floating tables COSTS `gate_report.pdf` a page, so the filter is retained
UNREGISTERED and opt-in via `render-pdf.ps1 -LuaFilter`.

The valuable output was fixing the instrument. Full writeup:
`docs/reviews/f36-float-tables-outcome.md`.

**The appendix did reach 3 pages**, by two team-lead suggestions: set pipe-table
column widths from the longest cell each column holds (every table used
`|---|---|`, giving "30" the same width as a sentence; removed 9 of 20 spilled
lines with zero content change), and move reference material to the public
repository. It has since returned to 4 pages with the compound-criterion
statement, tracked as F38.

## Pre-run audit: four protocol defects a passing smoke test missed

Found only because the team lead asked for a full sweep before re-running
(`docs/reviews/f3-preflight-audit.md`): no class weighting anywhere;
TransactionID and TransactionDT entering the model as raw features; the
shuffled-label control never actually run; and an MDE borrowed from a different
experimental design. The smoke test asserted the pipeline COMPLETES and nothing
about whether it was correct.

## Review

Copilot reviewed and raised three findings, all verified before acceptance and
all correct: "tuned classical arms" overstated fixed ULB-carried hyperparameters
(corrected in four places, in the direction that costs us -- the classical bar
is a FLOOR); the dedup annotation conflated rows removed with rows participating
in duplicate groups; and the variable arithmetic `6 + C(6,2)` was wrong while
its total happened to be right.

Copilot independently found the same folio defect found in self-review, and its
version was kept per the team lead's preference rule.

**Copilot's improved test then exposed a latent evidence-destruction bug**: it
executes the pipeline, and `run()` wrote to the evidence path regardless of
mode, so running the test suite replaced the full 590,537-row 3-fold results
file with a 1-fold smoke result. Caught from `git status`, restored before
anything committed over it, fixed by separating smoke output.

## Retrospective

`docs/sprints/SPRINT_8_RETROSPECTIVE.md`. Team lead rated all 16 categories
Very Good. Six improvements proposed, all approved and applied:

1. Runtime estimated separately from implementation (Task C ran 84 minutes
   without finishing a fold; it had been audited for compliance, never sized)
2. A card justified by a measurement must name its premise falsifier (F36's dry
   run could only confirm)
3. Smoke tests must assert correctness, not completion (6 new tests, each
   verified to fail against pre-audit commit a3186af)
4. Card-pruning scripts banned (one destroyed the same master-plan section
   twice; the second loss went unnoticed for a sprint)
5. Heredoc-with-backslash raised from guidance to an absolute (fourth
   occurrence, third since the rule was written)
6. Verify a tool before trusting its verdict

## Numbers

| | Sprint start | End |
|---|---|---|
| Tests passing | 145 | 156 |
| Test files | 15 | 18 |
| Commits | -- | 30 |
| Metered seconds | -- | 0 |

One test fails by design: `test_page_count_within_limit[appendix.pdf-3]`, the
appendix at 4 of 3 pages, tracked as F38.

## Registered to the backlog

- **F37** (SUBMISSION BLOCKER): make the repository public. Appendix C now cites
  it for the environment, checksums, preregistration, reference list and all 37
  QCi job records. An anonymous API request returned 404 on 2026-09-06.
- **F38** (SUBMISSION BLOCKER): appendix back to 3 pages.
- **F39** (HOLD until after submission): fact database with per-fact confidence
  between 0.0% and 99.9%, so 1,000+ asserted facts have one source of truth.

## Carried into Sprint 9

Card #40 stays OPEN: the QCi package send is the team lead's action and moved to
Sprint 9, with further letter feedback outstanding.
