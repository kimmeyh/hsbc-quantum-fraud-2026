# Outline: the submission, explained

Task A of Sprint 15 (F73, GitHub issue #101). F74 was folded into F73, so this
outline is part of that card rather than a separate one.

**Acceptance criterion for this file**: every heading names what a reader LEARNS
there, not what topic it covers. "Class imbalance" is a topic. "Why counting
right answers makes a useless fraud detector" is what the reader learns.

## Ordering, and why it is not the submission's order

The team lead's suggested spine: the challenge as written, then each dataset,
then how ML is done against each, then what we did and found.

The submitted proposal opens with problem framing and reaches the quantum device
in section 2. This document reaches it in section 5 of 7. **The quantum part
comes last on purpose.** A reader who meets Dirac-3 before understanding why
fraud detection is hard will file the whole document under "quantum computing",
which is the wrong shelf. The finding is about measurement discipline, and the
quantum device is the thing that got measured.

One consequence worth stating: a reader who stops after section 4 still learns
something true and useful. That is the test of whether the ordering is right.

---

## 1. Why banks cannot simply catch fraud

**Learns**: that fraud detection is a decision under two constraints, not a
puzzle with a right answer.

- Someone steals a card number. The bank has seconds to decide.
- Two ways to be wrong, and they cost differently: a miss becomes a chargeback,
  a false alarm loses a customer who was buying a sandwich.
- Humans can only review so many flagged transactions a day. That budget is
  fixed, and it is small.
- **The idea that unlocks the rest**: the question is never "is this fraud?" It
  is "of everything I could send to a human today, which few are worth it?"

## 2. Why counting right answers makes a useless fraud detector

**Learns**: why accuracy is the wrong measure, by working the count.

- In the ULB data, about 17 transactions in every 10,000 are fraud.
  (0.17%. Checked: 0.17% of 1,000 is 1.7, so the honest example uses 10,000.)
- A detector that says "never fraud" is right 9,983 times out of 10,000. It is
  99.83% accurate and completely worthless.
- So accuracy gets thrown out. What replaces it: of the transactions we flagged,
  how many were really fraud, and of the real frauds, how many did we catch?
- **Ties back to section 1**: the measure has to match the decision. The decision
  is a ranked list under a budget, so the measure is about the top of the list.

## 3. Where the data comes from, and what each set can and cannot tell you

*(Two datasets, not three. See the SPECTRA correction below.)*

**Learns**: that a dataset is a set of choices someone made, not a neutral window
onto the world.

- **ULB**: 284,807 real European card transactions over two days. Most columns
  are outputs of a transformation that hides what they originally meant, for
  privacy. License: DbCL v1.0, may be copied.
- **IEEE-CIS**: 590,540 transactions from Vesta Corporation, a payments company,
  released for a competition. Fraud rate 3.5%, twenty times ULB's. License:
  competition data, paraphrase and cite, never copy.
- **SPECTRA is NOT in this section.** Corrected 2026-09-16 while writing Task C:
  `grep` finds SPECTRA zero times in the submitted proposal and appendix. It is
  four datasets about steel plants, gas turbines, maintenance and telecom churn
  (`docs/references.md`), used as prior art for the complete-classical-bar
  argument, not as fraud data. This document explains the submission, and the
  submission used TWO datasets. Listing three would have taught a reader
  something false.
  - Separately, the licensing pre-flight lists SPECTRA as "unverified" while
    `docs/references.md` records CC BY 4.0. The pre-flight is stale on this
    point. It changes nothing here, since the dataset is out of scope.
- **The two-day problem**: ULB spans two days. You cannot learn how fraud changes
  over months from two days, which is why the second dataset exists.
- **What this section must not do**: present the datasets as interchangeable
  sources of "transactions". Their differences are load-bearing later.

## 4. How a machine learns to rank transactions, and the one mistake that fakes success

**Learns**: how training works, and why testing on data you trained on is
cheating. This is the most load-bearing section in the document.

- A feature is a fact about a transaction: amount, hour, how far from the last
  purchase.
- Training: show the machine many past transactions with the answer attached.
  It looks for patterns that separate the two groups.
- Testing: hide the answers on transactions it has never seen and score it.
- **The cheat**: test on the same rows you trained on and the score is
  meaningless. The machine memorized rather than learned.
- **The subtler cheat, and the one that matters here**: split your data at
  random when it is ordered in time, and the machine gets to see Thursday while
  predicting Wednesday. Fraud patterns change week to week, so this flatters the
  result. Splitting by time instead is harder and honest.
- **Ties forward**: this is why one number in our own results fell from 0.7671 to
  0.7095 when tested honestly by time.

## 5. What the quantum machine actually does, and what we compared it against

**Learns**: what was compared with what, which is the whole experiment.

- Dirac-3 is not a gate-based quantum computer. It is a photonic machine that
  uses light and feedback to search for the low point of a mathematical
  landscape. We claim no quantum resource, and the proposal says so.
- CVQBoost: build many simple voters, each looking at one or a few features.
  Each votes guilty or innocent. Then choose how much each vote counts.
- Choosing the weights is the math problem. Dirac-3 solves it with light.
- **The control that makes it an experiment**: an ordinary computer solves the
  identical problem exactly, and can prove its answer is the best possible one.
- **So the question is answerable**: not "is quantum good?" but "does this
  device's answer beat an answer already proven optimal?"

## 6. What we found, and why "it did not help" is a real result

**Learns**: what a null result is and why publishing one is useful.

- The headline: CVQBoost on the quantum device scored 0.7671. A well-tuned
  ordinary model on the same features scored 0.8070. The quantum arm trailed, on
  9 of 10 attempts.
- **Why, measured rather than argued**: the voters were nearly identical to each
  other. When every voter says the same thing, how you weight them cannot
  matter. We measured this at the pool rather than inferring it.
- The device agreed with the exact classical answer to within 0.0010. So it
  solved the problem faithfully. The problem just was not worth solving.
- **Where the real gain came from**: better voters, not better weighting. Fixing
  how the voters were built gained +0.0319. The optimizer's own contribution was
  +0.0047, below what the experiment can even resolve.
- **Why say so publicly**: someone else would have spent the same months. A null
  that is measured and traceable saves that. An unpublished null saves nobody.
- **The honest caveat**: one configuration did gain (+0.0256), two things changed
  at once, so it cannot yet be attributed. That experiment is named and unrun.

## 7. How to know whether to believe any of this

**Learns**: what makes a result checkable, and how to check this one.

- Everything was written down BEFORE running: what we would test, what would
  count as success, how many attempts. Frozen, with a commit hash.
- Changing a frozen plan is allowed; hiding that you changed it is not. Thirty-two
  dated amendments, including three corrections after publication and one
  correction that was itself wrong.
- Every number carries a tag saying whether it came from hardware, simulation or
  projection.
- A gate failed (0.8296 against a 0.85 floor) and was recorded as failed.
- **What the reader can do**: the repository is public. The numbers regenerate
  from a script.

---

## Disclaimer placement

Team lead's required wording goes at the TOP, before section 1, not buried at the
end. A reader deciding whether to trust the document should meet its limits
first.

## Level recording

Per ADR-0014 line 421: every section states the grade level it achieved. Start at
8; escalate one grade only where an honest explanation is not achievable; record
what landed.

**Expected hard cases**: section 5 (what a QUBO is without algebra) and section 6
(what "below the minimum detectable effect" means). If either lands above 10,
that is a finding to record, not a failure to hide.
