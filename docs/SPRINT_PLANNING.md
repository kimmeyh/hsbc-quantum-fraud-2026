# Sprint Planning

Adapted 2026-08-30 from spamfilter-multi's SPRINT_PLANNING.md. Governs how sprints are scoped, staffed, estimated, and carded. Execution mechanics live in SPRINT_EXECUTION_WORKFLOW.md.

## Team roles

| Role | Assigned to |
|---|---|
| Customer Representative / Product Owner / Agile Coach / Scrum Master / Chief Architect / Chief Developer / Chief Test Engineer | Harold Kimmey (the team lead) |
| Assistant Scrum Master, Architecture Development Team, Senior Test Engineers, Development Team | Claude Code (whichever model executes the task; parallel subagents allowed) |
| Lead Developer | Claude Code top tier (Fable 5 preferred, Opus otherwise) |
| Senior Developers | Claude Code Sonnet (subagents) |
| Developers | Claude Code Haiku (subagents) |

## Activities requiring the top tier (Fable/Opus) -- MANDATORY

Sprint planning; retrospectives; backlog refinement; architecture/protocol deep dives; ADR authoring; best-practices research; security-sensitive review; adversarial review passes on the paper; any statistical-methodology decision touching the frozen preregistration. Implementation tasks (loaders, scripted runs, doc edits) may be delegated to Sonnet/Haiku subagents. Before starting a top-tier activity, confirm the active model is top tier; escalate if not.

## ADR-first approach

Architectural or protocol-shaping changes get an ADR designed and team-lead-approved BEFORE implementation. For this project, the frozen preregistration is the master ADR for methodology; ADRs in docs/adr/ record engineering decisions around it (pipeline structure, data handling, tooling). Amendments to the frozen protocol are ADR-class decisions with their own dated log.

## Audience-first rule for deliverables (Sprint 4 retro improvement 3)

Before drafting ANY external-facing document (results memo, paper section, sponsor package, submission artifact), state at the top of the task: who reads this, and what must they believe or decide after reading it. That statement shapes structure and emphasis, and it belongs at the START of the task -- a framing correction after the draft exists costs a rewrite. (Sprint 4: the production-bound framing arrived after the results memo was drafted and materially changed it.)

## Config-provenance check (mandatory when porting configs; Sprint 3 retro improvement 2)

A frozen or tuned configuration carried from one dataset to another is a HYPOTHESIS, not a setting. Planning any item that ports a config records where the config came from (dataset, class balance, scale) and sanity-checks it against the target's characteristics -- imbalance first. A config whose provenance data differs materially gets a cheap proxy/smoke evaluation before full runs.

## Capability pre-flight (mandatory for tool-dependent items)

Any item that depends on an external capability (a Dirac-3/eqc-models feature, a Braket simulator behavior, a Kaggle endpoint, a library API) gets a ~5-minute spike proving the single primitive it depends on BEFORE the item is estimated or built. If the spike fails, the item is re-scoped first. Also applies to environment preconditions in validation steps: confirm the environment actually works now, do not assume.

**The pre-flight inventories CODE, not only documents (Sprint 10 improvement 6).** Grep the source tree for whatever the item is about to change, not just the docs that mention it. F40's card listed four documents referencing the path being moved and was verified against exactly those four. It missed `data.py`, which hardcoded the ULB dataset location -- so the repository that Appendix C promises "regenerates every figure" would have worked on no machine but the author's. The card was right about every document and silent about the one line that mattered.

## Defined-scope rule (team lead, 2026-08-30 -- binding)

Sprint scope is DEFINED, never additive: the team lead's selection list IS the complete scope. Items previously proposed, drafted, or carded are NOT in scope unless they appear in the selection. If an unselected item looks critical-path, raise it as a question during refinement; never plan it in by inference. Cards created for unselected items are closed as premature and recreated at the sprint that selects them.

## Planning inputs and outputs (Phase 3)

Inputs: sprint goal (1-2 sentences), refined candidates (BACKLOG_REFINEMENT.md format), velocity actuals. Outputs: SPRINT_N_PLAN.md (objective, tasks, quantifiable acceptance criteria, estimates in minutes, risk, model assignments), previous sprint's SUMMARY doc, one GitHub sprint card per task (template in .github/ISSUE_TEMPLATE/sprint_card.yml), draft PR updated.

## Card standards

- **Definition of Ready** (one line): scope clear, acceptance criteria quantifiable, estimate assigned, no unresolved blockers, priority set, owner named.
- **Task-level Definition of Done** (referenced, not copy-pasted): acceptance criteria met with evidence; tests green; results in results.json with evidence tags where applicable; docs updated in the same commit; committed with the issue number.
- Every card carries: Sprint number, Category, Priority, What/Why, Acceptance Criteria, Model Assignment + Complexity, Owner (team lead or Claude).
- Team-lead-owned cards (portal actions, external sends, approvals) are tracked like any other card; Claude verifies and records completion evidence but never executes them.

## Estimation

Minutes, from recorded actuals of comparable step-types; `[no-history]` + timebox where uncalibrated. Re-estimate after plan-to-branch-state verification findings (workflow 3.2.2.1/3.2.2.2). Record actuals at task completion; recompute at retro Category 3.

### The sprint total is DERIVED from the cards, never asserted in the plan (Sprint 17 improvement 1)

**Order of operations, and the order is the point:**

1. **Each card carries its own estimate**, written on the card during
   refinement, from that card's detailed scope.
2. **Dependencies between cards are stated on the cards**, because a
   dependency changes what can run in parallel and therefore what the sprint
   costs in elapsed time. A card that blocks another is not the same cost as
   one that does not.
3. **The total is COMPUTED from those card estimates and their dependencies,
   and recorded.**
4. **The plan is then written or updated FROM the recorded total.** The plan
   document reports the number; it does not originate it.

**A total typed into the plan document is not an estimate. It is a guess that
looks like an estimate**, and it has been wrong in two consecutive sprints:
Sprint 16's draft said 590 against an actual 585, and Sprint 17's said 605 and
716 against an actual 585 and 696. Both were caught only by summing the table
during the mandatory plan-to-branch-state verification, which is late.

Estimating before the cards are detailed is worse than useless: the number is
stale before it is written, because the detail that would change it does not
exist yet. Estimate the cards first, derive the total, then write the plan.

**When a card's estimate changes mid-sprint**, the recorded total is recomputed
and the plan updated, not left to drift. A plan whose total no longer matches
its own cards is reporting a number nothing owns.

### Runtime is estimated SEPARATELY from implementation (Sprint 8 improvement 1)

Any task that produces results by running over a dataset carries TWO numbers in
the plan's task table: **Est** (time to write the code) and **Runtime** (expected
wall-clock of the run itself, computed from the ACTUAL row count, not assumed
from a smaller run).

Sprint 8 Task C was estimated at 120 minutes, which covered writing the runner.
The run then consumed 84 minutes without finishing a single fold and was killed
by its own timeout. The cause was a KNN H-matrix build that is
O(n_train x n_query) at 495,902 rows. The task had been audited for protocol
compliance and never once sized for runtime: those are different questions and
only one was asked.

Rules:

- State the dominant cost and its complexity in the task row, e.g. "KNN H-build
  O(n_train x n_query), 495,902 x 56,746".
- **NAME the dominant term and show its measurement (Sprint 9 improvement 2).**
  This rule was FOLLOWED in Sprint 9 and the estimate still missed by 47x: 10
  minutes planned against 7.9 hours actual, per run, three times. The twins and
  the GBDTs were both sized from real fits, and the GAM twin was piloted
  specifically because it looked like the risk. What was never sized was the
  CVQBoost pool build -- 300 seconds of the 335 per cell, the single dominant
  term, simply not on the list of things being thought about.

  So "I estimated the runtime" is not the bar. The bar is naming which
  component dominates and showing the number: "pool build 300s of 335s per
  cell, measured on the real split". If you cannot say which component
  dominates, the sizing is not finished -- enumerate every step the task
  executes, not the ones that come to mind.
- If the runtime cannot be estimated, say `[unbounded]` and add a PILOT on a
  subsample as a preceding task. Never let an unsized run start.
- Any run expected to exceed 30 minutes must emit heartbeat progress to a file
  before it is launched, not after it worries someone.

### A card justified by a measurement must name what would disprove it (Sprint 8 improvement 2)

If a card's rationale rests on a measurement, the card states a **Premise
falsifier**: the specific observation that would show the premise is wrong. If
no such observation can be named, the premise is unverified and the card does
not start.

F36 is the worked counter-example, and it cost a full card. Its premise was that
the appendix wasted page space to table break-waste. Its dry run removed all
five tables and observed the document shrink to 3 pages, which was read as
confirmation. It could not have been anything else: removing tables removes
their content AND their space, so the document was always going to shrink. The
check could only confirm. Direct measurement later showed every page already
filled its text block, with zero free space anywhere.

A check that cannot fail is not evidence. Write the falsifier first, and if the
dry run cannot produce the failing observation, redesign the dry run.

### A verification sprint GENERATES work; budget for it (Sprint 13 improvement 2)

A sprint whose tasks are "check that X is true" produces a second body of work
the moment a check fails, and that work is invisible at planning time because it
is contingent on findings that do not exist yet.

Sprint 13 measured it. Tasks A to D were estimated at about 200 minutes and ran
close to that. The six approved document corrections, the A32 amendment, one
backout and two re-renders added roughly 60 minutes that no card carried. None
of it was scope creep: every item came from a check doing exactly its job.

Rule: any sprint whose scope is dominated by verification carries a stated
**30% findings allowance** on top of its task estimates, named in the plan rather
than absorbed silently. If the checks all pass, the allowance is returned and the
sprint finishes early, which is the good outcome and should be recorded as such.

### A WRITING sprint carries a sourcing allowance (Sprint 15 improvement 3)

The rule above covers sprints dominated by verification. Sprint 15 was dominated
by WRITING and generated the same shape of uncarded work, for a different
reason: prose makes claims, and every claim has to be traced to a source or
removed.

Sprint 15 measured it. Five claims were caught and corrected during writing --
two dataset details and a nationality written from background knowledge rather
than from the repository, an acronym expansion asserted as fact, and a
publication year taken from one vendor source while another disagreed. None had
a card. Each cost a research step, a rewrite, or both.

Rule: any sprint whose scope is dominated by producing prose that makes factual
claims carries a stated **30% sourcing allowance** on the writing estimate, named
in the plan rather than absorbed silently. Same discipline as the findings
allowance: if every claim sources cleanly, the allowance is returned and the
sprint finishes early.

## Risk assessment per sprint plan

Each plan lists its top risks with mitigation: for this project always consider hardware budget (Criterion H), leakage, deadline (submission-ready Sep 8), grant timing, and context/session continuity.
