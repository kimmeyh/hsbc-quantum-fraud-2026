# ADR-0007: Training discipline -- checkpointed stages, atomic rows, resumable by construction

## Status

Accepted

## Date

2026-09-02

## Context

The campaign's long runs (6 Optuna studies, 80 refits, pool builds) span hours and survive session breaks, usage-limit resets, and machine sleep. Sprint 1-2 retro history shows sessions end mid-work; TIME LIMIT is explicitly not a stopping criterion, so the code must make interruption harmless.

## Decision

(1) Every long-running stage checkpoints at its natural unit: tuning per completed study (tuned_params.json), refits and proxy solves per completed row (results.json), WSL pool builds per saved .npz. (2) All state files are written atomically (temp file + os.replace) so a kill never leaves a torn JSON. (3) Re-running any entry point skips completed work by key, making "just run it again" the universal recovery procedure. (4) Long-running scripts carry a KNOWN FAILURE MODES header (retro improvement) stating expected duration and kill-safety. (5) Fits are never parallelized across arms by us -- each library already saturates cores (n_jobs=-1); parallelism is at most process-level between independent tracks (Optuna vs proxy vs WSL builds).

## Alternatives Considered

### Optuna RDB storage + journal for resume
- **Description**: SQLite-backed studies resumable mid-study.
- **Pros**: Finer-grained tuning resume.
- **Cons**: A study is ~30-60 min; the marginal saving does not buy the operational complexity (locks, files, cleanup).
- **Why Rejected**: Study-level checkpointing is enough at this scale.

## Consequences

### Positive
Any interruption costs at most one in-flight unit. Recovery requires zero thought.
### Negative
A killed 100-trial study restarts from trial 0.
### Neutral
Same pattern extends to F3/F4 runners.

## Preregistration touchpoints

Section 11 (results.json schema; every row complete at write time). The preregistration governs methodology; this ADR records engineering decisions only.

## References

experiments/src/run_classical.py, qubo_proxy.py; docs/QUALITY_STANDARDS.md known-failure headers; SPRINT_STOPPING_CRITERIA criterion 8/9; card #15.
