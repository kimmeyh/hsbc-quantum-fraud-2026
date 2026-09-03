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

## Config-provenance check (mandatory when porting configs; Sprint 3 retro improvement 2)

A frozen or tuned configuration carried from one dataset to another is a HYPOTHESIS, not a setting. Planning any item that ports a config records where the config came from (dataset, class balance, scale) and sanity-checks it against the target's characteristics -- imbalance first. A config whose provenance data differs materially gets a cheap proxy/smoke evaluation before full runs.

## Capability pre-flight (mandatory for tool-dependent items)

Any item that depends on an external capability (a Dirac-3/eqc-models feature, a Braket simulator behavior, a Kaggle endpoint, a library API) gets a ~5-minute spike proving the single primitive it depends on BEFORE the item is estimated or built. If the spike fails, the item is re-scoped first. Also applies to environment preconditions in validation steps: confirm the environment actually works now, do not assume.

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

## Risk assessment per sprint plan

Each plan lists its top risks with mitigation: for this project always consider hardware budget (Criterion H), leakage, deadline (submission-ready Sep 8), grant timing, and context/session continuity.
