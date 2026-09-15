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

## Things Claude Should NOT Do

Added 2026-09-15. Every entry below is a failure that actually happened in THIS
repository, with the sprint that paid for it. Memory is recalled selectively;
this file is read in full every session, which is why these live here and not
only in memory.

- **Don't ask a decision question as prose or as an AskUserQuestion menu. Use a
  PLAIN NUMBERED LIST answerable by typing a digit.** The test is mechanical: if
  the team lead cannot answer by typing `1`, the format is wrong. Applies to
  yes/no (`1. Yes  2. No`), option comparisons and path selection, everywhere,
  including outside any sprint enforcement window. (Corrected four times in
  spamfilter-multi: three were AskUserQuestion by reflex, the fourth was two
  bolded paragraphs with a recommendation and no tool at all. This repository's
  CLAUDE.md never carried the rule, which is how it failed to reach
  EvidenceBasedDB when that repo was seeded from this one.)

- **Don't put two decisions in one question.** Each question gets one
  unambiguous answer form. Never write a question where "yes" maps to two
  different actions; split it or number the parts.

- **Don't refer the team lead back to instructions he would have to scroll for.
  Re-present them in full, every time.** "The plan from earlier" may be 5, 20 or
  50 screens back behind tool output and test runs. This binds hardest at Manual
  Validation, which is handed over once and then followed by hours of review and
  fixes. Restating a list costs a few lines; making him hunt for it costs his
  time and breaks the task he was starting.

- **Don't present a list for approval that contains items you are not proposing
  to change.** A recommendation list is only the things to be changed. (Sprint
  13: a "recommendation" mixed a proposed edit with items to leave alone, and
  the team lead approved the fix believing he was approving the recommendation.
  He later confirmed the correct answer had been "do not change proposal.md" and
  said plainly: "I was just testing you.")

- **Don't claim a guard works because the suite is green. Prove it FAILS.** A
  test that cannot fail is worse than no test, because it buys false confidence.
  Break the thing it guards, watch it go red, then restore. (Three vacuous
  guards in two sprints: a substring assertion matching text that appeared twice,
  once cosmetically; a changelog-currency guard whose threshold was 14 days when
  the lapse it was written for was 8, so it passed on its own defect; and
  `test_guard_discipline.py` resolving its path one directory ABOVE the
  repository, reporting a file that exists as absent and skipping. The last one
  shipped in the repository created to prevent this class.)

- **Don't verify a background job's effect before the job has finished.** A
  mistimed check reads exactly like a passing one. (Sprint 13: a dry run
  overwrote committed hardware evidence -- `b3_hardware.json`, 12 fits and 62
  metered seconds -- and the "artifact untouched" check ran before the
  background job wrote. The check passed. The evidence was gone.)

- **Don't restate a number that another file owns.** The official record of a
  sprint is five files: `SPRINT_n_PLAN.md`, the review/retrospective,
  `SPRINT_n_SUMMARY.md`, `CHANGELOG.md` and `README.md`. Everything else
  REFERENCES those. Suite counts are never restated anywhere -- run the suite.
  (Sprint 14: `ALL_SPRINTS_MASTER_PLAN.md` said "counts are deliberately not
  restated here" and restated one two lines later, wrongly, in the same PR.)

- **Don't trust a PR review finding over the team lead's stated rule.** A review
  asked for ten deleted completion stubs to be restored as "the surviving audit
  trail". They were not -- the sprint summaries are, and each stub re-created a
  PR number owned elsewhere. Reviews are evidence, not instructions.

- **Don't stage a commit without reading what you are staging.** Run
  `git status --short` first and account for every entry. `git add -A` is fine
  once you have. (Sprint 14: `git add -A` in EvidenceBasedDB swept an
  uncommitted PowerShell-to-Python hook conversion that was not mine into a
  commit whose message described none of it. Unwound and split.)

- **Don't let a shell or a JSON parser eat an escape and call the result
  success.** This has now bitten three times in one sprint: a single backslash
  before `block-` in `.claude/settings.json` is a JSON backspace, so two
  Edit-matcher hooks pointed at nonexistent files and NEVER RAN; a test left
  Windows separators after substitution, so a path check was always False on
  POSIX and CI went red on four consecutive commits; and a heredoc doubled every
  backslash in a README so the paths would not work if pasted. The failure mode
  is a plausible wrong result, not an error.

- **Don't report a phase or close-out complete without opening the checklist and
  walking it line by line in the same turn.** "I believe I did that" is not
  verification. (Sprint 14: `CHECKLIST-Phase2-pre.md` was never reconciled --
  F67, F39 and F72 shipped and stayed unticked -- and it was found a sprint
  later.)

- **Don't state what an external system contains without opening it.** Reasoning
  from adjacent code or a stale note is not evidence. If it cannot be inspected
  this turn, write the claim with the word **unverified** and say what would
  settle it.
