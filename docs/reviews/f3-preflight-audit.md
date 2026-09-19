# F3 code audit against the protocol, before the full run

Run 2026-09-06 at the team lead's direction: sweep the Task B and C code against
what the preregistration actually requires, before spending 5-6 hours of compute
on it. The smoke run had already passed, so none of these would have failed
loudly. That is the point of the sweep.

Five findings. Four are real defects; one was a false alarm in my own test.

## 1. HIGH: no class weighting, which section 7 requires

Section 7: "Weighting only in house protocol (`scale_pos_weight` /
`auto_class_weights`; exactly one mechanism per library)." `run_ieee.py` applies
NONE. XGBoost, LightGBM and CatBoost all ran unweighted.

Why it matters beyond compliance: the ULB arms are weighted, so an unweighted
IEEE-CIS arm is not the same estimator, and any cross-dataset statement about
"the same classical baseline" would be false. At 3.5% prevalence the effect is
smaller than at ULB's 0.17%, but "smaller" is not "absent" and is not a reason to
skip a protocol step.

FIX: `scale_pos_weight` for XGBoost and LightGBM, `auto_class_weights="Balanced"`
for CatBoost. Exactly one mechanism each, no resampling anywhere.

## 2. HIGH: identifier columns entered the model raw

Section 5 item 5: "no identifier column enters any model raw." `TransactionID`
and `TransactionDT` both survived `IEEEFeaturePipeline` into the feature matrix.

The adversarial control DID remove both before the model saw them -- which is
the control working. But it stopped at its 20-round cap, so that removal was
luck rather than guarantee: on a fold where twenty other features ranked higher,
the raw clock would have gone in. `TransactionDT` is the timestamp; a model
given it can memorize WHEN fraud occurred in the training months, which is
precisely the leak rolling-origin evaluation exists to prevent.

FIX: drop identifier columns in the pipeline's `_finalize`, so compliance does
not depend on a downstream filter reaching them.

## 3. MEDIUM: the shuffled-label positive control is not run

Section 5 item 6: "Positive control: shuffled-label run must collapse test AUPRC
to the base rate; reported." A test asserts this on a fixture
(`test_ieee_features.py`), but the protocol run itself never does it, so no
reported IEEE-CIS figure carries the control the protocol attaches to it.

FIX: run it once per fold on the reduced feature set and record the collapsed
AUPRC beside the real one.

## 4. MEDIUM: the ULB MDE was reused on a different dataset and design

`run_ieee_cvqboost.py` sets `MDE = 0.0268`, which is the A5 value computed from
ULB pilot SEED variance across ten stratified seeds at 0.17% prevalence.
IEEE-CIS is three temporal FOLDS at 3.5% prevalence. Section 8 item 3 requires
the MDE to be "computed from pilot seed variance" -- for the design in question,
not borrowed from another one.

FIX: compute a fold-variance MDE from the IEEE-CIS folds themselves, and where
three folds are too few to support one, say so and report differences
descriptively rather than against a threshold that does not apply.

## 5. Adversarial loop hits its round cap rather than converging

Not a compliance defect, but a reportable finding: the loop dropped 20 features
and stopped because `ADVERSARIAL_MAX_ROUNDS` ran out, not because early and late
rows became inseparable. IEEE-CIS carries more drift than twenty drops remove.

Two consequences. The result must SAY it hit the cap, since a control stopping
at its bound is evidence about the data. And the attribution step
(`permutation_importance` over ~400 columns, 3 repeats, up to 20 rounds) is the
run's dominant cost -- about 3 CPU-hours for ONE smoke fold against 12 seconds
of actual model fitting. The check is cheap; only the attribution is not.

FIX: rank by the model's own feature importances instead of permutation, keep
the AUC check unchanged, and record `hit_round_cap` in the output.

## False alarm, recorded so it is not re-raised

`isFraud` appeared to survive into the features. It does not: `split_xy` removes
the label before the pipeline is called. My probe passed the full frame directly
to the pipeline, which the real code path never does. Checking the caller before
reporting a leak would have saved the alarm.
