# External Review Dispositions (Claude app review, 2026-09-04)

A second independent review of the rendered proposal and appendix, supplied by the team lead. Recorded because two of its findings were verified errors in shipped text and one corrected an error of mine.

## Verified and fixed

| # | Finding | Verification | Disposition |
|---|---|---|---|
| 1 | Wrong first author: "Chancellor et al., 2025" for arXiv 2503.11273 | Confirmed; correct order is Emami, Dyk, Haycraft, Spear, Nguyen, Chancellor | FIXED in appendix C.2 |
| 2 | G0b p-value is a t-approximation invalid at n = 5 | CONFIRMED BY RECOMPUTATION, and the reviewer was right where my first check was wrong: my initial permutation count used a floating-point comparison that dropped the four orderings landing exactly on rho = 0.9. Independent rank-difference calculation gives 5 of 120, one-sided p = 0.042, two-sided 0.083 | FIXED: exact permutation p reported in both documents; the 0.037 approximation removed |
| 3 | Section 2 claimed three-feature subsets; runs used one- and two- | Confirmed: k=13 schedule 2 gives 91 variables (matches every figure); schedule 3 would give 377, above the free-tier limit | FIXED: method text now matches the runs, with the reason stated; new appendix A.5 documents pool composition |
| 4 | "eight dated amendments" vs ten in the log | Confirmed (A1-A10) | FIXED |
| 5 | Typo "and and hardware objective values" | Confirmed | FIXED |
| 6 | Appendix B.2 date column wrapping | Confirmed in the rendered PDF | FIXED: dates compacted, column header relabeled |

## Accepted and applied

| # | Finding | Disposition |
|---|---|---|
| 7 | Operational comparison uses all-30 CatBoost while H1b uses matched-13 | Both now quoted in section 3; matched-13 row added to appendix A.2; the choice of the production detector as the operational baseline is stated |
| 8 | Per-seed bootstrap tagged [HW] in the body, [SIM] in the appendix | FIXED: [SIM] in both, with the reason inline. The reviewer correctly identified this as a tag the A9 sweep missed |
| 9 | Degeneracy warning and temporal reversal are in different sections and absent from the body | FIXED: both moved into section 3 as a single paragraph, including the statement that the healthy 9-feature configuration is the one we would carry into a trial |
| 10 | "Admits no exact classical proxy" overstates the cardinality-constrained case | FIXED: rephrased to no polynomial-time exact proxy in general, and the Phase 2 controls now name a time-capped MIQP solve plus greedy and annealing heuristics. This strengthens the experiment |
| 11 | Missing classical solve time | FIXED: milliseconds versus 4 to 5 billed seconds, in the body and appendix A.3 |
| 12 | Uncited 0.78 and ~0.80 figures | FIXED: AutoXGB named as the step-wise-AP comparator; the handbook's simulated-data caveat stated; the uncorroborated band's provenance pointed at the research memo in the reproducibility package |
| 13 | "Prior measured work" uncited | FIXED: attributed to the team lead's prior Dirac-3 campaign with its caveats (single seed, small margins, non-fraud benchmarks) |
| 14 | H4 partial status absent from the body | FIXED: one sentence in section 3 stating the two preregistered controls are unrun |
| 15 | "Regulatory precondition" overstated | FIXED: "regulatory expectation" under the Equality Act 2010 and FCA Consumer Duty |
| 16 | Proposal answers on ULB while the problem statement points at IEEE-CIS scale | PARTIALLY ADDRESSED: quantified impact illustration added ([PROJ] tagged), and an IEEE-CIS classical SCALE CHECK is running, deliberately labeled as outside the preregistered cells (raw features, single split, 3 seeds, reused parameters). It establishes that the pipeline runs at 590,540 rows and produces a classical number in the published band. The full preregistered IEEE-CIS protocol remains Phase 2 |

## Not actioned

| # | Finding | Reason |
|---|---|---|
| 17 | Verify against the actual portal rubric | The team lead has portal access; requirements-matrix rows A5, A5b, B1-B7 already record the verified format requirements from the official PDFs. Flagged for the team lead's compliance walk at F10 |

## Note on review quality

The reviewer flagged item 2 correctly and I initially miscomputed the check that was meant to verify it. Recorded because it is the second consecutive sprint in which an independent review found something the authoring session could not see, which is the argument for keeping the fresh-context review as a standing gate.
