# Requirements and Evidence Matrix

Status legend: OK = verified against the full official PDF text (docs/source/, verified 2026-08-29). TODO = not yet addressed in our submission.

This matrix is the final acceptance checklist. Stage 8 walks it line by line.

## A. Administrative and eligibility (T&C + Guidelines, verified)

| # | Requirement | Source | Status | Notes |
|---|---|---|---|---|
| A1 | Team lead 18+, legal authority, not under sanctions/export restrictions | T&C s2 | OK | Met |
| A2 | Individuals/teams worldwide eligible; no sponsor employees | T&C s2, Guidelines s3 | OK | Solo entry eligible |
| A3 | Team lead must accept T&C at point of submission | Guidelines s3 | OK | Harold does this in the portal |
| A4 | Deadline 15 Sep 2026; review 16 Sep to 14 Nov; finalists mid-Nov | Guidelines s2 | OK | Our target: ready Sep 8 |
| A5 | Submit via portal: Team Profile + Problem Statement Selection + Concept Proposal PDF + optional supplementary | Guidelines s4 | OK | Team Profile and statement selection are portal fields, OUTSIDE the 6 pages |
| A6 | One proposal per problem statement; multiple statements need separate submissions | Guidelines s4.2 | OK | We submit HSBC only |
| A7 | IP retained; non-exclusive license for administration/evaluation/marketing summary; sponsors review-only; full content not shared outside evaluation without consent | T&C s4, Guidelines s7 | OK | Public repo link is safe; anything public (arXiv, GitHub) loses the non-disclosure protection |
| A8 | Original work; no third-party confidential info; incomplete/late/non-conforming submissions may be rejected | T&C s3 | OK | Compliance walk at Stage 8 |
| A9 | Team member names not disclosed publicly without consent (Phase 1); Phase 2 finalists consent to name disclosure | T&C s4.2, s8 | OK | FYI only |

## B. Format (Guidelines s4.3 to s5, verified)

| # | Requirement | Status | Notes |
|---|---|---|---|
| B1 | Concept proposal max 6 pages, PDF, A4 or US Letter, min 10pt font | OK | Target 4 to 5 dense pages; guidelines say "a well-structured 4-page proposal will outperform a rambling 6-page one" |
| B2 | Appendices max 3 additional pages | OK | Results tables, preregistration registry, reproduction, references |
| B3 | English; file max 20 MB | OK | |
| B4 | Over-limit submissions may be returned or judged on first 6 pages only | OK | Hard stop at 6+3 |
| B5 | Public code repository link allowed as supplementary material | OK | Freeze repo at Stage 7 |
| B6 | Required content: the 7 sections (Problem Framing, Technical Approach, Feasibility/Resources, Expected Impact, Validation Plan, Hybrid Integration if applicable, Team Capability) | OK | Headings map one-to-one |
| B7 | Technical Approach must specify paradigm: gate-based, variational, quantum-inspired, hybrid, or other | OK | Ours: hybrid classical + quantum-inspired (Dirac-3 entropy optimizer) with gate-based Braket arm |

## C. Required proposal sections mapped to rubric (Assessment Criteria, verified)

| # | Section | Rubric criterion | Weight | Evidence needed | Status |
|---|---|---|---|---|---|
| C1 | Problem Framing | Problem Relevance & Impact | 25% | Named statement bottlenecks (detection-experience tradeoff, imbalance, adversarial adaptation); quantified stakes ($34bn fraud, $443bn false declines, $4.41 per $1) | TODO |
| C2 | Technical Approach | Technical Approach & Innovation | 25% | Method, paradigm, encoding, why quantum framing is credible not superficial | TODO |
| C3 | Feasibility and Resources | Feasibility | 20% | 3 to 4 month PoC realism, hardware/data/compute, stated assumptions | TODO |
| C4 | Expected Impact | Problem Relevance & Impact | 25% | What a successful PoC demonstrates, quantitative targets | TODO |
| C5 | Validation Plan | Validation Plan | 15% | Metrics, credible benchmarking, success definition; strongest differentiator per guidelines tips | TODO |
| C6 | Hybrid Integration | Hybrid / Cross-Domain | 5% | Classical-quantum pipeline rationale | TODO |
| C7 | Team Capability | Team Capability | 10% | Expertise, domain knowledge, appropriate composition; prior GIC 2026 entry, repos, Dirac-3 record | TODO |

Scoring guide: 5 = flagship demonstration; 4 = convincing with minor gaps. Target 4+ on every criterion. At least two reviewers per submission; moderation panel normalizes.

## D. HSBC-specific technical requirements (Challenge Statement, verified)

| # | Requirement | Source | Response plan | Status |
|---|---|---|---|---|
| D1 | Output: fraud probability float [0,1] per transaction | s5.2 | Calibrated head; report calibration | TODO |
| D2 | Output: binary prediction {0,1} via threshold | s5.2 | Threshold tuned on validation, documented | TODO |
| D3 | Output: feature attribution (vector or ranked list) | s5.2 | SHAP for GBDTs; QBoost weak-classifier weights are natively attributable | TODO |
| D4 | Metrics: AUC-ROC, AUPRC (recommended primary for imbalance), F1, Precision, Recall, confusion matrix, on held-out test | s4.1, 5.2 | All, with bootstrap CIs | TODO |
| D5 | Comparison with at least one classical baseline (XGBoost or LightGBM named; consistent with competition SOTA) | s5.2, 5.3 | Tuned XGBoost + LightGBM + CatBoost + logistic + structural control | TODO |
| D6 | Benchmark against published results and clearly report comparison methodology | s4.1 | Statement's own reference table: ULB XGB+SMOTE AUPRC 0.867, RF+SMOTE 0.871, stacking AUC 0.9887, CatBoost F1 0.8636, XRAI F1 0.9407; IEEE-CIS winner AUC 0.9459. Also quantum refs: VQC F1 0.88, QSVC F1 0.98 (Innan), Deloitte QNN precision 0.87 | TODO |
| D7 | Secondary objective: document where quantum/quantum-inspired improves over TUNED classical baselines; characterize under what conditions (feature sets, data subsets, encodings) | s4.2 | This is our Lane A thesis | TODO |
| D8 | Class imbalance handling documented (resampling, loss weighting, threshold tuning) | s5.3 | Weighting, no double-correction | TODO |
| D9 | Robustness: consistency across fraud types/partitions; behavior under distribution shift (temporal splits) | s4.2 | Temporal split protocol | TODO |
| D10 | Latency context: 100 to 300 ms end-to-end envelope; inference latency benchmark is good-to-have | s3.1, 5.3 | Report inference latency per arm | TODO |
| D11 | Good-to-have: training time quantum vs classical, qubit count/depth, simulator vs hardware comparison | s5.3 | Training time is where the CVQBoost speed story lands legitimately | TODO |
| D12 | Braket: exec summary "asks" participants to use Amazon Braket; scope allows ANY quantum or quantum-inspired framework; hardware optional, "not penalized" without it, encouraged with it; prototype on SV1/TN1/DM1 first | s2, 5.3, 5.4 | Dirac-3 [HW] results as quantum-inspired hardware evidence, plus a Braket-simulator gate-based arm and a Phase 2 Braket plan for full compliance | TODO |
| D13 | Datasets: IEEE-CIS primary (590k train, 3.5% fraud, up to 393 features), ULB secondary (284,807 rows, 0.172%, 30 features), Sparkov tertiary (1.3M synthetic). Focus on one or two is acceptable | s5.1, 5.4 | ULB shakeout + IEEE-CIS headline; Sparkov [PROJ] | TODO |
| D14 | Feature selection expected for quantum approaches; hundreds of features into circuits is impractical | s5.3 | Top-k MI selection, preregistered | TODO |
| D15 | Hardware subsampling must be stratified (preserve fraud ratio) and sample count explicitly stated | s4.2 | State counts; for Dirac-3 QBoost note the solve is over ensemble weights, weak learners train on full data; state both | TODO |
| D16 | In scope: CNP fraud, binary classification, batch evaluation. Out of scope: card-present, first-party fraud, account takeover, consortium models | s5.4 | Do not drift into out-of-scope framing | TODO |
| D17 | Explainability valued for governance: SHAP, attention, or circuit-level analysis | s4.2, 5.3 | Included per D3 | TODO |
| D18 | Reproducibility: workflow documented and reproducible (explicit in Phase 2 criteria, 30% PoC Quality + 20% Technical Rigour) | Assessment s4 | Public repo, seeds, preregistration | TODO |

## E. Credibility practices adopted from the TrueLoop example

| # | Practice | Status |
|---|---|---|
| E1 | Headings map one-to-one to rubric criteria | TODO |
| E2 | Evidence tags [HW] / [SIM] / [PROJ] on every quantitative claim | TODO |
| E3 | Preregistered gates, nulls published | TODO |
| E4 | Classical ceiling stated plainly | TODO |
| E5 | Under the page limit | TODO |
| E6 | Reproducibility repo linked as supplementary material | TODO |
