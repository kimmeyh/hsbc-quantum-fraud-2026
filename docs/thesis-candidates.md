# Thesis Candidates

## DECISION (Harold, 2026-08-30): Performance-first framing, scoped

The proposal leads with performance claims, scoped to where performance is provable: (1) in-segment detection wins over XGBoost on Dirac-3 hardware (FourierWall2, to be replicated per prereg H5), (2) AUPRC above the published semi-supervised anomaly-detection SOTA on ULB (SMU/OCBC configuration, to be reproduced per H1a), (3) training-time dominance at scale (H1c). The blanket claim "CVQBoost beats tuned classical baselines overall" is preregistered as H1b and gets promoted to the headline ONLY if Stage 3 evidence supports it (Sep 4 gate review). The regime-map machinery (Lane A below) remains the proof structure underneath the performance claims. Risk note: all current fair evidence shows tuned GBDTs winning overall AUPRC; the scoping above is what keeps the aggressive framing survivable under review.

The original candidate lanes below are kept for the record.

One gets chosen at Stage 1. The test for each: does it answer a question the HSBC statement explicitly asks, can we produce measured evidence for it by Sep 4, and is it differentiated from TrueLoop's occupied lane?

## Lane A (recommended): The regime map

**Thesis.** Tuned gradient-boosted trees dominate static tabular fraud detection, and the field lacks a systematic answer to the question the HSBC statement itself poses: under which feature subsets, data regimes, and encoding strategies do quantum feature representations contribute measurable incremental information? We build a screening methodology that predicts, from measurable data properties, where a quantum representation can add signal, and we validate its predictions with matched classical controls on ULB. The deliverable is a reproducible regime map with confidence intervals, including measured boundaries where quantum adds nothing.

**Why it can win.**
- It is the statement's own question ("determine under which conditions quantum approaches perform differently"), answered directly. Strong on the 25% Problem Relevance criterion.
- TrueLoop's F1 null made them abandon this lane for training economics. It is open.
- It is robust to negative results: a measured boundary is a deliverable, not a failure. That protects the 15% Validation score.
- The SPECTRA-lite screening idea from earlier work slots in as the mechanism, but only earns headline billing if its predictions correlate with measured QML behavior. Otherwise it stays an internal tool.

**Phase 2 story.** Apply the validated map to IEEE-CIS at scale, add shot noise and hardware runs on Braket, and preregister which regimes should and should not show quantum contribution. A prediction that survives hardware is a genuinely novel result.

**Risk.** The map may show quantum adds nothing anywhere on ULB. Mitigation: that is itself a publishable, preregistered finding, and the methodology remains the contribution.

## Lane B: Fair drift economics

**Thesis.** Extend TrueLoop's drift question but with the control they omitted: classical models refit for free, so quantify the full three-way frontier (classical refit vs frozen quantum vs adapted quantum) under realistic budgets.

**Why not.** Head-on collision with a stronger incumbent who has a production runtime, hardware campaigns, and a year of results. We would be their reviewer, not their competitor. Use the fairness insight as a component of Lane A's drift section instead.

## Lane C: Attribution and calibration

**Thesis.** Quantum feature maps with closed-form readouts give per-feature attributions and calibrated probabilities that satisfy the statement's explainability requirement better than black-box kernels.

**Why not.** Explainability is a requirement to satisfy, not a differentiator to build on. SHAP already serves the classical side well, and the innovation score would be weak. Fold D1/D3 compliance into whichever lane wins.

## Recommendation

Lane A, with Lane B's fairness control absorbed into its drift subsection and Lane C absorbed as compliance items. Decision needed from Harold at Stage 1 (target Aug 30).
