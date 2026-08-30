# Reviewer Teardown: TrueLoop Compute HSBC Phase 1 Proposal

Source: https://github.com/MatthewLeibel/TrueLoop-Compute-HSBC-Challenge-Reproducibility (`proposal_hsbc.tex`), read 2026-08-29. Scores below are my estimates of how a Phase 1 review panel would score it, 1 to 5 per the official rubric. They are informed estimates, not the actual review outcome.

## Their thesis in one sentence

Quantum fraud components decay under drift and are prohibitively expensive to retrain on measurement-priced hardware; their retained-state runtime updates all circuit parameters from one execution per cycle, recovering most of the retraining benefit at 10% of the cost.

## Estimated scores

| Criterion | Weight | Est. score | Rationale |
|---|---|---|---|
| Problem Relevance & Impact | 25% | 4 | Anchors directly to the statement's adversarial-adaptation bottleneck and its $34bn fraud / $443bn false-decline figures. Docked because the problem is conditional: quantum retraining economics only matter if a quantum component is deployed at all, and their own G1 gate shows classical dominance. |
| Technical Approach & Innovation | 25% | 4 | The single-execution update mechanism is genuinely novel and the closed-form transparency is a strength. Docked because the Phase 1 circuit is classically simulable by construction (they admit it), so the quantum element is essentially deferred to Phase 2. |
| Feasibility | 20% | 4 | Concrete Braket cost model, named devices, working production endpoint, free eval key, measured 489x infrastructure overhead. Docked because everything is statevector-exact; the central mechanism is untested under shot noise, and it depends on measurement statistics. |
| Validation Plan | 15% | 5 | Best-in-class. Preregistered gates scored as committed, two published nulls, seed spreads, reproducibility package, Phase 2 hypotheses preregistered before running. |
| Team Capability | 10% | 3.5 | Solo independent researcher, honestly stated fraud-domain gap. Offset by three multi-vendor hardware campaigns and independently reproduced public repos. |
| Hybrid Integration | 5% | 4 | Clean classical-quantum-classical architecture with a stated role for each layer. |

Weighted estimate: roughly 4.1 of 5. This is a finalist-competitive submission. Treat it as the bar.

## Vulnerabilities a reviewer will find (and we must avoid)

1. **The conditional-problem trap.** Their drift-economics argument presumes you already want a quantum component, but their own results show XGBoost (AUPRC 0.894) dominates every quantum arm (best quantum-augmented linear head: 0.804). A reviewer can ask: why maintain an expensive quantum component whose classical competitor retrains for free? Any thesis we choose must matter even if classical stays ahead, or must directly attack the question of when quantum adds signal.
2. **Missing classical drift baseline.** Their drift ladder compares quantum training methods against each other. XGBoost with per-period refit on the same drifted Sparkov data is absent. That is the comparison an HSBC reviewer actually cares about. We should include the classical-refit control in any drift claim.
3. **Budget realism.** The 30-executions-per-period budget is exactly the regime where parameter-shift (2n+1 per update) completes zero updates. The extinction result is arithmetic, not discovery. A reviewer may call the budget choice favorable framing.
4. **Suspicious baseline.** Their runtime at 30 executions beats full retraining at 300 executions at n=64 and 256. A 10x-budget method losing suggests the retrain baseline is under-tuned. Our comparisons must survive the question "did you tune the thing you beat?"
5. **Synthetic drift.** Sparkov with rotated fraud categories is controlled ground truth, which is good practice, but the frozen-transform collapse (0.68 to 0.34) is an aggressive synthetic scenario. Real drift on IEEE-CIS temporal splits is untested.
6. **No hardware in Phase 1.** All [SIM]. Their [HW] evidence is from other domains (channel regulation, not fraud).

## Practices to adopt

1. Headings that map one-to-one onto the seven required sections and the rubric.
2. Evidence tags on every number: [HW] hardware, [SIM] simulation, [PROJ] projected. Never let a reviewer confuse the three.
3. Preregistration with gates scored as committed, including published nulls. Their F1 null (training methods indistinguishable on static data, all within ±0.02 AUPRC) bought them credibility, not penalty.
4. State the classical ceiling plainly and first. "Tuned gradient-boosted trees dominate tabular fraud" then define the narrower, honest quantum claim.
5. Come with measured Phase 1 evidence, not promises. The competitive bar is real experiments before the ideation deadline.
6. Stay under the page limit. They used 5 of 9 permitted pages.
7. Reproducibility repo with seeds, preregistration file, and one-command reproduction.

## The open lane they left us

TrueLoop's F1 null led them to abandon static-data quantum value and pivot to training economics. The HSBC statement explicitly asks participants to determine **under which conditions (feature subsets, data regimes, encoding strategies) quantum approaches behave differently.** Nobody in the public field is answering that question systematically. A submission whose headline deliverable is a measured, reproducible regime map, with matched classical controls and fair refit baselines, answers the statement's own question more directly than TrueLoop does. See `thesis-candidates.md`.
