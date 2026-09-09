# Sprint 10 Plan: Publish What We Promised

**Dates**: 2026-09-09 to 2026-09-11 (evidence freeze Sep 12, target submit Sep 13, hard deadline Sep 15)
**Branch**: `feature/20260909_Sprint_10`
**Scope** (DEFINED, team lead 2026-09-08): **F40 only.**

**RE-SCOPED 2026-09-08 after initial approval** (Class 3, team-lead directed):
F37 and F38 moved to Sprint 11. Cards #56 and #57 stay open and remain
SUBMISSION BLOCKERS against the Sep 13 target; they are simply not this
sprint's work. Sprint 10 is the segmentation step alone, which is also the
step that must precede F37 whenever F37 runs.

## Objective

Segment non-public material out of the working tree, so that making the
repository public (F37, Sprint 11) publishes only what is intended. This is the
prerequisite step: F37 cannot safely run until it is done, and doing it early
means the irreversible visibility flip is never taken under deadline pressure.

## Audience-first statement (mandatory, Sprint 4 retro improvement 3)

**F40/F37 reader**: anyone who opens the public repository, including the HSBC
judging panel following Appendix C. They must find the pinned environment, both
dataset checksums, the full preregistration and all 37 QCi job identifiers, and
must NOT find team-lead working notes or the prior Fourier Wall work the team
lead has decided stays out of the submission.

**F38 reader**: the judging panel, reading a 6-page proposal and a 3-page
appendix. They must lose no figure, no control, and no caveat relative to
today's over-limit drafts.

## Scope decisions carried in (do not re-litigate)

- **F5 and F29 moved to HOLD** at 2026-09-08 refinement. F5 is blocked on the
  QCi grant; F29 scores against no rubric criterion and needs page space that
  F38 is trying to reclaim.
- **Issue #40 stays open** by explicit team-lead decision, pending QCi's
  substantive reply. It is not a Sprint 10 task.
- **Git history is NOT rewritten** in F40 (team lead's explicit decision). The
  `0*` files and fourierwall2 remain in history, and a public repo exposes
  history. Accepted: the exposure is the team lead's own contact details and
  prior-work references, not credentials.

## Capability pre-flight (mandatory, run 2026-09-08 BEFORE estimating)

Every number below is measured today, not carried from the cards.

| Check | Card said | Measured now | Consequence |
|---|---|---|---|
| appendix.pdf | 4 of 3 pages, ~76pt over | **5 of 3 pages, 186pt spill, 28pt slack, 158pt to cut** | Card's own warning was right: do not trust its figure. Effort revised UP |
| proposal.pdf | 7 of 6 pages | 7 of 6, 70pt spill, 48pt slack, **21pt to cut** | Small. The appendix is 7.5x the problem |
| `0*` tracked files | 7 | 7 | Matches |
| fourierwall2 | 2MB, 42 files | 2.0M, 42 files | Matches |
| fourierwall2 doc refs | 3 | **4** (SPRINT_9_SUMMARY.md added since the card) | One more edit than carded |
| `.env` tracked | never | never (`git log --all` empty) | Confirmed safe |
| Repo visibility | private | anonymous API 404 | Confirmed private |
| `confidentiality-scan.ps1` | assumed present | present | F37 step 1 can run |
| Destination folder | holds the sent .msg | README.md + the .msg | Ready |

## Tasks

F40 is the whole sprint. It remains the hard prerequisite for F37 (Sprint 11),
because making the repository public publishes the working tree.

| # | Task | Est | Runtime | Dominant cost | Model |
|---|---|---|---|---|---|
| A | **F40** Segment non-public material out of the tree | 60m | ~3m | `render-all.ps1` (3 submission + 7 QCi package PDFs) + full suite (~105s) | Opus |

**Deferred to Sprint 11**: F37 (#56), F38 (#57).


**Estimate calibration.** 60m covers the move, the cache removal, the .gitignore
entries, 4 doc rewordings and the verification pass. The dominant runtime cost is
the render + suite at the end, ~3m.

### Task A -- F40: segment non-public material (60m)

1. Move 7 `0*.txt` files and `experiments/reference/fourierwall2/` to
   `D:\Data\Harold\hsbc-quantum-fraud-2026\`
2. `git rm --cached` each
3. Add `0*.txt` and `experiments/reference/fourierwall2/` to `.gitignore`
4. Reword **4** doc references (CHECKLIST.md, docs/adr/0013, master plan,
   SPRINT_9_SUMMARY.md) to point at the external folder. Reword, do not delete:
   ADR-0013's reasoning still stands
5. Update the destination README recording what moved, when, why, from which commit
6. Re-run the full suite and `render-all.ps1`

**Acceptance**: `git ls-files` returns nothing matching `0*.txt` or
`fourierwall2`; full suite passes; all 10 PDFs still render (3 in docs/paper/out/, 7 in
docs/paper/out/qci_package/); destination README updated.

**Premise falsifier**: the premise is that nothing in the codebase depends on
the fourierwall2 path. Falsifier: any test or script failing after the move.
If one does, the move is wrong and the path must be preserved or the dependency
fixed first.

**Never read the `0*` files.** CLAUDE.md forbids it. Structural scan only; the
move needs no content inspection, which is exactly why segmentation beats review.

### Deferred to Sprint 11

**Task B -- F37 (#56)** and **Task C -- F38 (#57)** were moved out of this sprint
by team-lead decision after plan approval. Their full task detail, acceptance
criteria and premise falsifiers stay in cards #56 and #57. The Sprint 10
pre-flight measurements (appendix 5 of 3 needing a 158pt cut; proposal 7 of 6
needing 21pt) are recorded there and MUST be re-run before that work starts,
because both figures move whenever content lands.

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| F40 misses something that should not be public | Low | Structural scan already inventoried the tree; the acceptance check is `git ls-files`, not judgment. F37 (Sprint 11) adds a full-history scan before anything is published |
| **Deadline: 2 blockers now deferred to Sprint 11, T-5 to target submit** | **Raised by the re-scope** | Sprint 11 must carry both F37 and F38. Flagged, not mitigated here: scope is the team lead's call |
| Hardware budget (Criterion H) | None | Zero metered seconds planned. No Dirac-3 run in this sprint |
| Grant timing | None this sprint | F5 held; issue #40 awaits QCi independently |
| Context/session continuity | Medium | Each task commits independently; the chain order is recorded here |

## Decision-Class checkpoints (invariant 7)

- **Class 1 (protocol)**: none planned. No task touches the frozen preregistration
- **Class 2 (evidence claims)**: none planned. F40 moves files, it does not
  change any claim
- **Class 3 (scope)**: already exercised. F37 and F38 were deferred to Sprint 11
  by explicit team-lead direction on 2026-09-08, which is the only way approved
  work may be deferred

## Definition of Done

F40's acceptance met: `git ls-files` returns nothing matching `0*.txt` or
`fourierwall2`; full suite green (the two page-limit xfails REMAIN xfail, since
F38 is deferred); all 10 PDFs render; destination README updated; tree clean; PR
updated and still DRAFT until 7.7.
