# CLAUDE.md

Guidance for Claude Code sessions in this repository. The authoritative process docs are `docs/SPRINT_PROCESS.md` (always-loaded overlay) and the full set it names; the authoritative methodology is `experiments/PREREGISTRATION.md` (FROZEN, amendments only).

## Review scope: generated evidence artifacts are OUT of scope

`experiments/results/*.json` and `experiments/results/gate_report.md` are GENERATED evidence artifacts, not source code. A sprint diff routinely adds thousands of lines of them.

**Do not code-review these files.** When running `/code-review` or any review pass on a PR in this repository, state the exclusion in the invocation and review only:
- code that produces the evidence: `experiments/src/*.py`, `scripts/*`
- documents that interpret it: `docs/*.md`

The evidence files have their own verification path: `score_gates.py` regenerates every reported figure, `docs/STATISTICAL_REVIEW_CHECKLIST.md` is walked before any figure becomes gate evidence, and the section-11 row schema is enforced by `test_row_schema.py` in CI. (Corrected 2026-09-12: this line previously said `store.py` enforces the schema AT WRITE TIME. It does not -- `store.py` does config hashing, atomic writes and a lock, and validates no fields, so a malformed row is written successfully and caught afterwards by the suite. An overstated guarantee is worse than a documented gap, because it invites reliance that is not there.) Reviewing the data files consumes large review budget for no signal and has caused review runs to stall (Sprint 3 and Sprint 4).

## Status footer: generate it, never type it

End decision-point and milestone replies with the footer line. **Generate it
with the script every time. Never assemble it by hand, and never carry a
timestamp forward from an earlier message.**

```
<venv python> scripts/status_footer.py
```

The interpreter is per-OS; `docs/ENVIRONMENT.md` is the single place it is
recorded. Output:

```
09/20/2026 12:30pm | Sprint 17 Phase 5.0 Review & Validation
```

- Reads the live clock on every call, and reads the sprint number and phase
  from `.claude/sprint_status.json` -- the same file the auto-advance hook
  reads, so the footer and the hook cannot disagree about the phase.
- A missing, malformed or phase-less status file still prints a usable line
  with an honest marker naming the path to check. It never raises, never exits
  nonzero and never prints nothing.
- `--sprint` and `--phase` override the file when needed.
- **Do not use the global PowerShell script** (`~/.claude/scripts/status-footer.ps1`)
  in this repository. It expects spamfilter-multi's prose status convention
  ("Sprint 70 Phase 5.3 MANUAL VALIDATION"); this repo writes snake_case slugs
  ("phase_5_validation"), so its regex silently fails and it prints
  "Sprint 17" with NO PHASE. A footer that quietly drops a field is the same
  defect class as the stale timestamp the script exists to prevent. F78 also
  removed PowerShell from this repository because CI runs ubuntu-latest.

(Added 2026-09-20 after a hand-assembled footer reported a time an hour stale,
copied forward from an earlier message. The sprint number and phase in that
same line were correct, because they came from a file that was actually read.
The one field filled from memory was the one that was wrong.)

## Standing rules (see docs/SPRINT_PROCESS.md for the full set)

- All PR merges are the team lead's action, at every level. Claude never merges.
- Metered Dirac-3 runs ALWAYS stop for explicit per-block approval with call count and expected seconds stated (Criterion H).
- Team-lead `0*` working files at repo root: commit with a neutral message, never read.
- `--no-verify` is banned; the pre-commit confidentiality hook stays active.
- Every reported number originates in `results.json` with an evidence tag.
- **US English, always.** The team lead writes and expects US English, even though
  HSBC is based in England. Prefer `-ize` over `-ise`, `-or` over `-our`, `-er`
  over `-re`, `-se` over `-ce` in nouns like `license` and `defense`, and single
  `-l-` before a suffix as in `labeled` and `modeling`. The full list lives in
  `experiments/src/test_us_english.py`, which enforces it, and
  `scripts/us_english_fix.py` applies the conversion. (This bullet deliberately
  spells out no counter-example: the guard scans every tracked markdown file,
  including this one, so a document cannot carry the spellings it bans.) The
  submitted documents (`docs/paper/`, `docs/submission/`) and the FROZEN
  `experiments/PREREGISTRATION.md` are EXEMPT and must never be swept: they are
  documents of record for a filing made 2026-09-12. (Team lead, 2026-09-16.)
- **This repository's sessions NEVER write to another repository.** Work in
  `hsbc-quantum-fraud-2026` does not create, edit, commit or push files in
  `spamfilter-multi` or `EvidenceBasedDB`. Reading them on request is fine.
  (Team lead, 2026-09-15.)

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

- **Don't write into another repository from this one.** `spamfilter-multi` and
  `EvidenceBasedDB` are read-only from here, and only when asked. If work in this
  repository implies a change over there, say so and hand it to a session running
  in that repository; do not make the edit yourself, however small or obviously
  correct it looks. (Team lead, 2026-09-15, after a session working this
  repository's PR review also edited EvidenceBasedDB's guard, ADR, CLAUDE.md and
  test file, then committed and pushed them. Each change was defensible on its
  own and the boundary was still wrong: changes arrived in that repository
  without its own review, tests or sprint record.)

- **Don't touch more than one file or surface on a request without echoing the
  requirement back first.** One sentence: "I understand you want X to happen on
  Y, with Z behavior. Correct?" Wait, then proceed without re-asking for the
  same task. Skip it for trivial one-line fixes and doc-only edits with no scope
  ambiguity.

- **Don't use grid or ASCII tables for terminal task summaries and validation
  checklists.** Use bullet lists. Markdown tables inside committed docs are fine;
  this is about terminal readability only.

- **Don't end a turn announcing work you have not started.** "Continuing with
  Task C" as a closing sentence, followed by no Task C, is worse than saying
  nothing: it reports progress that did not happen. The tell is the future tense
  in the last line of a turn. Either do the thing in that turn, or say plainly
  what is not done and why. (Sprint 15: I wrote exactly that and stopped, and
  the team lead had to point out there was no activity. Distinct from the entry
  below, which covers reporting a finished batch as a stopping point; this one
  covers announcing the NEXT action and not taking it.)

- **Don't report a mid-sprint batch of completed tasks as though it were a
  stopping point.** Before ending any turn: is every approved task DONE, or does
  a specifically named criterion in `docs/SPRINT_STOPPING_CRITERIA.md` apply to
  EACH remaining one? If not, continue with the next task.

- **Don't invent "context window running low" as a stopping reason.** The only
  valid stopping reasons are the named criteria in
  `docs/SPRINT_STOPPING_CRITERIA.md`. If genuinely uncertain whether an upcoming
  task fits, do the task; a failure for that reason is itself the signal, not a
  guess made in advance.

- **Don't act on a recalled memory without checking it against current repo state
  first.** Compare its date and its claims against git log, sprint status and the
  docs it names before trusting its "next steps". A memory that was true when
  written can be stale when recalled. (The Dirac-3 queue-timing memory here is
  dated and describes hardware behavior that must be re-checked against the
  current allocation and ledger before it drives a run.)

- **Don't re-render, re-run or regenerate a SUBMITTED artifact to prove a tool
  works. A submitted artifact is evidence, not a test fixture.** Render to a
  scratch path and compare; that costs one extra argument. (Sprint 16 IMP-1: to
  prove the converted renderer reproduced the three filed PDFs, I re-rendered
  them IN PLACE. It did reproduce them -- identical text, page counts and sizes
  -- but a PDF carries a per-build `/ID` trailer, so the bytes changed and the
  files were no longer the ones submitted on 2026-09-12. Recoverable only
  because a backup existed and the hashes were recorded in two documents.
  `test_published_artifacts.py` now fails on any rebuild of a tracked PDF.)

- **Don't move an ignored file without writing its rule at the DESTINATION
  first.** A file's protection usually comes from where it sits, so relocating
  it silently revokes that protection. Run `git check-ignore` on the
  destination path BEFORE the move; if it returns nothing, write the rule
  first. (Sprint 16 IMP-2: moving the QCi correspondence from
  `docs/paper/out/qci_package/` to `docs/qci_package/` would have published a
  private commercial negotiation, because the parent rule was doing all the
  work and nothing under `docs/` replaced it.)
  - **And remember `git mv` keeps a file TRACKED.** An ignore rule does nothing
    for a file already in the index; `git rm --cached` is what untracks it. The
    same move hit this first: `git mv` relocated the letter and left it staged
    for commit.

- **Don't trust an injection that reports success without asserting the
  mutation landed.** Break the thing, CHECK THE BYTES, then run the guard.
  (Sprint 16 IMP-4: two injections printed "77 passed" while injecting nothing
  -- the replace target never matched -- and a green suite reads exactly like a
  successful injection test. Three of that sprint's four errors were defects in
  the VERIFICATION rather than in the thing verified, and each looked
  identical to a real defect.)

- **Don't tell the team lead a Phase 3 artifact is "your call". The DRAFT PR
  and the task issues are Claude's job; only the MERGE is his.**
  `SPRINT_CHECKLIST.md` Phase 3 requires a draft PR (which stays draft until
  7.7), one issue per task before the first task file is touched, and the
  approval recorded. (Sprint 17 ran nine tasks, Manual Validation and a full
  retrospective with `pr: null`, `github_issues: []` and
  `plan_approved: false`, and I said "no PR opened; that's your call" across
  several turns. That moved my own omission onto him. Found only because he
  asked whether the PR was part of the checklist. The close-out hook missed it
  because it tested `plan_approved is True and pr is None` -- reading one stale
  field to decide whether to distrust another.)

- **Don't ship a guard with an override flag in the commit that creates it.**
  If an escape hatch is genuinely needed it arrives LATER, in its own commit,
  with its own justification. (Sprint 17: `render_all.py` rebuilt the three
  SUBMITTED PDFs on any invocation. The fix added
  `--allow-overwrite-submitted`, and the very NEXT command passed it -- not to
  rebuild a submission, but because the flag was the quickest way to get an
  unrelated test to run. The filed bytes were destroyed a second time. An
  escape hatch easier to reach than the correct path is not a guard. The flag
  is gone and `test_render_all.py` asserts it stays gone.)

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
