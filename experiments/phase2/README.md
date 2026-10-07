# experiments/phase2

Phase 2 code and evidence, kept apart from Phase 1's files
(`docs/PHASE_SEPARATION.md`, F123).

- `src/`: Phase 2 modules. They IMPORT Phase 1 code from `experiments/src/`
  read-only and never edit it; where Phase 2 needs different behavior, it
  wraps.
- `results/`: Phase 2 evidence, one JSON file per experiment, each carrying
  its generator, card, evidence tag and metered seconds (team lead decision
  D7, Sprint 22). Rows in the section-11 schema, in a Phase 2
  `results.json`, start with the first run under the Phase 2
  preregistration (F102) or the first device run, whichever comes first.
  `results/device_samples/` holds device responses recovered in full by job
  id.

Tests stay in `experiments/src/test_*.py`, where CI already runs them.

**This layout is temporary.** The team lead decided at Sprint 22 Manual
Validation that Phase 2 moves to its own private repository, after which this
repository is restored as filed and archived (`docs/PHASE_SEPARATION.md`
section 9, card F127).
