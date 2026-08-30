# Pilot Variance and Minimum Detectable Effect

Sprint 1 task 4, run 2026-08-30. Evidence tag [SIM]. This is the
seed-variance pilot required by PREREGISTRATION v1.1 section 8.3 before any
hardware approval; it is not the G0 tuned baseline (Sprint 2).

- Dataset: ULB, stratified 60/20/20, seeds 42-51, G0c preprocessing
  (log-Amount, Time retained, 1081 exact duplicates removed).
- Fixed pilot XGBoost (untuned, documented in pilot_variance.py).
- Test AUPRC per seed: 0.8428, 0.8238, 0.8463, 0.8438, 0.8249, 0.8222, 0.8526, 0.8387, 0.7748, 0.7976
- Mean 0.8268, across-seed SD 0.0243.
- **Minimum detectable across-seed mean delta-AP (10 seeds, alpha 0.05,
  power 0.80): 0.0242.** Observed H1b margins below this value are
  reported as indistinguishable, not as wins, per the frozen protocol.
