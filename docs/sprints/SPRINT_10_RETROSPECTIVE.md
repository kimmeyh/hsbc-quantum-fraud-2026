# Sprint 10 Retrospective

Sprint 10: F40 segmentation, plus the correctness work two adversarial reviews surfaced.
Conducted 2026-09-09 after Phase 6, before `gh pr ready`.

Team-lead feedback is recorded VERBATIM. Claude's lines come from
`docs/sprints/drafts/SPRINT_10_RETROSPECTIVE_claude_draft.md`.

## Sprint 10 Retrospective Feedback

### 1. Effective while as Efficient as Reasonably Possible

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good

- **Claude Code Development Team**:

  F40 delivered inside its 60m estimate and the sprint stayed at its defined
  scope. But the sprint was efficient partly because it was re-scoped twice: F37
  and F38 moved to Sprint 11 after plan approval. That was the right call and the
  team lead made it, yet it means Sprint 10's efficiency is not evidence the
  planning was right-sized -- a one-card sprint is hard to overrun.

  The real inefficiency was mine: I violated a rule I had read in the same
  session (the 8.2 no-pruning-script rule) and had to verify no damage after the
  fact. Reading a rule and following it are different acts, and I did the first.

### 2. Testing Approach

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good

- **Claude Code Development Team**:

  Good outcome, arrived at late. The suite grew 197 -> 201 and the four new tests
  are the useful kind: they compare the gate report against results.json and I
  verified they fail on the original bug rather than assuming they would.

  The gap is what the suite did NOT catch. score_gates.py under-reported the
  campaign total for weeks and no test compared the artifact to its source. Two
  external reviewers found real defects in one day; our own suite found none of
  them. The tests we have check that code runs, not that documents agree with
  evidence.

### 3. Effort Accuracy

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good

- **Claude Code Development Team**:

  F40 estimated 60m, delivered close to it. The pre-flight was worth its cost: it
  found the appendix at 5 of 3 pages rather than the carded 4 of 3, and 158pt to
  cut rather than 76pt. That is the second consecutive sprint where measuring
  before estimating changed the plan.

  Unestimated work dominated the back half: the two review passes and the
  gate-report fix were not in any plan. That is not an estimation failure, but it
  means "Sprint 10 hit its estimate" describes about a third of what happened.

### 4. Planning Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good

- **Claude Code Development Team**:

  The plan's premise falsifiers did their job -- F40's ("any test or script fails
  after the move") was checkable and did not fire. The capability pre-flight
  table is the strongest part of the plan and should stay mandatory.

  Weakness: the plan assumed the fourierwall2 doc references were the whole
  path-cleanup problem. They were not. `data.py` hardcoded the ULB dataset path,
  which no card mentioned and which broke reproduction for any clone. Planning
  inventoried documents and not code.

### 5. Model Assignments

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good

- **Claude Code Development Team**:

  All work ran on Opus in the main loop, correct for a sprint whose content was
  protocol-sensitive and evidence-bearing. No subagents were spawned, which was
  right: nothing here parallelized cleanly and the work needed continuity of
  context.

### 6. Communication

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good

- **Claude Code Development Team**:

  Commit messages carried the reasoning, including the parts against us -- the
  undercount commit states plainly that the verification tool was the source of
  the error. Reporting the Criterion 7 stop was prompt and specific.

  One failure: I answered "continue until backlog refinement" three times by
  stopping BEFORE backlog refinement, when the team lead meant through it. Three
  identical instructions producing three identical wrong results should have made
  me question my reading after the first, not the third.

### 7. Requirements Clarity

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good

- **Claude Code Development Team**:

  Mostly clear. The one genuine ambiguity, "rename QI", I asked about rather than
  guessed, and the answer showed the target did not exist in the repo -- asking
  was cheaper than a wrong rename.

  The sequencing instruction ("correctness first, page size last") arrived
  mid-turn and changed nothing about what I was doing, which suggests it was
  already implicit; still worth having stated, since F38 would otherwise have
  been cut twice.

### 8. Documentation

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good

- **Claude Code Development Team**:

  Both review passes are carded with their reproductions recorded (#59, #60), so
  neither card starts by re-deriving evidence. The destination README records
  what moved, when, why, from which commit, and the copy-integrity check.

  Gap: A20 is not yet registered for the F41 mechanism correction. The
  preregistration is FROZEN and currently states a mechanism we have measured to
  be wrong. That is the most important open documentation item in the project.

### 9. Process Issues

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good

- **Claude Code Development Team**:

  Three worth recording:

  - I hit the heredoc backslash-escape failure twice more this sprint (`\D` in a
    non-raw Python string). This is now the fifth-plus occurrence. The rule
    exists; the rule is not working. It needs to be mechanical, not remembered.
  - The 6.6 branch-source violation, now hook-enforced. The hook was written and
    verified against 8 block/allow cases plus 3 false-positive cases.
  - `git stash` was correctly blocked by the existing hook, which is evidence
    that hooks work where discipline does not.

### 10. Risk Management

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good

- **Claude Code Development Team**:

  The identified risks did not materialize; the ones that hurt were unidentified.
  The plan's risk table named F38 page cuts, F37 publication and deadline
  pressure. What actually consumed the sprint was two adversarial reviews finding
  correctness defects in evidence we had already shipped to QCi.

  "An external reviewer finds a defect in published evidence" was not on the risk
  register and should have been, given that the QCi letter went out on Sep 8.

### 11. Next Sprint Readiness

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good

- **Claude Code Development Team**:

  Sprint 11 carries more than any sprint so far: F37, F38, F41, F42, and F10,
  against a Sep 12 evidence freeze. Three of those are submission blockers and
  two (F41, F42) are Class 1/Class 2 requiring explicit approval before documents
  are touched.

  I flag plainly: this is the tightest the schedule has been, and F42's rerun
  items may not all fit before the freeze.

### 12. Architecture Maintenance

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good

- **Claude Code Development Team**:

  The results.json schema held; every reported figure regenerates. The gate
  report now matches its source, which it did not at sprint start.

  The protocol-integrity problem is F41: the frozen preregistration describes a
  mechanism (majority-class collapse) that the saved pools disprove (80-84 of 91
  learners classify every training row correctly, zero all-negative). Code and
  documents agree with each other and both disagree with the evidence. That is
  the exact failure the freeze exists to surface, and it took an outside reader
  to surface it.

### 13. Minor Function Updates for the Next Sprint Plan

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none

- **Claude Code Development Team**:

  - [DEV] Register A20 for the F41 mechanism correction -- target: Sprint 11 plan, est: 30m
  - [DEV] Add "external reviewer finds a defect in shipped evidence" to the plan risk template -- target: Sprint 11 plan, est: 10m

### 14. Function Updates for the Future Backlog

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none

- **Claude Code Development Team**:

  - [DEV] F44: Evidence-vs-document consistency tests -- assert every figure quoted in the papers resolves to a results.json value, so the next contradiction fails a test rather than waiting for a reviewer -- estimated: 3h, priority: 6, depends on: F41 and F42 landing first so the tests encode corrected values

### 15. Assigned Coding Agents Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good

- **Claude Code Development Team**:

  No subagents were assigned this sprint, so there is no delegated-output quality
  to assess. The two external reviews (GPT-6 Astra, Fable 5.1) were not our
  agents but their output quality is worth recording: both produced reproducible,
  specific, correctly-located findings, and both were right on every claim I
  could independently verify.

### 16. Questions to be discussed before ending the sprint

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none

- **Claude Code Development Team**:

  - F42's rerun items against the Sep 12 freeze: which are in scope and which are
    cut? I recommend the team lead decide rather than my inferring it.
  - Whether the QCi letter's now-known-incorrect mechanism statement warrants a
    follow-up, given card #40 is already held pending their reply.

## Improvement Decisions

Team lead, 2026-09-09: **"all improvements as recommended"**, plus a separate
direction that the IEEE-CIS AUC-ROC work becomes a backlog item targeted at
Sprint 11 rather than a rerun inside Sprint 10.

| # | Improvement | Disposition | Where it landed |
|---|---|---|---|
| 1 | Mechanical fix for the heredoc escape failure | **APPLY NOW** | `.claude/hooks/block-unraw-escape.ps1`, registered in settings.json |
| 2 | Evidence-vs-document consistency tests | **BACKLOG** | F44, master plan, Priority 6, after F41/F42 |
| 3 | Register A20 for the F41 mechanism correction | **SPRINT 11** | Card #59 (F41), first item of the Sprint 11 plan |
| 4 | Add "external reviewer finds a defect in shipped evidence" to the risk template | **SPRINT 11** | Sprint 11 plan risk table |
| 5 | Repeated instruction means my reading is wrong | **APPLY NOW** | SPRINT_EXECUTION_WORKFLOW.md invariant 5 |
| 6 | Pre-flight inventories code, not just documents | **APPLY NOW** | SPRINT_PLANNING.md capability pre-flight |

### Separate team-lead directions recorded with this retrospective

- **IEEE-CIS AUC-ROC (Fable finding F8)**: backlog item, target Sprint 11. Carded
  as F43 (#61). NOTE the card corrects an error in my own analysis: I first
  reported this as needing a full IEEE rerun, having checked summary-level keys
  instead of the per-fold rows. `run_ieee.py` already computes and stores
  `auc_roc` per fold, and `ieee_classical.json` holds it for all nine folds --
  LightGBM 0.9139, CatBoost 0.8941, XGBoost 0.8640. The classical half is
  reportable from stored evidence today. Only the CVQBoost and ladder arms lack
  the metric.
- **QCi correspondence**: no re-sending of letters or PDFs per change. If a
  further communication is sent, it will carry ALL deviations found against what
  was previously sent, as one list, at that time. Card #40 stays held; the F41
  mechanism correction joins the deviation list rather than triggering a letter.

### Hook 1, written the hard way

The escape hook took four attempts because every method of building its
PowerShell source through another language's string literal ate the backslashes
or turned them into control characters -- once corrupting the settings.json path
it was meant to write. That is precisely the failure the hook exists to catch,
reproduced three times while writing the thing that catches it. It is the
clearest possible argument that this needed to stop being a remembered rule.

Verified against 9 cases before wiring in: blocks both real Sprint 10 failures,
allows the raw-string fix, the forward-slash fix, legitimate newline and tab
escapes, raw regexes, doubled backslashes, and non-python commands.
