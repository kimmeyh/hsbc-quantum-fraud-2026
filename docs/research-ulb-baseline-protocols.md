# ULB Baseline Protocols: Duplicates, Features, and the AUPRC Gap

Research date: 2026-09-03. Scope: methodology research for the G0 pipeline-honesty gate. This file is advisory. It changes no frozen protocol content.

## BLUF

Our tuned XGBoost mean test AUPRC of 0.8296 is **not evidence of a defective pipeline**. The 0.85-0.88 "honest band" in the frozen preregistration was never traced to a peer-reviewed table under our protocol, and our own prior report flagged this (research-baselines-best-practices.md, line 343). The most probable source of the band is a widely-cited tutorial that differs from our protocol in three ways that each bias its number upward: it computes PR-AUC by **trapezoidal interpolation** (which scikit-learn documents as "too optimistic"), it **retains the 1,081 duplicate rows**, and it uses **repeated 10-fold cross-validation over the entire dataset** (90 percent training data per fit, no held-out test fold, no tuning cost).

Each of those three differences moves the number in the same direction. Together they plausibly account for the entire 0.02 to 0.05 gap. Independent clean-protocol AUPRC values we did locate for ULB cluster at **0.776 to 0.782**, which sits *below* our result, not above it.

Recommendation: **amend to add a labeled exploratory protocol-sensitivity analysis** (three cells, no hardware cost) and, separately, note that G0's 0.85 threshold rests on a band that primary-source research does not support. The gate criterion itself must not be changed after observation; the amendment adds diagnostic cells only.

## Findings table

| Finding | Evidence / source URL | Estimated magnitude | Confidence |
|---|---|---|---|
| ULB has exactly 1,081 exact-duplicate rows (284,807 to 283,726) | [Frontiers/PMC 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12540476/) | Confirms our count exactly | Verified, high |
| Most published ULB work does **not** mention duplicates at all; no source found quantifying the AUPRC impact of dedupe | [MLM tutorial](https://machinelearningmastery.com/imbalanced-classification-with-the-fraudulent-credit-card-transactions-dataset/), [arXiv 2506.02703](https://arxiv.org/html/2506.02703), [arXiv 2412.07437](https://arxiv.org/html/2412.07437v1) | Gap in the literature | Verified absence, high |
| Trapezoidal PR-AUC is "too optimistic" vs step-wise AP; sklearn says so explicitly | [sklearn average_precision_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html) | Directional, always upward | Verified, high |
| Measured trapezoidal-vs-AP gap on skewed data | [Tran-The, TDS 2022](https://towardsdatascience.com/the-wrong-and-right-way-to-approximate-area-under-precision-recall-curve-auprc-8fd9ca409064/) | 0.53 vs 0.41 (+0.12) at 4 percent prevalence; gap widens with skew | Verified for that example; magnitude on ULB inferred |
| Linear PR interpolation is formally incorrect (original result) | [Davis and Goadrich, ICML 2006](https://mark.goadrich.com/articles/davisgoadrichcamera2.pdf) | Extreme case 0.50 vs 0.031 | Verified, high |
| The likely source of the 0.85-0.88 band uses trapezoidal AUC + all data + no dedupe | [MLM tutorial](https://machinelearningmastery.com/imbalanced-classification-with-the-fraudulent-credit-card-transactions-dataset/) | KNN 0.867, ExtraTrees 0.864, RF 0.855 | Verified, high |
| ULB authors' own handbook mandates step-wise AP and forbids interpolation | [Fraud Detection Handbook Ch.4](https://fraud-detection-handbook.github.io/fraud-detection-handbook/Chapter_4_PerformanceMetrics/ThresholdFree.html) | Confirms our choice is correct | Verified, high |
| Clean-protocol ULB AP with tuned XGBoost | [AutoXGB benchmark](https://github.com/kennethleungty/Credit-Card-Fraud-Detection-AutoXGB) | 0.782 (AutoXGB), 0.776 (tuned baseline) | Verified numbers; protocol partly undocumented |
| Pre-split resampling inflates metrics massively | [arXiv 2412.07437](https://arxiv.org/html/2412.07437v1) | F1 95.0 correct vs 99.97 leaky | Verified, high |
| Single-split results are unreliable; multi-seed averaging is required | [Handbook Ch.5](https://fraud-detection-handbook.github.io/fraud-detection-handbook/Chapter_5_ModelValidationAndSelection/ModelSelection.html) | SD approx 0.01 reported on AP | Verified, high |
| 60/20/20 is an accepted leakage-free fraud protocol | [arXiv 2606.10393](https://arxiv.org/abs/2606.10393) | AUPRC 0.6699 (IEEE-CIS, not ULB) | Verified, high |

## Q1: How do published ULB baselines handle the 1,081 duplicates?

**Verified.** The duplicate count is confirmed independently. Albalawi and Dardouri (Frontiers in AI, 2025, DOI 10.3389/frai.2025.1643292) report reducing the dataset "from 284,807 to 283,726 transactions" by removing duplicates. That is exactly 1,081 rows, matching our preprocessing.

**Verified negative result.** No source located reports the AUPRC impact of dedupe on ULB. This is a genuine gap in the literature, not a search failure. Three separate targeted searches returned nothing.

Practice splits into three groups:

1. **Remove, no impact reported.** Albalawi and Dardouri (2025) remove duplicates but report only ROC-AUC (RF 0.9759, XGBoost 0.9998, DL 1.0). Those values are high enough to suggest other leakage, and the paper reports no AUPRC, so it is not a usable comparator.
2. **Retain silently.** The MachineLearningMastery tutorial, the most likely origin of the 0.85-0.88 band, has no deduplication step. Its scores cover all 284,807 rows.
3. **Do not mention it.** Both methodological audits (arXiv 2506.02703, 2412.07437) catalog leakage mechanisms but neither discusses duplicate rows.

**Inferred, medium confidence.** Retaining duplicates should inflate AUPRC. Duplicated fraud rows can land in both train and test under a random stratified split, which is memorization-based leakage on exactly the rows the metric rewards most. Because AUPRC at 0.172 percent prevalence is dominated by top-ranked positives, a few leaked frauds carry leverage out of proportion to their row count. Our dedupe-before-split choice is conservative and correct, and should be expected to *lower* our number against sources that skip it.

## Q2: Leakage-free feature engineering on ULB

**Verified but thin.** No primary source was found that isolates the AUPRC delta of any single ULB feature transform under a clean protocol.

- **log(Amount).** Already in our G0c preprocessing. `Amount` is the only raw-scale feature and is strongly right-skewed. No source quantifies the gain. **Inferred:** near zero for GBDTs, which are invariant to monotone transforms of a single feature. It matters for the logistic floor control and distance-based weak learners in the CVQBoost pool, not for XGBoost.
- **Time-of-day cycle.** Deriving hour from `Time` as sin/cos is widely described; our QFE arm does this. **Caveat, verified:** ULB spans only two days, so the cycle is estimated from two periods and generalizes weakly by construction. Our preregistration already labels the ULB temporal split a stated-weak sensitivity check for the same reason.
- **Scaling.** The handbook and the leakage audit both require scaling fit on training data only, which our section 5 rule covers. Irrelevant to GBDT AUPRC, material to the logistic and KNN arms.

**Assessment:** V1-V28 are already PCA outputs, so classical interaction engineering has little headroom, and the record offers no measured feature-engineering win to chase. This *weakens* the case that our 0.8296 leaves easy performance on the table through missing features.

## Q3: What explains the gap between ~0.85-0.88 and our 0.8296?

Ranked by estimated magnitude. This is the core of the analysis.

### 1. Metric definition: trapezoidal PR-AUC vs step-wise AP (largest single factor)

**Verified.** The scikit-learn documentation states directly that `average_precision_score` "is different from computing the area under the precision-recall curve with the trapezoidal rule, which uses linear interpolation and **can be too optimistic**."

The likely band source computes its metric as:

```python
def pr_auc(y_true, probas_pred):
    p, r, _ = precision_recall_curve(y_true, probas_pred)
    return auc(r, p)          # trapezoidal, NOT average_precision_score
```

That is precisely the method our preregistration section 9 bans. Davis and Goadrich (ICML 2006) proved linear PR interpolation is incorrect; in their extreme skewed example it gave 0.50 against a true 0.031. Tran-The measured 0.53 vs 0.41 at 4 percent prevalence and noted the effect "is more likely to be observed when the data is highly skewed."

**Estimated magnitude: +0.01 to +0.04 upward bias in the band.** ULB at 0.172 percent prevalence is far more skewed than the 4 percent example, which argues for the upper end. Confidence: high on direction, medium on size, since no source measures this on ULB specifically.

The ULB group's own handbook settles the question: "Linear interpolation (as is used for ROC curves) **should not be used** for plotting PR curves, nor for assessing their AUC." Our choice is the one the dataset's authors endorse.

### 2. Training-data volume and absence of a held-out test fold

**Verified.** The band source uses `RepeatedStratifiedKFold(n_splits=10, n_repeats=3)` via `cross_val_score` over the entire dataset. Consequences:

- Each fit trains on 90 percent of data; we train on 60 percent. With 492 frauds (473 after dedupe), their training positive count is roughly 425 against roughly 284 for us. **Inferred magnitude: +0.01 to +0.03**, medium confidence: in this scarcity regime AUPRC is strongly positive-count-limited.
- No held-out test fold exists; every row is scored by a model that saw 90 percent of its peers.
- Their models are largely untuned defaults, so no tuning budget is spent but no selection bias is incurred either. Neutral to slightly downward for them.

### 3. Duplicate retention

Covered in Q1. **Inferred magnitude: +0.005 to +0.02.** Confidence: low-to-medium, unquantified in any source. Direction is confidently upward.

### 4. Single-split vs multi-seed averaging

**Verified, but this is a variance effect, not a bias effect.** The handbook reports AP with standard deviations of about 0.01 across folds and treats single evaluations as lacking robustness. Our 10-seed mean is a *better* estimate, not a lower one. However, a literature that reports single favorable splits will show a **max-of-N** selection bias. **Estimated magnitude: +0.01 to +0.02** for cherry-picked single splits relative to a 10-seed mean. Confidence: medium.

Our own measured seed SD (0.0269 on paired deltas, per amendment A5) confirms that any single-split ULB number carries roughly this much noise.

### 5. Test-set tuning leakage

**Verified as a real mechanism.** The handbook notes plainly that "the best parameters for the validation may not be the optimal parameter for the test set," showing depth 50 optimal on validation against depth 4 on test. Any study tuning on the test fold captures that difference as free performance. Our dedicated validation fold with early stopping forgoes it. **Estimated magnitude: +0.01 to +0.03** where present. Confidence: medium.

### 6. Resampling / SMOTE

**Verified, large where present, but not applicable to the band source.** Kabane (arXiv 2412.07437) measured F1 of 95.0 percent under correct post-split sampling against 99.97 percent when SMOTE preceded the split. Hayat and Magnier (arXiv 2506.02703) catalog the same failure across the literature and conclude "synthetic data in the dataset may overstate performance." Our weighting-only rule is correct and costs measured performance relative to leaky comparators. **Magnitude where present: +0.10 or more,** which is why our preregistration already treats results above 0.95 as artifacts.

### Corroborating datapoint from the other direction

The AutoXGB benchmark reports **AP 0.782** for tuned AutoXGB and **0.776** for a RandomizedSearchCV XGBoost baseline on ULB, explicitly using `average_precision_score`. Our 0.8296 with proper step-wise AP **exceeds** both. This is the single most protocol-comparable external number located, and it places our result above, not below, the clean-protocol reference.

**Synthesis (inferred).** Summing the mid-points of the six factors that apply to the band source (metric +0.025, training volume +0.02, duplicates +0.01) gives roughly +0.055 of upward bias. Applied to the band's 0.855-0.867 range, the implied clean-protocol equivalent is approximately **0.80 to 0.81**. Our 0.8296 sits above that. Confidence: medium. The arithmetic is additive and the factors may interact sub-additively, but the direction of every term is well established.

## Q4: Is there a well-cited "proper protocol" reference?

**Yes, and it is the ULB group's own.**

**Le Borgne, Siblini, Lebichot and Bontempi (2022), "Reproducible Machine Learning for Credit Card Fraud Detection - Practical Handbook," Universite Libre de Bruxelles.** This is authored by the same lab (Bontempi's MLG at ULB) that released the Kaggle dataset, making it the closest thing to a primary methodological source.

What it prescribes, all of which our protocol already satisfies: step-wise AP via `average_precision_score`; an explicit prohibition on trapezoidal or interpolated PR-AUC; repeated evaluation with reported standard deviations, treating single evaluations as unreliable; and model selection on validation, acknowledging that validation-optimal parameters differ from test-optimal ones.

**Important caveat, verified.** The handbook's headline AP table (Logistic 0.606, RF 0.658, XGBoost 0.639 on test) is computed on **simulated companion data**, not the real ULB Kaggle file, under a temporal train/delay/test protocol. Those numbers are **not** valid comparators for our 0.8296. Our prior report's table (lines 25-27) lists them adjacent to ULB rows, inviting exactly that misreading.

Dal Pozzolo, Caelen, Johnson and Bontempi (2015), IEEE SSCI, is the canonical dataset citation and the origin of the "use AUPRC for this dataset" recommendation. It addresses probability drift under undersampling and publishes no comparable tuned-GBDT AUPRC.

**Conclusion for Q4:** an authoritative protocol reference exists and we already comply with it. There is **no** authoritative source reporting tuned GBDT AUPRC of 0.85-0.88 on real ULB data under a clean multi-seed step-wise-AP protocol.

## Amendment recommendation

**Recommendation: amend to add one labeled exploratory protocol-sensitivity analysis. Do not change the G0 criterion.**

Rationale. The preregistration is explicit (section 11) that an amendment "may NEVER change a gate's pass/fail criterion." G0 was set at 0.85 and our observed 0.8296 falls below it. That outcome must be **reported as committed**. Lowering the threshold after observation would be a deviation and would damage the exact methodological credibility this submission rests on.

But G0 is a *pipeline-honesty* gate: its stated purpose is to detect a defective pipeline. This research establishes that its 0.85 threshold was calibrated against a band primary sources do not support, and which our own prior report declined to treat as citable. A gate firing because its reference value was wrong is a false positive about pipeline defect. The correct response is to keep the score as recorded and add diagnostic evidence separating "pipeline is broken" from "reference band was too high."

**Proposed amendment A7 (exploratory, reporting-only, zero metered seconds):**

Add a **protocol-sensitivity ladder** on ULB, tuned XGBoost only, 10 seeds, reported as exploratory and never substituted for the primary cell:

1. **Cell S1, metric sensitivity.** Recompute test AUPRC on the *existing* frozen predictions using trapezoidal `auc(recall, precision)` alongside step-wise AP. No refit needed. This directly measures, on our own data, the single largest suspected component of the gap. If the trapezoidal value lands at or above 0.85, the gap is substantially a metric-definition artifact and the pipeline is vindicated.
2. **Cell S2, duplicate-retained sensitivity.** Rerun the frozen pipeline with duplicates retained before splitting, everything else identical. Reported as a labeled contrast, never as a headline. This is the number the literature is implicitly reporting, and it produces the first published measurement of the dedupe effect on ULB AUPRC, which Q1 shows does not currently exist.
3. **Cell S3, split-ratio sensitivity.** Rerun at 80/10/10 (preserving a dedicated validation fold for early stopping, so no protocol violation) to isolate the training-volume term.

Cost: three cheap classical reruns, no Dirac-3 time, no change to any gate, arm, statistic, or budget. All three are pure additions under section 11's allowance for amendments that "add exploratory analyses."

**Reporting language proposed for the gate table:** G0 outcome recorded as **fail-as-committed**, with a footnote that the 0.85 threshold derived from a literature band which subsequent primary-source research (this document) could not corroborate, and that sensitivity cells S1 to S3 quantify the protocol differences involved. This is more credible to reviewers than a passing gate would have been, because it demonstrates the preregistration working as designed.

**Secondary note.** Correct the adjacency problem in `research-baselines-best-practices.md` lines 25-29 at the next legitimate editing opportunity: the handbook's 0.606/0.639/0.658 AP figures are on simulated data and must be labeled as such so they are never read as ULB comparators. Flagged here only; this document changes no other file, per instruction.

## Sources

- [scikit-learn, average_precision_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html)
- [Fraud Detection Handbook, Ch.4 Threshold-free metrics](https://fraud-detection-handbook.github.io/fraud-detection-handbook/Chapter_4_PerformanceMetrics/ThresholdFree.html)
- [Fraud Detection Handbook, Ch.5 Model selection](https://fraud-detection-handbook.github.io/fraud-detection-handbook/Chapter_5_ModelValidationAndSelection/ModelSelection.html)
- [Fraud Detection Handbook, Ch.3 Baseline modeling](https://fraud-detection-handbook.github.io/fraud-detection-handbook/Chapter_3_GettingStarted/BaselineModeling.html)
- [Davis and Goadrich, ICML 2006](https://mark.goadrich.com/articles/davisgoadrichcamera2.pdf)
- [Tran-The, "The wrong and right way to approximate AUPRC," 2022](https://towardsdatascience.com/the-wrong-and-right-way-to-approximate-area-under-precision-recall-curve-auprc-8fd9ca409064/)
- [Brownlee, "Imbalanced Classification with the Fraudulent Credit Card Transactions Dataset"](https://machinelearningmastery.com/imbalanced-classification-with-the-fraudulent-credit-card-transactions-dataset/)
- [Albalawi and Dardouri, Frontiers in AI 2025, DOI 10.3389/frai.2025.1643292](https://pmc.ncbi.nlm.nih.gov/articles/PMC12540476/)
- [Kabane, "Impact of Sampling Techniques and Data Leakage on XGBoost Performance," arXiv 2412.07437](https://arxiv.org/html/2412.07437v1)
- [Hayat and Magnier, "Data Leakage and Deceptive Performance," arXiv 2506.02703](https://arxiv.org/html/2506.02703)
- [Han and Wu, "Validation-Stage Combinatorial Fusion Analysis," arXiv 2606.10393](https://arxiv.org/abs/2606.10393)
- [Leung, Credit Card Fraud Detection AutoXGB](https://github.com/kennethleungty/Credit-Card-Fraud-Detection-AutoXGB)
- [Dal Pozzolo et al., "Calibrating Probability with Undersampling for Unbalanced Classification," IEEE SSCI 2015](https://www.researchgate.net/publication/283349138_Calibrating_Probability_with_Undersampling_for_Unbalanced_Classification)
