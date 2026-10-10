# Dirac-3 Sponsorship Request: 2026 Global Quantum + AI Challenge, HSBC Fraud Track

DRAFT V3, 2026-08-30. Harold's draft merged with the measured-cost and two-account updates. Canonical text; the Outlook HTML is generated from this.

---

I am entering the 2026 Global Quantum + AI Challenge, organized by Resonance Alliance Inc. (The Quantum Insider), in the HSBC track: "Quantum-Enhanced Credit Card Fraud Detection for Digital Payment Ecosystems." My submission is built around CVQBoost on Dirac-3. I am writing to request sponsored Dirac-3 compute time and a raised variable limit to support it. In return, Quantum Computing Inc. (QCi) hardware and algorithms are the centerpiece of a rigorously benchmarked, publicly reproducible entry evaluated by HSBC and an international review panel. Note: Progressive has given the OK, but is not sponsoring my participation.

## About the challenge

Enterprise problem statements from HSBC, E.ON, Cleveland Clinic, Airbus, and Volkswagen Group.

HSBC track objective:
- Develop a quantum or quantum-inspired fraud detection model and evaluate it against established classical baselines (XGBoost, LightGBM, CatBoost) on the IEEE-CIS, ULB, and Sparkov datasets.
  - Primary metrics: AUPRC, AUC-ROC, F1, precision, recall.
- The statement explicitly values training-time comparison between quantum and classical approaches, and asks participants to characterize the conditions under which quantum approaches perform differently.

Timeline:
- Phase 1 concept proposals due September 15, 2026.
- Finalists announced mid-November 2026.
- Phase 2 PoC Sprint runs November 17, 2026 to February 28, 2027.
- Winners announced by April 30, 2027.

Quantum-inspired methods and hardware are explicitly in scope.

## Why this is an opportunity for QCi

My submission reproduces and extends QCi's own published fraud results on a stage HSBC is watching: Emami et al., "Financial Fraud Detection with Entropy Computing" (arXiv:2503.11273), and Loke, Sahoo, Guan, Xu, Verma, and Griffin (SMU/OCBC, 2026), whose Dirac-3 CVQBoost with KNN weak classifiers reached AUC-PR 0.8108 on the ULB benchmark.

The evaluation is credible by design: preregistered hypotheses committed before runs, tuned XGBoost, LightGBM, and CatBoost baselines with equal tuning budgets, matched structural controls, bootstrap confidence intervals, and a public reproducibility repository. A CVQBoost result that stands in this protocol is far more persuasive to enterprise buyers than vendor-run benchmarks.

The submission directly targets the two claims QCi's papers make:
- Detection quality with heterogeneous weak-classifier pools, and
- Training-time scaling advantage as rows and features grow.

The IEEE-CIS dataset (590k rows, up to 393 features) is a natural showcase for the scaling story.

Deliverables QCi can reference: a public GitHub reproducibility package featuring Dirac-3, citation of QCi's papers in the proposal, and, if the entry advances, Phase 2 PoC results and finalist visibility with press coverage.

The pipeline is already proven at device scale. I have completed a full CVQBoost tuning campaign on Dirac-3 hardware, with weak-classifier pools up to ~850 variables and measured costs of 26 to 34 QPU seconds per tuned fit, using eqc-models 0.21.0 and qci-client 5.0.2 across six datasets to date, including credit card fraud. That campaign ran on a separate Dirac-3 account that is not available to me for this competition; my own account is free-tier limited. Sponsorship therefore converts an already-validated configuration directly into competition results, not into exploratory spending.

## What I am requesting

Phase 1 (now to Sep 15):
- Dirac-3 metered time: about 500 QPU seconds remain on my account at the time of this email. I request an additional ~2,500 metered seconds, for a total Phase 1 budget of ~3,000, sized from the measured 26 to 34 QPU seconds per tuned fit: a multi-seed replication campaign plus final preregistered runs on ULB and an IEEE-CIS subset.
- Transition the account from the free tier (100-variable limit) to the paid/educational tier's full device capability, approximately 950 to 1,000 variables; I would appreciate confirmation of the exact usable ceiling.
  - Why: heterogeneous weak-classifier pools with pairwise and triple terms expand the variable count to many multiples of the raw feature count (a 17-feature dataset at triple order needs 833 variables), and my measured results show this expansion is the accuracy lever. It also avoids sharding, which approximates the joint fit and costs extra solves.

Phase 2 (Nov 17 to Feb 28, if selected):
- Dirac-3 metered time:
  - [TBD, estimate ~2,000 metered seconds] for final preregistered runs on ULB and an IEEE-CIS subset.
  - [TBD, estimate ~20,000 to 40,000 metered seconds] for the full benchmark grid, tuning ladder, and scaling study.
- Technical contact:
  - A named engineering contact for solver-parameter questions (relaxation schedule, sum constraint, dynamic-range limits).

Cost discipline is built into my protocol and pipelines:
- All development is tested and vetted on a local classical proxy.
- Code debugging and vetting of the code, data, train, test, validation, and evaluation ML pipeline happen entirely off-device.
- Variable counts and QPU seconds are estimated before each run.
- Dirac-3 is used only for final preregistered result rows, so sponsored time translates directly into publishable results rather than debugging.
- I will only use the QPU seconds needed to get results and will return any unused time at the end.

## What QCi receives

- Attribution in the Phase 1 proposal, with QCi's papers cited as the foundation.
- Attribution in the Phase 2 materials, with QCi's papers cited.
- A public, independent, methodologically strict benchmark of CVQBoost against tuned gradient-boosting baselines on the datasets HSBC named, including training-time metrics.
- Feedback on eqc-models from an applied user.
- If the entry reaches the winners' podium, QCi hardware is named in the resulting coverage, and you are welcome to join me on the podium.
- Honest-benchmark disclosure.

My validation plan is preregistered and results are reported as measured, including any cells where tuned classical baselines win. I believe this strengthens rather than weakens the case for QCi: the published evidence already shows CVQBoost's advantages are conditional (detection quality with diverse weak-learner pools, and training-time scaling at high row and feature counts), and a fair map of those conditions is the most useful marketing artifact a vendor can have in front of a bank.

## About the team

"Claude Shannon's Fraud Catchers" is led by Harold Kimmey (BA Computer Science, Hiram College; MBA, Baldwin-Wallace University), an independent researcher and existing QCi customer, with prior Phase 1 experience in the qBraid/MITRE/JonesTrading Global Industry Challenge 2026. Development is AI-augmented using Anthropic's Claude Code as an engineering assistant under the team lead's direction. All work is reviewed and approved by the team lead.

I would welcome a short call to discuss scope and what QCi would find most useful from the results.

Thank you for considering the request.

Best regards,
Harold Kimmey
Team Lead, Claude Shannon's Fraud Catchers
kimmeyharold@aol.com | 216-357-9227
