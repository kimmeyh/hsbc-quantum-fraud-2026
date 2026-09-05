# Quality Standards

**What gets version-controlled is decided by REGENERATION COST, not file size (Sprint 5, team-lead agreed 2026-09-04)**: an artifact that can be rebuilt for free by running a script belongs in .gitignore; an artifact whose regeneration costs money, consumes metered hardware, or depends on an external service that may change belongs in git, however small. Sprint 5 lost the per-transaction Dirac-3 prediction scores to a key collision precisely because they had been classified as regenerable intermediate data alongside the classical and proxy scores, which genuinely are. They were never in a commit, and the nightly backup could not help either: the files existed for about twenty minutes inside the gap between two backup runs. Version control is the only durable record of an artifact that costs metered seconds to produce.

**Verify the artifact you ship, not a proxy for it (Sprint 5 retro improvement 7)**: a check that reads something OTHER than the delivered artifact can report success while the artifact is broken, which is worse than having no check, because it consumes the attention a real check would have earned. Sprint 5 shipped nine 11x17 TABLOID PDFs for days while `check-page-limits.py` reported "within limits", because it read page counts from Word's ComputeStatistics, which REFLOWS a PDF when it opens it. The same class recurred inside the sprint: the appendix was reported "3 of 3 pages" from a stale PDF while the rebuilt file was 4 against a hard limit. Both were caught by the team lead asking a question, never by a check. Rules: (1) read the finished artifact, in its delivered format, after the last step that changes it; (2) treat a passing check whose input you did not just regenerate as UNVERIFIED; (3) prove a new check fails on the defect it is meant to catch before trusting it to pass. `experiments/src/test_submission_artifacts.py` implements this for the submission PDFs.

**Re-read before write (Sprint 4 retro improvement 7)**: when a file may have been touched by another process, a background job, or an earlier in-flight write, RE-READ it immediately before writing. A stale-write overwrite is a defect class, not an accident: Sprint 4 lost a corrected results memo to one and paid a full rewrite. Whole-file writes to shared documents are the highest-risk case.

**Background-launch fencing rule (Sprint 3 retro improvement 5)**: before launching ANY background job that writes files, verify each output path is either gitignored or deliberately tracked -- in that turn, not after. A later `git add -A` must never be the moment output paths are first considered (Sprint 3: volatile pool/log artifacts swept into a commit before the fence landed).

**Purpose**: Documentation, code, and automation standards for this repository.
**Audience**: Claude Code sessions; the team lead.
**Last Updated**: 2026-08-30 (disposition items 14 and 17, adapted from spamfilter-multi QUALITY_STANDARDS.md and ADR-0017)

## Documentation standards

- Every doc in `docs/` opens with **Purpose**, **Audience**, **Last Updated**.
- File size cap ~40,000 characters; beyond it, extract sections to their own doc and cross-reference. Table of contents required above ~20,000 characters. (These docs are read by Claude every session; size is a cost.)
- No contractions in formal docs; no emoji; bracketed markers ([OK], [FAIL], [WARNING]) where a status glyph is needed; no em dashes.
- Templates are authoritative: read the template section in the same turn before producing its deliverable (workflow invariant 6).
- **Full-accounting-first rule (Sprint 2 retro improvement 5)**: when summarizing research or review output, state the complete accounting FIRST (totals and per-category counts), then present the triaged subset. A compressed summary that makes 30 findings read as 4 forces the team lead to challenge to surface the rest.

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
