# Sprint 5 Summary: The Paper and the QCi Package

Archival record (three-doc rule). Dates: Sep 4, 2026. Branch
`feature/20260904_Sprint_5` (carried forward from Sprint 4's head); PR #29 merged
to develop 2026-09-04; develop merged to main via PR #30. Sources:
SPRINT_5_PLAN.md, SPRINT_5_RETROSPECTIVE.md, the three external-review
dispositions in `docs/reviews/`, git history, PR #29.

## Objective

Turn the Sprint 4 evidence into the actual submission: a 6-page concept
proposal, a 3-page appendix, a team profile, and the QCi package. Scope:
F8 + F9 + F27 + F19 + F26 + F28 (defined-scope rule).

## Delivered

1. **F8/F9 the submission documents**: outline approved first, then proposal,
   appendix and team profile written against the guidelines section by section.
   All three render through pandoc + xelatex and are verified US Letter:
   proposal 6/6 pages, appendix 3/3, team profile 1/1.
2. **F27 production-trial design**: the 90-day shadow-mode trial with its
   acceptance gates, latency/calibration/drift requirements, and the two
   requirements stated rather than omitted (fairness testing, label latency).
3. **F26 cost-based operating points**: recall and precision at 0.05%, 0.1% and
   0.5% alert budgets with the budget CEILING stated, so the narrow gap is read
   as partly saturation rather than only model quality.
4. **F28 explainability thread**: the exact additive decomposition, measured on
   a real flagged fraud, with its honest counterpart (46 of 91 learners to reach
   half the weight) and the scope limit that anonymized PCA components make it
   an audit decomposition rather than a business-meaningful explanation.
5. **F19 QCi package**: six DRAFT PDFs (cover, proposal, appendix,
   preregistration, gate report, hardware plan), all US Letter. Team lead
   disposition 2026-09-04: "consider it sent."
6. **The mechanism controls that settled the flat optimum**
   (`mechanism_controls.py`, zero metered seconds): uniform 0.7659, frozen
   0.7681, class-weighted 0.7686, logistic-free 0.7681. The cause is POOL
   DEGENERACY measured directly at the learner level: off-diagonal Gram entries
   average 170,234.4 against a diagonal of 170,235, so any two of the 91
   depth-limited trees agree on 99.999% of training rows.
7. **Solver dispersion recovered at zero cost** (`hw_dispersion.py`): across 8
   samples per fit, 0 of 27 fits returned identical draws; within-fit energy
   spread median 0.019%, max 0.343%. Dirac-3 is measurably stochastic and its
   dispersion is small.
8. **Three external reviews applied**, each with a written disposition recording
   where the reviewer was right AND where wrong:
   - **Claude app**: found the prediction-key collision (below).
   - **Codex 5.5**: reproducibility record and solver stochasticity.
   - **Codex 5.6 "Sol"**: 30 findings, including the two below.
9. **Amendments A9 and A10**: prediction-store keying corrected with affected
   figures retagged [SIM]; hardware predictions placed under version control.

## The two defects that mattered most

**The prediction-key collision.** Hardware and its exact proxy deliberately
share a config_hash, because they solve the identical Hamiltonian over the
identical pool, and that identity is what G0b and H4 rest on. Keying predictions
by hash alone therefore let the proxy backfill silently OVERWRITE the hardware
predictions, and the cost table showed byte-identical rows under two different
evidence tags. Fixed by putting the arm in the key (A9). Caught by an external
review, not by any test.

**"Exactly uniform" was not exact.** The proposal, appendix and QCi cover all
claimed the solved weight vector was "exactly uniform" with "L1 distance
0.000000". The stored value is 8.0e-08 (7.2e-08 to 1.6e-07 across ten seeds):
six-decimal printing was read as zero. Codex 5.6 caught the internal
contradiction, since a truly identical vector cannot produce a different AP.
Their proposed cause (pipeline defect) was wrong; running it down found
TIE-BREAKING: uniform weights leave 95.3% of test rows tied on one score (78
distinct values), perturbations of order 1e-07 split those into 151, and average
precision is rank-based. Rounding the solved scores back to six decimals returns
the metric to the uniform value. **The correction strengthens the finding**: the
optimization step contributes nothing at all, not a small sub-MDE gain.

## The literature find

Loke, Sahoo, Guan, Xu, Verma and Griffin, "Improving credit card transaction
fraud detection using CVQBoosting", ICAART 2026 (Singapore Management
University). Same Dirac-3 hardware, same algorithm, same benchmark family, mean
AUC-PR above 0.8 against our 0.767 -- with a HETEROGENEOUS pool (KNN, LDA,
logistic regression, XGBoost) where ours is one family over many feature
subsets. This is the closest prior work in existence and we had not cited it.
It does not overturn our result; it independently corroborates our own
degeneracy diagnosis and converts the Phase 2 direction into a replication
target with a published number attached. Now cited in the proposal, appendix and
QCi cover. The team lead has spoken with two authors; they have NOT agreed to be
named beyond the citation, so the package claims no contact or endorsement.

## The page-size failure

All nine PDFs rendered 11x17 TABLOID because `render-pdf.ps1` set Word's
`PageSetup.PaperSize` AFTER opening the converted document, and Word does not
reflow. This also invalidated every page count, because Word's
`ComputeStatistics` reflows a PDF when it opens it: the appendix was reported as
4 pages when it was 6 against a hard 3-page limit, and the team profile was 2
pages against a 1-page limit. Both would have hit a rejection criterion.

Found only because the team lead asked whether the pages were 11x17 or Letter.
The Word path is now deleted; the script is pandoc/xelatex only, sets geometry
before layout, and verifies size AND count after rendering.

## Estimated vs actual

Document authoring ran close to estimate. Verification and rework did not: the
appendix 3-page fit consumed roughly an hour across ~8 render-measure-trim
cycles, because prose was trimmed repeatedly before measuring WHERE the page
break fell (a table was forcing an early break and wasting half of page 1). Zero
metered device seconds spent, as planned.

## Key decisions

- Proposal target set at 5 pages, 6 acceptable: "all the content is valuable."
- QCi package: "consider it sent."
- F31 (diverse weak-learner pool) approved for Sprint 6 entry.
- Affiliation stated as "independent researcher (unaffiliated)". "Kimmey
  Consulting" was considered and rejected: ORC 1329.01 makes fictitious-name
  REPORTING mandatory within 30 days even when trade-name registration is
  declined, and the surname exemption covers the legal name only.
- "QPU seconds" replaced with "metered device seconds" in the submission
  documents, but NOT in PREREGISTRATION.md, which is frozen and whose wording is
  part of the record.

## Retrospective improvements applied

Suite went 28 -> 50 tests. `test_submission_artifacts.py` now verifies page
geometry, page counts, absence of retired claims, and the presence of every
guidelines 4.1/4.3 required element, reading the RENDERED PDFs rather than a
proxy for them. `scripts/render-all.ps1` holds the per-document margins (the
appendix needs 0.9in or it silently becomes 4 pages) and runs the verification
itself. `QUALITY_STANDARDS.md` records the defect class: a check that reads
something other than the delivered artifact can report success while the
artifact is broken.
