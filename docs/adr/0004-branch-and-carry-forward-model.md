# ADR-0004: Branch and carry-forward model for sprint work

## Status

Accepted

## Date

2026-08-30

## Context

The project runs the sprint process adapted from spamfilter-multi, across many AI sessions, with a solo team lead holding release authority. Process decisions evaporate fastest in exactly this setup; the source repo's experience (its ADR-0015) shows that writing the branch policy down is what keeps an AI-assisted workflow safe.

## Decision

- Three tiers: `main` (stable; team-lead-only merges from develop), `develop` (integration, repository default; all PRs target it), `feature/YYYYMMDD_Sprint_N` (one per sprint).
- One DRAFT PR per sprint, created when the plan is drafted, kept draft through the retrospective, marked ready at exactly one point (workflow Phase 7.7). Draft status suppresses per-commit Copilot review noise.
- Carry-forward: on PR-merge notification, the next sprint branch is created FROM the just-merged branch's head, never from develop; post-merge work commits there. Stash is banned; recovery is cherry-pick.
- Sprint branches are never deleted.
- The frozen `experiments/src/` files change only with a preregistration amendment line, on any branch (ADR-0001).
- Scope is DEFINED, never additive: the team lead's selection list is the complete sprint scope (SPRINT_PLANNING.md defined-scope rule, 2026-08-30).
- Team-lead-owned tasks blocked at sprint close carry per stopping Criterion 2 without holding the sprint.

## Alternatives Considered

### Trunk-based development (commit to main)
- **Pros**: Less ceremony for a solo project.
- **Cons**: No integration buffer, no PR surface for Copilot review, no draft/ready lifecycle, diverges from the team lead's established practice.
- **Why Rejected**: The team lead's proven model transfers wholesale and its guard rails have already caught real mistakes here.

## Consequences

### Positive
- Every sprint has an auditable PR trail; nothing strands on merged branches.
### Negative
- Solo-project ceremony overhead, accepted deliberately for auditability.
### Neutral
- The public reproducibility repo is published separately at Stage 7, so branch history here can stay private.

## Preregistration touchpoints

None directly; section 12's freeze procedure interacts via ADR-0001. The preregistration governs methodology; this ADR records engineering decisions only.

## References

`docs/SPRINT_PROCESS.md`; `docs/SPRINT_EXECUTION_WORKFLOW.md` 3.3.1 and 6.6; `docs/SPRINT_PLANNING.md` defined-scope rule; spamfilter-multi ADR-0015.
