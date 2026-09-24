# Sprint 19 Plan: Send the QCi Package Clean

**Sprint**: 19
**Branch**: `feature/20260923_Sprint_19`
**Dates**: 2026-09-24 onward
**Scope**: F92 (team lead selection, 2026-09-24). Defined scope: nothing else.
**Metered Dirac-3 seconds**: ZERO. No approval stop.
**Approved**: 2026-09-24 00:10 by the team lead. Line 17: the memo stays SILENT
on the ask. Task C NOT approved; the hardware-plan sentence returns to the
backlog as F96. Passages 1 and 3-6 approved as recommended. Issues #142 (A),
#143 (B), #144 (D).

## Objective

Make every document in the QCi package agree with every other, so the team lead
can send it. The package is assembled and unsent. Its memo was written before
the Sprint 18 integer probes and the F91 attribution, and it now contradicts
the hardware plan it travels with.

## Ordering rule (team lead, 2026-09-24)

F92 goes first unless another item would update a QCi package document (the
memo, the hardware plan, the eqc-models feedback, or the results against
preregistered criteria). F92 is the only item in scope, so it goes first by
construction. If the scope question below extends F92 to the hardware plan, that
edit is part of F92 and runs inside it, before the consistency review.

## Audience-first statement (mandatory, SPRINT_PLANNING.md)

**The reader is QCi's technical staff, reading the package as one envelope.**
After reading they must believe that every figure traces to a measurement and
that no two documents state one fact two ways. They then decide on the
7,500-second Phase 2 request that the hardware plan leads with. One
contradiction between the memo and the plan undercuts the argument that our
estimates are measured rather than invented.

## Confidentiality note

The memo lives in `docs/qci_package/`, which is gitignored as private
correspondence. This plan names memo passages by LINE NUMBER AND TOPIC only.
The proposed wording is presented to the team lead in the approval message,
not committed here. The committed guards in `test_qci_document_requirements.py`
already carry short memo phrases; that precedent is followed and not extended.

## Capability and code pre-flight (run 2026-09-24 BEFORE estimating)

**What reads the memo (code, not only documents)**:
- `experiments/src/test_qci_document_requirements.py` reads the memo in six
  tests: five memo-specific ones and one parametrized across three documents. One of them, `test_the_memo_asks_for_nothing_but_thoughts`,
  bans "we request", "please grant" and "we are asking for", and encodes
  the Sprint 17 decision that the memo asks for nothing. The line-17
  decision below must stay inside that test or change it deliberately.
- `experiments/src/test_outward_readability.py` and
  `scripts/outward_readability.py`, the IMP-5 check.
- **The memo is gitignored, so every memo guard SKIPS in CI.** They protect
  this workstation only. Stated, not fixed: making the memo tracked would
  publish private correspondence.

**Stale passages in the memo, by line (full read, 2026-09-23)**:
1. Line 4: the currency statement dates everything to 2026-09-12, but the memo
   reports 2026-09-23 measurements.
2. Line 17: "nothing in this package asks", while the enclosed hardware plan
   opens with the 9,000-second ask.
3. Lines 141-145: the positive result is described as confounded; F64 and F91
   attributed it (subset order +0.0245, feature count +0.0001).
4. Lines 164-167: the memo declines to quote a cost for the integer block,
   which it then reports three sections later as measured.
5. Lines 199-200: "we do not expect to need more before Phase 2 proper", with
   no pointer to what Phase 2 itself needs.
6. Line 208: the integer solver is listed as not reached.

**Stale sentence OUTSIDE the memo** (scope question, see below): the hardware
plan, lines 198-201, lists "isolating the feature-count confound" as a future
proxy experiment. F64 and F91 ran it.

**Documents checked and found current**: the eqc-models feedback (its schedule-4
question is still open, which is true), the results against preregistered
criteria (rendered after F91 regenerated `gate_report.md`), and every package PDF
(rendered 2026-09-23 23:29, after the last source commit at 19:36).

**Figures to be used, each traced**: +0.0245 CI [+0.0187, +0.0302], +0.0001 CI
[-0.0024, +0.0026], interaction about +0.0001 (`docs/F64_LADDER_DECOMPOSITION.md`);
71 s and 165 s per fit (`docs/INTEGER_PROBE_RESULT.md`); 0.0440 behind CatBoost
(`docs/paper/proposal.md`); 9,000 and 1,681 (`docs/HARDWARE_PLAN_PHASE_2.md`).

## Tasks

### Task A: Apply the approved memo wording (F92) (~30m)

The six passages above, in the wording approved with this plan.

- **Acceptance**: each approved change present verbatim; no unapproved change;
  every figure in the edited passages matches its owning document above; the
  four passages that do not change (allocation, variables-not-levels, schedule
  4, Experiment 5 sizing) are untouched.

### Task B: Guards that each stale passage cannot return (F92) (~40m)

Extend `test_qci_document_requirements.py`.

- One assertion per removed claim: the refusal to quote a cost, the
  "confounded" description, the integer solver as not reached, and the
  single-date currency statement.
- `test_the_memo_asks_for_nothing_but_thoughts` updated only as far as the
  line-17 decision requires, with the reason in its docstring.
- **Each new guard proven RED** by injecting the old passage with the F89
  helper, checking that the bytes changed, then restoring.
- **Acceptance**: every new guard fails on the old text and passes on the new
  text; the full suite is green.

### Task C: Hardware plan sentence and package re-render (F92) (~25m) -- NOT APPROVED, moved to F96

- Lines 198-201: Experiment 1 described as already run on the proxy, dated,
  with its result. The header's "one section is newer" becomes two.
- Re-render with `scripts/render_all.py --qci-package`, which renders the
  package only.
- **Acceptance**: the new PDF carries the sentence; the three SUBMITTED PDFs are
  byte-identical before and after (`test_published_artifacts.py`); the
  existing hardware-plan guards stay green.

### Task D: Cross-document consistency review (F92) (~20m)

- `scripts/outward_readability.py` on the memo and the hardware plan: every
  hit either fixed or allowed with a reason.
- A fresh-context reviewer (subagent, no sprint context) reads all four package
  documents and lists every figure or claim that appears in two of them, and
  whether they agree. This is also the Phase 5 external-review pass.
- **Acceptance**: zero disagreements, or each one fixed through Task A or C
  wording and re-approved.

## Estimate

Derived from the card and recorded there before this plan was written
(SPRINT_PLANNING.md, Sprint 17 improvement 1). This plan reports the total and
does not originate it.

- A 30 + B 40 + C 25 + D 20 = **115 minutes**
- Writing portion (A, C) 55m: 30% sourcing allowance = **16.5m**
- Verification portion (D) 20m: 30% findings allowance = **6m**
- **Total: 138 minutes (2.3 hours)** with Task C; **105 minutes** without it
  (A 30 + B 40 + D 20 = 90, plus 9 + 6)
- **APPROVED SCOPE: 105 minutes** (Task C not approved)

Dependencies: B follows A (it pins A's final wording). D follows A and C (it
reviews their result). Nothing runs in parallel.

Calibration: Sprint 18 recorded no actuals, so this uses the documentation
ratio of about 1.0 from Sprints 13 and 14. Actuals are recorded in
`task_actuals` as each task completes (IMP-1).

## Metered summary (Criterion H)

None. F95 (relaxation schedule 4) is HELD until after the memo is sent (team
lead, 2026-09-23), and the memo continues to describe it as planned work.

## Premise falsifier (mandatory)

**Premise**: after the six memo passages (and, if approved, the one hardware
plan sentence) change, no two package documents disagree.

**The check**: Task D's fresh-context reviewer, who has not seen this plan's
list. If that reviewer finds a disagreement this pre-flight did not list, the
premise was wrong, and the finding goes through the 30% findings allowance.

**It can fail**: the pre-flight found the hardware-plan sentence only on a
second pass, after the backlog card had stated "only the memo is stale". A
list that has been wrong once is a list worth checking independently.

## Risks

- **The memo guards do not run in CI.** The memo is gitignored, so they skip
  there. Local runs are the only protection, and Task B's red-proof must run
  locally.
- **Private wording leaking into a tracked file.** Mitigated by the
  confidentiality note above and by the pre-commit confidentiality hook.
- **F93 could reopen the package.** If the SPECTRA reconciliation later changes
  Experiment 5's sizing in the hardware plan, the memo's balance section
  changes too. Accepted: the memo will state what the plan states on the day it
  is sent.
- **The re-render touching a submitted PDF.** `--qci-package` renders the
  package only, and `test_published_artifacts.py` fails on any rebuild of a
  tracked PDF.

## Definition of Done

- Every approved passage in the memo, and no unapproved change
- A guard for each removed claim, each proven red on the old text
- `outward_readability.py` clean or every hit allowed with a reason
- Zero cross-document disagreements from a fresh-context review
- Full suite green; CHANGELOG updated; three-doc rule satisfied at close

## Out of scope

- **Sending the package.** The team lead sends it; Claude never does.
- **F95**, held until after the memo is sent.
- **F93, F94, F90** and every other candidate: not selected.
- Any submitted document (`docs/paper/`, `docs/submission/`).
