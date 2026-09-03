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
