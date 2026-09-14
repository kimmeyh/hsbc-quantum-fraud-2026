# Sprint 14 Retrospective: Claude Development Team draft

Drafted per protocol step 2, in parallel with the team lead's feedback.

### 1. Effective while as Efficient as Reasonably Possible
Ten tasks, 27 commits, suite 321 -> 329, and every task found something its card
did not anticipate. The efficiency question is really about the ADR
conversation, which ran well past F39 and F72's carded scope. That work was
valuable and I should have flagged the drift earlier rather than at the point
where a hook stopped me.

### 2. Testing Approach
Three new guard files, each injection-verified. The one worth recording is
`test_changelog_currency.py`, which **passed on the exact lapse it was written
for**: I set 14 days, the real gap was 8, and only running the injection
revealed it. That is the vacuous-guard failure the standard exists to catch,
caught by the standard. The metachar hook also took three iterations, each
correction driven by a false positive against my own commands.

### 3. Effort Accuracy
Tasks A-J estimated ~17.5h plus the 30% findings allowance from Sprint 13's
improvement 2. The allowance was the right call: F68 grew from "fix two hooks"
to a new hook plus a test class, and F69 found two defects that needed fixing
before the README could be written honestly. What was NOT estimated is the ADR
conversation, which is now the larger part of the sprint's output.

### 4. Planning Quality
The pre-flight was the highest-value planning artifact for the second sprint
running. It found both dead hooks before any work started, which reordered the
sprint correctly. What the plan did not anticipate: that a design task (F39)
would turn into an extended design conversation with four rounds of team-lead
correction. That is not a planning defect so much as a category the plan had no
shape for.

### 5. Model Assignments
Three subagents, all read-and-report, all stayed inside their boundary. The
changelog-material agent and the acronym-inventory agent both returned
corrections to my assumptions rather than confirmations, which is the behaviour
worth having. The inventory agent's finding that seven acronyms I "knew" were in
scope are absent from the submission was a direct correction I would not have
caught alone.

### 6. Communication
Better than Sprint 13 on the specific failure, worse on a new one. The Class 4
presentation discipline held -- I stated plainly when something was a fix I
wanted approved. The new failure: on "add a sentence to proposal.md" I gave a
three-option table when the answer was one line, and the team lead said so
directly. I over-explained a settled question.

### 7. Requirements Clarity
Scope was clear and the team lead's corrections were specific and early. Four of
them changed the design materially -- agent economics, context collapse,
assertions-as-unit, early-innovation status -- and each arrived before I had
built far on the wrong assumption.

### 8. Documentation
Two ADRs, two research documents, a rebuilt README, a backfilled CHANGELOG and a
three-way checklist split. The research documents are the ones I would defend
hardest: both record what I could NOT establish alongside what I could, and both
carry corrections to my own prior beliefs at the top rather than buried.

### 9. Process Issues
The close-out hook fired correctly on a real contradiction I had missed --
`pr: null` against an open PR #94. Walking the checklist by hand then found the
larger item the hook could not see: no retrospective existed at all. Two
mechanical checks catching what I did not.

### 10. Risk Management
The identified risks did not fire. An unidentified one did: a dry run overwrote
the committed b3_hardware.json during F65 verification, and my "artifact
untouched" check had run BEFORE the background job finished. A mistimed
verification reads exactly like a passing one, which is the more general lesson.

### 11. Next Sprint Readiness
The submission is filed, the repository is durable, and the backlog is clear.
The team lead's request for an 8th-grade explanatory document is well-specified
and connects directly to the reading-level algorithm already in ADR-0014, which
means it is not a new mechanism, only a new application of one.

### 12. Architecture Maintenance
Seven hooks now registered and verified resolvable, where two had never run.
`test_hook_registration.py` covers the class rather than the instances. The
CLAUDE.md overstatement about `store.py` enforcing schema at write time was
corrected in Sprint 13 and holds.

### 13. Minor Function Updates for the Next Sprint Plan
- [DEV] The `applicability` collapse (ADR-0015 2d) should be checked against
  ADR-0014's context list when the DB is first built, since the two documents
  now share a vocabulary and nothing enforces it -- estimated: 15m, priority: 5
- [DEV] `docs/research/` is new and unindexed; add it to the README's key
  documents table -- estimated: 10m, priority: 6

### 14. Function Updates for the Future Backlog
- [DEV] A guard that the ADR context list and the record schemas do not drift
  once EvidenceBasedDB exists. Cross-repository, so it needs the other
  repository first -- estimated: 1h, priority: 7, depends on: the DB existing
- [DEV] The 20-paper checkpoint in both ADRs needs a card when it comes due, or
  it will be a note nobody actions -- estimated: 2h, priority: 6, depends on:
  ~20 papers imported

### 15. Assigned Coding Agents Quality
High and consistent. All three agents distinguished verified from inferred
without being asked twice, and two returned corrections rather than
confirmations. The changelog agent flagged a timezone discrepancy between PR
merge times and sprint documents rather than silently picking one, and flagged
two commits it could not confidently characterise rather than inventing entries.

### 16. Questions to be discussed before ending the sprint
None blocking. The open items are decisions rather than questions: whether
ADR-0015 is ready to accept, and the scope of the explanatory document.
