# Sprint 13 Summary

**Dates**: 2026-09-12 (one day). **Branch**: `feature/20260912_Sprint_13`.
**PRs**: #82 (to develop).

Sources: SPRINT_13_PLAN.md, SPRINT_13_RETROSPECTIVE.md, SPRINT_13_VALIDATION.md,
git history, PR #82, the amendment log A32, and the portal receipt. Not the
master plan.

## Scope, as delivered

Planned as **F10 only**: verify every claim against its evidence, then submit.
F64 was selected at refinement and withdrawn the same day on the team lead's
methodological reasoning, before any work began.

**The submission was filed on 2026-09-12, three days before the deadline.** The
portal returned "Your submission received."

Suite **320 -> 321**. Zero metered seconds.

## The submission

Three files to the HSBC track at `quantumaiportal.thequantuminsider.com`:
proposal 6 of 6 pages, appendix 3 of 3, team profile 1 of 1, all US Letter at
10.0pt. The portal renamed them on ingest to `proposal-1`, `appendix-6` and
`team_profile`, which is recorded so a later reader comparing the portal's list
against this repository does not find three names matching nothing.

Two upload slots remain unused.

**Requirements-matrix row A5 carried four unknowns that could not be settled
without uploading, and all four are now answered.** No per-file size cap is
displayed; there is no post-upload metadata prompt; the deadline timezone is not
shown anywhere in the challenge view, so it stays unresolvable from the UI and
was made moot by submitting early; and uploading is the committing action in two
steps -- selecting files stages them with the counter still at zero and a Remove
control per row, and clicking Upload commits.

That staging step is a real safety property and is recorded as one.

## What a verification sprint found

The sprint was scoped as a formality. It found **nine defects**, and the suite
caught none of them.

**One in the evidence artifacts.** `summarize_b2.py` wrote the B2 comparator as
"78 vars" into `b2_hardware.json` where every `hw_b1_dct` row carries **91**.
A24 had already recorded the correction in prose and the generator kept writing
78. Prose only: the regeneration changed one line, no computed figure moved, and
both published documents said 91 correctly throughout. A regression guard now
reads the count out of `results.json` rather than trusting a literal.

**Six in the requirements matrix**, which is the Stage 8 acceptance checklist
walked line by line before submitting. E5 still read "NOT MET as of Sprint 9,
proposal 7 of 6" and cited xfail markers F38 had removed. D12 said the Braket
arm was "gated on a classical feasibility screen" when the proposal now commits
unconditionally. E6 promised in future tense a repository F37 had already made
public. C1 cited dollar figures the page-limit trim removed, and C7 a "prior GIC
2026 entry" appearing in neither document.

**C5 and C6 pointed at the wrong sections.** F55 inserted the Validation plan as
section 5 and pushed Hybrid integration to 6; the rows kept the pre-F55
numbering. C5 is the 15%-weighted Validation Plan, which the guidelines call the
strongest differentiator, so a judge following that pointer lands in the wrong
place.

**Six in the submission documents**, found by an evidence walk against the
artifacts and each verified independently before presentation.

## The defect that justifies F39

Appendix A.5 read "LightGBM restricted to the same six features falls from
**0.5739** to 0.0734 ... fold 0". The artifact's control is fold-0 to fold-0 and
its baseline is **0.5424**; 0.5739 is the three-fold mean from a different file.
The sentence mixed protocols and ended by naming the protocol it had violated,
inflating the stated fall from 7.4x to 7.8x.

**Both numbers are real, which is why nothing caught it.**
`test_document_figures_resolve.py` does a global value-set lookup, and its own
docstring predicts exactly this: "It does NOT catch a figure that exists in the
store but is quoted in the wrong place." Only per-claim provenance closes it,
which is the F39 design. The case is now recorded on that card.

Also corrected: A31's linear-term spread quoted 16.0 as a maximum where the
stored per-pool values reach 28.0 (**A32**); the proposal's rank-one Gram claim
carried no threshold though A27 requires one stated where the claim is made
(recomputed: second eigenvalue 1.022e-06 of the largest, 9 of 91 above an
absolute 1e-4); the team profile claimed "28 known-answer tests" against a suite
of 322, a Sprint 5 total relabelled; and "one to three features" described an
order-2 configuration where no learner reads three.

## F64, withdrawn

Selected at refinement, withdrawn the same day. The reasoning is methodological
and is recorded on the card because it supersedes the Sprint 12 scheduling
deferral: F64 varies one axis with everything else frozen at values chosen for a
different configuration, so a one-factor-at-a-time probe measures that axis and
stays silent about the interaction where the leverage is expected to sit.

The result could not become false. It could become **unimportant** -- a true fact
about a formulation Phase 2 abandons.

Decisive: proposal section 6 already presents the cell as experiment 1 of six in
an ordered program, and experiment 3 is the cardinality-constrained formulation
A31 points to. Running experiment 1 early and reporting it alone would convert an
ordered program into one result plus five things undone.

Its pre-flight is preserved on the card, so Phase 2 starts measured: the
`CONFIGS` blocker and its one-line fix, a 6.6-7.3 s pool build against an
unsupported 735 s figure, the Windows `fork` failure, and the `score_gates.py`
argmax that can silently re-key the H1b confirmatory table.

## Process

One communication failure, recorded because the fix is now a rule. Six findings
were presented for approval and item 5 carried a recommendation to take **no**
action; the team lead approved all six, reasonably reading them as six fixes,
and the unwanted change was backed out. The workflow's Class 4 section now
states that a list presented for approval contains only items to be changed.

Manual Validation passed all four items. The one question it raised -- a
`mailto:` link on the email address -- was checked rather than acted on: the
PDF's annotations hold only the LinkedIn URI, and re-opening confirmed the link
was the viewer's own cached auto-detection. No change was made and none was
needed.

## Numbers

| | |
|---|---|
| Tests | 320 -> 321, 1 skipped |
| Amendments | A32 (32 total) |
| Metered seconds | 0; allocation unchanged at 1,961 of 3,000 |
| Defects found | 9, none caught by the suite |
| Submission | filed 2026-09-12, 3 days early, 6/3/1 pages |
| Retrospective | 16 categories x 4 roles, all 6 improvements applied |

## What carries forward

- **The develop-to-main merge**, which had not happened at close-out: main was
  18 commits behind and lacked the whole of Sprint 13, including the submission
  record
- F64 as Phase 2 experiment 1, F65, F66, F67, F48, and F2b's B4 and B5
- F67 specifically: `test_pool_mechanism.py` is the suite's only skip and is
  inert on a fresh clone, leaving the "80 to 84 of 91 learners" claim unguarded
