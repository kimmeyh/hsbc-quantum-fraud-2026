# Sprint 12 Summary

**Dates**: 2026-09-10 to 2026-09-12. **Branch**: `feature/20260910_Sprint_12`,
continued on `feature/20260910_F49_solver_certificate`.
**PRs**: #73 (to develop), #74 (develop to main), #75 (to develop).

Sources: SPRINT_12_RETROSPECTIVE.md, git history, PRs #73 and #75, the amendment
log A22-A31. Not the master plan.

## Scope, as delivered

Planned as F2b (B2 and B3 on hardware), document updates, and an independent
review. All three ran. The review then produced a second body of work larger
than the first: three external reviews found defects in what the sprint had just
published, and F49 through F63 were written, planned and executed in response.
F37 (repository public) and F38 (page limits) were also closed, both carried
from earlier sprints.

Suite **277 -> 315**. Hardware: **968 metered seconds** of a 2,000 s
authorization, 23 fits, zero device failures.

## What the hardware showed

**B2 ran in full and is the campaign's only positive result at scale (A24).**
Eleven fits at 833 continuous variables, 906 metered seconds. Against B1's
matched `dct` arm on identical seeds: **+0.0256 AUPRC, 95% CI [+0.0203,
+0.0310], 10 of 10 seeds**. Unpaired the effect is invisible inside a 0.030
seed-to-seed standard deviation; pairing cancels the shared variance. It still
trails full-feature CatBoost by 0.0440, so the null holds.

The comparator discipline mattered: B1's OVERALL mean of 0.7351 averages in the
weaker `lg` config and both temporal fits. The like-for-like arm is `hw_b1_dct`
stratified at 0.7671, and quoting the overall mean would have inflated the gain
from +0.026 to +0.056.

**B3 was published, withdrawn and re-run the same day (A22, A23).** The first
run built its pools on the whole training fold while the [SIM] arm it was quoted
against subsamples to 100,000 rows -- 4.1x to 5.8x more data and a different
lambda_coef. "Only the solver differs" was false as published. Re-run matched:
**12 fits, 62 seconds, every cell within 0.0013 of the classical ladder**, errors
scattering both ways. The corrected result is better than the one it replaced --
a clean solver-fidelity finding rather than an inflated performance claim.

## The three published claims that were withdrawn

**The solver was not converged (A26, F49).** `solve_weighted` stopped on
relative OBJECTIVE change at 1e-10. The frozen objective is nearly flat near its
optimum, so the test fired while the weights were still moving: KKT residual
**4.6e-05**. It certified the objective, not the solution. Now stops on a
certified KKT residual at **4.0e-10**.

Why no test caught it: our recomputation reproduced the published +0.0022
exactly, because the figure and the error came from the same solver. Every
internal check agreed with itself. An external reviewer solving the same ten
problems independently was the only thing that could have found it.

**The convexity claim was false (A27, F50).** `weak_cls_schedule` selects which
feature subsets each learner reads, not the Hamiltonian's order. Verified on
B2's own pool: H holds only -1 and +1, and the smallest eigenvalue of the
833x833 J is exactly the lambda term. The claim had been written the previous
day in response to an internal review and published within hours.

**Uniform is not the zero-penalty optimum (A27, F50).** At lambda = 0, equal
weights over the 82 perfect learners score 0.0097 BELOW uniform, on all ten
seeds. The sweep recorded the objective after solving FROM uniform -- the same
solved-from-versus-evaluated-at confusion as F49, in a different place.

## The deviation that had gone undeclared for eleven sprints

**G0's stopping rule (A28, F51).** The freeze commits that below 0.85 AUPRC "the
pipeline is presumed defective and everything halts". G0 scored 0.8296 and work
continued. The gate always read FAIL and nothing was rescored, so the scoring
was honest -- but reporting a failure is not honouring the consequence attached
to it. Now recorded as a deviation, with the uncomfortable ordering stated: the
floor was questioned only after it was missed.

Also corrected: "We did not find this paper before freezing" (of Loke et al.) is
false. The freeze names that configuration as H1a with its exact protocol.

## The finding that added evidence rather than removing error

**The 200:1 resolution argument (A31, F57).** We claimed hardware agreeing with
the classical proxy confirmed convexity and bounded resolution effects. The
second is backwards. On all ten pools the diagonal is 510,705 while off-diagonals
span at most 20.0, against a resolvable difference of 2,554 -- **nothing in the
problem is visible to the device.** Quantised at that resolution the off-diagonal
collapses to ONE distinct value and the minimiser is uniform to 2e-15. Hardware
returning uniform is forced, not evidence.

The same limit explains B2's previously unexplained 0.83 weight cosine: a diffuse
optimum over 833 learners averages 0.0012 per weight against a 0.005 resolution,
so it is not representable. All eleven retained responses confirm it -- exact
zeros in every fit, nonzero weights 0.0007 to 0.0029.

That turns the weakest mechanism paragraph into the strongest argument for the
Phase 2 direction: a device that cannot spread weight over ~200 learners has a
native problem class, and it is cardinality-constrained selection.

## The submission is within its limits

**F38 closed.** proposal 6 of 6, appendix 3 of 3, team profile 1 of 1. The strict
xfail markers fired the moment the documents came back under limit -- "whoever
closes F38 is forced to delete it", in the docstring's own words -- and are gone.

**F37 closed.** The repository is public and verified anonymously (HTTP 200,
freeze commit 95751b9 resolves, `prereg-freeze` tag intact). Appendix C's
reproducibility claim is true for the first time. Pre-flip scans across all 259
commits found no secret ever committed.

**F55** added the two required sections the proposal lacked -- "Feasibility and
Resource Requirements" and "Validation Plan" -- together 35% of the Phase 1
rubric, previously with no heading for a judge to score against.

## Two reviewer findings that were wrong

Recorded because verifying them was the right call and took real time.

**The allocation arithmetic.** A reviewer computed 3,000 - 1,141 = 1,859 and
called our 1,961 an error. The live endpoint confirms 1,961: 1,141 is the
CAMPAIGN total including 163 pre-grant free-tier seconds, and the grant
reconciliation is 10 + 61 + 62 + 906 = 1,039.

**The shuffled-label control.** A reviewer simulated a RANDOM scorer and called
our below-prevalence values defective. Ours trains a model on permuted labels and
scores true ones; below-chance is the expected direction and above-base-rate is
what indicates leakage. The control is sound, though "collapses" was loose
wording and the 2x criterion was generous -- both tightened.

## Numbers

| | |
|---|---|
| Tests | 277 -> 315, no xfails |
| Amendments | A22 -> A31 (31 total) |
| Metered seconds | 968 of 2,000 authorized; 1,961 of 3,000 remaining |
| Hardware fits | 23 this sprint (11 B2, 12 B3); 61 campaign total |
| Submission | 6 / 3 / 1 pages, all within limits |
| External reviews | 3, all findings fixed or recorded |
| Copilot findings | 1, fixed and resolved |

## What carries forward

- The k=17 order-2 decomposition cell (153 variables, zero metered cost), which
  separates k from subset order in B2's result and which B.3 currently has to
  describe as unrun
- `sprint_status.json` reconciliation
- PR #75 merge, which is the team lead's action
