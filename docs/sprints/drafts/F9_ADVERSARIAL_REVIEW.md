# F9 Adversarial Review

Reviewer stance: skeptical external judge, no prior contact with this work. Sources read: proposal.md, appendix.md, team_profile.md, gate_report.md, cost_report.md, EXPLAINABILITY.md, PREREGISTRATION.md sections 1-3 and amendment log.

Headline: the protocol discipline is genuinely strong and will score well. Two defects are serious enough to cost credibility if a judge checks: an operational-metrics mis-tag ([HW] on numbers that are proxy-derived), and a G0b gate whose 0.900 correlation is computed over five points, one of which is a completely broken solve.

---

## Pass 1: HSBC fraud-detection practitioner

**Reads as informed.** Section 1 is the strongest page. Fixed review capacity, asymmetric cost, ranking that must hold at the top of the list, "a model that optimizes accuracy is worthless": that is practitioner language, not academic language. Recall at 0.05/0.1/0.5% budget instead of headline AUPRC is the right frame. Cost ratio swept rather than assumed is correct and unusual.

**What I would challenge.**

1. **ULB is not a fraud dataset a bank can reason from.** Two days of European e-commerce, PCA-anonymized V1-V28, no merchant, no MCC, no device, no velocity, no account tenure, no card-present flag. Every real feature I would use is absent. The proposal never states this limitation in the body; it appears only obliquely in cost_report ("ULB spans two days, so these are capacity-shaped comparisons"). A judge from HSBC will notice immediately. Say it in section 3 in one sentence.

2. **No concept-drift evidence, and the one temporal signal is adverse.** Line 50 admits "on a single time-ordered split the ranking of two configurations reversed." That is correct to disclose, but it understates the reversal. gate_report shows hw_b1_dct falls 0.7671 -> 0.7095 temporally while hw_b1_lg rises 0.7014 -> 0.7776. The chosen headline configuration is the one that degrades under time ordering, and the rejected configuration is the one that improves. In production, time ordering is the only ordering that exists. This deserves more than a subordinate clause.

3. **Label latency and feedback loops are absent.** Real fraud labels arrive by chargeback, 30 to 90 days late, and only for transactions you did not block. The 90-day trial plan (line 48) has no ground-truth arrival model, which means "days 31-60 champion/challenger with a rollback trigger tied to precision at the alert budget" cannot actually be evaluated inside the window. Nothing here addresses the selective-labeling bias that any shadow-to-live transition creates.

4. **Missing before a pilot.** Throughput and p99 latency under load, not just "low tens of milliseconds" asserted. Model risk governance artifacts (SR 11-7 / PRA equivalent). Fairness and disparate-impact testing on declines, which is a hard regulatory gate at a UK bank and is not mentioned once. Data residency for a US-hosted quantum vendor touching production training data. Incident and fallback behavior when Dirac-3 is unreachable at retrain time. Cost of an analyst hour, without which the swept cost ratio is unanchored.

5. **Hand-wavy points.** "Fraud patterns decay in weeks" is asserted, not sourced. "Precision at the alert budget" as a rollback trigger needs a stated detection window and sample size, or it fires on noise. Line 52 claims explainability suits dispute handling, but a decline explanation citing "V2 + V21" is not customer-facing; PCA components cannot be given to a customer or a disputes team. The EXPLAINABILITY.md worked example makes this concrete and undermines the claim as written.

**Not wrong, but naive in framing.** "Analysts can only work so many alerts a day" is right; treating review budget as a single global fraction is not how a bank runs it. Budgets differ by segment, channel, and risk tier, and alerts are usually queued by expected loss, not by score rank. That is a one-line fix, not a rethink.

---

## Pass 2: quantum computing researcher

**(a) Claims stronger than their evidence tags.**

- Line 42, the operational comparison, is the worst offense. "CVQBoost on hardware catches 56.5% [HW]" is not a hardware measurement. cost_report.md states plainly: "Hardware predictions were not persisted in Sprint 4 ... so this runs on the EXACT PROXY of the same config." The tell is in cost_report's own table: `cvqboost_hw/hw_b1_dct` and `cvqboost_proxy/free/dct` have byte-identical recall and precision at every budget (0.283 / 0.565 / 0.819). Identical to four decimals across three operating points is not agreement, it is the same prediction vector. Appendix A.2 carries the same [HW] tag on the same row.
- Line 36, "Six of ten per-seed paired bootstrap intervals exclude zero," is tagged [HW] in Appendix A.3. cost_report labels every one of those ten rows "CVQBoost exact proxy [SIM] - CatBoost matched13." This is [SIM] evidence presented under an [HW] tag.
- Line 34, "Ranking agreement between the classical proxy and hardware ... Spearman 0.900 [HW]." The gate_report is explicit that this is Spearman over *validation* AP, n=5, p=0.037. The proposal drops the n, the p, and the validation qualifier. gate_report even self-flags "n=5, so the interval is wide." Reporting a five-point rank correlation as a passed fidelity gate without n is the kind of thing a quantum reviewer flags on sight.
- Related and more damaging: one of those five G0b configurations, hw_g0b_5, produced test AP 0.0017 with AUC 0.5000 and exactly **one distinct score**. That is a dead solve, not a low-ranked configuration. A rank correlation over five points where one point is a degenerate outlier at the bottom of both orderings is close to guaranteed to look good. The gate is technically passed as committed, but the evidence is thin and the proposal presents it as licensing "proxy-based development everywhere else in this work," which is a much larger claim than five points support.

**(b) The convexity and degeneracy argument.**

Correct in substance, and correctly scoped. Line 38 says the objective "is strictly convex on the simplex, so the classical solve returns the global optimum and the quantum solver can match but not exceed it," and line 40 explicitly limits it: "a negative result about one formulation, not about the approach." That scoping sentence is essential and it is present. Good.

Three technical caveats.

- "Strictly convex" is asserted, not shown. The QBoost-relaxation Gram matrix over correlated weak learners is positive *semi*definite in general; strict convexity requires the weak-learner output matrix to have full column rank. With 91 learners built from 13 features on heavily correlated one-, two-, and three-feature subsets, near-rank-deficiency is exactly what the flat optimum in A.5 suggests. The honest statement is "convex, and empirically near-degenerate," which is what A.5 actually measures. As written the two sentences are in mild tension: strict convexity implies a unique optimum, and near-degeneracy implies the optimum is not well-identified. Both can hold numerically, but the proposal should say so rather than leave a reviewer to reconcile them.
- The convexity argument makes hardware *irrelevant*, not merely unhelpful, on this formulation. The proposal gets close to conceding this ("any solver reproduces it") but does not say the obvious corollary: the 27 metered fits bought no information the classical solve did not already have, except the fidelity check itself. Saying that first is stronger than letting a judge find it.
- Dirac-3 is repeatedly and correctly called quantum-*inspired* entropy computing, and the gate-based arm is correctly flagged as a Phase 2 plan, not executed. That discipline is maintained throughout. Credit where due.

**(c) Quantum-methods errors.** None found in the physics or the solver description. The description of CVQBoost as a continuous relaxation of Neven's binary QBoost is accurate, and citing Neven 2012 as "the original binary formulation this work relaxes" is precise. The prereg's ban on plain Ry angle encoding for the Phase 2 gate-based arm, on Inverse-Born-Rule grounds, is a sophisticated call that most entrants would not make.

**(d) Phase 2 program.** Technically sound, and lever four is the best idea in the document. Cardinality-constrained sparse subset selection is NP-hard, is genuinely the native Dirac-3 integer problem, and follows *logically* from the convexity finding rather than being bolted on. That is a real research argument. Two gaps: no statement of what classical baseline it must beat (greedy forward selection and L0 via mixed-integer programming on 91 variables are both tractable, and 91 variables is small enough that a MIP solver may simply close the problem, which would neutralize the advantage claim before it starts); and no statement of what problem size would make it non-trivial. Lever three, IEEE-CIS at "several hundred features," collides with the disclosed 949-variable device ceiling; at schedule 2 that caps n at about 43 features, far short of "several hundred." Line 72 gestures at this but the arithmetic is not shown in the proposal body.

**(e) Hardware overclaiming.** The 27 fits, 120 QPU seconds, zero failures and zero retries are reported accurately and match gate_report exactly. The -0.0010 hardware-minus-proxy delta with CI containing zero is honest and is the most valuable hardware number here. The claim I cannot verify is "hardware objective values sit 0.013% to 0.413% above the exact minimum." gate_report reports objective gaps as absolute values (+25.41, +173.2, +614.3, +96.32), not percentages, and gives no objective scale from which to derive the percentages. Either show the denominator or drop the precision.

---

## Pass 3: rubric scoring

| Criterion | Weight | Score | Justification |
|---|---|---|---|
| Problem Relevance | 25% | 4 | Section 1 frames the business problem better than most entrants will, but the work never confronts that ULB lacks every feature a real fraud system uses. |
| Technical Approach | 25% | 4 | Preregistration, matched-feature controls, structural control arm, and the convexity finding are genuinely rigorous; the hardware campaign is small and the primary result is a null. |
| Feasibility | 20% | 4 | Inference is a linear vote and the quantum device sits at training time only, which is the correct architecture; the pilot plan omits label latency and model-risk governance. |
| Validation | 15% | 3 | The statistical machinery is excellent, but two headline figures carry [HW] tags on proxy-derived evidence and the fidelity gate rests on five points including one dead solve. |
| Team | 10% | 3 | Credible and honest hardware experience, but a solo entry with an unresolved editorial note still in the shipped text. |
| Hybrid Integration | 5% | 4 | The router-plus-specialist shape with nothing quantum in the live path is the right answer and is stated crisply in one paragraph. |

**Lowest: Validation (3).** It is also the criterion where the fix is cheapest, because the underlying work is already correct; only the labeling is wrong.

**Three changes that would raise it most.**

1. **Fix the two mis-tags.** Change the operational figures at proposal line 42 and Appendix A.2 from [HW] to [SIM], with a one-clause note that hardware weights were not persisted and that hardware-minus-proxy was measured at -0.0010 with the interval containing zero, so the substitution is evidenced. Do the same for the "6 of 10" row in A.3. This costs nothing and removes the single finding most likely to be read as inflation.
2. **Report G0b honestly in the proposal body.** "Spearman 0.900 over 5 configurations on validation AP (p = 0.037), one of which failed to a degenerate single-score solution." Then narrow the conclusion from "licenses proxy-based development everywhere else in this work" to "consistent with proxy transferability at n = 5; a wider fidelity check is Phase 2 work."
3. **Add a two-line degeneracy caveat to section 4.** Appendix A.4 already discloses that the headline configuration has a 95.1% modal score share and that its alert-budget precision and calibration numbers are "weaker evidence than the AUPRC." Section 4 leans on exactly those alert-budget numbers with no caveat. Carrying the warning forward converts a hidden weakness into a visible strength.

---

## Evidence-tag audit

Requested figures, verified against gate_report.md and cost_report.md.

| Figure | Where | Tag | Verdict |
|---|---|---|---|
| 0.8368 | prop 30, app A.1 | [SIM] | Verified, catboost/full. Correct. |
| 0.8296 | prop 32, app B.1 | [SIM] | Verified, xgboost/full. Correct. |
| 0.7671 | app A.1 | [HW] | Verified, cvqboost_hw/hw_b1_dct/stratified. Correct. |
| 0.0399 | prop 36, app A.3 | [HW] | Verified. Correct. Note gate_report gives -0.0347 vs XGBoost and -0.0353 vs LightGBM; the proposal quotes the largest gap. Defensible (prereg says "best of the trio") but a reviewer will see selection of the worst-looking number. |
| 0.900 | prop 34, app A.3 | [HW] | Value verified. Under-qualified: n = 5, p = 0.037, validation AP, one degenerate config. |
| -0.0010 | prop 38, app A.3 | [HW] | Verified. Correct, and the strongest hardware claim in the document. |
| 0.593 | prop 42, app A.2 | untagged in prop / [SIM] row | Verified, catboost/full recall @ 0.10%. Fine. |
| 0.565 | prop 42, app A.2 | **[HW]** | **MIS-TAGGED.** Proxy-derived per cost_report. Must be [SIM]. |
| 46 of 91 | prop 52 | untagged | Verified in EXPLAINABILITY.md. Should carry [SIM] (exact proxy solve, seed 42, zero metered seconds). |

Additional tag problems.

- **prop 42**: "At 0.5% the figures are 85.5% and 81.9%" carries no tag at all. Values verified (0.855, 0.819); the second is proxy-derived and needs [SIM].
- **prop 42**: "stable across cost ratios from 20 to 100" is untagged; verified in cost_report, [SIM].
- **prop 30**: shuffled-label 0.0023 vs 0.0017 is untagged in the proposal body. Tagged [SIM] in B.1, so add the tag in the body.
- **prop 34**: "Twenty-seven metered Dirac-3 fits, 120 QPU seconds" untagged in the body. Verified. [HW].
- **prop 38**: cosine "0.975 to 0.999" [HW]. gate_report per-cell means run 0.9751 to 0.9987. The upper bound 0.999 rounds up from 0.9987, and that highest value belongs to hw_g0b_5, the dead solve. Use 0.975 to 0.996 excluding the degenerate config, or state the range as per-cell means.
- **prop 38**: "0.013% to 0.413% above the exact minimum" [HW]. **Not verifiable** from gate_report, which reports absolute gaps only.
- **app A.3**: "Per-seed paired BCa intervals excluding zero, 6 of 10" tagged [HW]. **MIS-TAGGED**, [SIM] per cost_report.
- **prop 32**: "Clean-protocol equivalents fall near 0.80, and a benchmark using the same step-wise metric we use reports 0.78." Two external literature figures with no tag and no citation in the proposal body. Not [HW]/[SIM]/[PROJ]; they need a source, since the whole paragraph's credibility rests on them.
- **prop 42**: "under three percentage points of caught fraud" is a rounding of 0.593 - 0.565 = 2.8pp at the 0.1% budget, but at 0.5% the gap is 3.6pp. "Under three percentage points" is true only at the budget that flatters the argument. Say "2.8 to 3.6 percentage points across budgets."
- **prop 28 / app A.1**: 284,807, 1,081 duplicates, prevalence 0.00167 all verified against prereg and gate_report. Correct.
- **prop 22**: "eight dated amendments" matches A1-A8. Correct.

---

## Prioritized fix list

1. Retag proposal line 42, Appendix A.2's CVQBoost row, and Appendix A.3's "6 of 10" row from [HW] to [SIM] with the persistence explanation. Highest credibility risk, near-zero cost.
2. Qualify G0b in the proposal body with n = 5, p = 0.037, validation AP, and the degenerate fifth config; narrow the conclusion it licenses.
3. Delete or source the "0.013% to 0.413%" objective-gap claim; it cannot be checked against the cited evidence.
4. Remove the editorial note at proposal line 82, "(Team lead: confirm or amend this section...)". It must not appear in a submitted document.
5. Add one sentence in section 3 stating ULB's feature limitation (PCA components, two days, no merchant/device/velocity) and what that does and does not license.
6. Promote the temporal-reversal finding from a subordinate clause in line 50 to its own sentence, naming that the headline configuration is the one that degrades under time ordering.
7. Carry Appendix A.4's degeneracy warning into section 4 wherever alert-budget numbers appear.
8. Soften "strictly convex" to "convex, and empirically near-degenerate," and add the corollary that on this formulation the hardware adds no information beyond the fidelity check.
9. State the classical baseline the Phase 2 cardinality-constrained experiment must beat (greedy forward selection and exact L0 by mixed-integer programming), and the problem size at which those stop being tractable.
10. Restate the 3pp gap as a range across budgets, 2.8 to 3.6 percentage points.
11. Fix the explainability claim for dispute handling: PCA components are not customer-facing, so scope the claim to internal model documentation and regulatory review.
12. Add fairness and disparate-impact testing to the 90-day trial's proceed criteria; its absence is conspicuous for a UK bank.
13. Show the IEEE-CIS variable arithmetic in the proposal body, since "several hundred features" and a 949-variable ceiling are in visible tension.
14. Add a label-latency and selective-labeling paragraph to the trial plan, or state explicitly that the 90-day window evaluates shadow agreement rather than realized chargeback outcomes.

Word count is within limit. Pages remain available: the proposal is 3 of 6, so every fix above can be additive rather than a trade.
