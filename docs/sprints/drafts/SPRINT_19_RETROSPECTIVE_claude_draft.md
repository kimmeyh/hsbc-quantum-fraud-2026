# Sprint 19 Retrospective: Claude Code Development Team draft

Written 2026-09-27, step 2 of the 7-step protocol. The team lead scored all
sixteen categories **Very Good**. Where I score lower, both are recorded and
the improvements are built from the lower score.

The sprint's objective was met: **the package was sent on 2026-09-25 at
12:23 PM**. Everything below is about how it got there.

### 1. Effective while as Efficient as Reasonably Possible

**Good.** The objective was met and the approved 105-minute scope was the
right cut: Task C was declined and became F96 rather than expanding the
sprint. Task D's fresh-context review was the highest-value 20 minutes in the
sprint, returning fourteen findings against a plan that predicted few.

The inefficiency is real and worth naming: **Task B built thirteen guards that
were retired within about 24 hours.** Every one caught a stale claim during a
revision round, so they were not waste in the moment. But the plan did not
anticipate that the memo would become a frozen artifact inside the same
sprint, and a card that had asked "is this document about to be frozen?" would
have scoped Task B differently. See category 4.

### 2. Testing Approach

**Very Good.** Every Task B guard was proven RED against the old text with the
F89 injection helper before being accepted, which is the standard this
repository has failed three times before. The same discipline caught a defect
in my own later work: `test_the_qci_package_is_clean` filtered its document
list through `exists()`, so deleting the memo would have narrowed the scan
from three documents to two and still passed. That is the
"could-not-check-reads-as-clean" class, found and fixed with a red-leg proof.

### 3. Effort Accuracy

**Needs Improvement.** Two problems.

**Task D's actual is NOT RECORDED**, for the reason in `sprint_status.json`:
it spanned an approval stop of several hours, so wall clock does not measure
the work. IMP-1 shipped last sprint to make actuals a completion-time habit,
and on its first real use it captured two of three tasks. The rule needs a
form for "this task contained a wait" rather than falling back to null.

**Post-validation work was substantial and unestimated**: the validation
document, the guard retirement, the HTML converter, and several rounds of BLUF
compression and fact-checking on the memo text. None was in the 105 minutes.
That is not scope creep -- it was all requested -- but the sprint's recorded
effort understates what the sprint cost.

### 4. Planning Quality

**Good.** The plan's structure was sound: dependencies stated (B follows A, D
follows A and C), the total derived from the cards rather than typed in, and
the premise falsifier that fired.

The miss: **the plan treated the memo as an editable document for its whole
life.** Task B's guards, the readability check's document list, and the
cross-document tests were all built on that assumption, and the memo was sent
three days later. A single planning question -- "which of these documents will
be frozen before the next sprint?" -- would have changed Task B's scope and
saved the retirement work.

### 5. Model Assignments

**Very Good.** The fresh-context reviewer for Task D was the right call and
produced the sprint's most valuable output. Consulting the advisor before
committing to the Phase 6/7 approach caught two things I would have gotten
wrong: I was about to restate suite counts in a committed document, and I had
not verified the sent PDF's contents before writing them up.

### 6. Communication

**Good.** The PR body and commit messages record what happened, including the
things that went wrong. Two failures:

**I referred the team lead back to earlier scrollback.** Asked for the BLUF
compressions, I answered "Answered above in three lengths" -- exactly the
behavior CLAUDE.md bans, in the session where I had just written a validation
document to a file specifically to avoid it. He had to ask twice.

**The schedule-4 inconsistency went out unresolved.** I flagged that the memo
commits to a ~60 s schedule-4 check and the hardware plan does not mention it,
offered to fix the plan, and the conversation moved to deleting the memo. The
email then went out with that plan attached. Verified after the fact with
`pypdf`: the sent PDF contains 1,681, 7,319, 7,500 and 9,000, and does not
contain "schedule 4". An open question I raised and did not carry to closure
before the irreversible action.

### 7. Assigned Coding Agents Quality

**Very Good.** The Task D reviewer had no sprint context and found fourteen
disagreements, each verified against the documents and `results.json` before
it reached the team lead. No false findings required rework.

### 8. Requirements Clarity

**Good.** The six memo passages were drafted and approved during planning,
which is why Task A took two minutes. Two ambiguities I handled by asking
rather than assuming: whether "OK on your 1. and 2." approved an observation
or selected an option, and whether the `_files` folder or the `.htm` was the
sent document. Both were worth the question.

One I got wrong: I asserted the schedule retest needed its own bullet on cost
grounds, estimating 96 metered fits and ~2,000 seconds. The team lead asked
why, and the master plan already scoped it as F95 at four fits and ~60
seconds. I had not searched the backlog before estimating. Correcting in
public was right; not searching first was not.

### 9. Documentation

**Good.** The three-doc rule is intact and the validation document now exists
as a file. But that document was **stale within two days of being written** in
three ways: it pointed at a deleted file, it restated the suite count (which
CLAUDE.md bans outright), and it described the memo as a draft after it had
been sent. I wrote a durable handover and then let it rot, in the same sprint.

### 10. Process Issues

**Good.** Three worth recording:

- **A hand-rolled PDF extractor produced a confident wrong answer.** My zlib
  stream-parse reported "9,000 ABSENT" from a document whose headline is the
  9,000-second ask. Only checking against `pypdf` -- the method the repo
  already uses -- exposed it. A broken tool reporting ABSENT reads exactly
  like a real finding.
- **A regex escape was eaten by the shell again** (the F82 class), in a
  one-liner checking the PDF. Fixed by writing to a file.
- **My AST-based guard retirement missed a decorator.** Scanning function
  bodies for `MEMO` found thirteen tests but not the `parametrize` list, so
  collection failed with `NameError`. Caught by running the suite.

### 11. Risk Management

**Very Good.** The irreversible actions were handled correctly. I refused to
delete the memo draft myself and said so. I did not edit
`HARDWARE_PLAN_PHASE_2.md` after its PDF was sent, because that would create
the version problem the AS SENT convention exists to prevent, and flagged the
freeze question as the team lead's decision rather than making it. Zero
metered seconds spent.

### 12. Next Sprint Readiness

**Very Good.** The backlog is clear and the dependencies resolved:

- **F95 is now unblocked** -- it was held until the memo was sent. Four fits
  at schedule 4, ~60 s, against the 1,681 balance.
- **F96** holds Task C (the hardware plan's Experiment 1 sentence and the
  package re-render), now complicated by the plan having been sent.
- **F90** is the schedule-3 decision at 833 variables, ~1,236 s, which would
  spend 74% of the remaining balance and needs its own approval.
- The schedule-4 documentation gap is a new item.

### 13. Architecture Maintenance

**Very Good.** `scripts/outlook_htm_to_md.py` is a reusable tool rather than a
throwaway, verified byte-identical to the hand conversion and verified to fail
closed when a named figure does not survive. The AS SENT naming convention now
has a second instance, which makes it a pattern rather than a one-off.

### 14. Minor function updates for the next sprint plan

The schedule-4 gap between the memo and the hardware plan needs a disposition:
either the plan gets the line and is re-rendered (inside F96), or the
inconsistency is accepted and recorded as known.

### 15. Function updates for the backlog

None beyond the F95/F96/F90 items already registered.

### 16. Questions before ending the sprint

One, and it blocks nothing: **is `HARDWARE_PLAN_PHASE_2.md` now frozen like
the memo?** Its PDF was sent on 2026-09-25. If it is frozen, F96's Task C work
needs a new file rather than an edit, and its guards should be retired the way
the memo's were. If it is not, the next edit silently diverges from what QCi
holds.
