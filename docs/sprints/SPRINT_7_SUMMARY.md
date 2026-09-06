# Sprint 7 Summary: Direction into Result

Archival record (three-doc rule). Date: Sep 5, 2026. Branch
`feature/20260905_Sprint_7` (carried forward from Sprint 6's head); PR #41.
Sources: SPRINT_7_PLAN.md, SPRINT_7_RETROSPECTIVE.md, git history, PR #41.

## Objective

Sprint 6 established that the CVQBoost optimizer does real work on a
heterogeneous pool but bought no accuracy with it. F33 tested whether the
remaining gap to Loke et al.'s reported ~0.8 is learner quality and tuning
rather than pool composition. Scope: F33 + F34 + the QCi/paper update.

## Delivered

1. **F33, the result.** A tuned four-family pool reaches **0.7827 AUPRC**
   (SD 0.0283) over ten seeds, against 0.7565 untuned and ~0.80 reported by
   Loke et al. on the same hardware and benchmark family.
2. **The matched comparison, which is the one reported.** The tuned pool is k=6
   while both earlier comparators are k=13, so the frozen single-family pool was
   rebuilt AT k=6 on the SAME splits for a paired per-seed test: **+0.0198**
   (SD 0.0203), positive on 9 of 10 seeds, **still below the 0.0268 MDE**. The
   frozen pool scores 0.7629 at k=6 against 0.7681 at k=13, so six features are
   slightly WORSE for it and part of any raw cross-k gap is feature count. The
   +0.0198 is paired at matched k=6, which is why it is the reported figure.
3. **The finding worth carrying forward: the accuracy came from the learners,
   not the optimizer.** Solved-minus-uniform on the tuned pool is +0.0043. Adding
   imbalance handling AT FIT TIME (class weighting in the tree and logistic
   learners; LDA and KNN accept none) drops the Gram off-diagonal ratio from
   0.9988 to 0.92 and lifts absolute accuracy. The selected arm also tightened the
   KNN neighbourhood, so the accuracy figure carries two interventions while the
   diversity figure is attributable to class weighting alone (A16), while the optimization step stays
   nearly free either way. For CVQBoost at low prevalence the leverage is pool
   construction.
4. **F34, eight spend-guard property tests.** Each asserts the property whose
   violation caused a real defect: a cap above its approval, a double-count that
   halted a block at half its spend, first-found rather than conservative
   billing, an unguarded metered call, and an unrecorded failure. Verified to
   FAIL on the originals rather than trusted to pass.
5. **Amendments A13 and A14.** A13 registered the tuned-pool protocol BEFORE the
   ten-seed run with its scope limits stated. A14 records the matched comparator
   and both corrections below.
6. **Paper and QCi letter updated** with the two-step account. The letter sends
   Monday night 2026-09-07 and card #40 stays open for team-lead feedback.

## Two corrections to our own interpretation

Both registered as A14 rather than left in a conversation.

**A mid-run prediction was wrong.** A note predicted the tuned pool was
"unlikely to clear 0.7681" on the basis of sweep VALIDATION AP, compared against
comparators that are TEST AP. Different quantities: validation runs about 0.005
below test on this split design, and seed 42's validation fold is markedly
harder than its test fold (0.7133 against 0.8230). The sweep's SELECTION was
unaffected, since it ranked candidates against one another on a single
consistent metric; the inference drawn from it was not.

**The comparators were not like-for-like.** Quoting a k=13 frozen figure against
a k=6 tuned arm is the order-mismatched comparison ADR-0013 identifies as the
mechanism by which apparent quantum wins are manufactured. Caught before
anything reached the paper, and the Sprint 7 plan itself had invited it by naming
the k=13 figure as an acceptance criterion.

## Estimated vs actual

Tasks A and B ran close to estimate once the capability pre-flight had sized
them. Task C overran, entirely on page-limit cycles that were not estimated and
should have been, since the same overrun happened in Sprint 6.

## Key decisions

- Sprint 8's IEEE-CIS arms run BOTH pool configurations: the frozen arm as the
  preregistered comparator for continuity, the tuned arm as the configuration
  the evidence now favours.
- The question of whether F33 changes the Phase 2 priority is HELD until after
  the submission is approved, with the argument on both sides recorded so it is
  not re-derived: a small optimizer contribution on a CONVEX problem does not
  predict a small one on the NP-hard problem the integer solver would face.
- The QCi letter's F33 account stands as written.

## Retrospective improvements applied

Suite 125 -> 132. `comparators.py` refuses a difference whose arms mismatch on
k, protocol, schedule or dataset, and refuses validation against test, with
tests that reconstruct both Sprint 7 errors. QUALITY_STANDARDS now requires
`page-fill-report` to run FIRST on an over-limit document and forbids cutting
prose until it reports a length problem, and requires edit scripts carrying
LaTeX or regex escapes to be written to a file rather than heredoc'd. F35
registered to extend comparison guards from computation time to document time.

## The process lesson

The page-limit overrun repeated, and this time the tool that diagnoses it
correctly already existed: `page-fill-report` printed "FIX THE BREAK, not the
prose" and named the underfilled page on its first run, and four more prose
trims followed before the verdict was acted on. The real cause was pandoc's
`\\maketitle` band wasting ~1400 characters of page 1 while ~300 spilled.
Building a tool and then ignoring its output is a worse failure than not having
the tool, which is why improvement 2 is a rule rather than another tool.
