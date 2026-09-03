# Sprint 2 Summary: Process Foundations and External Readiness

Archival record (three-doc rule). Dates: Aug 31 - Sep 2, 2026. Branch `feature/20260831_Sprint_2` (carried forward from Sprint 1's head); PR #2 merged to develop 2026-09-02; develop merged to main via PR #12. Sources: SPRINT_2_PLAN.md, SPRINT_2_RETROSPECTIVE.md, git history, PR #2.

## Objective

Adopt the full sprint execution process, adapt the spamfilter-multi best-practices corpus, and clear the external blockers (portal, QCi letter) so the evidence campaign can start without process debt. Scope was team-lead-defined: F15, F12, F11 only (defined-scope rule).

## Delivered

1. **F15 best-practices and ADR review**: 42-ADR spamfilter-multi inventory dispositioned (8 adopted, 4 authored fresh, 18 declined with reasons); ADR system live (`docs/adr/` with template incl. mandatory Preregistration-touchpoints section; ADRs 0001-0004, 0011; 0005-0010 reserved for the F1 sprint); QUALITY_STANDARDS, STATISTICAL_REVIEW_CHECKLIST, WINDOWS_POWERSHELL_GUIDE, TESTING notes; data manifest + verifier (ADR-0003 implementation).
2. **F12 portal verification (team-lead-owned)**: submission mechanism confirmed as a 5-slot file upload (PDF/PNG/PY/JSON/CSV/DOC and more); no team-profile form, so a one-page Team Profile PDF plan added (requirements-matrix A5/A5b); do-not-upload-until-final risk recorded.
3. **F11 QCi sponsorship letter**: completed by the team lead (sent 2026-08-30).
4. **Full sprint process suite adapted**: SPRINT_EXECUTION_WORKFLOW (phases 1-8), SPRINT_CHECKLIST, SPRINT_STOPPING_CRITERIA (Criterion H), SPRINT_RETROSPECTIVE (16x4 protocol), SPRINT_PLANNING (defined-scope rule), BACKLOG_REFINEMENT (F#-only rule), ALL_SPRINTS_MASTER_PLAN, one-page SPRINT_PROCESS overlay; CHANGELOG same-commit policy; sprint-card issue template; update-sprint-status.ps1.
5. **Dual PR review, all findings fixed**: Claude review (10 confirmed findings) + Copilot review (2, overlapping). Fix highlights: manifest rewritten portable and hard-failing, moved to scripts/; .gitignore negation repaired so MANIFEST.json (12 files) is actually committed; 16-category unification; criteria 4/7 precedence; all 12 review threads replied-to and resolved.
6. **Preregistration amendments A2 + A3 (team-lead approved)**: A2 corrects the variable-count formula to the sequential-strategy count (verified exactly against FourierWall2 measured hardware runs: 105/560 vars at n=15) and cites QCi's documented 949 device ceiling; A3 adds the full-pair CVQBoost build (Linux/WSL2) as a preregistered side-by-side option with a proxy-based zero-metered-seconds selection rule. Bounds unchanged (free tier n<=13, device n<=17).
7. **F18 registered**: mine the team lead's Dirac-3 integration notes (qml-unlocked/DIRAC3.md) before hardware blocks; two of ten checklist items already completed (variable-count math; QSVM sign augmentation confirmed already frozen in section 4).
8. **Standing rules recorded**: all PR merges are team-lead-only at every level; Copilot reviews must be requested via the web UI (CLI/API silently fail); freeze honored, amendments-only (team-lead decision 2026-09-02).

## Estimated vs actual

F15 estimated ~3h, actual ~45 minutes (4x over-estimate; velocity log starts in the F1 sprint). The sprint's one process failure: the initial plan carried F1 forward on inference against defined scope, costing a re-plan cycle and six prematurely created cards (closed).

## Key decisions

- Defined-scope rule made binding: scope approval is not additive.
- Braket: no execution before submission/acceptance; covered as [PROJ] plan + team-lead AWS/Braket expertise (F6 to HOLD).
- F17 (Dirac-3 simulator) registered post-submission per team-lead prioritization.
- Retro improvement decisions: all 7 approved "as recommended" and applied.

## Hardware

Zero metered seconds.

## Links

PR #2 (merged), PR #12 (develop->main), docs/sprints/SPRINT_2_PLAN.md, docs/sprints/SPRINT_2_RETROSPECTIVE.md, issues #10 #11 (closed).
