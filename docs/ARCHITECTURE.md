# Architecture

**Purpose**: The experiment pipeline's structure and the ADRs that govern each part.
**Audience**: Claude Code sessions; submission reviewers via the public package.
**Last Updated**: 2026-09-02

The methodology authority is `experiments/PREREGISTRATION.md` (FROZEN; amendments A1-A4). This document maps the code that implements it. Every module decision traces to an ADR (docs/adr/).

## Pipeline

```
experiments/src/
  data.py          Loaders (ULB / IEEE-CIS / SPECTRA), splits, top-k MI features,
                   qubo_vars (A2). Frozen at prereg-freeze. [ADR-0005, ADR-0006, ADR-0010]
  tune.py          Frozen Optuna search spaces, 100-trial budget, CV objective. [prereg 6]
  metrics.py       THE metrics implementation: step-wise AP, stratified BCa,
                   paired deltas, t-intervals, Wilson, equal-mass ECE. [ADR-0009]
  run_classical.py F1 campaign runner: dedupe -> tune stage -> per-seed refit
                   stage -> results.json rows. Checkpointed, atomic, resumable.
                   [ADR-0007, ADR-0008; amendment A4]
  qubo_proxy.py    CVQBoost proxy: eqc-models-native pool builds, exact Hamiltonian
                   (J=HH^T+lambda*I, C=-2Hy, simplex), FISTA solve, A3 build/solve
                   split (WSL full-pair). [ADR-0002; amendments A2/A3/A4]
  smoke_test.py, test_metrics.py, test_qubo_proxy.py   Known-answer suites.

experiments/results/
  results.json     Single evidence store; append-only schema-complete rows. [ADR-0008]
  tuned_params.json  Tuning-stage checkpoint (params, cv_ap, trials, wall time).
  pools/           Intermediate H matrices (gitignored; regenerable).

scripts/
  manifest.py      Dataset provenance manifest (portable keys). [ADR-0003]
  update-sprint-status.ps1  Parsed-JSON sprint state updates.
  wsl_build_pools.sh        A3 full-pair pool builds under WSL.
```

## Execution modes and platforms

- Windows is the primary platform; CVQBoost weak-pool builds run `sequential`
  (frozen config; also the Windows-only option). The A3 full-pair variant builds
  under WSL2 (fork) and is solved on Windows from saved H matrices.
- Hardware (Dirac-3) runs are gated by Criterion H, always; the proxy is the
  development and tuning surface (ADR-0002; zero metered seconds off-device).
- Everything long-running is background-launched with a log file and per-unit
  checkpointing (ADR-0007), so any interruption costs at most one unit.

## Logging conventions

Python loggers use the `frd.*` namespace (`frd.classical`, `frd.proxy`; future:
`frd.hardware`, `frd.qfe`), stdlib logging, `%(asctime)s %(name)s %(levelname)s`.
Long scripts log stage boundaries with bracket tags (`[TUNE]`, `[REFIT]`,
`[PROXY]`, `[BUILD]`, `[DATA]`, `[DONE]`) so logs grep cleanly. eqc-models'
own stdout chatter is captured by the run logs, never suppressed.

## Process layer

Sprint process: docs/SPRINT_PROCESS.md (overlay) + the execution doc set;
branch/carry-forward per ADR-0004; hooks (.claude/hooks/) enforce the stash ban
and close-out verification; the pre-commit confidentiality hook guards secrets
(ADR-0011). Governance of the frozen protocol: ADR-0001.
