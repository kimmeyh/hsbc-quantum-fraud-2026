# Velocity Actuals Log

**Purpose**: Recorded estimate-vs-actual per task, feeding SPRINT_PLANNING.md estimation (Sprint 2 retro improvement 6). Record at task completion; recompute patterns at retro Category 3.
**Audience**: Sprint planning sessions.
**Last Updated**: 2026-10-07 (rows 15-22 added, IMP-7 Sprint 22 retrospective)

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
| 13 | Task A evidence walk (agent + own verification) | verify | 90m | ~90m | 1.0 | agent 15m in parallel; found 6 document defects |
| 13 | Task B requirements-matrix walk, 92 rows | verify | 60m | ~60m | 1.0 | found 6 stale rows, 4 unknown before the walk |
| 13 | Task C confidentiality scan + compliance walk | verify | 30m | ~30m | 1.0 | scripted; 0 HIGH |
| 13 | Task D final render + page check | build | 20m | ~20m | 1.0 | run 3x in total as findings landed |
| 13 | UNPLANNED: 6 approved corrections, A32, backout, 2 re-renders | code+docs | 0m | ~60m | n/a | findings-driven; the 30% allowance now exists for this |
| 14 | F68 freeze artifacts + two dead hooks | tooling | 120m | ~150m | 1.25 | grew: new hook + test class |
| 14 | F69 README rebuilt, executed on a fresh clone | docs | 120m | ~120m | 1.0 | found 2 defects the working tree hid |
| 14 | F70 CHANGELOG backfill + workflow step | docs | 90m | ~90m | 1.0 | guard threshold wrong on first write |
| 14 | F71 CHECKLIST split into three | docs | 90m | ~60m | 0.7 | |
| 14 | F48, F65, F66, F67 tooling cards | tooling | 165m | ~180m | 1.1 | F48 took three iterations |
| 14 | F39 + F72 ADRs (design only) | design | 420m | ~600m | 1.4 | four team-lead corrections mid-design |
| 14 | UNPLANNED: 20 review findings | fix | 0m | ~120m | n/a | 2 vacuous guards; the 30% allowance did not cover it |
| 15-19 | (per-task actuals not recorded) | n/a | n/a | n/a | n/a | the log lapsed after Sprint 14; Sprint 19 recorded two of three tasks, in its summary only |
| 20 | Task A (F97) five tests stop reading live state | tooling | 40m | 52m | 1.3 | `SPRINT_20_SUMMARY.md`; first sprint with complete per-task actuals |
| 20 | Task B (F93) one SPECTRA configuration | analysis | 60m | 47m | 0.8 | |
| 20 | Task C (F98) hook timeout budget | tooling | 30m | 34m | 1.1 | |
| 20 | Task D (F99) tracked hash for correspondence | tooling | 20m | 28m | 1.4 | |
| 21 | Task A (F90) bring in the device result | verify | 45m | 0m | 0 | already satisfied |
| 21 | Task B (F122) four guards rewritten | tooling | 45m | 58m | 1.3 | |
| 21 | Task C (F90) B5 and B4 on Dirac-3 | code+compute | 240m | 229m | 0.95 | plus 653 device seconds |
| 21 | Task D (F100) classical bar | code+compute | 360m | 133m | 0.37 | `[no-history]` |
| 21 | Task E (F101) in-pocket provenance | analysis | 60m | 34m | 0.57 | |
| 22 | Task A (F123) phase separation document | design+docs | 120m | 30m | 0.25 | later superseded at validation (F127) |
| 22 | Task B (IMP-3) suite may not change evidence | tooling | 30m | 32m | 1.1 | includes hardening after a security review |
| 22 | Task F (F125) close-out hook ref | tooling | 20m | 45m | 2.25 | the card's diagnosis was incomplete |
| 22 | Tasks D+E (F17 emulator, F20 soft votes) | research+code | 570m | 54m | 0.09 | run in parallel, not separable; includes D's 20m acceptance test (corrected in PR #159 review from 34m, 0.06) |
| 22 | Task C (F124) SPECTRA lever research | research | 240m | 95m | 0.4 | `[no-history]` |
| 22 | UNPLANNED: Manual Validation rounds 1-3 | docs+decisions | 0m | 45m | n/a | B2 recovery attempt, F126/F127 carded |
| 22 | UNPLANNED: retrospective and improvements IMP-1 to IMP-7 | process+tooling | 0m | 70m | n/a | IMP-3's tracked pre-commit hook was the code item |
| 22 | UNPLANNED: second security review, 12 findings fixed | fix | 0m | 55m | n/a | evidence guard moved to the root conftest |
| 22 | UNPLANNED: PR #159 code review, 15 findings fixed | fix | 0m | 85m | n/a | 1 critical: the confidentiality scan missed renamed files |

**Pattern, recomputed at the Sprint 22 retrospective.** Tooling cards land
near their estimate (ratio 0.95-1.4 in Sprints 20-22; a wrong diagnosis
doubles one). Research and analysis cards marked `[no-history]` ran at
0.09-0.57 of their estimate in Sprints 21-22: they were sized as if every
branch would be explored, and the evidence cut most branches early. The
estimation rule in `SPRINT_PLANNING.md` now applies this.
