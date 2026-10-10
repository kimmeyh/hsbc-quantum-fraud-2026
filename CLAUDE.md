# CLAUDE.md

Guidance for Claude Code sessions in this repository. The authoritative process docs are `docs/SPRINT_PROCESS.md` (always-loaded overlay) and the full set it names; the authoritative methodology is `experiments/PREREGISTRATION.md` (FROZEN, amendments only).

## Review scope: generated evidence artifacts are OUT of scope

`experiments/results/*.json` and `experiments/results/gate_report.md` are GENERATED evidence artifacts, not source code. A sprint diff routinely adds thousands of lines of them.

**Do not code-review these files.** When running `/code-review` or any review pass on a PR in this repository, state the exclusion in the invocation and review only:
- code that produces the evidence: `experiments/src/*.py`, `scripts/*`
- documents that interpret it: `docs/*.md`

The evidence files have their own verification path: `score_gates.py` regenerates every reported figure, `docs/STATISTICAL_REVIEW_CHECKLIST.md` is walked before any figure becomes gate evidence, and the section-11 row schema is enforced by `test_row_schema.py` in CI. (Corrected 2026-09-12: this line previously said `store.py` enforces the schema AT WRITE TIME. It does not -- `store.py` does config hashing, atomic writes and a lock, and validates no fields, so a malformed row is written successfully and caught afterwards by the suite. An overstated guarantee is worse than a documented gap, because it invites reliance that is not there.) Reviewing the data files consumes large review budget for no signal and has caused review runs to stall (Sprint 3 and Sprint 4).

## Standing rules (see docs/SPRINT_PROCESS.md for the full set)

- All PR merges are the team lead's action, at every level. Claude never merges.
- Metered Dirac-3 runs ALWAYS stop for explicit per-block approval with call count and expected seconds stated (Criterion H).
- Team-lead `0*` working files at repo root: commit with a neutral message, never read.
- `--no-verify` is banned; the pre-commit confidentiality hook stays active.
- Every reported number originates in `results.json` with an evidence tag.
