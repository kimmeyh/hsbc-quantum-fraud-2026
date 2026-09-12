# Velocity Actuals Log

**Purpose**: Recorded estimate-vs-actual per task, feeding SPRINT_PLANNING.md estimation (Sprint 2 retro improvement 6). Record at task completion; recompute patterns at retro Category 3.
**Audience**: Sprint planning sessions.
**Last Updated**: 2026-09-11

| Sprint | Task | Type | Estimate | Actual | Ratio | Note |
|---|---|---|---|---|---|---|
| 2 | F15 review + ADR system | research+docs | 180m | ~45m | 0.25 | agent-assisted research |
| 3 | Task A (F18 notes mining) | research+docs | 60m | ~35m | 0.6 | 2 items pre-completed |
| 3 | B pre-flights (Optuna smoke, WSL spike) | spike | 10m | ~25m | 2.5 | WSL python3.12 install + quoting detours |
| 3 | B1 runner build+smoke | code | 90m | ~50m | 0.6 | tune.py skeleton existed |
| 3 | B5 proxy module + tests | code | 120m | ~75m | 0.6 | eqc source reading included |
| 3 | ADRs 0005-0010 | docs | 90m | ~40m | 0.45 | modules already existed to cite |
| 3 | Hook ports + registration + payload tests | tooling | 60m | ~30m | 0.5 | sources adapted, not rewritten |
| 3 | B1 tuning studies (unattended) | compute | 240-480m | 256m | ~0.8 | CatBoost slowest (56m full); CPU shared with proxy track |
| 3 | B2-B4 refits + gate scoring | compute+code | 100m | ~95m | 0.95 | incl. one checkpoint-key fix + relaunch |
| 3 | B6 A3 side-by-side (builds+solves) | compute | 60m + 60m timebox | ~75m | 0.6 | WSL setup consumed the timebox's first half |
| 3 | B7 hardware request doc | docs | 30m | ~20m | 0.7 | |
| 4 | Task A (F22) A1 health flags + A2 harness + smoke | code | 110m | ~70m | 0.65 | |
| 4 | Task A (F22) 100-trial study (unattended, WSL) | compute | 120-240m | ~85m | 0.5 | fork builds + H cache |
| 4 | Task A (F22) refits + rank + report updates | code+compute | 60m | ~45m | 0.75 | |
| 4 | Task B (F21) research memo (agent) | research | 120m | ~9m agent + 15m fold-in | 0.2 | primary-source finds decisive |
| 4 | Task D (F7) memo + checklist walk + positive control | docs | 120m | ~60m | 0.5 | |
| 4 | Task C (F2) hardware runner + 27 metered fits | code+compute | 240m | ~150m | 0.6 | 0 failures, 0 retries; 120 QPU s |
| 12 | F49-F63 review-response cards (15 cards) | code+docs | ~360m | ~370m | ~1.0 | estimated from a completed analysis, not mid-review |
| 12 | F2b B2 block (11 metered fits) | compute | ~450 QPU s | 906 QPU s | 2.0 | frozen grid assumed ~40 s/fit; measured 82 s. See F2b card |
| 12 | F2b B3 block (12 metered fits, matched re-run) | compute | ~650 QPU s | 62 QPU s | 0.1 | reduced recipe far cheaper per sample than B2 |
| 12 | F38 page limits | docs | 45m (first card) | ~5x that, across 4 re-measures | >5 | an estimate that grows 5x across one sprint is not an estimate |
| 12 | F37 repository public | tooling | 45m | ~45m | 1.0 | pre-flip secret scan across 259 commits included |
