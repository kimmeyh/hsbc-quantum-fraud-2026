# Sprint 14 Retrospective

Conducted 2026-09-14 after Manual Validation and before the PR was marked
ready. The team lead's feedback is recorded VERBATIM as given; Claude's lines
come from `drafts/SPRINT_14_RETROSPECTIVE_claude_draft.md`, written in parallel
per protocol step 2 and before the team lead's arrived.

## Sprint 14 Retrospective Feedback

### 1. Effective while as Efficient as Reasonably Possible

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Ten tasks, 27 commits, suite 321 -> 329, and every task found something its card
did not anticipate. The efficiency question is really about the ADR
conversation, which ran well past F39 and F72's carded scope. That work was
valuable and I should have flagged the drift earlier rather than at the point
where a hook stopped me.

### 2. Testing Approach

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Three new guard files, each injection-verified. The one worth recording is
`test_changelog_currency.py`, which **passed on the exact lapse it was written
for**: I set 14 days, the real gap was 8, and only running the injection
revealed it. That is the vacuous-guard failure the standard exists to catch,
caught by the standard. The metachar hook also took three iterations, each
correction driven by a false positive against my own commands.

### 3. Effort Accuracy

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Tasks A-J estimated ~17.5h plus the 30% findings allowance from Sprint 13's
improvement 2. The allowance was the right call: F68 grew from "fix two hooks"
to a new hook plus a test class, and F69 found two defects that needed fixing
before the README could be written honestly. What was NOT estimated is the ADR
conversation, which is now the larger part of the sprint's output.

### 4. Planning Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The pre-flight was the highest-value planning artifact for the second sprint
running. It found both dead hooks before any work started, which reordered the
sprint correctly. What the plan did not anticipate: that a design task (F39)
would turn into an extended design conversation with four rounds of team-lead
correction. That is not a planning defect so much as a category the plan had no
shape for.

### 5. Model Assignments

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Three subagents, all read-and-report, all stayed inside their boundary. The
changelog-material agent and the acronym-inventory agent both returned
corrections to my assumptions rather than confirmations, which is the behaviour
worth having. The inventory agent's finding that seven acronyms I "knew" were in
scope are absent from the submission was a direct correction I would not have
caught alone.

### 6. Communication

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Better than Sprint 13 on the specific failure, worse on a new one. The Class 4
presentation discipline held -- I stated plainly when something was a fix I
wanted approved. The new failure: on "add a sentence to proposal.md" I gave a
three-option table when the answer was one line, and the team lead said so
directly. I over-explained a settled question.

### 7. Requirements Clarity

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Scope was clear and the team lead's corrections were specific and early. Four of
them changed the design materially -- agent economics, context collapse,
assertions-as-unit, early-innovation status -- and each arrived before I had
built far on the wrong assumption.

### 8. Documentation

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Two ADRs, two research documents, a rebuilt README, a backfilled CHANGELOG and a
three-way checklist split. The research documents are the ones I would defend
hardest: both record what I could NOT establish alongside what I could, and both
carry corrections to my own prior beliefs at the top rather than buried.

### 9. Process Issues

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The close-out hook fired correctly on a real contradiction I had missed --
`pr: null` against an open PR #94. Walking the checklist by hand then found the
larger item the hook could not see: no retrospective existed at all. Two
mechanical checks catching what I did not.

### 10. Risk Management

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The identified risks did not fire. An unidentified one did: a dry run overwrote
the committed b3_hardware.json during F65 verification, and my "artifact
untouched" check had run BEFORE the background job finished. A mistimed
verification reads exactly like a passing one, which is the more general lesson.

### 11. Next Sprint Readiness

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The submission is filed, the repository is durable, and the backlog is clear.
The team lead's request for an 8th-grade explanatory document is well-specified
and connects directly to the reading-level algorithm already in ADR-0014, which
means it is not a new mechanism, only a new application of one.

### 12. Architecture Maintenance

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Seven hooks now registered and verified resolvable, where two had never run.
`test_hook_registration.py` covers the class rather than the instances. The
CLAUDE.md overstatement about `store.py` enforcing schema at write time was
corrected in Sprint 13 and holds.

### 13. Minor Function Updates for the Next Sprint Plan

- **Product Owner**: Need a detailed write-up in the `D:\Data\Harold\hsbc-quantum-fraud-2026` directory related to the submitted on 9/12/26 proposal and appendix documents

  - Disclaimer that it is a good and reasonably accurate document, but no guarantee of 100% accuracy or expectation that the reader will fully understand upon reading
  - It should be written as if a learning document for an 8th grader (individual or 3 people working together)
  - Explain everything at an 8th grade level (math, science, English language) whenever possible. When not possible, re-write at the next higher grade level until it can be achieved (same algorithm as other parts of the repository)
  - Like we were writing a paper (topics, sub-topics, references to outside sources...)
  - identify items that would be difficult to a reader would need to know more (ex. the datasets: what are they, how are they gathered, what do they represent, why would we use them, how does it match to real business situations, what are the key features and why, how does Machine Learning predict results with the dataset) - not sure, we will need to figure this out.
    - Are there any references that we can use from the internet to better explain the datasets (can we copy and use official references or do we need to reference)
- **Scrum Master**: Need a detailed write-up in the `D:\Data\Harold\hsbc-quantum-fraud-2026` directory related to the submitted on 9/12/26 proposal and appendix documents

  - Disclaimer that it is a good and reasonably accurate document, but no guarantee of 100% accuracy or expectation that the reader will fully understand upon reading
  - It should be written as if a learning document for an 8th grader (individual or 3 people working together)
  - Explain everything at an 8th grade level (math, science, English language) whenever possible. When not possible, re-write at the next higher grade level until it can be achieved (same algorithm as other parts of the repository)
  - Like we were writing a paper (topics, sub-topics, references to outside sources...)
  - identify items that would be difficult to a reader would need to know more (ex. the datasets: what are they, how are they gathered, what do they represent, why would we use them, how does it match to real business situations, what are the key features and why, how does Machine Learning predict results with the dataset) - not sure, we will need to figure this out.
    - Are there any references that we can use from the internet to better explain the datasets (can we copy and use official references or do we need to reference)
- **Lead Developer**: Need a detailed write-up in the `D:\Data\Harold\hsbc-quantum-fraud-2026` directory related to the submitted on 9/12/26 proposal and appendix documents

  - Disclaimer that it is a good and reasonably accurate document, but no guarantee of 100% accuracy or expectation that the reader will fully understand upon reading
  - It should be written as if a learning document for an 8th grader (individual or 3 people working together)
  - Explain everything at an 8th grade level (math, science, English language) whenever possible. When not possible, re-write at the next higher grade level until it can be achieved (same algorithm as other parts of the repository)
  - Like we were writing a paper (topics, sub-topics, references to outside sources...)
  - identify items that would be difficult to a reader would need to know more (ex. the datasets: what are they, how are they gathered, what do they represent, why would we use them, how does it match to real business situations, what are the key features and why, how does Machine Learning predict results with the dataset) - not sure, we will need to figure this out.
    - Are there any references that we can use from the internet to better explain the datasets (can we copy and use official references or do we need to reference)
- **Claude Code Development Team**: - [DEV] The `applicability` collapse (ADR-0015 2d) should be checked against
  ADR-0014's context list when the DB is first built, since the two documents
  now share a vocabulary and nothing enforces it -- estimated: 15m, priority: 5
- [DEV] `docs/research/` is new and unindexed; add it to the README's key
  documents table -- estimated: 10m, priority: 6

### 14. Function Updates for the Future Backlog

- **Product Owner**: Suggest an outline

  - Challenge
  - start with the problem from the 3 challenge documents and the challenge for participants - as written
    - Each dataset used
    - How ML is done against each dataset
    - ...
- **Scrum Master**: Suggest an outline

  - Challenge
  - start with the problem from the 3 challenge documents and the challenge for participants - as written
    - Each dataset used
    - How ML is done against each dataset
    - ...
- **Lead Developer**: Suggest an outline

  - Challenge
  - start with the problem from the 3 challenge documents and the challenge for participants - as written
    - Each dataset used
    - How ML is done against each dataset
    - ...
- **Claude Code Development Team**: - [DEV] A guard that the ADR context list and the record schemas do not drift
  once EvidenceBasedDB exists. Cross-repository, so it needs the other
  repository first -- estimated: 1h, priority: 7, depends on: the DB existing
- [DEV] The 20-paper checkpoint in both ADRs needs a card when it comes due, or
  it will be a note nobody actions -- estimated: 2h, priority: 6, depends on:
  ~20 papers imported

### 15. Assigned Coding Agents Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: High and consistent. All three agents distinguished verified from inferred
without being asked twice, and two returned corrections rather than
confirmations. The changelog agent flagged a timezone discrepancy between PR
merge times and sprint documents rather than silently picking one, and flagged
two commits it could not confidently characterise rather than inventing entries.

### 16. Questions to be discussed before ending the sprint

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: None blocking. The open items are decisions rather than questions: whether
ADR-0015 is ready to accept, and the scope of the explanatory document.
## Improvement Decisions

Team lead disposition, 2026-09-14: **"all as recommended"**.

| # | Improvement | Source | Type | Disposition |
|---|---|---|---|---|
| 1 | Card the 8th-grade explanatory document, with a falsifier | PO/SM/LD cat. 13 | deliverable | **Applied** -- F73 registered, next sprint |
| 2 | Fold the outline into F73 rather than carding it separately | PO/SM/LD cat. 14 | planning | **Applied** -- F74 recorded as folded, struck as independent |
| 3 | Resolve dataset-reference licensing before drafting | PO/SM/LD cat. 13 question | research | **Applied now** -- `docs/research/dataset-reference-licensing.md` |
| 4 | Add `docs/research/` to the README key-documents table | Claude cat. 13 | docs | **Applied** -- README |
| 5 | Card the 20-paper ADR checkpoint so it is actioned | Claude cat. 14 | process | **Applied as backlog** -- F75 |
| 6 | Guard the shared vocabulary between ADR-0014 and ADR-0015 | Claude cat. 13 | tech debt | **Applied as backlog** -- F76 |

### The licensing answer, since it shapes F73

The team lead's open question was whether official dataset descriptions can be
copied or must be cited. **Answer: it varies, so write everything in our own
words.**

- **ULB creditcard** is Database Contents License v1.0, which grants a
  royalty-free irrevocable licence including sublicensing, explicitly permits
  commercial use, and specifies no attribution requirement. **We may copy it.**
  We will attribute anyway -- an explanatory document that hid its sources would
  contradict the posture of the project it explains.
- **IEEE-CIS** is Vesta Corporation's real-world e-commerce data under Kaggle
  competition rules, which are behind acceptance and were not retrievable
  anonymously. **Treat as cite-never-copy.** The burden of proof runs the wrong
  way: we would be asserting an unverified right, publicly, over another
  company's commercial data.
- **SPECTRA** unverified; treat as restrictive until checked.

One reuse right out of three is not worth the inconsistency, so F73 paraphrases
uniformly and records each dataset's licence beside it -- a reader learning
about datasets should learn that datasets have licences.

## Transition note

Sprint 14 delivered F68 through F72 plus the four carried tooling cards, and the
Evidence Based DB design conversation that followed them. **The summary document
is written during Sprint 15 planning** per workflow 3.2.1.

ADR-0014 is ACCEPTED with early-innovation status; **ADR-0015 remains Proposed**
and is the team lead's call.
