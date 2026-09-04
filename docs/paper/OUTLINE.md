# Concept Proposal Outline (Task C / F8) -- FOR TEAM-LEAD APPROVAL

**Status**: Outline only. Drafting starts on approval (framing decisions are Class 2).
**Constraints**: 6 pages max proposal + 3 pages appendix, PDF, min 10pt, English, under 20 MB (requirements-matrix B1-B4). The guidelines themselves say a well-structured 4-page proposal outperforms a rambling 6-page one, so the budget below targets **5 pages** and holds one in reserve.
**Spine**: the production-bound program framing DECIDED by the team lead 2026-09-04 (RESULTS_MEMO.md).
**Paradigm declaration (B7)**: hybrid classical + quantum-inspired (Dirac-3 entropy optimizer), with a gate-based Braket arm as a Phase 2 [PROJ] plan.

## Page budget

| Section | Rubric weight | Pages |
|---|---|---|
| 1. Problem framing | Problem Relevance 25% | 0.75 |
| 2. Technical approach | Technical Approach 25% | 1.25 |
| 3. What we measured | Validation 15% | 1.25 |
| 4. Production trial and impact | Feasibility 20% + Impact | 1.0 |
| 5. Hybrid integration | Hybrid 5% | 0.25 |
| 6. Phase 2 program | Feasibility 20% | 0.25 |
| 7. Team capability | Team 10% | 0.25 |
| **Proposal total** | | **5.0** |
| A. Results tables | | 1.0 |
| B. Preregistration registry (hypotheses, gates, amendments A1-A8) | | 1.0 |
| C. Reproduction and references | | 1.0 |
| **Appendix total** | | **3.0** |

## Section content

### 1. Problem framing (0.75 pp)
Card fraud as a decision under asymmetric cost and a fixed review budget, not as an offline accuracy contest: a missed fraud costs the chargeback, a false positive costs a good customer, and analysts can only review so many alerts a day. Class imbalance at 0.17% is the reason AUPRC and not accuracy is the working metric. States plainly what is on trial: whether a quantum-inspired component earns a place in a system that already works.

### 2. Technical approach (1.25 pp)
The system: tuned GBDT ensemble as the production detector; CVQBoost on Dirac-3 as the evaluated candidate; the exact classical proxy as a structural control. Declares the paradigm (B7). Explains the CVQBoost formulation (weak-learner pool, QUBO, continuous weights on the simplex) and the preregistered protocol that governs every comparison: frozen hypotheses, gates scored as committed, amendments-only changes, leakage controls, evidence tags on every number. The preregistration IS the technical differentiator and is presented as such.

### 3. What we measured (1.25 pp) -- the honest core
- G0 FAIL as committed, with the F21 finding that its threshold traced to an uncorroborated band (footnoted, not headlined).
- G0b PASS: proxy-hardware rank agreement 0.900 across 27 metered fits.
- H1b null: CVQBoost on hardware trails the best tuned GBDT by 0.040, CI excluding zero, 9 of 10 seeds.
- H4 solver-fidelity component: hardware minus exact proxy = -0.0010, CI containing zero; weight cosine 0.975-0.999.
- The structural explanation: strictly convex objective, near-degenerate optimum confirmed by a lambda sweep showing uniform weights even at lambda = 0. This is the paper's most defensible original contribution.
- Cost-based operating points (Task A) and the temporal-sensitivity reversal, both labeled at their evidence strength.

### 4. Production trial and impact (1.0 pp) -- from Task D
The 90-day trial: shadow mode, champion/challenger, review-capacity operating point, latency budget, calibration for the rules engine, drift monitoring with retraining triggers, and the explainability path for disputes and regulators (Task B). Names the free-tier feature constraint honestly and gives the production sizing math.

### 5. Hybrid integration (0.25 pp)
Where each component sits in a deployed pipeline and why the hybrid split is the right one: classical detector, quantum-inspired specialist candidate, routing between them.

### 6. Phase 2 program (0.25 pp)
The four open levers with their preregistered tests: representation (QFE/H6), in-segment specialization (H5), larger sparser regimes (IEEE-CIS/H3), and the non-convex cardinality-constrained formulation (F25) where no exact classical proxy exists. Includes the Braket [PROJ] arm.

### 7. Team capability (0.25 pp)
Solo team lead with the measured record: prior Dirac-3 hardware campaigns, quantum reservoir computing, quantum feature engineering, QML explainability work, near-expert AWS and hands-on Braket experience. Claude Code disclosed as an AI tool. RESOLVED 2026-09-04: the prior-challenge line was removed (the entry was withdrawn before submission, so it is not a track record); explainability is evidenced in-repo rather than cited externally.

## Appendices
A: per-arm results tables with prevalence and CIs, hardware campaign detail, cost table.
B: preregistration registry -- hypotheses, gates scored as committed, amendment log A1-A8.
C: reproduction (public package link, environment pins, config hashes) and references.

## What this outline deliberately does NOT do
- No claim of quantum advantage on the primary endpoint.
- No invocation of the compound falsification trigger (H3/H5 unrun; the framing is an early choice and says so).
- No number without an evidence tag and a config_hash trail.
