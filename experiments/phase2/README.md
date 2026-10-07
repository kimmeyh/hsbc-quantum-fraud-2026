# experiments/phase2

Phase 2 code and evidence, kept apart from Phase 1's files
(`docs/PHASE_SEPARATION.md`, F123).

- `src/`: Phase 2 modules. They IMPORT Phase 1 code from `experiments/src/`
  read-only and never edit it; where Phase 2 needs different behavior, it
  wraps.
- `results/`: Phase 2 evidence: its own `results.json` (the same row schema,
  plus `"phase": 2`), its own cost ledger, its own reports.

Tests stay in `experiments/src/test_*.py`, where CI already runs them.

Provisional from Sprint 22; the team lead confirms or adjusts the layout at
Sprint 22 Manual Validation.
