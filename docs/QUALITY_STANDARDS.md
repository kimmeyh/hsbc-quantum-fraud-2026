# Quality Standards

**Purpose**: Documentation, code, and automation standards for this repository.
**Audience**: Claude Code sessions; the team lead.
**Last Updated**: 2026-08-30 (disposition items 14 and 17, adapted from spamfilter-multi QUALITY_STANDARDS.md and ADR-0017)

## Documentation standards

- Every doc in `docs/` opens with **Purpose**, **Audience**, **Last Updated**.
- File size cap ~40,000 characters; beyond it, extract sections to their own doc and cross-reference. Table of contents required above ~20,000 characters. (These docs are read by Claude every session; size is a cost.)
- No contractions in formal docs; no emoji; bracketed markers ([OK], [FAIL], [WARNING]) where a status glyph is needed; no em dashes.
- Templates are authoritative: read the template section in the same turn before producing its deliverable (workflow invariant 6).

## Analysis-code standards (KISS / YAGNI)

- The simplest implementation that satisfies the frozen protocol wins. No speculative abstraction: build for the preregistered grid, not imagined future studies. A 10-line change to metrics code is top-tier-review work here; complexity budget goes to statistical correctness, not architecture.
- Single implementation per concept: one metrics module, one splits provider, one config schema. Duplication of methodology-bearing code is a defect.
- Type hints on signatures; module docstrings state which preregistration section the file implements; no debugging prints left behind; known failure modes documented in the header of long-running scripts (disposition item 18, F1 sprint).
- Frozen files (`experiments/src/` at tag `prereg-freeze`) change only with an amendment line in the same commit (ADR-0001).

## Automation standards (PowerShell-native)

- Automation scripts on this machine are PowerShell (`.ps1`), executed natively, never wrapped in bash (wrapping loses toolchain context on this exact host; spamfilter-multi ADR-0017 lesson). POSIX scripts only where a tool demands them.
- Long jobs run in the background with output files; per-trial/per-fit persistence so interruption loses one unit, not the run.
- `--no-verify` is banned; hooks are part of the quality system.

## Testing standards (summary; full doc lands with the F1 sprint, disposition item 15)

- pytest green before any commit touching `experiments/src/`.
- Known-answer tests for statistical code (cross-validate against reference implementations).
- Isolated-branch guard tests for safety-critical branches (leakage controls); synthetic fixtures with realistic class overlap; scratch probes never enter the repo.
