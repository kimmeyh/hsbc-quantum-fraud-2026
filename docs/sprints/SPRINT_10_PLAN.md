# Sprint 10 Plan: Publish What We Promised

**Dates**: 2026-09-09 to 2026-09-11 (evidence freeze Sep 12, target submit Sep 13, hard deadline Sep 15)
**Branch**: `feature/20260909_Sprint_10`
**Scope** (DEFINED, team lead 2026-09-08): F40 -> F37 -> F38, in that order. Nothing else.

## Objective

Clear all three remaining submission blockers. Every task is a gate on submitting
at all, not an improvement to what is submitted: an over-limit PDF is a rules
failure independent of content quality, and the appendix's 3-page limit is met
only because material was moved OUT of the PDF and INTO a repository that is
still private, so its citation is currently a dead link.

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

Order is a hard dependency chain, not a preference: F40 must complete before
F37, because making the repository public publishes the working tree.

| # | Task | Est | Runtime | Dominant cost | Model |
|---|---|---|---|---|---|
| A | **F40** Segment non-public material out of the tree | 60m | ~3m | `render-all.ps1` (3 submission + 7 QCi package PDFs) + full suite (~105s) | Opus |
| B | **F37** Make the repository public | 45m | ~2m | Full-history confidentiality scan | Opus + team lead |
| C | **F38** Appendix to 3 pages AND proposal to 6 | 90m | ~2m/cycle | Render + page-fill measure per cut cycle | Opus |

**Estimates are calibrated against recorded actuals, and deliberately pessimistic
on C.** Sprint 7 overran specifically on page-limit cycles that were not
estimated. C is now a 158pt cut, not the 76pt the card assumed, on a document
where every page is already full. 90m is the timebox; if the cut cannot be made
without losing evidence, that is a Decision-Class 2 event (see below), not a
reason to cut deeper.

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

### Task B -- F37: make the repository public (45m, team-lead action)

1. Run `scripts/confidentiality-scan.ps1` over **full history**, not just the tip
2. Confirm the `0*` resolution from Task A left nothing tracked
3. Confirm QCi job records carry no account or credential material
4. Confirm both dataset licences permit redistributing derived checksums and
   results (raw ULB and IEEE-CIS data are NOT redistributed)
5. **Team lead flips visibility** -- Claude never does this
6. Verify anonymously: `curl` the API for 200, and resolve the Appendix C URL
   in a logged-out browser

**Acceptance**: anonymous fetch returns 200 AND `experiments/requirements.txt`,
`experiments/PREREGISTRATION.md` and the results store are reachable without
authentication, verified logged out rather than from an authenticated session.

**Premise falsifier**: the premise is that the scan finds nothing publishable-
sensitive after Task A. Falsifier: any scan hit outside the known-and-accepted
history exposure. A hit stops the flip and returns to Task A.

**Irreversible.** Once public, published is published; history rewriting after
publication is not reliable. This is the one step that cannot be undone, which
is why it runs before the deadline pressure of Sep 13, not on it.

### Task C -- F38: page limits (90m)

Appendix needs 158pt cut; proposal needs 21pt. Both measured 2026-09-08.

1. Re-run `page-fill-report.py` on both PDFs immediately before cutting (the
   figures move whenever content lands)
2. Proposal first: 21pt against 48pt of slack is the cheaper problem
3. Update the xfail `reason` string too -- it still says "appendix 4 of 3",
   stale as of today's 5 of 3
4. Appendix: candidate already drafted and measured once -- condensing Appendix
   C's artifact list to one sentence recovers ~3 lines. That is nowhere near
   158pt on its own
5. Re-render and re-measure after each cut; do not batch

**Do NOT cut**: any figure, control, caveat, the A15/A17/A12 disclosures, or the
B.1 compound-falsification statement. The 2026-09-06 pass already removed all
restatement that was free to remove; what remains is evidence.

**Acceptance**: `python scripts/check-page-limits.py` reports OK 6 of 6 and
3 of 3, AND a numeric diff against the current render shows no figure lost
(extract all decimals from both PDFs, compare as sets). The two
`xfail(strict=True)` page-limit cases FLIP TO FAILING, which is the designed
signal that the markers must be removed in the same commit.

**Premise falsifier**: the premise is that 158pt can be reclaimed without losing
evidence. Falsifier: reaching the end of the non-evidence material with the
document still over. If that happens, STOP -- cutting evidence to fit is a
Decision-Class 2 change and needs explicit team-lead approval, not a judgment call.

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| **F38 cannot reach 3 pages without cutting evidence** | Medium-high. 158pt is large and every page is full | Falsifier above stops the task rather than quietly cutting evidence. Escalate as Class 2 |
| F37 published something that should not be public | Low after Task A | Task A precedes it; full-history scan; irreversibility respected by sequencing it early |
| Page-limit cycles overrun, as in Sprint 7 | Medium | Estimated at 90m against a measured 158pt, not the card's stale 76pt |
| Deadline: 3 blockers, T-5 to target submit | Medium | This sprint is only the blockers. F5 and F29 already moved to HOLD |
| Hardware budget (Criterion H) | None | Zero metered seconds planned. No Dirac-3 run in this sprint |
| Grant timing | None this sprint | F5 held; issue #40 awaits QCi independently |
| Context/session continuity | Medium | Each task commits independently; the chain order is recorded here |

## Decision-Class checkpoints (invariant 7)

- **Class 1 (protocol)**: none planned. No task touches the frozen preregistration
- **Class 2 (evidence claims)**: triggered if F38 cannot fit without cutting a
  figure, control or caveat. STOP and surface
- **Class 3 (scope)**: triggered if any of the three cards is proposed for
  deferral. All three are submission blockers; deferring one is a team-lead
  decision, never a time-pressure judgment call

## Definition of Done

All three acceptance blocks met; full suite green with the two page-limit xfail
markers REMOVED (not flipped to skip); 10 PDFs render; repository anonymously
reachable; tree clean; PR updated and still DRAFT until 7.7.
