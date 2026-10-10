# Testing Strategy

**Purpose**: What gets tested, how, and why, for the experiment pipeline.
**Audience**: Claude Code sessions; reviewers auditing the statistics.
**Last Updated**: 2026-09-02

Adapted 2026-09-02 from spamfilter-multi's TESTING_STRATEGY.md to a research-code
context: the product here is EVIDENCE, so tests exist to make numbers trustworthy,
not to cover UI surface.

## The known-answer principle

Every statistical or numerical routine is tested against an INDEPENDENT reference,
never against itself:

- BCa bootstrap vs `scipy.stats.bootstrap`; Wilson vs `statsmodels` (test_metrics.py, 11 tests).
- FISTA simplex QP vs `scipy.optimize` SLSQP on the identical Hamiltonian; simplex
  projection against hand-computable cases (test_qubo_proxy.py, 4 tests).
- Pool sizes vs the A2 closed-form (`data.qubo_vars`), which itself was verified
  against eqc-models source AND measured hardware runs (105/560 @ n=15).

A new metric or solver enters metrics.py/qubo_proxy.py only WITH its known-answer
test (ADR-0009; amendment-gated for frozen files).

## Guards as tests

Failure modes found in research (F18) become raising guards with tests: the n<4
schedule guard, the constructed-attribute round-trip assert (silent-kwarg-drop),
the {-1,+1} label contract. A guard that cannot fire in a test does not exist.

## Injection verification: prove the guard fails

**Mandatory for any test whose purpose is to fail** (Sprint 12 improvement 2).
Write the guard, then BREAK the thing it guards and confirm it goes red. Restore,
confirm green. Record in the test's docstring that it was verified by injection.

This is not ceremony. Three guards were written in Sprint 12 and injection-tested;
ONE of them passed vacuously on first write. `test_the_withdrawn_claim_does_not_return`
searched for a marker phrase that the markdown wraps across a line break, so the
literal substring never matched and the assertion could not fail. It would have
shipped as false assurance -- a green line asserting nothing, on a claim the
submission had just withdrawn.

The other two caught real defects when injected: the B3 pool-row guard failed on
the exact comparability defect that reached the documents, and the dispersion
grouping guard failed on the collapsed single-group artifact.

A guard that has never been seen to fail is a guard nobody has tested. The cost
is two minutes per guard; the alternative is a suite that is green for reasons
nobody has checked.

## Smoke before scale

Every campaign entry point has a `--smoke` mode (minutes, small stratified sample,
reduced trials/seeds) run BEFORE the full launch in the same session -- the
capability pre-flight rule from SPRINT_PLANNING.md applied to our own code.
Smoke artifacts are deleted before real runs (they share the checkpoint files).

## Leakage controls as executable tests

The shuffled-label positive control (prereg 5.6) runs with the IEEE-CIS campaign
(F3): test AUPRC must collapse to the base rate, else the pipeline leaks. Loader
row/label asserts (data.py) run on every import path. Dedupe-before-split counts
are recorded in results.json meta and checked at gate review.

## What is deliberately not tested

One-shot documents, sprint tooling scripts (verified by use), and plots. The
results.json store is validated by schema-shaped construction (ADR-0008) plus the
STATISTICAL_REVIEW_CHECKLIST walk at gate review, not by a test double.

## Running

```powershell
.\.venv\Scripts\python.exe -m pytest experiments/src -q     # full suite (~15 tests)
.\.venv\Scripts\python.exe experiments\src\run_classical.py --smoke
```
