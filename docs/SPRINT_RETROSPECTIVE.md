# Sprint Retrospective Guide

Adapted 2026-08-30 from spamfilter-multi's SPRINT_RETROSPECTIVE.md. The 14-category x 4-role structure and the 7-step protocol are preserved verbatim in shape; examples are adapted to this project.

## Rules

- Retrospectives are MANDATORY for every sprint, conducted after Phase 6 (PR updated) and BEFORE the PR is marked ready.
- **A retrospective is NEVER complete unless ALL 14 categories are addressed by ALL 4 roles.** The team lead wears Product Owner, Scrum Master, and Lead Developer; Claude provides the Development Team perspective. A role with nothing to say writes `No issues -- expectations met.` explicitly; silence is not acceptable.
- Record the team lead's words VERBATIM; never paraphrase or substitute Claude's draft for them.

## The 7-Step Protocol (run in order; do not collapse, reorder, or skip)

1. **Send the prompt**: ask the team lead for PO/SM/LD feedback across all 14 categories (combined per-category lines acceptable), noting that Claude is drafting its own role's feedback in parallel.
2. **Draft in parallel**: Claude writes its Development Team feedback for all 14 categories into `docs/sprints/drafts/SPRINT_N_RETROSPECTIVE_claude_draft.md` while waiting.
3. **Record verbatim**: paste the template into `docs/sprints/SPRINT_N_RETROSPECTIVE.md`; the team lead's exact words per category; Claude's lines from the draft. Exit gate: 14 categories, 4 roles, no placeholders.
4. **Combine and display** in chat, both feedback sets together per category.
5. **Propose improvements** from the combined feedback; per proposal: Title / Source / Type / Effort / Recommendation. Display; do NOT auto-apply.
6. **Team lead disposes each**: apply now, backlog, or skip (blanket disposition acceptable). Record in an "Improvement Decisions" section.
7. **Apply**: now-items as commits on the sprint branch; backlog-items to ALL_SPRINTS_MASTER_PLAN.md; skips noted. Then the mandatory completion updates (master plan Last Completed Sprint, summary doc scheduling, CHECKLIST reconciliation). THEN `gh pr ready`.

## The 14 Mandatory Categories

1. **Effective while as Efficient as Reasonably Possible** -- right outcome, least reasonable effort, workflow followed, rework counted.
2. **Testing Approach** -- did automated tests catch problems before validation; coverage adequate for the scope (for this project: known-answer statistical tests, leakage positive controls, loader validations).
3. **Effort Accuracy** -- estimates vs actuals per task; variance patterns.
4. **Planning Quality** -- task clarity, acceptance-criteria sufficiency, dependencies, scope fit.
5. **Model Assignments** -- were subagent/model choices right (reviews, research agents, main-loop work); escalations needed.
6. **Communication** -- narration, timely blocker reporting, commit/PR clarity.
7. **Requirements Clarity** -- ambiguity encountered; hidden requirements surfaced mid-sprint.
8. **Documentation** -- docs updated with the work; prereg amendments recorded properly; reference docs current.
9. **Process Issues** -- errors, blockers, tooling friction, anything that belongs in a troubleshooting note or hook.
10. **Risk Management** -- risks identified vs materialized (hardware budget, leakage, deadline, grant timing); mitigation effectiveness.
11. **Next Sprint Readiness** -- blockers for next sprint; master plan current.
12. **Architecture Maintenance** -- for this project: protocol integrity (does anything in code diverge from the frozen preregistration; are amendments logged), pipeline structure, results.json schema adherence.
13. **Minor Function Updates for the Next Sprint Plan** -- sub-hour items to fold inline into Sprint N+1. Format: `[ROLE] <one-line> -- target: Sprint N+1 plan, est: <Xm>`.
14. **Function Updates for the Future Backlog** -- larger items for ALL_SPRINTS_MASTER_PLAN.md "Next Sprint Candidates" with a new F#. Format: `[ROLE] <title> -- estimated: <X>, priority: <N>, depends on: <list>`.

## Mandatory Feedback Template (copy verbatim into `docs/sprints/SPRINT_N_RETROSPECTIVE.md`)

```markdown
## Sprint N Retrospective Feedback

### 1. Effective while as Efficient as Reasonably Possible

- **Product Owner**: [feedback]
- **Scrum Master**: [feedback]
- **Lead Developer**: [feedback]
- **Claude Code Development Team**: [feedback]

### 2. Testing Approach
[same four-role block]

### 3. Effort Accuracy
[same four-role block]

### 4. Planning Quality
[same four-role block]

### 5. Model Assignments
[same four-role block]

### 6. Communication
[same four-role block]

### 7. Requirements Clarity
[same four-role block]

### 8. Documentation
[same four-role block]

### 9. Process Issues
[same four-role block]

### 10. Risk Management
[same four-role block]

### 11. Next Sprint Readiness
[same four-role block]

### 12. Architecture Maintenance
[same four-role block]

### 13. Minor Function Updates for the Next Sprint Plan
[same four-role block]

### 14. Function Updates for the Future Backlog
[same four-role block]

## Improvement Decisions

| # | Title | Source | Type | Effort | Decision (now/backlog/skip) |
|---|---|---|---|---|---|
```

## Transition note

Sprint 1 (2026-08-30) closed under the earlier lightweight three-question retro before this guide was adopted; its retrospective doc records that explicitly. The full protocol applies from Sprint 2 onward.
