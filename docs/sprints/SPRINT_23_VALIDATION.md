# Sprint 23 Manual Validation

**Sprint**: 23 (the last sprint in this repository) | **PR**: #167
**Handed over**: 2026-10-08, after Task A (#168)

The durable copy. The items were listed to the screen at handover.

## V1. The restore changes exactly the approved paths

Task A's dry run, in a detached worktree at `69c9da1`, committed nothing.
`git diff --cached --stat f35699c` named exactly 7 paths:

- `.gitignore`: kept at current content (D1)
- `docs/paper/out/proposal.pdf`, `appendix.pdf`, `team_profile.pdf`: kept;
  SHA-256 equal to the values in `docs/submission/PACKAGE.md`
- `docs/submission/PACKAGE.md`, `docs/submission/SUBMISSION_RECEIPT.md`:
  kept at their post-filing text
- `docs/paper/qci_cover.md`: removed (private correspondence)

All 260 files ignored in this working tree stay ignored. The pre-commit scan
ran on the staged restore and blocked a planted match.

## V2. What the restore takes away from this repository's tree

Everything added or changed since 2026-09-12 leaves the tree, except V1's
paths. It stays in git history and in the Phase 2 repository. This includes:

- `CLAUDE.md`, `.claude/` hooks and settings, `.github/workflows/ci.yml`:
  back to their 2026-09-12 versions (the PowerShell hooks; a status file
  that says Sprint 14)
- `.githooks/pre-commit`: removed (it did not exist on 2026-09-12)
- `docs/sprints/` for Sprints 15-23, `docs/phase2/`, `experiments/phase2/`,
  and every results file added since: removed. Sprint 7, 8 and 11-14 records
  edited or added after the filing go back to their 2026-09-12 state
- `experiments/PREREGISTRATION.md`: loses amendment A33 (2026-09-19)

## Decisions

- V1: 1, approved (team lead, 2026-10-08)
- V2: 1, accepted (team lead, 2026-10-08)
