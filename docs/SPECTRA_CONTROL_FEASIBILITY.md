# The matched random-segment control is infeasible on energy_steel

Found 2026-10-05 at Sprint 21 Task C's local pilot, before any metered call.
Zero device seconds were spent discovering this.

## What the defect is

`spectra_segment.matched_random_segment` builds H5(ii)'s negative control by
drawing a random segment of the **same size and same positive count** as the
`in_pocket` segment, **from the complement of that segment**. Drawing from the
complement is correct and deliberate: a control that shares rows with the
segment it controls for pulls the reported edge toward zero and biases H5(i)
*against* detecting a real in-segment effect. The module contract always said
"complement pool".

**On energy_steel the complement does not contain enough positives, on all
five seeds.** The segment holds more than half of the positives in the test
fold, so a size-and-rate-matched control cannot be drawn from what is left.

| Cell | Seed | Segment positives | Positives OUTSIDE segment | Feasible |
|---|---|---|---|---|
| energy_steel | 42 | 927 | 855 | **no** |
| energy_steel | 43 | 950 | 832 | **no** |
| energy_steel | 44 | 918 | 864 | **no** |
| energy_steel | 45 | 946 | 836 | **no** |
| energy_steel | 46 | 949 | 833 | **no** |
| telecom_churn | 42-46 | 46-57 | 96-106 | yes |
| oilgas_gasturbine | 42-46 | 753-785 | 1,265-1,297 | yes |

**5 of the 15 frozen cells cannot produce the control the preregistration
requires.** The assertion in `matched_random_segment` fires and the cell
raises.

The function's own docstring says the match "can only be matched exactly when
the segment's size and base rate are jointly feasible against the full pool
(asserted below); SPECTRA's pockets are a small fraction of each split so this
always holds in practice." **That last clause is false for energy_steel**,
where the pocket is not a small fraction of the positives.

## Why the committed evidence does not show it

`experiments/results/spectra_proxy_dry_run.json` was generated at `932daaf`
(F24 prep). The complement-pool correction landed later, at `775942b`
("Address all 13 Claude review findings on PR #36").

So the committed rows were produced by the **older, overlapping**
construction. All five energy_steel rows report `status: "scored"` with a
control of exactly 927-950 positives — a draw that is impossible from a
complement holding 832-864. Those controls necessarily overlapped the segment
they were controlling for.

The five control AUCs in those rows (0.949-0.973) are therefore **not** the
H5(ii) control. They are a partly-self-overlapping comparison, and the
derived edges (-0.052 to -0.077 AUPRC on energy_steel) do not mean what the
documents citing them say they mean.

## What cites the affected figures

- `docs/ALL_SPRINTS_MASTER_PLAN.md` (F90 card): "13 of 13 scored in-segment
  cells with a NEGATIVE edge at 560 and 816 variables"
- `docs/SPECTRA_BLOCK_RECONCILIATION.md`: the same "13 of 13" claim, in two
  places
- `docs/HARDWARE_REQUEST_B4.md` line 89: "The proxy solve shows NO in-segment
  edge over the matched control on any of the 13 scored (dataset, seed) proxy
  cells ... ranging -0.051 to -0.077 (energy_steel)"

The third is the document QCi holds a hardware plan against, which is why this
is not a quiet internal fix.

**What is NOT affected**: the cost anchor. B2's 82.4 s/fit is a hardware
measurement at 833 variables and has nothing to do with the control
construction. The 10 telecom_churn and oilgas_gasturbine rows remain feasible,
so 8 of the 13 scored cells are unaffected and all of them are still negative.
The direction of the finding does not change; its completeness does.

## Why this is Criterion 7 and not Criterion 4

`SPRINT_STOPPING_CRITERIA.md`: "a defect that invalidates recorded results, or
any leak/protocol violation, is NEVER Criterion 4 -- it is ALWAYS Criterion 7
(stop, document, wait) ... Never silently fix and re-run evidence-bearing
results."

This invalidates five recorded `[PROJ]` rows and touches how H5(ii)'s control
is constructed, which the frozen preregistration specifies. Re-running the
dry run would overwrite evidence that three documents cite. Both halves of
that rule apply, so the work stops here and the options go to the team lead.

## The options

Each is a Class 1 decision if it changes H5(ii)'s control definition, and a
Class 2 decision if it changes what the existing figures claim.

**Option 1 — drop energy_steel from the frozen cells.** B4 becomes 10 fits
(telecom_churn and oilgas_gasturbine, 5 seeds each), about **676-824 s**
rather than 1,084-1,235. The cells are frozen in the preregistration, so this
is a Class 1 amendment. It also removes the one cell where the prior work
reported an overall CVQBoost win, which is the cell most likely to show the
effect — the strongest argument against this option.

**Option 2 — relax the control to size-matched only on energy_steel**, with
the positive count unmatched and the mismatch reported beside every figure.
Keeps all 15 fits and about 1,084-1,235 s. Class 1, because H5(ii) specifies a
rate-matched control, and the weaker control must be labeled wherever it is
cited.

**Option 3 — control from the full pool, with the overlap measured and
reported.** This is what the committed rows actually did, made explicit rather
than accidental. Keeps all 15 fits. Class 1, and it reinstates the bias the
`775942b` correction removed, so it needs the overlap fraction stated with
every energy_steel edge.

**Option 4 — run B4 on the 10 feasible fits now and defer energy_steel** until
the control question is settled. Spends about 676-824 s, leaves 857-1,005 s,
and keeps the decision reversible. No preregistration amendment is needed to
run a subset of frozen cells; the deferral is reported.

**In every option, the three documents citing "13 of 13" are corrected to say
8 of 13 feasible**, because that correction is required whatever happens to
the cells.

## Recommendation

**Option 4**, then settle the control question for energy_steel separately.

It is the only option that needs no amendment to the frozen preregistration to
proceed, it spends real seconds on the two cells whose controls are valid, and
it leaves energy_steel — the highest-value cell and the one with the actual
problem — to a decision taken with the evidence in hand rather than under time
pressure. Options 1, 2 and 3 all commit to a control definition before anyone
has measured what the alternatives do to the result.
