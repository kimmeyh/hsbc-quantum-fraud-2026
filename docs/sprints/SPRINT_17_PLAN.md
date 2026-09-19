# Sprint 17 Plan: Clear the Deck for Phase 2

**Sprint**: 17
**Branch**: `feature/20260919_Sprint_17`
**Dates**: 2026-09-19 onward
**Scope**: F86 (new), F82, F83, F84. F85 CLOSED into F86.
**Metered Dirac-3 seconds**: ZERO

## Objective

Close every non-hardware item on the board so that Sprint 18 can start on F64,
F2b and the HOLD list without anything else competing.

The team lead's stated goal: *"address all of these so we can get to F64, F2b
and all on hold items starting next sprint."* That makes this sprint's success
condition unusual and worth naming: **it succeeds if the backlog afterwards
contains only experiments.**

## Scope note

The team lead's selection IS the complete scope.

**F85 is CLOSED and replaced**, not carried. It renamed one PDF for a QCi
audience; F86 sends a package to QCi of which that rename is one line. Keeping
both would split one deliverable across two cards.

**F81 is CLOSED**: the explainer went to a real reader and the team lead
recorded no feedback.

## Audience-first statement (mandatory, SPRINT_PLANNING.md)

**F86's reader is QCi's technical staff**, who granted Dirac-3 access and have
heard nothing since the submission. After reading they must believe three
things: the work was done and filed, their hardware behaved well and we say so
plainly, and there is a concrete Phase 2 plan their remaining seconds feed.

**What they must NOT be asked to do is decide anything.** This is an update,
not a request. The 30,000-second ask was the previous letter; re-asking inside a
thank-you would undercut both.

**F82/F83/F84's reader is a future session on a machine that is not this one.**

## Capability pre-flight (run 2026-09-19 BEFORE estimating)

**F86:**
- All three renamed sources exist: `docs/QCI_EQC_MODELS_FEEDBACK.md` (160
  lines), `docs/HARDWARE_REQUEST_B1_G0b.md` (50), `experiments/results/gate_report.md` (134)
- The three submitted PDFs are committed and hash-match the filing
- `render_all.py` already builds all three DRAFT PDFs; only output names change

- **DATE DISCREPANCY, and it must be settled before the memo is written.** The
  team lead's request says "note on submission 9/14". `SUBMISSION_RECEIPT.md`
  records **2026-09-12**, three days before the 2026-09-15 deadline, with the
  portal confirmation quoted. The memo will say 2026-09-12 unless the team lead
  corrects it. A date wrong in a letter to the hardware vendor is the kind of
  small error that costs credibility on everything around it.

- **QPU ARITHMETIC DOES NOT RECONCILE YET.** The submission reports 61 fits and
  1,141 metered seconds. `qpu_cost_ledger.json` holds 52 calls of which only 28
  carry billing, totalling 130 s. The appendix says "4 to 92 s per fit", so the
  spread is real and the ledger covers the free tier only. **The memo states
  remaining seconds, so this must be reconciled from artifacts BEFORE it is
  written, not estimated.** Task A owns it.

**F82:** the class appeared 9 times in Sprint 16 including twice while writing
the retrospective and the cards. `block_unraw_escape` and
`block_shell_metachar_expansion` guard COMMANDS; every instance was a backslash
sequence written inside a heredoc that landed in a file.

**F83:** `experiments/requirements-lock.txt` pins all 18 dependencies.
`results.json` holds 168 rows carrying `config_hash` only, so no row records
which OS produced it.

**F84:** section 11 of the FROZEN preregistration defines the row schema, so
this needs an amendment rather than an edit.

## Tasks

### Task A: Reconcile the QPU figures from artifacts (~40m)

Before any prose. Establish, from `qpu_cost_ledger.json`, `results.json` and the
hardware artifacts: total metered seconds, the grant size, and seconds
remaining.

- **Acceptance**: three figures, each traced to a named artifact, and the
  free-tier/paid-tier split explained. If they cannot be reconciled, the memo
  says what is known and what is not rather than presenting an estimate as fact.
- This is the config-provenance rule applied to numbers in an outward document.

### Task B: Confirm the submission date with the team lead (~5m)

The request says 9/14; the receipt says 2026-09-12. Team-lead decision, asked
once, in one line. Not a blocker for the other tasks.

### Task C: Rename the three PDF outputs (F85, folded in) (~30m)

In `render_all.py` only:

| Current | New |
|---|---|
| `DRAFT_eqc_models_feedback.pdf` | `Phase 1 - eqc_models Feedback.pdf` |
| `DRAFT_hardware_plan.pdf` | `Phase 1 - Hardware Plan for Phase 2.pdf` |
| `DRAFT_gate_report.pdf` | `Phase 1 - Results Against Preregistered Criteria.pdf` |

- **Source files are NOT renamed.** `experiments/results/gate_report.md` is
  referenced by `score_gates.py` and several tests; renaming it would touch the
  evidence pipeline for a presentational reason.
- **Filenames contain spaces.** Every consumer must quote them. A test asserts
  the produced files exist by their exact names.
- Acceptance: the three PDFs render under the new names; page counts unchanged.

### Task D: Refresh the three documents to submission-time content (~90m)

The team lead's constraint is explicit and narrow: **"only based on what we know
at the time of submission."** No post-submission finding enters these documents.

- Each refreshed document states the date its content is current to.
- Every changed number is traced to `results.json` with its evidence tag.
- **Acceptance**: a diff review showing no claim postdates 2026-09-12.

### Task E: Write `Phase 1 - QCi memo.txt` (~90m)

Plain text, friendly. Order is mine to recommend:

1. **The news**: submitted, on the recorded date, three documents
2. **Thank you**: the grant made the campaign possible, said early and plainly
3. **What we found about Dirac-3**, the part QCi actually wants: 61 fits, zero
   failures, zero retries; hardware agreed with the exact classical solve to
   within 0.0010 AUPRC; and the 200:1 resolution finding, which is a real
   engineering result about their device rather than a complaint
4. **The null, stated without hedging**, and why it is a result about the
   problem rather than about their machine
5. **Phase 2 hardware plan**, updated
6. **How the remaining seconds get used** in pre-Phase-2 preparation
7. **Known areas of QCi exploration** we have not reached
8. **Open to your thoughts** — the close, since it is the only ask

- **The tone risk worth naming**: a null result sent to the vendor whose
  hardware produced it can read as blame. It is not, and the memo must make
  that unmistakable — the device did what it was asked to do, and the diagnosis
  is at the pool.
- Acceptance: every figure traced; no claim postdating the submission; no
  request for anything except thoughts.

### Task F: Assemble and scan the package (~30m)

Seven files: three submitted PDFs, three renamed PDFs, one memo.

- **Acceptance**: `confidentiality_scan.py` returns 0 on every markdown source.
  The scan now BLOCKS on unreadable or missing input, so a clean pass means
  every file was actually read.
- The package is assembled for the team lead to send. **Claude does not send it.**

### Task G: Hook the escape-eaten class (F82) (~60m)

A PreToolUse guard for a backslash sequence written inside a heredoc destined
for a file.

- **Acceptance, both directions by injection**: a heredoc writing content with
  an unescaped backslash sequence BLOCKS; a heredoc writing legitimate prose
  about backslashes does NOT. A guard that blocks correct work gets bypassed.

### Task H: Measure venv parity (F83) (~120m)

- **H1. Settle the Appendix C claim first.** It states "Python 3.12, Linux"; the
  campaign ran on Windows. Determine which arms ran where, from artifacts. This
  may be a submission-accuracy finding rather than a tooling one, and it is the
  half that matters most.
- **H2. Measure, do not argue.** Run the suite and a subset of classical arms on
  both platforms, compare row by row.
- **REPRODUCE FAITHFULLY, DO NOT CHANGE** (team lead, explicit): `results*.json`
  and the `.md` documents are the post-results record. This task TESTS whether
  they reproduce; it does not edit them. Any divergence is a FINDING.
- Acceptance: a measured divergence figure, and a stated finding on Appendix C.

### Task I: Environment in the row schema (F84) (~120m)

- Amendment written and dated; OS, Python, BLAS and thread count on new rows
- Does NOT retrofit the 168 existing rows, and says so
- Acceptance: `test_row_schema.py` enforces the fields; the amendment is logged
- Depends on: **Task H**, which decides whether the question is live

## Findings allowance

Tasks A, F and H are verification; Tasks D and E are writing. Both allowances
apply (SPRINT_PLANNING.md, Sprint 13 and Sprint 15 improvements):

- 30% on the 190m verification portion = **57m**
- 30% on the 180m writing portion for sourcing = **54m**

Stated rather than absorbed. If everything sources cleanly the allowance returns.

## Premise falsifier (mandatory)

**Premise**: the QCi package says only what was known on 2026-09-12 and every
figure in it is true.

**The check**: a fresh reader with the package and `results.json`, asked to find
any claim that postdates the submission or any figure that does not trace. Not
"is this good" — a reviewer asked that says yes.

**It can fail**, and the QPU reconciliation in Task A is the most likely place:
the ledger and the submission already disagree on their face.

## Risks

- **A wrong number in a vendor letter** costs credibility on everything around
  it. Task A exists to prevent one.
- **The null reading as blame.** Mitigated by Task E's structure: the
  hardware findings come BEFORE the null, and the diagnosis is at the pool.
- **Scope creep in Task D**, where "refresh" invites adding what we learned
  later. The acceptance criterion is a diff review against the date.
- **Task H may generate work** rather than close it. That is the point, and the
  allowance covers only small findings; anything large becomes a card.

## Definition of Done

- Seven-file package assembled, scanned clean, ready for the team lead to send
- No claim in it postdates 2026-09-12; every figure traced to an artifact
- F82's guard proven by injection in both directions
- F83's divergence measured and the Appendix C claim settled
- F84's amendment written; new rows carry the environment
- `results*.json` and the `.md` documents UNCHANGED by Task H
- Suite green; CHANGELOG updated; three-doc rule satisfied

## Out of scope

- **Sending the package.** Assembled for the team lead; Claude never sends.
- Any Dirac-3 run. Zero metered seconds.
- F64, F2b and the HOLD list — the sprint exists to clear the way for them.
- Retrofitting the 168 existing rows with environment fields.

## Estimate

9 tasks, **585 minutes**, plus 111 minutes of stated allowance: **696 minutes,
11.6 hours.** The verification and writing halves are roughly balanced (190m and
180m), which is why both allowances apply.

(Verified by summing rather than asserting. The draft said 605 and 716, both
wrong. This is the second consecutive sprint where the plan's own total was off
until it was computed -- Sprint 16's draft said 590 against an actual 585.)
