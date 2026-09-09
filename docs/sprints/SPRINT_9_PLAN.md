# Sprint 9 Plan: Representation, and Paying What We Promised

**Dates**: 2026-09-07 to 2026-09-09
**Branch**: `feature/20260907_Sprint_9`
**Scope (team lead selection, DEFINED not additive)**: F4, F16, F14
**Metered Dirac-3 seconds planned: ZERO.**

## Objective

Run the last preregistered experimental arm (H6 representation effect) with the
classical twins that make it honest, and assemble the eqc-models feedback the
QCi letter already promises. Add CI so the suite runs on every PR.

## Calendar position

5 days to the Sep 12 evidence freeze, 6 to the Sep 13 target submission. F4 is
the last preregistered arm that can still produce evidence before the freeze.

## Scope note

The selection is F4, F16 and F14 only. F37 (repository public) and the QCi
package send were discussed at refinement and are NOT in this sprint's scope.
The send remains card #40, team-lead owned.

## Velocity

Sprints 5, 6, 7 at ~1 day each; Sprint 8 at ~1.5 days. This plan totals 285
minutes against a 2-day window, which is deliberately under-packed: Sprint 8
ran 1.5 days on a 420-minute plan, and the last sprint before an evidence
freeze is the wrong one to overcommit.

## Tasks

| # | Task | Est | Runtime | Metered |
|---|---|---|---|---|
| A | F4: QFE phase arms with order-matched twins | 150m | **~10m measured** | 0 |
| B | F14: eqc-models feedback package for QCi | 90m | none | 0 |
| C | F16: minimal CI on PRs | 30m | ~1m per PR | 0 |
| | Close-out, retro, review loop | 15m | -- | 0 |

**Runtime is estimated separately from implementation** (Sprint 8 improvement
1). Both numbers are stated because Task C last sprint was estimated at 120
minutes for the code and then burned 84 minutes of runtime without finishing a
fold.

### Task A: F4, QFE phase arms with order-matched twins (150m)

**What.** H6 (preregistration section 3, exploratory): the QFE phase
representation is given to EVERY arm, and the question is whether it shifts the
quantum-minus-classical delta. Every H6 cell's classical bar must include a
trained-frequency GAM, a GA2M, and an order-matched JOINT twin alongside the
GBDTs.

**Why the twins are the point.** The Fourier Wall result is that omitting the
order-matched twin is how apparent quantum wins get manufactured. A phase
representation gives a quantum arm access to periodic structure; if the
classical bar has no model that can also use periodic structure, any gap is an
artifact of the comparison rather than a finding. The twins are not extra rigor
here, they are what makes the cell interpretable.

**Runtime, sized before planning rather than after** (improvement 1):

| Component | Cost | Source |
|---|---|---|
| ULB GBDTs, 20 cells x 3 arms | 3.0 min | measured fit times |
| IEEE GBDTs, 6 cells x 3 arms | 4.1 min | `ieee_classical.json`, 10-20s per fit |
| GA2M twin | 3.0s per cell | measured, 60k x 40 |
| JOINT twin | 0.1s per cell | measured |
| GAM twin | 0.4s per cell | **piloted**, linear scaling to 60k |
| **Total** | **under 10 min** | |

GAM was the one unbounded term and was PILOTED before this plan was written:
GLMGam with BSplines scales linearly (0.0s / 0.2s / 0.4s at 5k / 20k / 60k
rows), so the family that could have blown up does not. No task starts unsized.

**Capability pre-flight: already done.** `experiments/src/h6_twin_preflight.py`
(Sprint 6) proved all three primitives in this environment: statsmodels GLMGam
for GAM, sklearn `HistGradientBoostingClassifier(interaction_cst=...)` for
GA2M, and a coarse-to-fine cosine scan plus LogisticRegression for JOINT.
pygam and interpret are NOT installed and are not needed.

`experiments/src/qfe.py` already implements the Fourier Wall encoder with nine
tests covering rank invariance, phase bounds, low-cardinality exclusion,
train-only whitening and leakage.

**Acceptance criteria**:
1. Every H6 cell carries all three twins plus the three GBDTs. A cell missing a
   twin is not reported, since a partial classical bar is the failure mode the
   twins exist to prevent.
2. The QFE encoder is fitted on TRAIN folds only; a test asserts that fitted
   state differs between two training sets that share test rows.
3. Results land in `results.json` with `[SIM]` tags and a configuration hash.
4. The delta reported is quantum-minus-classical WITH the phase representation
   against the same delta WITHOUT it. The hypothesis is about the SHIFT, so a
   single-representation number does not answer it.
5. Registered as exploratory under a dated amendment BEFORE the run, per the
   frozen preregistration.
6. Written up in proposal and appendix with whatever it shows, including a null
   or a result that weakens our position.

**Premise falsifier** (Sprint 8 improvement 2): this task's premise is that a
phase representation could shift the delta. It is disproved if the QFE and
baseline representations give deltas whose difference is within seed noise --
that is a real, reportable answer, not a failed task.

### Task B: F14, eqc-models feedback package for QCi (90m)

**What.** Assemble the integration feedback the QCi letter already promises
under "What we give back", as a standalone document that can be attached.

**Why now, when the card said "assemble after the hardware campaign".** The
letter has not sent yet, and it promises this package. A letter promising
deliverables with none attached is weaker than one where a reviewer can see the
work exists. This is the highest-leverage item available for the QCi ask, and
it costs no metered time.

**Source material, verified present before estimating**:
- Free-tier ceiling: a 312-variable job refused server-side with the exact
  message, before billing (`run_hardware_f32.py:60`). Documented 949 limit is a
  sum over `num_levels` for integer-encoded jobs and does not bind continuous
  sum-constrained runs -- a documentation/implementation divergence.
- Billing field not readable as a dictionary key, with a conservative
  `UNPARSEABLE_CALL_CHARGE_S = 10.0` guard built around it
  (`run_hardware.py:60`, `run_hardware_f32.py:58`), plus the property test that
  pins the vendor-format failure (`test_hardware_guards.py:43`).
- Pool construction requires fork and fails on Windows; the full-pair build runs
  in WSL and the `.npz` is solved on Windows (`qubo_proxy.py:13-22`).
- Measured cost model: 37 metered fits, 163 device seconds, 4-5s per fit, zero
  failures, zero retries; within-fit energy spread median 0.019%, max 0.343%.
- The classical proxy itself, already offered in the letter as a deliverable.

**Acceptance criteria**:
1. A single document at `docs/QCI_EQC_MODELS_FEEDBACK.md`, renderable by
   `render-all.ps1 -QciPackage`.
2. Every claim cites the file and line, or the results row, that establishes it.
   A vendor-facing bug report whose claims cannot be checked is worthless.
3. Each finding states what we observed, what we expected, and what we did
   about it -- not a complaint list.
4. No account identifiers, API keys or job tokens. Verified by
   `confidentiality-scan.ps1` before commit.
5. The QCi letter's "What we give back" section references the attached
   document rather than describing it in prose.

**Explicitly out of scope**: sending anything. Card #40 is team-lead owned.

### Task C: F16, minimal CI on PRs (30m)

**What.** GitHub Actions running `pytest -m "not slow"` and a lint pass on PRs
to develop. Sub-minute, no dataset access, no metered access.

**Why it earns its place in the last week.** Sprint 8 shipped a bug where
RUNNING THE TEST SUITE overwrote the evidence file every reported IEEE figure
traces to. It was caught from `git status` by luck. CI is the tripwire for that
class of defect, and it is 30 minutes.

**Acceptance criteria**:
1. Workflow runs on PRs to develop, completes in under 2 minutes.
2. Runs `pytest -m "not slow"`; the slow marker keeps the 89-second live
   pipeline test out of the PR path.
3. **A dirty working tree after the test run FAILS the build.** This is the
   specific Sprint 8 defect: a test that modifies tracked files is a defect
   whether or not its assertions pass.
4. No dataset and no QCi credentials required; the run works from a clean
   checkout.
5. The known-failing F38 page-limit test does not block the build, since it
   fails by design and is tracked. Excluded by name with a comment pointing at
   F38, not by weakening the test.

## Risks

| Risk | Mitigation |
|---|---|
| F4's twins produce a null and there is no headline | A null IS the H6 answer and is reported as one. The compound falsification criterion already stands at two of three; a third measured null is a finding, not a failure |
| F4 registered as exploratory but read as confirmatory | The amendment is written BEFORE the run and says exploratory. H1b remains the sole confirmatory endpoint |
| CI fails on the tracked F38 test and blocks PRs 5 days from freeze | That test is excluded by name with a comment; F38 stays a tracked blocker |
| F14 leaks an identifier into a vendor-facing document | `confidentiality-scan.ps1` before commit, per acceptance criterion 4 |
| Sprint runs long against the Sep 12 freeze | Plan is 285m against 2 days. If it slips, Task C drops first: it protects future work, while A is the last preregistered arm and B is a promise already made |

## Model assignments

All tasks on this model. Task A is protocol reasoning against a frozen
preregistration, Task B is technical writing that must be exactly accurate to
external readers, and Task C is small. No subagents.

## Definition of Done

Per `sprint_planning.md`: acceptance criteria met with evidence; tests green;
results in `results.json` with evidence tags; docs updated in the same commit;
committed with the issue number.
