# Backlog Refinement Process

Adapted 2026-08-30 from spamfilter-multi's BACKLOG_REFINEMENT.md. The presentation format below is AUTHORITATIVE: read this section in the same turn immediately before producing any candidate presentation; mirror it exactly; ad-hoc tiers, grid tables, or unregistered IDs are process violations.

## When refinement runs

Refinement is MANDATORY and runs TWICE per cycle as part of Phase 8:

- **Pass 1 -- Completeness Sweep (Phase 8.2)**: immediately after the sprint PR merges to develop, in parallel with the team lead's main merge. Purpose: confirm every close-out step actually happened (issues closed, docs triad present, master plan rolled, shipped items pruned). Corrections only; NEVER selects scope.
- **Pass 2 -- Scope Selection (Phase 8.4)**: after the delivery-cycle artifacts are current. Presents the slate; the team lead selects; feeds Phase 3. The ONLY pass that selects scope.

A pass can be SHORT when little needs correcting or selecting; short is not skipped.

## Session structure (timeboxed, 30-60 minutes total)

Prepare (read master plan + repo CHECKLIST, gather velocity actuals) -> Review (stale/obsolete items) -> Prioritize (value x effort x risk; team lead makes the final call) -> Estimate (minutes, calibrated from recorded actuals, never remembered totals; unknowns tagged `[no-history]` and timeboxed) -> Add new items -> Cleanup -> Commit (`docs: Backlog refinement - <date> - <summary>`).

## Item identification

Every item carries a real registered ID: **F#** for features/process/tech-debt items (next available number from ALL_SPRINTS_MASTER_PLAN.md), or **Issue #N** for GitHub issues without an F#. Never invent unregistered slugs.

**F#-only rule (team lead, Sprint 2 retro, 2026-08-30)**: in every refinement presentation and candidate slate, items are referenced by their backlog identifier (F#) and NOTHING else. GitHub issue numbers, task letters, and card references never appear in a candidate presentation; they belong on sprint cards and PR bodies only.

## Backlog Presentation Format (AUTHORITATIVE)

**Summary Index first** -- every item's header line only, in presentation order, HOLD items one line each in the same full shape (never a bare ID list):

```markdown
## Candidates at a glance

- **F3. IEEE-CIS reduced Deotte recipe (~4h) Priority 10**
- **F5. QFE phase arms with JOINT twins (~3h) Priority 12**
- ...
- F9. Phase 2 Braket hardware validation (~unknown) Priority HOLD
```

**Item format** (verbatim):
```markdown
**<ID>. <Title> (~<effort>) Priority <N>**
- Phase: <phase/stage name>
- Platform: <ULB | IEEE-CIS | SPECTRA | Dirac-3 | Braket | docs | N/A>
- <description bullet>
- <description bullet>
- Depends on: <dependencies if any>
```

**Rules**:
- Priorities are NUMERIC, increments of 10; items that should sprint together use increments of 2. Never ad-hoc groupings.
- Group items under `### <Phase Name>` section headers matching the master timeline (Experiments, Paper, Finalize, QCi/External, Phase 2).
- HOLD items use `Priority HOLD` in a `### HOLD Items (<reason>)` section at the bottom, with full detail bullets there.
- Bugs and tech debt interleave by priority within their phase group; no separate sections.
- Completed items are REMOVED (history lives in sprint docs and git).
- No grid tables for the presentation.

## Definition of Ready

Clear scope, quantifiable acceptance criteria, minute-based estimate, no unresolved blockers, clear priority. Not-ready states: Needs Clarification / Needs Research / Blocked / Too Large (split it).

## Anti-patterns

Analysis paralysis (timebox); premature detail on far-future items (title + priority only); stale backlog (review anything 3+ sprints old); missing value statements (every item answers "this enables / this prevents"); uncalibrated estimates; scope creep during refinement (defer new ideas to the add step, sized, not designed).
