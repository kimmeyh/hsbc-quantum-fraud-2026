# Sprint 11 Validation Package

For team-lead manual validation. Plain-language first, evidence second.

**Deferred to Sprint 12 by team-lead direction**: F37 (repository public) and the
fresh-eyes evidence review Phase 5 normally requires. Both are recorded in the
sprint plan as Class 3 decisions.

---

## In plain terms: what changed and why it matters

**We were telling people the wrong reason for our own result.**

The submission explained a key finding by saying our weak classifiers were
"depth-limited" trees that, at 0.17% fraud, mostly predicted "not fraud" and so
all looked alike. An outside reviewer checked the saved data. The trees are not
depth-limited at all -- they grow without limit -- and **not one** of them
predicts "not fraud" everywhere. What actually happens is that 80 to 84 of the 91
classifiers **memorize the training data exactly**, which makes them literally
the same thing as each other. Same observation, wrong explanation.

The measurement was right the whole time; the story attached to it was wrong.
That is now corrected in the preregistration (A20) and in every document.

**Our headline improvement came from something other than we thought.**

The paper reports a +0.0319 gain for the tuned classifier pool. Three things
changed at once to produce it, and we had never separated them. Now we have:

| What changed | Effect | Matters? |
|---|---|---|
| Using four kinds of classifier instead of one | **-0.0047** | No -- below our detection threshold |
| Handling class imbalance while training | **+0.0328** | **Yes** -- this is the whole gain |
| Tweaking the nearest-neighbor settings | +0.0038 | No |

So the benefit came from imbalance handling, not from classifier variety. That
is a **better** finding than the one we had: it is a simpler, cheaper
intervention, and now we can say which lever actually works.

We also checked whether the result depended on the one seed we used to pick the
configuration. Removing it changes the answer by 0.0006 -- essentially nothing.

**We were quoting a phrase the vendor never wrote.**

Our proposal said QCi's hardware paper describes Dirac-3 as a "hybrid
photonic-electronic **entropy quantum computer**". The paper says "hybrid
photonic-electronic computer" and never uses the phrase "entropy quantum
computer". We had put a word in the vendor's mouth and then leaned on it. Now we
quote what they actually wrote and claim no quantum resource -- more
conservative, and checkable in one click by a physics-literate judge.

**We now answer HSBC on their own metric.**

Their problem statement names AUC-ROC 0.9459 on the IEEE-CIS dataset. We had
reported a different metric only. It turned out our numbers were already
computed and stored, just never published: LightGBM 0.9139, CatBoost 0.8941,
XGBoost 0.8640. Now reported, with a plain statement that theirs is a different
test set so the comparison is not like-for-like.

**QCi granted 3,000 seconds, and the ceiling that shaped everything is gone.**

The whole hardware campaign was squeezed to fit a 100-variable limit. One
carefully sized test call proved that limit was a **billing tier restriction,
not a machine capability**. At 105 variables the job ran fine. This does not
change any number we have already reported -- it changes what is now possible.

**Three new safety nets, because our own tests caught none of the above.**

Every defect in this list was found by outside readers. The tests now check that
figures in the papers resolve to real stored evidence, that claims about what
evidence *means* match the evidence, and that generated reports match the data
they came from.

---

## What I would most like you to check

1. **A20 and A21** in `experiments/PREREGISTRATION.md`. These change a published
   explanation and record that the ceiling moved. You saw A20's text before it
   was committed; A21 followed the probe.
2. **The decomposition paragraph** in proposal section 3. It now says our gain
   came from imbalance handling rather than classifier variety. That is a
   materially different story from the one we were telling.
3. **The hardware description** in proposal section 2, which is now the vendor's
   words rather than ours.

---

## Acceptance criteria, walked with evidence

| Task | Criterion | Evidence |
|---|---|---|
| A (F41) | A20 registered | A1..A21 contiguous, verified |
| A | no "depth-limited" claim contradicting the code | zero occurrences in `docs/paper/*.md` |
| A | test asserts 80-84 of 91 per pool | `test_pool_mechanism.py`, 32 passed |
| B (F42) | lambda=0 spread reported | proposal quotes L1 0.90 apart, 9.1e-12 objective |
| B | decomposition reported per step | +0.0328 / -0.0047 / +0.0038 in proposal |
| B | 9-seed figure alongside 10-seed | +0.0313 stated |
| B | external claims verified or corrected | F7 corrected against arXiv:2407.04512 |
| B | F6, F13, F16, F17 corrected | each verified present in the document |
| C (F43) | AUC-ROC reported per classical arm | 0.9139 / 0.8941 / 0.8640 |
| C | mismatch caveat stated, not implied | leaderboard-vs-rolling-origin stated |
| C | figures trace to the artifact | recomputed from `ieee_classical.json` |
| E (F45) | perturbation fails a commit | verified by injection, tree left clean |
| F (F44) | every figure resolves or is registered | 5 tests pass over 3 documents |
| G (F35) | catches the B.1 contradiction | verified by injection |
| G | catches retracted wording | verified by injection |
| H (F46) | balance from the API, not the email | 3000 recorded, then 2990 after |
| H | ceiling answered by a device response | accepted at 105 variables |
| I (F47) | id on disk before the wait | forced with a fake client |
| I | job id alone retrieves a result | all 27 campaign ids readable |
| I | every request in the ledger | intent written before submission |

**Suite**: 279 passed, 1 skipped, 2 xfailed. The 2 xfails are the F38 page
limits, deferred by design. **Zero unapproved metered seconds**; one approved
call, 10 seconds.

---

## Things I got wrong this sprint, and how they were caught

Recorded because the pattern matters more than the individual errors.

- **The decomposition, first attempt**: decomposed the wrong configuration and
  used a pooled comparator instead of per-seed. Caught by checking whether it
  reproduced the published number. It did not, by 0.0069.
- **The probe's cost**: recorded 5.0 seconds, which was a *default* the code
  falls back to, not a measurement. The balance said 10. Caught by checking the
  balance rather than trusting the artifact.
- **The billing rule**: I proposed one that failed its own validation. Your
  suggestion -- round *up* the runtime sum alone -- matched all 27 jobs exactly.
- **Three assumptions in F47**: the enum import path, contiguous counters, and
  fixed timestamps. All three were checkable against data already in the repo,
  and all three were caught by tests rather than by me.

The common thread: every one was caught by checking against data rather than
reasoning from expectation. That is what the three new test files institutionalise.
