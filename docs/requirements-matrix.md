# Requirements and Evidence Matrix

Status legend: OK = verified against the full official PDF text (docs/source/, verified 2026-08-29). TODO = not yet addressed in our submission. PARTIAL = addressed but bounded, with the bound stated in the submission rather than hidden (Sprint 5 sweep, 2026-09-04). Rows C1-C7, E1-E6 and A5b were verified against the RENDERED PDFs, not against intent; several are additionally enforced by experiments/src/test_submission_artifacts.py.

This matrix is the final acceptance checklist. Stage 8 walks it line by line.

## A. Administrative and eligibility (T&C + Guidelines, verified)

| # | Requirement | Source | Status | Notes |
|---|---|---|---|---|
| A1 | Team lead 18+, legal authority, not under sanctions/export restrictions | T&C s2 | OK | Met |
| A2 | Individuals/teams worldwide eligible; no sponsor employees | T&C s2, Guidelines s3 | OK | Solo entry eligible |
| A3 | Team lead must accept T&C at point of submission | Guidelines s3 | OK | Harold does this in the portal |
| A4 | Deadline 15 Sep 2026; review 16 Sep to 14 Nov; finalists mid-Nov | Guidelines s2 | OK | Our target: ready Sep 8 |
| A5 | Submit via portal: Team Profile + Problem Statement Selection + Concept Proposal PDF + optional supplementary | Guidelines s4 | OK | PORTAL VERIFIED 2026-08-30 (F12, team-lead walkthrough with screenshots). Login works (quantumaiportal.thequantuminsider.com); all five tracks listed, HSBC "Not submitted". SUBMISSION MECHANISM IS FILE UPLOAD, NOT A FORM: the HSBC challenge page has a "YOUR SUBMISSION" panel with drag-and-drop, "0 uploaded, 5 slots left", allowed formats PDF, PNG, JPG, WEBP, GIF, PY, JSON, JS, XLS, XLSX, CSV, DOC, DOCX. Problem-statement selection is implicit (upload lives on the track page). "My files" area tracks files with an "Added to" column. NO team-profile form observed: plan a one-page Team Profile PDF as its own upload slot (see A5b). Residual unknowns: per-file size cap display, any post-upload metadata prompt, deadline timezone, whether uploading immediately marks "submitted". DO NOT upload anything until the final package is ready. |
| A5b | Team Profile delivery: no portal form found, so the profile (team name, lead contact, member description, prior experience, Claude Code disclosure) ships as a one-page PDF in its own upload slot | Guidelines s4.1 + portal walkthrough | OK | Slot budget: 1 proposal PDF (6pp) + 1 appendix PDF (3pp, or combined with proposal) + 1 team-profile PDF still leaves 2 spare slots of the 5 DELIVERED Sprint 5: docs/paper/team_profile.md -> out/team_profile.pdf, 1 of 1 page, US Letter. Guidelines 4.1 elements all present and TESTED (test_submission_artifacts.py::test_team_profile_has_required_fields): team name, lead full legal name, affiliation (independent researcher, unaffiliated), email, phone, LinkedIn, member description, prior experience, Claude Code disclosure. |
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
| C1 | Problem Framing | Problem Relevance & Impact | 25% | Named statement bottlenecks (detection-experience tradeoff, imbalance, adversarial adaptation); quantified stakes ($34bn fraud, $443bn false declines, $4.41 per $1). DELIVERED: proposal section 1. | OK |
| C2 | Technical Approach | Technical Approach & Innovation | 25% | Method, paradigm, encoding, why quantum framing is credible not superficial. DELIVERED: proposal section 2. Paradigm stated as hybrid classical-quantum per QCi hardware paper; no advantage claimed. | OK |
| C3 | Feasibility and Resources | Feasibility | 20% | 3 to 4 month PoC realism, hardware/data/compute, stated assumptions. DELIVERED: proposal sections 3 and 6, with the ULB-to-bank feature-mapping constraint stated. | OK |
| C4 | Expected Impact | Problem Relevance & Impact | 25% | What a successful PoC demonstrates, quantitative targets. DELIVERED: proposal section 4, impact quantified against the alert-budget ceiling. | OK |
| C5 | Validation Plan | Validation Plan | 15% | Metrics, credible benchmarking, success definition; strongest differentiator per guidelines tips. DELIVERED: proposal sections 3 and 4 plus appendix B; gates scored as committed including the failure. | OK |
| C6 | Hybrid Integration | Hybrid / Cross-Domain | 5% | Classical-quantum pipeline rationale. DELIVERED: proposal section 5. | OK |
| C7 | Team Capability | Team Capability | 10% | Expertise, domain knowledge, appropriate composition; prior GIC 2026 entry, repos, Dirac-3 record. DELIVERED: proposal section 7 and the team profile. The withdrawn GIC 2026 entry was REMOVED at team-lead direction (never submitted). | OK |

Scoring guide: 5 = flagship demonstration; 4 = convincing with minor gaps. Target 4+ on every criterion. At least two reviewers per submission; moderation panel normalizes.

## D. HSBC-specific technical requirements (Challenge Statement, verified)

| # | Requirement | Source | Response plan | Status |
|---|---|---|---|---|
| D1 | Output: fraud probability float [0,1] per transaction | s5.2 | Calibrated head; report calibration. Scores produced; calibration layer specified for the trial, not fitted in Phase 1. | PARTIAL |
| D2 | Output: binary prediction {0,1} via threshold | s5.2 | Threshold tuned on validation, documented. Operating points reported at 0.05/0.1/0.5% budgets rather than a single tuned threshold. | PARTIAL |
| D3 | Output: feature attribution (vector or ranked list) | s5.2 | SHAP for GBDTs; QBoost weak-classifier weights are natively attributable. Exact additive per-learner decomposition, proposal s4, with its anonymized-PCA scope limit. | OK |
| D4 | Metrics: AUC-ROC, AUPRC (recommended primary for imbalance), F1, Precision, Recall, confusion matrix, on held-out test | s4.1, 5.2 | All, with bootstrap CIs. AUPRC primary (step-wise AP), AUC-ROC reported; appendix A.1. | OK |
| D5 | Comparison with at least one classical baseline (XGBoost or LightGBM named; consistent with competition SOTA) | s5.2, 5.3 | Tuned XGBoost + LightGBM + CatBoost + logistic + structural control. Tuned XGBoost, LightGBM and CatBoost, equal 100-trial Optuna budgets; appendix A.1. | OK |
| D6 | Benchmark against published results and clearly report comparison methodology | s4.1 | Statement's own reference table: ULB XGB+SMOTE AUPRC 0.867, RF+SMOTE 0.871, stacking AUC 0.9887, CatBoost F1 0.8636, XRAI F1 0.9407; IEEE-CIS winner AUC 0.9459. Also quantum refs: VQC F1 0.88, QSVC F1 0.98 (Innan), Deloitte QNN precision 0.87. AutoXGB 0.782 cited as illustrative, not like-for-like; Loke et al. 2026 compared on design. | OK |
| D7 | Secondary objective: document where quantum/quantum-inspired improves over TUNED classical baselines; characterize under what conditions (feature sets, data subsets, encodings) | s4.2 | This is our Lane A thesis. H1b null reported as committed (-0.0399); conditions characterized via the degeneracy finding. | OK |
| D8 | Class imbalance handling documented (resampling, loss weighting, threshold tuning) | s5.3 | Weighting, no double-correction. 0.17% prevalence handled by class weighting; the class-weighted control is reported in A.4. | OK |
| D9 | Robustness: consistency across fraud types/partitions; behavior under distribution shift (temporal splits) | s4.2 | Temporal split protocol. Single time-ordered split reported with its reversal; a proper temporal protocol is Phase 2. | PARTIAL |
| D10 | Latency context: 100 to 300 ms end-to-end envelope; inference latency benchmark is good-to-have | s3.1, 5.3 | Report inference latency per arm. Latency stated as a Phase 2 target to be measured (p50/p95/p99), not claimed as measured. | PARTIAL |
| D11 | Good-to-have: training time quantum vs classical, qubit count/depth, simulator vs hardware comparison | s5.3 | Training time is where the CVQBoost speed story lands legitimately. Training time vs sample count named as the sharper untested experiment; proposal s6. | PARTIAL |
| D12 | Braket: exec summary "asks" participants to use Amazon Braket; scope allows ANY quantum or quantum-inspired framework; hardware optional, "not penalized" without it, encouraged with it; prototype on SV1/TN1/DM1 first. PORTAL OBJECTIVE (2026-08-30 walkthrough) states it more strongly: "Develop an explainable, deployable quantum or quantum-inspired fraud detection model using Amazon Braket that shows measurable gains over classical baselines" and names the baseline trio (XGBoost, LightGBM, or CatBoost) | s2, 5.3, 5.4 + portal | RESOLVED (team-lead steering 2026-08-30): no Braket execution before submission/acceptance. The proposal covers Braket via (a) the written Phase 2 Braket plan (SV1/DM1 then hardware), tagged [PROJ], and (b) Team Capability citing the team lead's near-expert AWS experience and hands-on Amazon Braket experience, which makes the plan credible without Phase 1 spend. Dirac-3 remains the measured [HW] evidence. The frozen run grid commits no Braket fits, so this is grid-consistent.. Braket named as a conditional Phase 2 arm gated on a classical feasibility screen. | OK |
| D13 | Datasets: IEEE-CIS primary (590k train, 3.5% fraud, up to 393 features), ULB secondary (284,807 rows, 0.172%, 30 features), Sparkov tertiary (1.3M synthetic). Focus on one or two is acceptable | s5.1, 5.4 | ULB shakeout + IEEE-CIS headline; Sparkov [PROJ]. ULB delivered; IEEE-CIS is F3, not yet run. | PARTIAL |
| D14 | Feature selection expected for quantum approaches; hundreds of features into circuits is impractical | s5.3 | Top-k MI selection, preregistered. 13 features via correlation-ranked selection; variable arithmetic in appendix. | OK |
| D15 | Hardware subsampling must be stratified (preserve fraud ratio) and sample count explicitly stated | s4.2 | State counts; for Dirac-3 QBoost note the solve is over ensemble weights, weak learners train on full data; state both. Stratified throughout; counts stated (284,807 rows, 1,081 duplicates removed, 60/20/20). | OK |
| D16 | In scope: CNP fraud, binary classification, batch evaluation. Out of scope: card-present, first-party fraud, account takeover, consortium models | s5.4 | Do not drift into out-of-scope framing. CNP binary classification, batch evaluation; scope respected. | OK |
| D17 | Explainability valued for governance: SHAP, attention, or circuit-level analysis | s4.2, 5.3 | Included per D3. Per-learner attribution delivered; SHAP not required given native attributability. | OK |
| D18 | Reproducibility: workflow documented and reproducible (explicit in Phase 2 criteria, 30% PoC Quality + 20% Technical Rigour) | Assessment s4 | Public repo, seeds, preregistration. Freeze commit, tag, version pins, dataset checksum, results store with config hashes. | OK |

## E. Credibility practices adopted from the TrueLoop example

| # | Practice | Status |
|---|---|---|
| E1 | Headings map one-to-one to rubric criteria. Proposal headings map to guidelines 4.3 items 1-7; TESTED by test_proposal_covers_every_required_section. | OK |
| E2 | Evidence tags [HW] / [SIM] / [PROJ] on every quantitative claim. [HW]/[SIM]/[PROJ] on every quantitative claim. | OK |
| E3 | Preregistered gates, nulls published. G0 FAIL, G0b PASS, H1b NULL, H4 PARTIAL, all scored as committed. | OK |
| E4 | Classical ceiling stated plainly. CatBoost 0.8368 stated as the ceiling the quantum arm did not beat. | OK |
| E5 | Under the page limit. Proposal 6/6, appendix 3/3, team profile 1/1; TESTED by test_page_count_within_limit. | OK |
| E6 | Reproducibility repo linked as supplementary material. Public package described; repository becomes public at submission. | OK |

## Portal document verification (2026-09-04)

The external review asked whether our format and rubric assumptions match what the portal currently serves. The team lead re-downloaded all three governing documents from the logged-in portal on 2026-09-04; each is BYTE-IDENTICAL (SHA-256) to the copy archived in `docs/source/` on 2026-08-22 and read in full during Sprint 2:

| Document | SHA-256 (first 16) | Status |
|---|---|---|
| Phase 1 Submission Guidelines | 74db5b7b01b16515 | unchanged since 2026-08-22 |
| Assessment Criteria | 646aa97ca06c8283 | unchanged since 2026-08-22 |
| Terms and Conditions | 3d3a8323aade01f7 | unchanged since 2026-08-22 |

Consequence: every row in this matrix (page limits, format, minimum font, file size, section structure, upload mechanism, judging weights) was derived from the current documents and requires no revision. The portal dashboard additionally confirms the HSBC problem statement is listed and shows status "Not submitted", and that no files have yet been uploaded.
