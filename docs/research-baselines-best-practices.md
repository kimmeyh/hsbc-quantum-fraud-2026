# Classical Baselines and Benchmark Best Practices for Fraud Detection

Research report supporting the 2026 competition submission. Covers published state-of-the-art results for the three benchmark datasets, and a cross-cutting methodological checklist for the benchmark protocol.

Prepared 2026-08-30. All claims carry source URLs. Items that could not be verified against a primary source are flagged explicitly.

---

## Summary

The defensible published ceilings are roughly AUPRC 0.85 to 0.88 on ULB, AUPRC 0.64 to 0.67 on IEEE-CIS, and AUC-ROC 0.995 to 0.998 on Sparkov, which is effectively saturated. A large share of the published fraud-detection literature is unusable as a reference point because resampling was applied before the train and test split, producing inflated metrics. The IEEE-CIS competition was scored on AUC-ROC only, so no winning AUPRC exists to cite; the AUPRC figures below come from independent leakage-free reproductions and must be attributed as such.

For the protocol itself, four points dominate. Fit every transform inside the training fold. Prefer class weighting over resampling, and report calibration alongside discrimination. Compute AUPRC as a step-wise average precision, never by trapezoidal interpolation. Give every model family the same tuning budget, and report every headline number with a confidence interval.

---

# Part 1: Best published results per dataset

## 1.1 ULB European Cardholder credit card fraud

Dataset: Kaggle `mlg-ulb/creditcardfraud`. 284,807 transactions, 492 frauds (0.172 percent), 30 features. Features V1 to V28 are PCA components; only `Time` and `Amount` are in original units. The data covers two days of September 2013.

| Source and setting | Model | AUC-ROC | AUPRC (AP) |
|---|---|---|---|
| Fraud-Detection Handbook, temporal train/delay/test split, simulated companion data | Random Forest | 0.867 | 0.658 |
| Same protocol (SIMULATED data, not ULB) | XGBoost | 0.862 | 0.639 |
| Same protocol (SIMULATED data, not ULB) | Logistic Regression | 0.871 | 0.606 |
| Same protocol (SIMULATED data, not ULB) | Decision Tree, depth 2 | 0.763 | 0.496 |
| Commonly reported range, stratified split, tuned `scale_pos_weight`, no resampling -- NOT CORROBORATED by primary sources (F21 research 2026-09-03: probable origin is a tutorial using trapezoidal PR-AUC, no held-out test fold, no dedupe; clean-protocol equivalent ~0.80-0.81; AutoXGB step-wise AP 0.78) | XGBoost / LightGBM | approx. 0.97 to 0.98 | approx. 0.85 to 0.88 (see docs/research-ulb-baseline-protocols.md) |
| Pre-split resampling, leaky, do not emulate | XGBoost | 0.9997 | reported above 0.99 |

Sources: [Fraud-Detection Handbook baseline modeling](https://fraud-detection-handbook.github.io/fraud-detection-handbook/Chapter_3_GettingStarted/BaselineModeling.html), [Impact of Sampling Techniques and Data Leakage on XGBoost](https://arxiv.org/html/2412.07437v1), [Data Leakage and Deceptive Performance](https://arxiv.org/pdf/2506.02703).

The honest ceiling is approximately AUPRC 0.85 to 0.88 and AUC-ROC 0.97 to 0.98 under a clean stratified split with no resampling before the split. Results above roughly 0.95 AUPRC are leakage artifacts. Two studies document the inflation directly. Pre-split sampling produced precision 99.94 percent, recall 100 percent and F1 99.97 percent, against 97 percent, 93 percent and 95 percent for the same model with post-split sampling. A separate leakage audit reports that leaky protocols show AUC near 0.99 and AUPRC near 0.95 where correct protocols give substantially lower values.

Because the 28 principal features are already PCA components, feature engineering is largely closed off on this dataset. The available levers are the treatment of `Amount` and `Time`, the imbalance handling strategy, and threshold selection.

**Tuning practice.** The dataset originates with the ULB Machine Learning Group, whose own handbook mandates AUPRC as the primary metric. At 0.172 percent prevalence the average-precision baseline is 0.00172, while the ROC baseline remains 0.5 regardless of imbalance. The handbook argues that ROC is actively misleading in this setting because investigators can review only about 0.1 to 1 percent of transactions, so "99.9 percent of what is represented on the ROC curve has little relevance from the perspective of an operational fraud detection system." Current best practice is to use `scale_pos_weight` in XGBoost, or exactly one of `is_unbalance` or `scale_pos_weight` in LightGBM, in preference to SMOTE; to early stop on `aucpr` or `average_precision`; and to select the decision threshold on a validation fold rather than on test. Note that the two-day span of this dataset makes a strict temporal split weak, which should be stated rather than overclaimed.

Source: [Fraud-Detection Handbook, threshold-free metrics](https://fraud-detection-handbook.github.io/fraud-detection-handbook/Chapter_4_PerformanceMetrics/ThresholdFree.html).

## 1.2 IEEE-CIS Fraud Detection

Dataset: Kaggle competition `ieee-fraud-detection`. 590,540 training rows, up to 393 features, 3.5 percent fraud.

| Source and setting | Model | AUC-ROC | AUPRC |
|---|---|---|---|
| Kaggle first place (FraudSquad), private leaderboard | CatBoost + LightGBM + XGBoost blend | **0.9459** (public 0.9677) | not reported |
| First place, single model, public / private | CatBoost | 0.9639 / 0.9408 | not reported |
| First place, single model, public / private | LightGBM | 0.9617 / 0.9384 | not reported |
| First place, single model, public / private | XGBoost | 0.9602 / 0.9324 | not reported |
| Amazon Fraud Dataset Benchmark, temporal 95/5 split | AFD TFI | 0.940 | not reported |
| Amazon FDB, same split | Auto-sklearn | 0.932 | not reported |
| Leakage-free 60/20/20 stratified split, tuned on AUPRC | LightGBM | 0.9343 | **0.6480** |
| Same protocol | XGBoost | 0.9335 | 0.6402 |
| Same protocol | Random Forest | 0.9048 | 0.5982 |
| Same protocol | TabNet | 0.8717 | 0.4161 |
| Same protocol, best fusion | Random Forest + XGBoost + LightGBM | 0.9405 | 0.6699 |

Sources: [Kaggle first place solution part 2](https://www.kaggle.com/competitions/ieee-fraud-detection/writeups/fraudsquad-1st-place-solution-part-2), [NVIDIA writeup](https://developer.nvidia.com/blog/leveraging-machine-learning-to-detect-fraud-tips-to-developing-a-winning-kaggle-solution/), [Amazon Fraud Dataset Benchmark](https://arxiv.org/html/2208.14417v2), [Validation-Stage Combinatorial Fusion Analysis](https://arxiv.org/html/2606.10393).

The competition metric was AUC-ROC alone. No AUPRC was ever published for the winning solution. The AUPRC values near 0.65 come from an independent leakage-free reproduction and are the realistic reference point for a benchmark that reports AUPRC at 3.5 percent prevalence. They must be attributed to that reproduction, not to the competition.

### The winning solution's feature engineering

The decisive insight was recovering client identity from anonymized fields. The team constructed a unique identifier as `UID = card1_addr1 + '_' + floor(day - D1)`. This works because D1 represents days since the card began being used, so `TransactionDay - D1` is approximately constant for a given card. The same normalization was applied to the other timedelta columns, computing `D1n = D1 - TransactionDT/86400` for D2, D4, D10, D11 and D15. This normalization alone moved validation AUC from 0.923 to 0.934.

Roughly 47 aggregation features were then built by grouping over the UID: mean and standard deviation of `TransactionAmt`, means of the C1 through C14 count columns and the M1 through M9 match columns, aggregates over D4, D9, D10 and D15, and frequency or count encodings of combinations such as `card1_addr1` and `card1_addr1_P_emaildomain`. Adding these UID aggregates moved local cross-validation from 0.9363 to 0.9472.

The critical design decision is that **the UID itself was excluded from training**. Only its aggregates entered the model. This is what allows the model to learn transferable client-behaviour regularities rather than memorizing identifiers that will not recur in the test period.

The V columns were reduced from 399 to approximately 138 by grouping columns on their missing-value patterns, computing Pearson correlations within each group, retaining columns correlated above 0.75, and keeping the member with the highest cardinality from each correlated cluster. A final post-processing step replaced each client's individual predictions with that client's mean prediction.

Reported hyperparameters for the XGBoost component were `max_depth=12`, `learning_rate=0.02`, `subsample=0.8`, `colsample_bytree=0.4`, a large `n_estimators` with early stopping at 100 rounds, and GPU histogram tree construction.

### Covariate-shift handling

Validation used GroupKFold with calendar month as the group, so training data always preceded validation data in time. Feature selection used a time-consistency check: train a single-feature model on the first month, test it on the last month, and discard any feature that fails to achieve AUC above 0.5 on both. This removed C3, M5, id_07, id_08, id_14, id_21 through id_27, id_30, and id_32 through id_34, all features whose relationship to the target drifts across the period.

Adversarial validation is the general form of this technique. Train a classifier to distinguish training rows from test rows. An AUC near 0.5 indicates matched distributions; an AUC near 1.0 indicates shift. The remedy is to inspect feature importance in that adversarial classifier and recursively drop the highest-importance features until the AUC returns toward 0.5.

Sources: [NVIDIA writeup](https://developer.nvidia.com/blog/leveraging-machine-learning-to-detect-fraud-tips-to-developing-a-winning-kaggle-solution/), [Chris Deotte, XGB Fraud with Magic](https://www.kaggle.com/code/cdeotte/xgb-fraud-with-magic-0-9600), [IEEE-CIS top 5 percent solution](https://towardsdatascience.com/ieee-cis-fraud-detection-top-5-solution-5488fc66e95f/), [Managing dataset shift by adversarial validation](https://arxiv.org/abs/2112.10078).

### A defensible reduced version

The goal here is a fair, reproducible classical baseline, not a leaderboard win. A reduced version should retain the following: D-column time normalization; a single UID built from `card1`, `addr1` and `D1`; a small fixed and pre-declared set of UID aggregations covering `TransactionAmt` mean and standard deviation, the C-column means, and a handful of count encodings; frequency encoding of card, address and email-domain combinations; and V-column reduction based on missing-value grouping and within-group correlation.

It should drop the client-mean post-processing step and the multi-model blend, both of which are competition-specific rather than methodologically general. The time-consistency filter should be applied inside the training folds only, never on the full dataset.

This reduced configuration should land near AUC-ROC 0.93 to 0.94 and AUPRC 0.64 to 0.67, which is the leakage-free reproduction band, rather than the 0.9459 blend result.

## 1.3 Sparkov synthetic fraud

Dataset: Kaggle `kartik2112/fraud-detection`, generated by the Sparkov Data Generation tool. The distribution ships a fixed temporal split of 1,296,675 training rows and 555,719 test rows, simulating 1000 customers against 800 merchants.

| Source and setting | Model | AUC-ROC | AUPRC |
|---|---|---|---|
| Amazon FDB (`sparknov`), temporal split, 1,296,675 train / 20,000 test | AFD OFI | **0.998** | not reported |
| Same | AutoGluon | 0.997 | not reported |
| Same | H2O | 0.997 | not reported |
| Same | Auto-sklearn | 0.995 | not reported |

Sources: [Amazon Fraud Dataset Benchmark](https://arxiv.org/html/2208.14417v2), [FDB repository](https://github.com/amazon-science/fraud-dataset-benchmark), [Sparkov Data Generation](https://github.com/namebrandon/Sparkov_Data_Generation), [Kaggle dataset](https://www.kaggle.com/datasets/kartik2112/fraud-detection).

**Sparkov is effectively saturated at AUC-ROC 0.995 to 0.998.** There is no headroom left in that metric to distinguish model families.

**Tuning practice and an important caveat.** Report AUPRC and recall at a fixed alert rate on this dataset, not AUC-ROC, since the latter cannot separate competent models at this level. More importantly, the literature's own caution should be reproduced in the preregistration: classifiers perform very well on this simulated data but substantially worse on real-world data, because the generator's rules are deterministic and are learned quickly. Sparkov should therefore be treated as a pipeline and sanity check that confirms the implementation is correct, not as evidence of real-world superiority. Substantive conclusions should rest on IEEE-CIS and ULB.

## 1.4 A caution on the wider literature

Much of the published ULB literature cannot serve as a state-of-the-art reference. Papers reporting ROC-AUC of 1.0, recall of 100 percent, or AUPRC above 0.99 with SMOTE have generally applied resampling before the split, or evaluated against a synthetically balanced test set. Such results are excluded from the tables above. One widely circulated tutorial applies SMOTE to the full dataset and then reports that "fraudulent transactions are 50.00 percent of the test set," which is a direct statement that the test set was contaminated. The preregistration should state which prior results it treats as unreliable and why.

---

# Part 2: Benchmark protocol checklist

Applicable to any algorithm and any dataset in this study.

### Feature analysis and selection

1. **Fit every transform inside the training fold.** Scalers, imputers, target and frequency encoders, and feature selectors must be fit on training data only and then applied to validation and test. Scaling before splitting is a documented leakage source that inflates reported AUC. Source: [Data Leakage and Deceptive Performance](https://arxiv.org/pdf/2506.02703).

2. **Perform feature selection inside the cross-validation loop.** Selecting features on the full dataset and then cross-validating is selection leakage and biases estimates optimistically. Cawley and Talbot show the selected configuration otherwise "retain[s] a partial memory of the data that now form the test partition." Source: [Cawley and Talbot, JMLR 2010](https://www.jmlr.org/papers/v11/cawley10a.html).

3. **Screen for target leakage and covariate drift together.** Run adversarial validation, where a classifier trained to separate train from test should score near AUC 0.5. Apply per-feature time-consistency checks by training early and testing late, discarding features that fail to exceed AUC 0.5. Run both inside the training folds. Source: [Managing dataset shift by adversarial validation](https://arxiv.org/abs/2112.10078).

### Leakage prevention

4. **Never resample before splitting.** Applying SMOTE or undersampling to the full dataset copies minority-class information across the train and test boundary. Measured inflation on ULB was precision 99.94 versus 97 percent, recall 100 versus 93 percent, and F1 99.97 versus 95 percent. Source: [Impact of Sampling Techniques and Data Leakage](https://arxiv.org/html/2412.07437v1).

5. **Respect temporal ordering.** For IEEE-CIS and Sparkov, split and cross-validate temporally, using GroupKFold by month or a prequential rolling-origin scheme with a delay period reflecting label feedback lag. Random k-fold on temporal fraud data leaks future information. Source: [Fraud-Detection Handbook validation strategies](https://fraud-detection-handbook.github.io/fraud-detection-handbook/Chapter_5_ModelValidationAndSelection/ValidationStrategies.html).

6. **Deduplicate before splitting.** Exact and near-duplicate rows that straddle the train and test boundary inflate every metric. Report duplicate counts per dataset.

### Missing and bad data handling

7. **Handle missing values according to model family.** Gradient-boosted decision trees learn a default branch direction for missing values during training, so pass NaN through rather than imputing. Avoid sentinel values such as -999 that can collide with real values or distort split points. Note that XGBoost treats zero as missing in a scipy sparse matrix but as a valid split value in a dense array, so the same data in two containers yields different models. Source: [XGBoost FAQ](https://xgboost.readthedocs.io/en/stable/faq.html).

8. **Know each library's missing-value conventions.** LightGBM treats negative categorical values as missing and treats categories unseen during training as missing; `use_missing` defaults to true and `zero_as_missing` defaults to false. Source: [LightGBM Advanced Topics](https://lightgbm.readthedocs.io/en/latest/Advanced-Topics.html).

9. **Use each library's native categorical support correctly.** LightGBM applies the Fisher optimal-split method over integer-coded categories and documents an overfitting risk controlled by `min_data_per_group` (default 100), `cat_smooth` (default 10.0), `cat_l2` (default 10.0) and `max_cat_threshold` (default 32); its documentation notes that for high-cardinality features, treating them as numeric often performs better. CatBoost uses ordered target statistics computed only from preceding rows under random permutations, which is the mechanism that prevents target leakage, with `one_hot_max_size` switching low-cardinality features to one-hot; its documentation explicitly warns against one-hot encoding during preprocessing. XGBoost requires `enable_categorical` with the `hist` or `approx` tree method, and uses `max_cat_to_onehot` and `max_cat_threshold` to control partition-based splits. Sources: [LightGBM Advanced Topics](https://lightgbm.readthedocs.io/en/latest/Advanced-Topics.html), [CatBoost categorical features](https://catboost.ai/docs/en/features/categorical-features), [CatBoost ordered target statistics](https://catboost.ai/docs/en/concepts/algorithm-main-stages_cat-to-numberic), [XGBoost categorical tutorial](https://xgboost.readthedocs.io/en/stable/tutorials/categorical.html).

10. **Set CatBoost's boosting type deliberately.** Ordered boosting, the permutation-driven scheme that CatBoost introduced specifically to counter "a prediction shift caused by a special kind of target leakage present in all currently existing implementations of gradient boosting," is the default only for CPU datasets under 50,000 objects. All three datasets in this study exceed that, so CatBoost will default to `Plain`. If the ordered-boosting property is being claimed, it must be set explicitly. Sources: [CatBoost paper](https://arxiv.org/abs/1706.09516), [CatBoost common parameters](https://catboost.ai/docs/en/references/training-parameters/common).

### Class imbalance handling

11. **Prefer class weighting over resampling.** Use `scale_pos_weight` in XGBoost and LightGBM, or `auto_class_weights` in CatBoost. In LightGBM, `is_unbalance` and `scale_pos_weight` are mutually exclusive; the documentation states to choose only one. In CatBoost, `auto_class_weights`, `class_weights` and `scale_pos_weight` are likewise mutually exclusive. Sources: [LightGBM Parameters](https://lightgbm.readthedocs.io/en/latest/Parameters.html), [CatBoost common parameters](https://catboost.ai/docs/en/references/training-parameters/common).

12. **Treat SMOTE-style resampling as discouraged, and justify it if used.** Resampling changes ranking little, with PR-AUC moving within roughly plus or minus 0.03, while damaging calibration. Random undersampling is considerably worse than SMOTE, with expected calibration error rising from 0.008 to 0.395 at an imbalance ratio of 70. Source: [The Hidden Cost of Resampling](https://arxiv.org/html/2606.29720).

13. **Recognize that weighting itself carries a calibration cost.** XGBoost's documentation states that if you care about predicted probability rather than ranking, you cannot rebalance the dataset, and should instead set `max_delta_step` to a finite value such as 1. LightGBM's documentation independently warns that enabling `is_unbalance` or `scale_pos_weight` "will also result in poor estimates of the individual class probabilities." Two clinical-prediction studies found that imbalance correction produced strong miscalibration without improving discrimination, and that the damage was not always correctable by recalibration. This justifies reporting an uncorrected model alongside any weighted variant. Sources: [XGBoost parameter tuning](https://xgboost.readthedocs.io/en/stable/tutorials/param_tuning.html), [LightGBM Parameters](https://lightgbm.readthedocs.io/en/latest/Parameters.html), [van den Goorbergh et al., JAMIA 2022](https://academic.oup.com/jamia/article/29/9/1525/6605096), [Carriero et al., Statistics in Medicine 2025](https://arxiv.org/abs/2404.19494).

### Training and validation

14. **Separate the early-stopping set from the test set.** Early stop on a dedicated validation fold, never on test. The stopping iteration is a fitted hyperparameter, so selecting it on the evaluation partition produces the optimistic bias Cawley and Talbot formalize, measured at 0.02 to 1.19 percentage points and optimistic on all 13 of their datasets. Source: [Cawley and Talbot, JMLR 2010](https://www.jmlr.org/papers/v11/cawley10a.html).

15. **Avoid the silent early-stopping traps.** XGBoost's `train()` returns the model from the last iteration, not the best one, so `best_iteration` with `iteration_range` or the `EarlyStopping` callback is required; with multiple eval sets it silently uses the last. CatBoost requires `use_best_model` together with a validation set, with `od_wait` defaulting to 20. LightGBM's `early_stopping` callback exposes `first_metric_only` and `min_delta`. Sources: [XGBoost Python intro](https://xgboost.readthedocs.io/en/stable/python/python_intro.html), [CatBoost overfitting detector](https://catboost.ai/docs/en/concepts/overfitting-detector), [LightGBM early_stopping](https://lightgbm.readthedocs.io/en/latest/pythonapi/lightgbm.early_stopping.html).

16. **Report the final tree count and how it was derived.** With cross-validation, early stopping happens independently in each fold; the standard practice is to take the mean or the argmax of the mean validation curve across folds, then refit on the full training set at that fixed count. Report the count, the patience, and the monitored metric.

17. **Equalize the tuning budget across model families.** Give XGBoost, LightGBM and CatBoost the same number of search trials and the same search method, and state the budget. Unequal budgets systematically advantage the family with the largest search space, which is the mechanism Cawley and Talbot identify when they find biased protocols favour the combinations most prone to overfitting in model selection. Defensible anchors from the benchmark literature: Grinsztajn et al. used approximately 400 random-search iterations per dataset, reporting performance as a function of iteration count so that budget matching is visible rather than assumed; Shwartz-Ziv and Armon used 1,000 HyperOpt steps; McElfresh et al. used 30 Optuna trials. Sources: [Grinsztajn et al., NeurIPS 2022](https://arxiv.org/abs/2207.08815), [Cawley and Talbot](https://www.jmlr.org/papers/v11/cawley10a.html).

18. **Prefer random or TPE search over grid search.** Bergstra and Bengio show randomly chosen trials are more efficient because objective functions of interest have low effective dimensionality, and that grid search is reliable only in one or two dimensions. Note that the widely repeated claim that 60 random trials reaches the top 5 percent of configurations with 95 percent probability **does not appear in that paper and should not be cited to it**; the paper contains only the analogous algebra for a 1 percent target volume. Source: [Bergstra and Bengio, JMLR 2012](https://jmlr.org/papers/v13/bergstra12a.html).

19. **Tune on the right metric.** Optimize AUPRC, via `aucpr` in XGBoost, `average_precision` in LightGBM, or `PRAUC` in CatBoost, rather than accuracy or ROC, at these prevalences.

20. **Choose the validation architecture deliberately.** With a large dataset and a temporal holdout, a single well-constructed time-based train, validation and test split is defensible and much cheaper than nested cross-validation. Nested cross-validation earns its cost when n is small or the selection space is large. Note that Bengio and Grandvalet proved no universal unbiased estimator of k-fold cross-validation variance exists, so all variance estimates from folds are heuristics. State which scheme was used and why. Sources: [scikit-learn nested CV](https://scikit-learn.org/stable/auto_examples/model_selection/plot_nested_cross_validation_iris.html), [Bengio and Grandvalet, JMLR 2004](https://www.jmlr.org/papers/v5/grandvalet04a.html).

### Probability calibration

21. **Calibrate on genuinely held-out data.** Use `CalibratedClassifierCV`. scikit-learn warns that using training-data outputs to fit the calibrator "would thus result in a biased calibrator that maps to probabilities closer to 0 and 1 than it should," meaning the failure mode is overconfidence, the opposite of the intent. Source: [scikit-learn calibration guide](https://scikit-learn.org/stable/modules/calibration.html).

22. **Choose the calibration method by effective sample size.** scikit-learn documents isotonic regression as performing as well as or better than sigmoid when there are more than approximately 1,000 samples. In fraud the binding constraint is the number of positives, not rows: 1,000 rows at 0.2 percent prevalence yields two frauds, far too few for isotonic. Use Platt scaling below that threshold. Isotonic recalibration has been measured to cut expected calibration error from 0.061 to 0.025 at a cost of roughly 0.002 AUC. Sources: [scikit-learn calibration guide](https://scikit-learn.org/stable/modules/calibration.html), [The Hidden Cost of Resampling](https://arxiv.org/html/2606.29720).

23. **Do not present the Brier score as a calibration metric.** By Murphy's decomposition it combines reliability, resolution and uncertainty. scikit-learn states that "a lower Brier loss ... does not necessarily mean a better calibrated model, it could also mean a worse calibrated model with much more discriminatory power." Either report the decomposition, or pair Brier with an explicit calibration measure. At 0.172 percent prevalence the uncertainty term dominates and all Brier scores will be small and close together. Sources: [scikit-learn calibration guide](https://scikit-learn.org/stable/modules/calibration.html), [Murphy 1973](https://doi.org/10.1175/1520-0450(1973)012<0595:ANVPOT>2.0.CO;2).

24. **Report ECE with equal-mass binning and a stated bin count, alongside a reliability diagram.** Binned ECE is sensitive to implementation, has non-negligible statistical bias, and "systematically predicts large errors for perfectly calibrated models"; equal-mass binning consistently outperforms equal-width. At fraud prevalences equal-width binning is actively misleading because nearly every sample falls in the first bin. Sources: [Roelofs et al., AISTATS 2022](https://proceedings.mlr.press/v151/roelofs22a/roelofs22a.pdf), [Kumar, Liang and Ma, NeurIPS 2019](https://arxiv.org/abs/1909.10155).

### Results presentation

25. **Compute AUPRC as step-wise average precision.** Use `average_precision_score`, never `auc(recall, precision)`. scikit-learn documents that the trapezoidal approach "uses linear interpolation and can be too optimistic." Davis and Goadrich quantify the error on a dataset at 0.76 percent positives, squarely the ULB regime: correct AUC-PR 0.031 against 0.50 by linear interpolation, a sixteen-fold inflation. Note also that XGBoost's own `aucpr` uses continuous interpolation, so it is acceptable for early stopping but the headline reported figure should come from `average_precision_score`. Sources: [scikit-learn average_precision_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html), [Davis and Goadrich, ICML 2006](https://ftp.cs.wisc.edu/machine-learning/shavlik-group/davis.icml06.pdf), [XGBoost parameters](https://xgboost.readthedocs.io/en/latest/parameter.html).

26. **Check for tied prediction scores.** A 2024 survey of ten AUPRC tools used across more than 3,000 studies found AUPRC for identical predictions ranging from 0.416 to 0.684, and identifies scikit-learn as potentially over-optimistic specifically in its linear interpolation across ties, not in the general case. Tree ensembles do produce ties. Report the tie frequency and cross-check against PRROC or torcheval if ties are common. Source: [Chen et al., Genome Biology 2024](https://genomebiology.biomedcentral.com/articles/10.1186/s13059-024-03266-y).

27. **Never compare or average AUPRC across datasets.** The average-precision baseline equals prevalence: 0.0017 for ULB, 0.035 for IEEE-CIS, approximately 0.057 for Sparkov. An AUPRC of 0.30 at 0.2 percent prevalence is a far stronger result than 0.30 at 5 percent. Report the prevalence beside every AUPRC value, or use a normalized form such as (AP minus baseline) divided by (1 minus baseline). AUC-ROC does not have this problem, which is the standard argument for reporting both. Sources: [Saito and Rehmsmeier, PLOS ONE 2015](https://doi.org/10.1371/journal.pone.0118432), [scikit-learn metrics guide](https://scikit-learn.org/stable/modules/model_evaluation.html).

28. **Report thresholded metrics at a stated operating point.** Precision, recall, F1 and confusion matrices depend entirely on the threshold. Select it on validation, for example at a fixed alert budget or top-k, never on test, and disclose it. Consider precision at k, or card precision at 100, as the operationally meaningful metric matching investigator capacity. Source: [Fraud-Detection Handbook](https://fraud-detection-handbook.github.io/fraud-detection-handbook/Chapter_4_PerformanceMetrics/ThresholdFree.html).

29. **Give every headline number a confidence interval.** Use a stratified BCa bootstrap with approximately 2,000 resamples for AUPRC and AUC-ROC. DiCiccio and Efron state that 2,000 replications is "10 times too many for estimating a standard error, but not too many for the more delicate task of setting confidence intervals." BCa is preferred over the percentile method because it is second-order accurate and transformation invariant, which matters for bounded skewed statistics such as AUPRC. Stratify by class: at 0.172 percent prevalence an unstratified resample can contain almost no positives. Source: [DiCiccio and Efron, Statistical Science 1996](https://projecteuclid.org/journals/statistical-science/volume-11/issue-3/Bootstrap-confidence-intervals/10.1214/ss/1032280214.full).

30. **Use Wilson intervals for precision and recall, and the bootstrap for F1.** Brown, Cai and DasGupta found "the chaotic coverage properties of the Wald interval are far more persistent than is appreciated" and recommend Wilson. This matters acutely for recall, whose denominator on ULB is only about 100 frauds in a test fold. F1 is a ratio of dependent counts with no closed-form binomial interval, so it requires the bootstrap. Sources: [Brown, Cai and DasGupta, Statistical Science 2001](https://projecteuclid.org/journals/statistical-science/volume-16/issue-2/Interval-Estimation-for-a-Binomial-Proportion/10.1214/ss/1009213286.full), [statsmodels proportion_confint](https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.proportion_confint.html).

31. **Report seed and split variation, randomizing multiple sources.** Run at least five repetitions and report the distribution rather than a single value. Bouthillier et al. recommend randomizing as many sources as possible, including initialization, data sampling, splits and hyperparameter optimization, because less-correlated runs reduce the standard error of the mean through a bagging-like effect. Vary splits, not only seeds. Source: [Bouthillier et al., MLSys 2021](https://arxiv.org/abs/2103.03098).

32. **Use paired tests on identical folds and seeds for within-dataset comparisons.** Dietterich found the paired t-test on repeated random resampling has Type I error high enough that it "should never be used," and that the paired t-test on 10-fold cross-validation folds is also elevated; he recommends the 5x2cv paired t-test, or McNemar's test where refitting is expensive. Nadeau and Bengio's corrected resampled t-test, which scales the variance by (1/J + n2/n1), is the inexpensive correction. For two correlated ROC AUCs use the DeLong test; note it does not apply to AUPRC, which requires a paired bootstrap. Sources: [Dietterich 1998](https://doi.org/10.1162/089976698300017197), [Nadeau and Bengio 2003](https://link.springer.com/article/10.1023/A:1024068626366), [DeLong et al. 1988](https://doi.org/10.2307/2531595), [pROC roc.test](https://www.rdocumentation.org/packages/pROC/versions/1.19.0.1/topics/roc.test).

33. **For cross-dataset comparison, use Friedman followed by pairwise Wilcoxon with Holm correction, not Nemenyi.** Demsar originally recommended Friedman with Nemenyi post-hoc, but Benavoli, Corani and Mangili later showed the mean-ranks test gives pool-dependent verdicts: "the difference between A and B could be declared significant if the pool comprises algorithms C, D, E and not significant if the pool comprises algorithms F, G, H." They recommend tests whose decision depends only on the two algorithms compared. A critical-difference diagram may still be drawn for communication, but significance claims should come from the pairwise tests. Sources: [Demsar, JMLR 2006](https://www.jmlr.org/papers/v7/demsar06a.html), [Benavoli, Corani and Mangili, JMLR 2016](https://jmlr.org/papers/volume17/benavoli16a/benavoli16a.pdf).

34. **Recognize that three datasets is too few for an omnibus test.** Bouthillier et al. note Demsar's tests "are hardly applicable on small sets of datasets," since the dataset count is the sample size and three to five yields very limited power. With N equal to 3, base cross-dataset conclusions on within-dataset paired tests across seeds and folds, or on a Bayesian signed-rank test with a stated region of practical equivalence, or on the probability that A outperforms B with a percentile bootstrap interval. Sources: [Bouthillier et al., MLSys 2021](https://arxiv.org/abs/2103.03098), [Benavoli et al., JMLR 2017](http://www.jmlr.org/papers/v18/16-305.html).

35. **Never average metrics across datasets.** Demsar states that if results on different datasets are not commensurable, "their averages are meaningless," and that averages are susceptible to outliers, allowing excellent performance on one dataset to mask poor performance overall. This compounds with the prevalence-dependence of AUPRC in item 27. Source: [Demsar, JMLR 2006](https://www.jmlr.org/papers/volume7/demsar06a/demsar06a.pdf).

36. **Correct for multiple comparisons and report effect sizes.** With three model families across three datasets and several metrics, apply Holm, which Demsar describes as "more powerful than the Bonferroni-Dunn's" with no additional assumptions. Reserve Benjamini-Hochberg for false-discovery-rate screening of many variants rather than for headline comparisons. Report effect sizes and intervals, not p-values alone. Sources: [Demsar, JMLR 2006](https://www.jmlr.org/papers/v7/demsar06a.html), [statsmodels multipletests](https://www.statsmodels.org/stable/generated/statsmodels.stats.multitest.multipletests.html).

37. **Pin and publish the environment.** Record library versions, seeds, hardware, and the exact hyperparameter search spaces. Gradient-boosting results shift measurably between library versions.

### A note on framing the classical baselines

The claim that gradient-boosted trees beat deep learning on tabular data should be stated carefully, because the 2023 to 2026 literature qualifies it and a knowledgeable reviewer will know this. Grinsztajn et al. found tree-based models remain state of the art on medium-sized data, but tested XGBoost, Random Forest and GradientBoostingTrees, not LightGBM or CatBoost. McElfresh et al., across 176 datasets and 538,650 trained models, concluded the debate is "overemphasized" and that light hyperparameter tuning on a GBDT matters more than the choice between neural networks and GBDTs for about a third of datasets. TabPFN v2 outperforms tuned baselines below 10,000 samples, though it is scoped to small and class-balanced tasks.

The defensible framing is that tuned GBDTs are the benchmark-established baseline for tabular fraud detection, that they are specifically favoured in the regimes characterizing fraud, and that any new method must beat a properly tuned GBDT to be taken seriously. Two findings support the fraud-specific half precisely: McElfresh et al. found GBDTs "much better than NNs at handling skewed or heavy-tailed feature distributions," which describes fraud amounts and velocities, and TabReD found that evaluation on time-based splits changes method rankings relative to random splits, with GBDTs among the best performers.

Sources: [Grinsztajn et al.](https://arxiv.org/abs/2207.08815), [Shwartz-Ziv and Armon](https://arxiv.org/abs/2106.03253), [McElfresh et al.](https://arxiv.org/abs/2305.02997), [TabReD](https://arxiv.org/abs/2406.19380), [TALENT](https://arxiv.org/abs/2407.00956), [A Closer Look at TabPFN v2](https://arxiv.org/abs/2502.17361).

---

# Recommendations for the preregistration

1. **Declare AUPRC, computed as `average_precision_score`, the primary metric on all three datasets**, with AUC-ROC secondary. State explicitly that AUPRC will not be compared or averaged across datasets because its baseline equals prevalence, and report the prevalence beside every value.

2. **Fix and publish the splits now.** Use temporal GroupKFold by month for IEEE-CIS, the shipped fraudTrain and fraudTest temporal split for Sparkov, and a stratified split for ULB with a temporal holdout sensitivity check. State that ULB spans only two days, so temporal splitting is weak there, rather than overclaiming.

3. **Preregister a prohibition on any resampling before splitting**, and default to class weighting over SMOTE. If SMOTE is evaluated at all, run it as a clearly labelled ablation inside training folds only. Report an uncorrected model alongside any weighted variant, since weighting itself degrades calibration.

4. **Fix an equal tuning budget across model families**, for example 100 to 200 Optuna TPE trials per family per dataset, with matched search-space depth and early-stopping patience, and state it as an explicit fairness guarantee. This is the strongest single defence of the claim that the classical baselines are state of the art. Do not cite the "60 trials reaches the top 5 percent" figure: it is folklore and is verified absent from Bergstra and Bengio.

5. **Preregister the IEEE-CIS reduced feature set explicitly**: D-column time normalization, one UID from `card1`, `addr1` and `D1`, a named list of UID aggregations, frequency encodings, and V-column reduction by missing-value grouping, with the UID itself excluded from the model. Commit in advance to no client-mean post-processing and no model blending.

6. **Preregister the time-consistency and adversarial-validation feature filters with their thresholds**, namely discarding features whose single-feature train-early and test-late AUC does not exceed 0.5, and targeting an adversarial AUC near 0.5. Require both to run inside training folds only.

7. **Commit to at least five repetitions with randomized splits as well as seeds**, and to stratified BCa bootstrap confidence intervals with approximately 2,000 resamples for every headline number. Use Wilson intervals for precision and recall, and the bootstrap for F1. Report distributions, not single runs.

8. **Preregister the statistical comparison plan.** Within each dataset, use paired tests on identical folds and seeds, specifically 5x2cv paired t-tests or McNemar where refitting is costly, DeLong for ROC AUC pairs, and a paired bootstrap for AUPRC differences. Across datasets, note that N equal to 3 gives an omnibus test almost no power, and base cross-dataset conclusions on the within-dataset paired results, or on a Bayesian signed-rank test with a stated region of practical equivalence. If an omnibus test is reported at all, use Friedman followed by pairwise Wilcoxon with Holm correction, not Nemenyi. State an effect-size threshold for a meaningful difference.

9. **Add calibration as a reported outcome.** Fit calibration on a held-out fold, choosing Platt scaling unless the positive count supports isotonic. Report a reliability diagram and ECE with equal-mass binning and a stated bin count. If the Brier score is reported, present it as a joint score or give Murphy's decomposition, never as a standalone calibration measure. A quantum-versus-classical comparison reporting only ranking metrics would miss probability quality entirely.

10. **State the Sparkov caveat in advance.** It is near-saturated at AUC-ROC 0.995 to 0.998 and deterministic by construction, so it functions as a pipeline correctness check. Declare that substantive conclusions about fraud-detection performance rest on IEEE-CIS and ULB. Separately, disclose that the Amazon FDB benchmark deliberately reports AUC-ROC alone as "robust against class imbalance," which contradicts the ULB handbook position adopted here, and use that tension as explicit motivation for reporting AUPRC where FDB did not.

---

# Sources

### Datasets and benchmarks
- [ULB creditcardfraud dataset](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud)
- [IEEE-CIS Fraud Detection competition](https://www.kaggle.com/competitions/ieee-fraud-detection)
- [Sparkov / kartik2112 dataset](https://www.kaggle.com/datasets/kartik2112/fraud-detection)
- [Sparkov Data Generation](https://github.com/namebrandon/Sparkov_Data_Generation)
- [Amazon Fraud Dataset Benchmark, arXiv 2208.14417](https://arxiv.org/html/2208.14417v2)
- [Fraud Dataset Benchmark repository](https://github.com/amazon-science/fraud-dataset-benchmark)

### Competition solutions and reproductions
- [NVIDIA, Leveraging ML to Detect Fraud, first place writeup](https://developer.nvidia.com/blog/leveraging-machine-learning-to-detect-fraud-tips-to-developing-a-winning-kaggle-solution/)
- [Kaggle IEEE-CIS first place solution part 2](https://www.kaggle.com/competitions/ieee-fraud-detection/writeups/fraudsquad-1st-place-solution-part-2)
- [Chris Deotte, XGB Fraud with Magic](https://www.kaggle.com/code/cdeotte/xgb-fraud-with-magic-0-9600)
- [IEEE-CIS top 5 percent solution](https://towardsdatascience.com/ieee-cis-fraud-detection-top-5-solution-5488fc66e95f/)
- [Validation-Stage Combinatorial Fusion Analysis, arXiv 2606.10393](https://arxiv.org/html/2606.10393)

### Leakage, validation and imbalance
- [Fraud-Detection Handbook, baseline modeling](https://fraud-detection-handbook.github.io/fraud-detection-handbook/Chapter_3_GettingStarted/BaselineModeling.html)
- [Fraud-Detection Handbook, threshold-free metrics](https://fraud-detection-handbook.github.io/fraud-detection-handbook/Chapter_4_PerformanceMetrics/ThresholdFree.html)
- [Fraud-Detection Handbook, validation strategies](https://fraud-detection-handbook.github.io/fraud-detection-handbook/Chapter_5_ModelValidationAndSelection/ValidationStrategies.html)
- [Impact of Sampling Techniques and Data Leakage on XGBoost, arXiv 2412.07437](https://arxiv.org/html/2412.07437v1)
- [Data Leakage and Deceptive Performance, arXiv 2506.02703](https://arxiv.org/pdf/2506.02703)
- [The Hidden Cost of Resampling, arXiv 2606.29720](https://arxiv.org/html/2606.29720)
- [Managing dataset shift by adversarial validation, arXiv 2112.10078](https://arxiv.org/abs/2112.10078)
- [van den Goorbergh et al., JAMIA 2022](https://academic.oup.com/jamia/article/29/9/1525/6605096)
- [Carriero et al., Statistics in Medicine 2025](https://arxiv.org/abs/2404.19494)

### Library documentation
- [XGBoost parameter tuning](https://xgboost.readthedocs.io/en/stable/tutorials/param_tuning.html)
- [XGBoost parameters](https://xgboost.readthedocs.io/en/latest/parameter.html)
- [XGBoost categorical tutorial](https://xgboost.readthedocs.io/en/stable/tutorials/categorical.html)
- [XGBoost FAQ](https://xgboost.readthedocs.io/en/stable/faq.html)
- [XGBoost Python intro](https://xgboost.readthedocs.io/en/stable/python/python_intro.html)
- [LightGBM Parameters](https://lightgbm.readthedocs.io/en/latest/Parameters.html)
- [LightGBM Parameters Tuning](https://lightgbm.readthedocs.io/en/latest/Parameters-Tuning.html)
- [LightGBM Advanced Topics](https://lightgbm.readthedocs.io/en/latest/Advanced-Topics.html)
- [LightGBM early_stopping](https://lightgbm.readthedocs.io/en/latest/pythonapi/lightgbm.early_stopping.html)
- [CatBoost, transforming categorical features](https://catboost.ai/docs/en/concepts/algorithm-main-stages_cat-to-numberic)
- [CatBoost categorical features](https://catboost.ai/docs/en/features/categorical-features)
- [CatBoost training parameters](https://catboost.ai/docs/en/references/training-parameters/common)
- [CatBoost overfitting detector](https://catboost.ai/docs/en/concepts/overfitting-detector)
- [CatBoost paper, arXiv 1706.09516](https://arxiv.org/abs/1706.09516)

### Tabular benchmarks and hyperparameter search
- [Grinsztajn et al., NeurIPS 2022, arXiv 2207.08815](https://arxiv.org/abs/2207.08815)
- [Shwartz-Ziv and Armon, arXiv 2106.03253](https://arxiv.org/abs/2106.03253)
- [McElfresh et al., NeurIPS 2023, arXiv 2305.02997](https://arxiv.org/abs/2305.02997)
- [TabReD, arXiv 2406.19380](https://arxiv.org/abs/2406.19380)
- [TALENT, arXiv 2407.00956](https://arxiv.org/abs/2407.00956)
- [A Closer Look at TabPFN v2, arXiv 2502.17361](https://arxiv.org/abs/2502.17361)
- [Bergstra and Bengio, JMLR 2012](https://jmlr.org/papers/v13/bergstra12a.html)
- [Optuna, arXiv 1907.10902](https://arxiv.org/abs/1907.10902)
- [Cawley and Talbot, JMLR 2010](https://www.jmlr.org/papers/v11/cawley10a.html)
- [Varma and Simon, BMC Bioinformatics 2006](https://bmcbioinformatics.biomedcentral.com/articles/10.1186/1471-2105-7-91)
- [scikit-learn nested cross-validation](https://scikit-learn.org/stable/auto_examples/model_selection/plot_nested_cross_validation_iris.html)

### Statistical comparison and metric reporting
- [Demsar, JMLR 2006](https://www.jmlr.org/papers/v7/demsar06a.html) ([PDF](https://www.jmlr.org/papers/volume7/demsar06a/demsar06a.pdf))
- [Benavoli, Corani and Mangili, JMLR 2016](https://jmlr.org/papers/volume17/benavoli16a/benavoli16a.pdf)
- [Benavoli et al., JMLR 2017](http://www.jmlr.org/papers/v18/16-305.html)
- [Dietterich, Neural Computation 1998](https://doi.org/10.1162/089976698300017197)
- [Nadeau and Bengio, Machine Learning 2003](https://link.springer.com/article/10.1023/A:1024068626366)
- [Bengio and Grandvalet, JMLR 2004](https://www.jmlr.org/papers/v5/grandvalet04a.html)
- [Garcia and Herrera, JMLR 2008](https://jmlr.org/papers/v9/garcia08a.html)
- [Benjamini and Hochberg, JRSS-B 1995](https://doi.org/10.1111/j.2517-6161.1995.tb02031.x)
- [Bouthillier et al., MLSys 2021](https://arxiv.org/abs/2103.03098)
- [DiCiccio and Efron, Statistical Science 1996](https://projecteuclid.org/journals/statistical-science/volume-11/issue-3/Bootstrap-confidence-intervals/10.1214/ss/1032280214.full)
- [Brown, Cai and DasGupta, Statistical Science 2001](https://projecteuclid.org/journals/statistical-science/volume-16/issue-2/Interval-Estimation-for-a-Binomial-Proportion/10.1214/ss/1009213286.full)
- [DeLong, DeLong and Clarke-Pearson, Biometrics 1988](https://doi.org/10.2307/2531595)
- [pROC roc.test](https://www.rdocumentation.org/packages/pROC/versions/1.19.0.1/topics/roc.test)
- [Davis and Goadrich, ICML 2006](https://ftp.cs.wisc.edu/machine-learning/shavlik-group/davis.icml06.pdf)
- [Chen et al., Genome Biology 2024](https://genomebiology.biomedcentral.com/articles/10.1186/s13059-024-03266-y)
- [Saito and Rehmsmeier, PLOS ONE 2015](https://doi.org/10.1371/journal.pone.0118432)
- [Raschka 2018, model evaluation review](https://arxiv.org/abs/1811.12808)
- [mlxtend paired_ttest_5x2cv](https://rasbt.github.io/mlxtend/user_guide/evaluate/paired_ttest_5x2cv/)
- [statsmodels multipletests](https://www.statsmodels.org/stable/generated/statsmodels.stats.multitest.multipletests.html)
- [statsmodels proportion_confint](https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.proportion_confint.html)
- [scipy.stats.bootstrap](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html)

### Calibration
- [scikit-learn probability calibration guide](https://scikit-learn.org/stable/modules/calibration.html)
- [scikit-learn CalibratedClassifierCV](https://scikit-learn.org/stable/modules/generated/sklearn.calibration.CalibratedClassifierCV.html)
- [scikit-learn average_precision_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html)
- [scikit-learn metrics and scoring guide](https://scikit-learn.org/stable/modules/model_evaluation.html)
- [Murphy 1973, Journal of Applied Meteorology](https://doi.org/10.1175/1520-0450(1973)012<0595:ANVPOT>2.0.CO;2)
- [Roelofs et al., AISTATS 2022](https://proceedings.mlr.press/v151/roelofs22a/roelofs22a.pdf)
- [Kumar, Liang and Ma, NeurIPS 2019](https://arxiv.org/abs/1909.10155)
- [Nixon et al., CVPR Workshops 2019](https://arxiv.org/abs/1904.01685)

---

# Items flagged as unverified

These should not be cited without independent confirmation.

1. The claim that 60 random search trials reaches the top 5 percent of configurations with 95 percent probability is **verified absent** from Bergstra and Bengio 2012. Do not attribute it to that paper.
2. The total compute-hours figure for McElfresh et al. is not stated in the paper. Use the figure of 538,650 models trained instead.
3. Davis and Goadrich theorem numbering was taken from the abstract and body text, not a machine-readable PDF.
4. TabPFN v2 quotations come from the indexed Nature abstract; the full text is paywalled.
5. The stepwise tuning order used by LightGBMTunerCV is not documented; any published ordering is an inference.
6. Shwartz-Ziv and Armon journal page numbers come from secondary metadata.
7. The ULB range of AUPRC 0.85 to 0.88 is corroborated across multiple secondary reports under clean stratified protocols but was not traced to a single peer-reviewed table. Treat it as a range to be reproduced in this study, not as a citable point estimate.
