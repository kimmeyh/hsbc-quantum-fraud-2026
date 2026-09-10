# Sprint 11 Retrospective

Sprint 11: Correctness Before Compression. Conducted 2026-09-09 after Phase 5
manual validation, before `gh pr ready`.

Team-lead feedback recorded VERBATIM. Claude's lines come from
`docs/sprints/drafts/SPRINT_11_RETROSPECTIVE_claude_draft.md`.

## Sprint 11 Retrospective Feedback

### 1. Effective while as Efficient as Reasonably Possible

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good

- **Claude Code Development Team**:

  Seven planned tasks plus two added mid-sprint, all delivered except the one that
  is the team lead's to perform. 15 commits, 3,391 insertions, one approved
  metered call.

  The efficiency came from a specific discipline: every task's premise was checked
  before building on it. The F47 spike found the seam already existed in
  `process_job`, which made the build smaller than planned. The F43 pre-flight
  found the AUC-ROC already stored, turning a "full IEEE rerun" into minutes of
  reporting.

  Against that: I re-did the +0.0319 decomposition entirely because the first
  version decomposed the wrong arm against the wrong comparator. That was
  avoidable by reading `tuned_pool.json`'s `summary.configuration` first.

### 2. Testing Approach

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good

- **Claude Code Development Team**:

  The strongest sprint yet on this axis and still the weakest area. 201 -> 279
  tests, nine new files, and each new guard was verified by INJECTING the defect
  it targets rather than assumed to work.

  Three of my own assumptions were overturned by tests I had just written: the
  enum import path, contiguous ObjectId counters, and fixed timestamps. All three
  were checkable against data already in the repository.

  The uncomfortable finding: my F44 test passed locally and failed in CI because
  it scanned untracked files. It was passing for the wrong reason, which is worse
  than failing. A guard that is trusted and weak is a liability.

### 3. Effort Accuracy

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good

- **Claude Code Development Team**:

  Estimated 11h50m across nine tasks. The two items the cards called expensive
  were measured cheap before committing (lambda=0 sweep seconds not minutes, the
  decomposition 8 minutes not "a few CPU hours"), and both held.

  The miss was the ceiling probe: approved at "0-5 seconds", cost 10. Two causes,
  both mine -- the response no longer carries `device_usage_s` on the paid tier,
  and I quoted an estimate from free-tier anchors without saying it was an
  extrapolation. Criterion H approval is worth less when the number attached to it
  is soft.

### 4. Planning Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good

- **Claude Code Development Team**:

  Premise falsifiers earned their place. F41's ran first and did not fire, which
  licensed A20. F47's did not fire either, and finding that out cost 15 minutes
  and saved a wrapper we did not need.

  The overlap audit was the sprint's best planning artifact: checking each task
  against the repository rather than its card found that F42's card would have
  split across two sprints, and that "depth-limited" appeared in 10 places rather
  than 4.

  Weakness: the plan did not anticipate that new evidence would move the page
  budget. F38 is now further from fitting than when the sprint started.

### 5. Model Assignments

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good

- **Claude Code Development Team**:

  All Opus in the main loop. Correct for a sprint that touched the frozen
  preregistration twice and changed published claims. No subagents; nothing here
  parallelised cleanly and the work needed continuity.

### 6. Communication

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good

- **Claude Code Development Team**:

  Commit messages carried the reasoning including what went wrong, and the
  validation package led with plain language rather than waiting to be asked.

  Where I fell short: I twice presented a conclusion before verifying it. "The
  local pool build is the bottleneck" was wrong -- it was queue wait, and the team
  lead corrected it. "Device metrics are not the billing basis" was about to be
  written up when the team lead suggested the variant that works. Both times the
  data to check was already in hand.

### 7. Requirements Clarity

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good

- **Claude Code Development Team**:

  Clear throughout. The one genuine ambiguity -- a document for a different
  repository -- I asked about rather than acting on, and the answer was that it
  should go nowhere near either repo.

  The "is there a benefit to being an entity" question was answered from the
  source documents rather than intuition, which is the right instinct for anything
  touching eligibility.

### 8. Documentation

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good

- **Claude Code Development Team**:

  A20 and A21 registered with their evidence and their scope limits. The
  validation package records the four things I got wrong and how each was caught,
  which is more useful to a future reader than a clean narrative would be.

  Gap: `run_hardware.py` still scrapes `device_usage_s` from a repr. It works on
  the free tier and silently defaults on the paid tier. It is now documented as
  unreliable but not yet fixed.

### 9. Process Issues

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good

- **Claude Code Development Team**:

  - The escape hook fired correctly several times this sprint, and I still hit
    bash backtick expansion in a Python string, which mangled a master-plan line.
    The hook covers Python escapes, not shell metacharacters.
  - Three tool results were lost to timeouts mid-command, once leaving a commit
    unexecuted that I only noticed by checking `git log`.
  - The F46 probe wrote no job id, making "was the approved call spent?"
    answerable only from the allocation balance. That is now fixed by F47.

### 10. Risk Management

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good

- **Claude Code Development Team**:

  The named risks behaved. The unnamed one that bit was estimate softness on a
  metered call, which is a Criterion H integrity issue rather than a cost issue --
  10 seconds of 3,000 is nothing, but an approval given against a wrong number is
  worth less than it appears.

  New risk now visible: every correctness fix adds text, and F38 must remove
  229pt from the appendix. Correctness and page budget pull against each other,
  and the sprint made that worse before it makes it better.

### 11. Next Sprint Readiness

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good

- **Claude Code Development Team**:

  Sprint 12 carries F37, F38, F10, the fresh-eyes review and any approved Dirac-3
  work against a Sep 12 freeze. That is the heaviest sprint of the project against
  the least calendar, and two of those items are irreversible or near-irreversible.

  I flag plainly: if Dirac-3 work is wanted, it should run in the evening window
  early in the sprint, not late.

### 12. Architecture Maintenance

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good

- **Claude Code Development Team**:

  The frozen preregistration gained two amendments, both correction-class, neither
  changing a gate or a reported figure. No analysis-path code changed this sprint,
  verified against the branch point rather than asserted.

  The results schema held. The gate report regenerates with no diff. A21 records
  that the ceiling constraint which shaped the campaign was a billing tier, which
  is a protocol-relevant fact even though it changes no existing number.

### 13. Minor Function Updates for the Next Sprint Plan

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good

- **Claude Code Development Team**:

  - [DEV] Replace the `device_usage_s` repr scrape in `run_hardware.py` with
    `metered_call`/`qpu_cost_model` -- target: Sprint 12 plan, est: 30m
  - [DEV] Re-run `page-fill-report.py` before F38 starts; the 229pt figure predates
    this sprint's additions -- target: Sprint 12 plan, est: 5m

### 14. Function Updates for the Future Backlog

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none

- **Claude Code Development Team**:

  - [DEV] F48: extend the escape hook to shell metacharacters (backticks, `$(...)`)
    inside quoted strings passed to Bash -- estimated: 45m, priority: 9, depends
    on: nothing

### 15. Assigned Coding Agents Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good

- **Claude Code Development Team**:

  No subagents assigned. The two external reviews from earlier sprints continued
  to pay: every F42 finding traced to them, and each one I could verify was
  correct.

### 16. Questions to be discussed before ending the sprint

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none

- **Claude Code Development Team**:

  - Sprint 12 sequencing: F37 is irreversible and F38 depends on final content. If
    Dirac-3 work lands new evidence, F38 must follow it and F37 should follow both.
    Worth deciding the order before the sprint rather than during it.

## Improvement Decisions

Team lead, 2026-09-09: **"now: 1, 2, 3, 5. backlog 4"**.

| # | Improvement | Disposition | Where it landed |
|---|---|---|---|
| 1 | Retire the `device_usage_s` repr scrape | **APPLIED** | `run_hardware.py` returns None rather than defaulting; unused `import re` removed |
| 2 | Criterion H requests state estimate provenance | **APPLIED** | `SPRINT_STOPPING_CRITERIA.md`, Criterion H |
| 3 | Re-measure page fill before F38 cuts | **APPLIED** | F38 card, as its first action |
| 4 | Escape hook covers shell metacharacters | **BACKLOG** | F48, master plan, Priority 9 |
| 5 | Decide Sprint 12 sequencing now | **APPLIED** | Master plan, under the Finalize row |

### On improvement 1

The scrape is gone but `UNPARSEABLE_CALL_CHARGE_S = 10.0` STAYS. It is a
deliberate conservative charge for an unreadable bill, and the F46 probe cost
exactly 10 seconds -- so the default over-charges rather than under-records,
which is the right direction for a spend guard. `_metered` now returns None when
it cannot establish a cost, and the caller applies that charge knowingly instead
of recording a scraped figure that silently became a default.

### On improvement 5

The Sprint 12 order is forced by dependencies rather than preference: Dirac-3
work (if approved) produces evidence, evidence changes documents, F38 must cut
against final content, and F37 is irreversible so nothing that could still
change a document may follow it. F10 depends on all three.

If the calendar forces a cut, the Dirac-3 work goes: it is the only one of the
four that is not a submission blocker.
