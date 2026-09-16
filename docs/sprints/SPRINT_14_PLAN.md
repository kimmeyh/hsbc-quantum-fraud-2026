# Sprint 14 Plan: Make the Record Durable

**Dates**: 2026-09-12 onward. **No deadline.**
**Branch**: `feature/20260912_Sprint_14`
**Scope** (DEFINED, team lead 2026-09-12): **F68, F69, F70, F71, F39, F72, F66,
F48, F65, F67.** F68 first.

## Objective

The submission is filed and judged-as-is. This sprint makes the repository
durable for two audiences that arrive next: a judge who may open it during the
review window, and us in mid-November with two months of forgotten context.

## The calendar changed, and it changes how this sprint is estimated

Finalist notification is **mid-November 2026** (Guidelines s2), and Phase 2
begins at the same milestone. **Nothing in this sprint is time-bound.** That is
recorded because thirteen sprints of estimating against a deadline built a habit:
there is no reason to compress, defer on time intuition, or accept a partial fix.
Criterion 9 already says wall-clock hours are not a stop signal; here there is
not even a distant date behind them.

## Audience-first statement (mandatory)

**F68/F69's reader is a stranger with no context** -- a judge during review, or a
reproducer. They must be able to find what was submitted, retrieve it exactly,
and run something. **F70/F71's reader is us in mid-November.** **F39/F72's reader
is the team lead deciding whether to fund a build.**

## Capability pre-flight (run 2026-09-12 BEFORE estimating)

Code inventoried, not just documents. **Five findings, one of them serious.**

| Check | Expected | Measured | Consequence |
|---|---|---|---|
| Class 4 hook fires | working (Sprint 13 retro said so) | **NEVER RUN** -- see below | F68 goes first and grows |
| Amendment hook fires | working | **NEVER RUN**, same cause | same |
| CHANGELOG currency | current | **stops 2026-09-04**, 8 days missing | F70 backfills Sprints 7-13 |
| CHECKLIST currency | current | titled "Submission-Ready by Sep 8", 18 stale unchecked boxes | F71 restructures |
| README currency | current | points at a `paper/` path that does not exist; "Immediate to-do" asks for PDFs staged weeks ago | F69 rebuilds |

### The finding that reorders the sprint

**Both Edit-matcher hooks have never run.** `.claude/settings.json` registers
them as `...\\hooks\block-...`. The single backslash before `b` is a JSON
backspace escape, so the parsed path is `hooks\x08lock-...`, which does not
exist, and Claude Code skips a missing hook silently.

Broken since `7a57065` -- the commit that created them. Verified by parsing both
the working tree and the committed blob.

**The Sprint 13 retrospective recorded "the Class 4 hook worked exactly as
designed". That was false**, and it was mine. Every submission-document edit in
Sprint 13 was unguarded. The process held because the team lead approved each
change in conversation, not because anything enforced it. The correction belongs
in this plan rather than only in a commit message, because it changes what the
repository can claim about its own controls.

It is also **F48's exact defect class** -- a silent escape corruption -- sitting
in the file that registers the guard against it. F48 is in scope this sprint,
which is the right order.

### Runtime

No task in this sprint runs over a dataset. The dominant cost is reading and
writing, and the one measurable risk is F69's reproduce section, which must be
executed rather than drafted: **a README that does not work makes Appendix C's
regeneration claim false for the first reader who tries it.**

## Tasks

| # | Card | Task | Est | Owner |
|---|---|---|---|---|
| A | **F68** | Fix both hook registrations; injection-prove them; add a test that every registered hook path resolves and carries no control characters; extend to history rewrites and tag moves; README as-submitted section | 120m | Opus |
| B | **F69** | README rebuilt: key documents, HOW TO REPRODUCE (clone, venv, one quick test, each major test with caveats), as-submitted retrieval. **Reproduce section executed, not drafted** | 120m | Opus |
| C | **F70** | CHANGELOG backfilled Sep 5-12 from git, sprint summaries, amendment log, PRs; unreconstructable days said so explicitly; workflow Phase 8 names the step before refinement | 90m | Opus |
| D | **F71** | CHECKLIST into three ordered sections: PRE-PHASE 2 (live), PHASE 2 (from the proposal's six-experiment program), CHALLENGE SUBMISSION (completed, corrected to actuals) | 90m | Opus |
| E | **F48** | Escape hook extended to shell metacharacters | 45m | Opus |
| F | **F66** | Copilot reviewer-request procedure into the workflow | 15m | Opus |
| G | **F65** | Per-fit artifact write in the hardware runner | 45m | Opus |
| H | **F67** | Pool-mechanism guard; needs the pools-vs-fixture decision | 60m | Opus + **team lead** |
| I | **F39** | Fact-database investigation and ADR. Design only | 240m | Opus + **team lead** |
| J | **F72** | Reference-library proposal. Design only, gated on I's storage decision | 180m | Opus + **team lead** |

### F69's reproduce section: how it gets executed (team lead asked, 2026-09-12)

**Against a FRESH CLONE in a scratch directory, never this working tree.**

This tree cannot test the README. It holds a built `.venv`, staged datasets that
are not redistributable, and cached pool `.npz` files. Every one of those would
let a broken instruction appear to work, which is the same
passes-for-the-wrong-reason failure the injection standard exists to catch.

The procedure, run in this order:

1. `git clone` the PUBLIC URL into the scratch directory, anonymously where
   possible, so the clone sees exactly what a stranger sees
2. Create a fresh virtual environment by the README's own words
3. Install from the README's own command, against the committed lock file
4. Run the quick test the README names, and record what it actually prints
5. Run each major test group the README names, and record which ones PASS,
   which SKIP for want of data, and which FAIL
6. Write the caveats from that record, not from memory

**The expected and correct outcome is a partial pass.** The ULB, IEEE-CIS and
SPECTRA datasets are not redistributed -- their licenses do not permit it -- so
data-dependent tests must skip on a fresh clone. The README's job is to say so
plainly and tell the reader how to stage the data, not to imply a clean full run
that nobody can reproduce.

If a step fails for any reason other than absent data, that is a defect in the
repository and it is fixed in this sprint rather than documented around.

### F39 and F72 start OFF-repository (team lead, 2026-09-12)

Both begin outside this repository. Some or all of either may be brought in
later, and that is a separate decision made on the evidence rather than now.
Consequence for this sprint: neither card adds runtime dependencies here, and
F39's ADR records the boundary as provisional rather than settled.

**Sequence**: A first, by direction and by merit -- it repairs a control that is
currently absent. Then B (depends on A's as-submitted section), then C, D in
either order. E, F, G are independent and can interleave. H needs a decision. I
then J, because J is gated on I's storage choice.

**Total ~17.5 hours**, plus the standing **30% findings allowance** (Sprint 13
improvement 2) = **~23 hours**. This is a multi-day sprint and there is no
deadline pressing it.

## Premise falsifier (mandatory)

**Premise**: the repository's controls, records and entry points are accurate.

**Already disproved, three times, before the sprint began**: two hooks that never
ran, a CHANGELOG eight days stale, a README describing a layout that does not
exist. The premise is known false; the open question is how much else is.

**The check cannot merely confirm**: F68's test asserts registered paths resolve
on disk, which is independent of whether anyone believes they do. F69's reproduce
section is executed. Both can fail.

## Risks

| Risk | Mitigation |
|---|---|
| **Other silent hook or config breakage** | F68's test covers every registered hook, not the two known-broken. Treat the class as suspect, not the instances |
| **F39 and F72 duplicate a storage decision** | J is explicitly gated on I. One decision, two consumers |
| **F39 sprawls from design into build** | The card says ADR only. An implementation card comes after approval, not inside this one |
| **README reproduce steps drift from reality** | Executed during Task B on this machine, and its caveats state what needs data that is not redistributed |
| **Editing the submitted documents** | F68 makes this harder rather than relying on memory. The documents are a record now |
| Deadline | None. Mid-November is the next date and nothing here bears on it |

## Definition of Done

- Both Edit-matcher hooks demonstrably fire, verified by injection
- A test fails if any registered hook path is unresolvable or holds a control character
- README lets a stranger clone, set up and run a test, with steps that were executed
- Retrieval of the as-submitted state is documented and works anonymously
- CHANGELOG has an entry for every day with commits from 2026-09-05, or an explicit note that a day could not be reconstructed
- CHANGELOG maintenance named in the Phase 8 close-out, before refinement
- CHECKLIST carries three ordered sections, the first actionable today
- F48, F66, F65 complete; F67 complete or its decision recorded
- F39 ends in an ADR covering assertions, acronyms and terms, naming the storage tool and repository boundary
- F72 ends in a written proposal gated on F39's storage decision
- Suite green

## Out of scope

F64 (Phase 2 experiment 1), F2b B4/B5, F25, F30, F17, F20, F29, F5, F6, F13.
Not planned in by inference.
