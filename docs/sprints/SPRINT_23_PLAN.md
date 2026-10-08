# Sprint 23 Plan: Restore the Repository as Filed

**Sprint**: 23 | **Branch**: `feature/20261007_Sprint_23`
**Planned**: 2026-10-08 | **Status**: DRAFT, awaiting approval
**Scope**: F127, the steps that run in this repository (the team lead's
selection, 2026-10-08: "F127 only, planned and recorded here as usual")
**Metered Dirac-3 seconds**: **0**.

## Objective

Make this public repository show what was filed on 2026-09-12, then hand it
to the team lead to archive. The proposal and appendix cite its URL, so a
reader who follows the link should find the filed tree.

Phase 2 work has moved to `kimmeyh/hsbc-quantum-fraud-2026p2`, and Claude
sessions are split (team lead, 2026-10-08). This sprint covers only the
cleanup here. The other session owns the rest of F127 step (5) (the new
repository's CLAUDE.md boundary update), IMP-6, F128, F130 and F131.

## Already done (2026-10-07, before this plan)

F127 steps (2) to (4) and the CI half of (5): all 32 branches and 2 tags in
the new repository with matching tips; 195 ignored paths copied and
hash-verified; a fresh venv from the lock file; the full suite run there; CI
green on its draft PR #1. The Phase 1.3 record (`aff86e1`) is pushed to both
repositories.

## What the pre-flight found, before any estimate

Each finding changes a task.

1. **The as-filed `.gitignore` exposes private files.** At `f35699c` it does
   not ignore `docs/qci_package/` (18 files of private QCi correspondence),
   `.claude/settings.local.json`, `.claude/scheduled_tasks.lock` or
   `experiments/results/b3_hardware.dryrun.json`. All four exist in this
   working tree. A plain restore leaves them unignored in a public repository,
   and one `git add -A` would publish them. This is the Sprint 16 IMP-2 class.
   Decision D1 below.
2. **The restore brings back old process files.** At `f35699c`, `.claude/`
   holds the PowerShell hooks and a status file that says Sprint 14,
   `phase_5_manual_validation`, `pr: null`, `plan_approved: true`. That is the
   exact pair the old close-out hook blocks on (CLAUDE.md, Sprint 17 entry).
   So the restore is built in a separate git worktree, and this session's
   working tree never checks out the restored tree.
3. **The restore deletes `.githooks/pre-commit`**, which did not exist at
   `f35699c`. If the file leaves the disk before the commit, the
   confidentiality scan does not run on the commit that removes it. The
   recipe keeps the file on disk, untracked, until the commit is made.
4. **`docs/paper/qci_cover.md` is tracked at `f35699c`.** A plain restore
   brings it back. The exception list keeps it out, so the recipe removes it
   explicitly.
5. **The three filed PDFs are not tracked at `f35699c`.** "Stay in" means they
   are carried forward from the current tree. Their bytes are checked against
   the SHA-256 values in `docs/submission/PACKAGE.md`.
6. **The guarded documents do not change.** `proposal.md`, `appendix.md` and
   `team_profile.md` are identical at `f35699c` and `HEAD`. The restore does
   revert `experiments/PREREGISTRATION.md` by one amendment (A33, 2026-09-19).
   That is the point of an as-filed tree; A33 lives on in the new repository.
7. **The protection hooks do not block the recipe.** The restore is a new
   forward commit: no force push, no reset to a remote ref, no move of
   `prereg-freeze`, and no Edit or Write on a guarded document.

## Decisions needed at approval

**D1. The as-filed `.gitignore` (pre-flight finding 1).**

1. Keep the current `.gitignore` as a fourth restore exception. The tree then
   differs from `f35699c` by one more file, which holds ignore rules only, not
   filed content (recommended)
2. Restore the as-filed `.gitignore`, and protect the four paths only in this
   clone's `.git/info/exclude`. The tree is closer to filed, but the
   protection is untracked and lives on one machine
3. Restore the as-filed `.gitignore`, and delete the four paths from this
   working tree. The new repository holds hash-verified copies

**D2. Sprint numbering in the new repository.** This sprint's records stay on
`feature/20261007_Sprint_23`. The new repository already has that branch, with
draft PR #1 and a status file that says Sprint 23.

1. The new repository's first sprint is Sprint 24, on a new branch cut from
   `feature/20261007_Sprint_23` at `aff86e1`. Its session never commits to the
   Sprint 23 branch and closes draft PR #1. This repository pushes its final
   Sprint 23 record to that branch before the restore (recommended)
2. The new repository keeps the number 23, and this repository's sprint is
   renumbered

## Tasks

| Task | Card | What | Est | Depends on |
|---|---|---|---|---|
| A | F127 (6) | Restore recipe, dry run in a scratch worktree: `git read-tree -m -u f35699c`, then the exceptions; verify | 45 | D1 |
| B | F127 (3) | Sprint 23 retrospective written and committed; branch pushed to the new repository before the restore commit | 30 | A, Manual Validation |
| C | F127 (6) | Restore commit on this branch, built in a worktree; push; CI; PR marked ready | 25 | B |
| D | F127 (6) | After the team lead merges to `develop` and `main`: tag `as-filed` on `main`, push the tag, verify | 15 | C, team-lead merges |
| - | F127 (7) | **Team lead** archives this repository | - | D |

**Derived total: 115 minutes**, the sum of the task estimates above.

### Task A detail: the restore recipe and its checks

In a scratch worktree, detached at this branch's tip:

1. `git read-tree -m -u f35699c`
2. Exceptions: `git rm --cached docs/paper/qci_cover.md` and delete it if
   present; `git checkout <tip> --` for `docs/paper/out/proposal.pdf`,
   `appendix.pdf`, `team_profile.pdf`, `docs/submission/PACKAGE.md`,
   `docs/submission/SUBMISSION_RECEIPT.md`, and `.gitignore` if D1 is 1
3. Checks, each recorded with its output:
   - `git diff --cached --stat f35699c` names only the exception files
   - the three PDFs' SHA-256 equal the values in `PACKAGE.md`
   - under the resulting `.gitignore`, every one of this tree's currently
     ignored paths is still ignored (`git check-ignore`), or D1's chosen
     handling covers it
   - the confidentiality scan runs on the staged diff

The dry run commits nothing. Its output goes to the Manual Validation list.

### Task C detail

Task A's recipe again, on the branch tip after Task B, in a worktree. The
worktree keeps `.githooks/pre-commit` on disk, untracked, so the hook runs on
the commit; the file is deleted after. CI on the PR runs the as-filed
`ci.yml` and suite. A red result there goes to a background agent as usual,
and it is reported, not hidden: the as-filed suite last ran on 2026-09-12.

## Deviations from the process, for approval

- **Three-doc rule.** There is no Sprint 24 in this repository, so
  `SPRINT_23_SUMMARY.md` is written in the new repository, by its session, at
  its next planning, from this sprint's retrospective. This repository's
  restore removes the plan and retrospective from the tree; they survive in
  history and on the new repository's `feature/20261007_Sprint_23`.
- **Phase 7 runs before the restore commit, not after.** The retrospective
  (Task B) is written before Task C. After the merge, this repository's hooks
  and status file are the as-filed ones, so no close-out step can run here.
- **Main-merge tag by Claude.** The `as-filed` tag is created by Claude on the
  commit the team lead merged. It is not a merge.

## Premise falsifiers

- **F127's acceptance**: `git diff --stat f35699c as-filed` shows only the
  approved exceptions. **Falsifier**: any other path appears. Then the restore
  is wrong, whatever the CI result.
- **No exposure**: every path ignored today is still ignored after the
  restore, or handled under D1. **Falsifier**: one is not.

## Risks

- **The as-filed suite on today's CI runner.** It may fail on runner or
  package drift since 2026-09-12. That says nothing about the filed content,
  but it is reported as found.
- **The restored tree's hooks.** Covered by pre-flight finding 2: built in a
  worktree, never checked out here.
- **Branches and tags.** No branch is deleted here or in the new repository
  (Phase 2.2 retention rule). `prereg-freeze` does not move.
- **Allocation.** None spent; the balance stays 1,022 s.

## Model assignments

All tasks on the top tier in the main loop. No subagents planned.

## Definition of Done

- `as-filed` tag on `main`; `git diff --stat f35699c as-filed` shows only the
  approved exceptions
- The three PDFs' bytes equal their recorded SHA-256
- No private path unignored (D1)
- The Sprint 23 plan and retrospective are on the new repository's
  `feature/20261007_Sprint_23`
- Zero metered seconds
- The team lead archives the repository (the team lead's step)
