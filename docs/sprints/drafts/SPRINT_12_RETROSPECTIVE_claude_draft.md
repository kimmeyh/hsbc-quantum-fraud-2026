# Sprint 12 Retrospective — Claude Code Development Team draft

Drafted 2026-09-12. Development Team perspective only; the team lead's PO/SM/LD
feedback is recorded verbatim in the combined document.

### 1. Effective while as Efficient as Reasonably Possible

The sprint delivered its planned scope (B2 and B3 on hardware) and then absorbed
a second body of work it did not plan: responding to three external reviews that
found defects in what it had just published. That is the right outcome and it
was not efficient, because a large share of the effort was rework. B3 was run,
published, withdrawn and re-run inside one day at a cost of 61 wasted metered
seconds; A22 was rewritten twice; the convexity claim was written, published and
retracted within hours. The sprint spent roughly as much effort correcting
Sprint 12's own output as producing it.

The efficiency question worth asking is not whether the rework was avoidable in
hindsight — the defects were real and finding them was the correct outcome — but
whether it was avoidable at the time. Two of the three cases say yes: B3's
comparability defect would have been caught by comparing the two runners before
publishing, and the convexity error by checking the code before asserting a
claim about it. Both were checks we could have run and did not.

### 2. Testing Approach

This is the category the sprint has the most to say about, and the honest
summary is that the suite performed exactly as designed and that was not enough.

The suite grew 277 → 315 tests and stayed green through every defect that
mattered. It caught real regressions: the F44 figure guard flagged eight
unresolvable B3 figures and later the entire A.2 operating-point table; the F35
artifact guard forced the B3 and B2 artifact tests into existence; the strict
F38 xfail markers fired the instant the documents came back under limit, which
is precisely what they were written to do.

It missed every defect that changed a claim's meaning. The under-converged
solver is the clearest case: our recomputation reproduced the published +0.0022
exactly, because the figure and the error came from the same solver. Every
internal check agreed with itself. No test we could have written from inside
that assumption would have caught it — it took an external reviewer solving the
same ten problems independently.

Three tests written this sprint were verified by INJECTION rather than trusted:
the B3 pool-row guard, the F57 prose guard, and the dispersion grouping guard.
The F57 one passed vacuously on first write (the marker phrase was split across
a line break) and would have shipped as false assurance. Injection testing
should be the default for any guard whose job is to fail.

### 3. Effort Accuracy

Estimates were accurate where the work was understood and absent where it was
not. The cards written from the review analysis (F49–F63) estimated ~6 hours and
ran close to that. The unplanned work had no estimates at all because it was not
planned.

Two measured variances worth recording. B2's per-fit cost was estimated in the
frozen grid at ~40 s and measured at 82 s — a 2x underestimate that would have
mattered if the block had been budgeted tightly. And F38 was estimated at 45
minutes when first carded, then re-measured at 689pt, 2,028pt, 3,197pt and
~3,840pt as successive corrections added text; the eventual fix took the team
lead trimming the sources directly. An estimate that grows 5x across one sprint
is not an estimate, and the card said so each time it was re-measured.

### 4. Planning Quality

The sprint plan was clear and its acceptance criteria were sufficient for the
work it named. It had no mechanism for the work it did not name, which turned
out to be more than half the sprint.

The plan also assumed a sprint boundary that the work did not respect. Sprint
12's branch, PR #73, was merged mid-sprint while work continued on a branch cut
from it, and `sprint_status.json` still reads `phase_4_execution` with `pr: null`
against a sprint that has since had two PRs.

### 5. Model Assignments

Delegation worked where the task was gathering and failed nowhere, but the
boundary mattered. Four review agents (statistical, code-quality, compliance,
reproducibility) produced findings of real value, including two neither external
reviewer found: `hw_dispersion.json` stale at 27 of 48 fits, and the
`mechanism_controls.py` silent-degradation path. The F53 and F54 gathering
agents were given explicit "gather and verify, do not decide" instructions after
the earlier lesson, and that was the right constraint — F53 found the AutoXGB
dataset misattribution, which was load-bearing and which no external review
caught.

The one failure mode was mine, not the agents': I acted on an internal review
finding without verifying it, and published a false convexity claim within
hours. The agents reported accurately; the main loop did not check.

### 6. Communication

Blockers were reported promptly and with their diagnosis: the WSL/Python
Criterion 7 stop, the B2 process death, the Copilot reviewer-attachment failure.
Commit messages carried the reasoning rather than the change, which is what made
the A22/A23 withdrawal legible afterwards.

Two communication defects. I reported a possible B3 stall that was not one, on
incomplete evidence, and had to retract it in the next status. And I twice
over-read partial ladder data mid-run — drawing conclusions from fold 0 before
folds 1 and 2 existed — and stated them as findings before correcting myself.
Both are the same error: narrating an interpretation before the data supports
it.

### 7. Requirements Clarity

The requirement that mattered most was never stated and had to be discovered:
that the submission guidelines mandate a "Feasibility and Resource Requirements"
section and a "Validation Plan", together 35% of the Phase 1 rubric, and the
proposal had neither heading. That was found by an external reviewer reading the
rules PDF against our document. We had a requirements matrix and it did not
contain the requirement.

Otherwise ambiguity was low and the team lead's direction was decisive at the
points where it mattered (the 2,000 s ceiling, the deferral of F38, the
instruction to analyse before amending).

### 8. Documentation

Six amendments were registered (A22 through A31, with revisions), each with
rationale, and three of them record corrections to figures this sprint had
itself published. The amendment log is now the most useful artifact in the
repository for understanding what happened and why.

One documentation gap, and it is smaller than I first reported: Sprints 10 and
11 have their full triads. Only SPRINT_12_SUMMARY.md is missing, and this
retrospective is the second of Sprint 12's three docs. I stated a three-sprint
gap in an earlier draft on the basis of a truncated directory listing -- the
kind of error that reads as diligence and is not.

### 9. Process Issues

The process issue of the sprint is that **amending under time pressure
reproduced the defect class the amendments exist to record**. The convexity
claim was written in response to a review, published within hours, and was
false. The team lead's intervention — stop, analyse both reviews fully, address
findings through planned cards — is what broke the loop, and it should become a
standing rule rather than a one-time correction.

Tooling friction, recorded because each cost real time: the Copilot review
attachment fails silently through `gh pr edit`, REST, and GraphQL with the wrong
bot id, and the correct actor is `copilot-pull-request-reviewer[bot]`
(`BOT_kgDOCnlnWA`), not `Copilot` and not `copilot-swe-agent`; REST
`requested_reviewers` returns only users, so a successful bot request reads as
empty and looks like failure. PR #73 never got a review for this reason and
nobody noticed. Separately, heredocs with apostrophes broke three times, and PDF
file locks blocked four renders.

### 10. Risk Management

The metered-spend risk was managed well: 968 s of a 2,000 s authorization,
every cost balance-measured, intent recorded before outcome, and the guards
tightened mid-sprint when the review found that failed fits recorded zero spend
and were then skipped forever on resume. That hole was real and is closed.

The risk that materialised was not on the register: that published work would be
found wrong by external review after being committed. It happened three times.
The mitigation that worked was the amendment protocol, which made withdrawal
possible without damaging the record.

One risk remains open and is the team lead's: the submission deadline is
2026-09-15 and the branch carrying all of this work is unmerged.

### 11. Next Sprint Readiness

The submission documents are within limits (6/3/1), 315 tests pass, the
repository is public and verified, and every external review finding is fixed or
recorded. Sprint 13 can begin from a clean base.

Three things should carry forward: the sprint-document backlog (Sprints 10–12
missing their three docs), `sprint_status.json` being stale, and the k=17
order-2 decomposition cell — 153 variables, zero metered cost — which is the
first thing Phase 2 should run and which B.3 currently lists as unrun.

### 12. Architecture Maintenance

Protocol integrity held under strain. No gate was rescored, no criterion
changed, and the one deviation that had gone undeclared for eleven sprints (the
G0 "everything halts" rule) is now on the record with its rationale and its
uncomfortable ordering stated.

Two code-level divergences from the documents were found and fixed: B2's null
`config_hash` (11 of 168 rows, which had already silently deleted a gate-report
line), and the dispersion generator grouping on the device parameter rather than
the pool order — the same conflation F60 had just corrected in the prose,
surviving in the code that produces the prose's evidence. The lesson is that
correcting a document does not correct the generator behind it.

### 13. Minor Function Updates for the Next Sprint Plan

- [DEV] Run the k=17 order-2 proxy cell (153 variables) to decompose the B2 confound — target: Sprint 13 plan, est: 45m
- [DEV] Update `sprint_status.json` to reflect the true sprint, branch and PR — target: Sprint 13 plan, est: 10m
- [DEV] Record the Copilot reviewer-request procedure in SPRINT_EXECUTION_WORKFLOW.md — target: Sprint 13 plan, est: 15m

### 14. Function Updates for the Future Backlog

- [DEV] Sprint document backlog: plan, retrospective and summary for Sprints 10, 11, 12 — estimated: 2h, priority: 6, depends on: nothing
- [DEV] Injection-verification standard for guard tests: any test whose purpose is to fail must be proven to fail — estimated: 1h, priority: 7, depends on: nothing

### 15. Assigned Coding Agents Quality

First-pass correctness was high and spec adherence was complete: every agent
stayed inside its "gather and verify, do not edit" boundary, and none required
rework. The four-way review produced two findings neither external review found.
The F53 agent flagged one of its own reviewer's claims as wrong (FG22/5 para
5.12 does say what we claimed), which is the behaviour I want — agents that
adjudicate rather than relay.

The constraint that made this work was instructing them to gather and verify but
not decide. The one time I let a review finding drive an edit without
independent verification, I published a false claim.

### 16. Questions to be discussed before ending the sprint

None. The two open items — merging PR #75 and the Sprint 13 scope — are
decisions rather than questions.
