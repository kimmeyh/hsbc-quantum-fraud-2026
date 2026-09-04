# Sprint 5 Plan: The Paper (Draft V1, Reviews) and the QCi Package

Dates: Sep 4-7, 2026. Branch: `feature/20260904_Sprint_5` (carried forward from Sprint 4's head). PR target: `develop` (DRAFT until Phase 7.7).
Status: AWAITING TEAM-LEAD APPROVAL.
Scope defined by the team lead 2026-09-04 (defined-scope rule): **F8 + F9 + F27 + F19 + F26 + F28**.

## Audience-first statement (planning rule, Sprint 4 improvement 3)

**Who reads the deliverable**: HSBC fraud-domain reviewers and challenge judges scoring Problem Relevance 25%, Technical Approach 25%, Feasibility 20%, Validation 15%, Team 10%, Hybrid 5%. Separately, QCi reads the F19 package as a sponsor deciding on grant support.

**What they must believe after reading**: that this team built a deployable fraud-detection system, evaluated a quantum-inspired component against it with preregistered rigor and reported the result honestly in both directions, understands precisely why the current formulation behaves as it does, and has a concrete path into a production trial and a Phase 2 program where quantum optimization is necessary rather than optional.

## Objective

Produce the submission's core artifact: a rubric-mapped concept proposal built on the decided production-bound spine, hardened by adversarial review, with the operational evidence (cost-based operating points, explainability) that makes it read as production-bound rather than academic, and package the result for QCi.

## Tasks

### Task A / F26: Cost-based operating-point analysis (~2h, zero metered)

Prerequisite inside this task: **prediction persistence** (the enabling change A7 already registered) so operating points and paired bootstraps can be recomputed without refitting. Then report every arm at a realistic review capacity (alerts per day) and under an asymmetric cost assumption, with a sensitivity range over the cost ratio.

- **Acceptance**: predictions persisted for all 10-seed cells; a cost table covering the classical arms and the hardware CVQBoost arm at 2-3 review-capacity levels; cost assumptions stated explicitly as assumptions with a sensitivity range; per-seed paired BCa intervals now computed for H1b (closing the Sprint 4 OPEN item); zero metered seconds.
- **Model**: top tier (statistical). **Owner**: Claude.

### Task B / F28: Explainability thread (~3h, zero metered)

Structural argument plus measured evidence: weight concentration in the CVQBoost ensemble, per-weak-learner feature attribution, and a worked single-decision explanation for both the CVQBoost arm and the CatBoost baseline on the same transaction.

- **Acceptance**: `docs/EXPLAINABILITY.md` with the weight-concentration figures, the attribution method stated, and one worked decision explained end to end for both arms; the honest caveat that near-uniform weights (the Sprint 4 finding) cut against a simple "few learners explain it" story and are reported as such.
- **RESOLVED 2026-09-04 (team lead)**: the prior QML explainability work cannot be brought forward, so F28 REPRODUCES the evidence here on this project's own arms. No external citation carries evidentiary weight; Team Capability may mention the prior experience in prose only. This strengthens the section: every claim is checkable against results.json and the committed pools.
- **Model**: top tier. **Owner**: Claude drafts; team lead supplies the citation.

### Task C / F8: Outline + Draft V1 (~1 day)

`docs/paper/` as Markdown sources: seven rubric-mapped sections plus appendices. Outline presented for team-lead approval BEFORE drafting (prereg-adjacent framing decisions are Class 2). Every number carries its evidence tag and traces to results.json by config_hash; prevalence beside every AUPRC; the amendment log becomes the preregistration-registry appendix.

- **Inline addition** (Sprint 4 retro improvement 1, approved): known-answer tests for `score_gates.py` aggregation (gate verdicts, paired deltas, Spearman, cell keying) against hand-computed fixtures (~45m).
- **Acceptance**: outline approved; Draft V1 complete within the 6-page proposal limit plus 3-page appendix; every quantitative claim tagged and traceable; page-count check against requirements-matrix B1; score_gates tests green.
- **Model**: top tier. **Owner**: Claude drafts; team lead approves the outline and the Team Capability content.

### Task D / F27: Production-trial design section (~2h)

The 90-day trial as a paper section: shadow-mode scoring, champion/challenger against the incumbent, the review-capacity operating point from Task A, latency budget, calibration for the downstream rules engine, drift monitoring with named retraining triggers, and the dispute/regulator explainability path from Task B. Names the free-tier feature constraint honestly (13 features fit the device tier, not the problem) with the production sizing math.

- **Acceptance**: section drafted inside the page budget, every claim either measured (citing our rows) or labeled as a plan; no capability claimed that the evidence does not support.
- **Model**: top tier. **Owner**: Claude.

### Task E / F9: Adversarial reviews V2/V3 + rubric pass (~0.5 day)

Domain-reviewer pass, quantum-reviewer pass (evidence-tag audit, encoding diagnostics, does any claim exceed its tag), and a rubric-scoring pass that fixes the lowest-scoring criterion. Per Sprint 4 improvement 6, at least one pass runs as a fresh-context review with no drafting history.

- **Acceptance**: V2 and V3 recorded with findings and dispositions; rubric scored per criterion with the lowest one addressed; evidence-tag audit finds zero untagged or over-tagged numbers.
- **Model**: top tier (adversarial passes are top-tier mandatory). **Owner**: Claude; team lead does an independent read-through.

### Task F / F19: QCi draft package (~2h + team-lead send)

Assemble the Sprint-5-end package: the reviewed draft plus preregistration with amendments A1-A8, gate report, and hardware plan, rendered as PDFs marked DRAFT. **Mandatory pre-send confidentiality scan of every page** (Stage 7 scan run early, scoped to the sent artifacts: no employer references, no account identifiers, no QPU balances tied to a named account, no `.env` content). Include the Phase 2 non-convex ask (F25) as the "why Dirac-3 is necessary" item.

- **Acceptance**: PDFs render and open cleanly; scan walked page by page with evidence recorded; package handed to the team lead with a one-paragraph cover summary; **the team lead sends it, not Claude**; what was sent and when recorded in requirements-matrix.
- **Model**: top tier. **Owner**: Claude assembles; team lead reviews and sends.

## Capability pre-flights

- PDF rendering toolchain (~10m): confirm Markdown-to-PDF produces A4/Letter output at 10pt minimum with tables intact, before drafting depends on it.
- Prediction persistence smoke (~5m): one cell round-trips predictions and reproduces its recorded AP exactly.

## Explicitly out of scope

F3 (IEEE-CIS), F4/F5 and their prep (F23/F24), F29, F30, F2b hardware, F16, F10. No metered Dirac-3 execution in this sprint. Portal upload happens only in the finalize window.

## Risks

- **Page budget**: six sections plus two new evidence threads competing for 6 pages. Mitigation: the outline allocates page counts before drafting; the appendix absorbs detail.
- **Framing drift**: the decided spine could soften under drafting pressure. Mitigation: the decision is recorded in RESULTS_MEMO.md and re-read at V2.
- **Overclaiming**: the production framing invites capability claims the evidence does not support. Mitigation: the V3 evidence-tag audit is an explicit acceptance criterion.
- **Deadline**: this sprint produces the artifact that makes Sep 13 submission possible; if F26/F28 run long they yield to F8/F9, and their content moves to Sprint 6 (a Class-3 decision surfaced, not taken silently).
- **Usage limits**: reviews run scoped per the CLAUDE.md exclusion rule; no multi-agent pass over generated evidence.

## Estimate total

~2.5 days of work across Sep 4-7, front-loaded: Tasks A and B feed C, C and D produce the draft, E hardens it, F packages it.
