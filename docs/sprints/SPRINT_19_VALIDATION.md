# Sprint 19 Manual Validation

**Sprint**: 19, Send the QCi Package Clean (F92)
**Branch**: `feature/20260923_Sprint_19` | **PR**: #141 (draft)
**Handed over**: 2026-09-25 | **Re-verified**: 2026-09-25

Written to a file rather than only to the terminal, so it can be reopened
without scrolling back through a session (CLAUDE.md: re-present, never refer
back). Every line below was re-checked against the repository on the date
above, not carried forward from the handover message.

## What to validate

Four things, in the order that makes them easiest to check.

### 1. The memo says what you approved

`docs/qci_package/Phase 1 - QCi memo.txt`

This file is **git-ignored on purpose** (`.gitignore:62`), because
`docs/qci_package/` holds private commercial correspondence. It is therefore
NOT in the PR diff and never will be. Read it on disk.

The six approved passages were applied, plus four corrections from the Task D
review (M1-M4). Spot-check these:

- Three experiments cost zero device seconds, not four (line 164)
- The 280 seconds read as spent out of 1,681
- The confound is described in the past tense: our submission flagged it,
  and after filing we ran the missing cells
- The -0.0010 figure is scoped to its arm, not to "the campaign"

Four passages were deliberately NOT changed: allocation, variables-not-levels,
schedule 4, and Experiment 5 sizing.

### 2. The hardware plan's Phase 2 ask

`docs/HARDWARE_PLAN_PHASE_2.md`

- The ask covers **now through the end of Phase 2**, not the Phase 2 period
  only. This was your correction of 2026-09-25 and it is guarded.
- 9,000 total, 1,681 already held, **7,319 rounded up to 7,500** as the
  additional request, with the rounding stated in the text.
- Experiment 5 is not counted twice.
- P1, P3, P4 and P6 from the Task D review are applied; P2 and P5 were left
  on your decision, recorded in the plan.

### 3. Fourteen disagreements, eight fixed

`docs/sprints/SPRINT_19_PLAN.md`, section "Scope extension after Task D"

A fresh-context reviewer who had not seen the plan's list read all four
package documents and found fourteen places where a figure or claim appears
in two documents and they disagree. Each was verified against the documents
and `results.json` before it reached you.

Your dispositions are recorded there: eight fixed, five left with a reason,
one answered without a change. Confirm the record matches what you decided.

### 4. Nothing submitted was touched

The three SUBMITTED PDFs are documents of record for the 2026-09-12 filing.
`test_published_artifacts.py` passes, and all six tracked PDFs are
byte-identical.

## Verification evidence, re-run 2026-09-25

- **Full suite**: 1,371 passed, 73 skipped
- **CI**: green on `b4f0d13` (`scripts/check_ci_status.py`, exit 0)
- **Document guards**: `test_qci_document_requirements.py`, 44 passed --
  these pin every corrected passage so a stale claim cannot return
- **Published artifacts**: `test_published_artifacts.py`, 12 passed
- **Outward readability**: clean on the memo, the hardware plan and the
  feedback document (exit 0)
- **Working tree**: clean
- **Every figure traced** to its owning document: +0.0245 and +0.0001
  (`F64_LADDER_DECOMPOSITION.md`), 71 s and 165 s
  (`INTEGER_PROBE_RESULT.md`), 9,000 / 1,681 / 7,500
  (`HARDWARE_PLAN_PHASE_2.md`)

## What is NOT in this sprint

**Task C was not approved** and moved to F96: the hardware plan's
Experiment 1 sentence and the package re-render. The approved scope was 105
minutes (A + B + D), not the 138 that included C.

## Task actuals

- A: 2 minutes (wording was drafted and approved during planning, so this
  measures only the edit)
- B: 6 minutes (includes the 4-minute suite run)
- D: **NOT RECORDED**. It spanned an approval stop of several hours (00:23
  to after 08:30), so wall clock does not measure the work, and an estimate
  of the active part would be a reconstruction. A fabricated actual is worse
  than a missing one, because it recalibrates future estimates against noise.

## After your validation

Phase 6 pushes and updates the draft PR; Phase 7 runs the retrospective and
is the only place `gh pr ready` happens. The merge is yours, at every level.
