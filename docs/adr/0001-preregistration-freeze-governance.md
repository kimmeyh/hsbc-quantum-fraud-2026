# ADR-0001: Preregistration freeze governance and amendment mechanics

## Status

Accepted

## Date

2026-08-30

## Context

The submission's central credibility claim is that hypotheses, budgets, splits, and statistics were committed before results existed. That claim is only auditable if the freeze is a verifiable artifact and every later change is visible. The project is a solo effort executed across many AI sessions, so the mechanics must survive total context loss.

## Decision

- The freeze is implemented in git: `experiments/PREREGISTRATION.md` v1.1 status line reads FROZEN; freeze commit `95751b9`; annotated tag `prereg-freeze`; amendment A1 in the file records the hash.
- Analysis code in `experiments/src/` froze at the same commit. Any post-freeze change to a frozen file must carry a dated amendment line in `PREREGISTRATION.md`'s Amendment log in the same commit.
- Amendments may add exploratory analyses or fix implementation bugs; they may never change a gate's pass/fail criterion, add cells to an observed hypothesis, or remove an observed hypothesis. Such changes are reported as DEVIATIONS in the gate table.
- Amendment content changes are Class 1 decisions requiring explicit team-lead approval before commit.
- The gate table (prereg section 11) is the scoring surface; nulls and failures are published.

## Alternatives Considered

### Freeze as a signed PDF snapshot outside git
- **Description**: Export the frozen protocol to an immutable external artifact.
- **Pros**: Cannot be edited at all.
- **Cons**: Diverges from the living amendment log; unverifiable linkage to the code state.
- **Why Rejected**: Git commit + tag gives equivalent immutability with better auditability and code co-versioning.

## Consequences

### Positive
- Any reviewer can verify what was committed before which result via `git log prereg-freeze..`.
### Negative
- Legitimate bug fixes in frozen code cost an amendment line each; friction is deliberate.
### Neutral
- The public reproducibility package must include the tag history to make the claim externally checkable.

## Preregistration touchpoints

Sections 11 (scoring, amendments, deviations) and 12 (freeze procedure). The preregistration governs methodology; this ADR records engineering decisions only.

## References

`experiments/PREREGISTRATION.md`; commit `95751b9`; tag `prereg-freeze`; `docs/SPRINT_PROCESS.md` decision classes.
