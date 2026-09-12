# Sprint 13 Plan: Decompose, Then Submit

**Dates**: 2026-09-12 to 2026-09-13 (hard deadline 2026-09-15)
**Branch**: `feature/20260912_Sprint_13`
**Scope** (DEFINED, team lead 2026-09-12): **F64** then **F10**. Nothing else.

Sprint numbering note: the team lead's selection message said "Sprint 12". Sprint
12 closed on 2026-09-11 (PR #75 to develop, PR #76 to main, retrospective and
summary complete). This is Sprint 13. Recorded rather than silently renumbered.

## Objective

Run the one experiment that resolves the confound in the campaign's only positive
result, then verify and submit. Both documents currently promise this cell as
Phase 2 experiment 1; running it now either upgrades that promise to a finding or
leaves it exactly as written.

## Audience-first statement (mandatory, SPRINT_PLANNING.md)

**F64's reader is a judge assessing Technical Approach (25%) and Validation Plan
(15%).** They must conclude: this team decomposes its own positive result before
claiming it. **F10's reader is the same judge plus the portal's conformance
check.** They must be able to open every cited artifact and find every quoted
number.

## Capability pre-flight (run 2026-09-11/12 BEFORE estimating)

Code inventoried, not just documents (Sprint 10 improvement 6). **Six findings
change the plan.**

| Check | Expected | Measured | Consequence |
|---|---|---|---|
| Is (k=17, order 2) reachable? | assumed yes | **NO** -- `CONFIGS` (`qubo_proxy.py:48-52`) holds only the two ladder ENDS, and `--config` is bounded by `choices=list(CONFIGS)` (lines 254, 259) | One dict entry needed; clears all 4 blockers |
| 153-variable count | 153 | **153 confirmed** (17 singles + C(17,2)=136), via `data.qubo_vars` | Matches A24 and proposal line 85 |
| Pool build at 153 vars | unmeasured | **6.6-7.3 s measured** (WSL, seed 42, 32 workers) | NOT the dominant term |
| Full-pair build on Windows | assumed OK | **FAILS** -- `ValueError: cannot find context for 'fork'` | WSL is mandatory, per A3 |
| `735.4 s/pool` in Sprint 12 plan | cited as fact | **unsupported** -- no artifact behind it; the 11 `hw_b2_full` rows span 3.2-3.7 min each | Do not carry it forward |
| Gate re-keying | not considered | **`score_gates.py:206-211` argmaxes val AP over full-pair proxy cells; incumbent 0.7816** | A confirmatory table can silently re-key |

### The finding that shapes the sprint

**A new ten-seed full-pair proxy cell enters a CONFIRMATORY selection
automatically.** `score_gates.py` picks the H1b proxy cell by argmax of mean
validation AP across full-pair cells, and ten seeds is exactly `N_SEEDS`. The
incumbent (`free/dct/full`) sits at **0.7816 mean validation AP**. The new cell
has four more features and may beat it.

If it does, the H1b paired-delta table re-keys and the reported confirmatory
delta changes **as a side effect of an exploratory cell**, against a FROZEN
preregistration. That is not acceptable as an accident. Task B therefore diffs
the `Proxy cell used:` line before and after, and if it moves, the run STOPS for
a team-lead decision rather than publishing a re-keyed gate report.

### Runtime, with the dominant term named and measured

Per the Sprint 9 rule, the dominant term is named and shown, not estimated.

| Step | Measured at 153 vars | Source |
|---|---|---|
| Prep (load, dedup, split, top-k) | **21.9 s** | timed, WSL, seed 42 |
| **Pool build** | **6.6-7.3 s** | timed twice, WSL, seed 42 |
| H-matrix x3 + solve + score | ~25-35 s (inferred from the 91-var cell's 55-59 s row span) | `results.json` timestamps |

**The pool build is NOT dominant at this size** -- it is roughly 7 s of a ~55 s
cell. That inverts the Sprint 9 lesson, and it is why the figure was measured
rather than assumed. **Ten seeds is about 10 minutes of WSL compute, not hours.**

Inferred, not measured: the solve at 153 variables. FISTA on a 153x153 J is
trivially small; the risk is nil and the cell is cheap enough that a wrong
estimate costs minutes.

## Tasks

| # | Task | Est | Runtime | Dominant cost | Owner / Model |
|---|---|---|---|---|---|
| A | **F64 enablement**: add the `CONFIGS` entry; parameterize `wsl_build_pools.sh` | 30m | -- | none | Opus |
| B | **F64 run**: 10 seeds at k=17 order 2; gate-report diff BEFORE publishing | 30m | **~10m WSL** | prep 21.9 s + build 7 s per seed, measured | Opus |
| C | **F64 interpretation**: what the cell says about the confound; amendment drafted if it changes attribution | 45m | -- | A32 drafting | Opus |
| D | **F64 document updates**: B.3 and proposal line 85, presented for Class 4 approval FIRST | 45m | ~2m render | page budget is 6/6 and 3/3 | Opus + **team lead** |
| E | **F10 evidence walk**: every number vs results.json; requirements-matrix line-by-line | 90m | ~2m suite | 2 stale matrix rows already found | Opus |
| F | **F10 confidentiality scan + compliance walk** | 30m | ~1m | scan is scripted | Opus + **team lead** |
| G | **F10 submission**: final PDFs, portal upload, receipt archived | 30m | -- | portal is team-lead-only | **team lead** |

**Sequence is forced, not preferred**: A -> B -> C -> D -> E -> F -> G. F10
verifies every number against `results.json`; running it before F64 means running
it twice. This is the same dependency logic that ordered Sprint 12.

## Premise falsifier (mandatory, Sprint 8 improvement 2)

**F64's premise**: the +0.0256 gain is a confound of two factors (k and subset
order) and the middle cell separates them.

**What would disprove it**: if the 153-variable cell scores at or above the
833-variable cell's 0.7928, the gain is attributable to k alone and "richer
learners" contributed nothing -- the opposite of what B.3 currently implies. If
it scores at or below the 91-variable cell's 0.7671, subset order carries the
entire gain. Both outcomes are publishable and both change B.3.

**The check cannot merely confirm**: the cell can land anywhere in or outside
[0.7671, 0.7928], and three of those regions contradict a different reading. This
is the F36 test -- a dry run that could only confirm is not evidence.

**Physics prediction that makes it a test**: A31 established the device cannot
spread weight over more than ~200 learners. At 153 it can; at 833 it cannot. If
the gain is attributable to k, it should appear at 153 under a faithful solve.

## Risks

| Risk | Mitigation |
|---|---|
| **Gate re-keying moves a confirmatory endpoint** | Task B diffs `Proxy cell used:` and STOPS on any change. Highest-severity risk in this sprint |
| **Appendix page budget: 2 lines** | MEASURED 2026-09-12: appendix p3 has 73 pt free = **6.1 lines** at the measured 12.0 pt pitch. Team lead's bar: F64's B.3 change must fit in **<= 2 added lines**. The proposal is NOT a constraint -- its 553 pt of page-6 slack absorbs insertions anywhere, because text before section 7 pushes section 7 down page 6 rather than off the document |
| **A new result forces an amendment 3 days from deadline** | A32 drafted in Task C, verified against the artifact before writing (the hook enforces this) |
| **F64 overruns and squeezes F10** | F64 is ~10 min of compute. If Task B or C slips past its estimate, DROP F64 and ship F10 alone -- the team lead's own Sprint 12 deferral reasoning |
| **WSL dependency** | Verified working 2026-09-11; full-pair build cannot run on Windows (`fork` unavailable) |
| Deadline 2026-09-15 | F10 is the only submission blocker. Everything else yields to it |

## Already-found F10 work (from the pre-flight)

Two requirements-matrix rows are stale and will fail the Stage 8 walk:

- **E5** reads "NOT MET as of Sprint 9 ... proposal 7 of 6, appendix 4 of 3" and
  cites xfail markers F38 removed. Actual: **6/6, 3/3, 1/1 verified**.
- **D12** says the Braket arm is "gated on a classical feasibility screen". The
  proposal now commits unconditionally ("will run ... will be reported whatever
  the outcome"). The matrix contradicts the shipped document.

One evidence-artifact defect:

- **`summarize_b2.py:178`** writes `B1 hw_b1_dct (78 vars)` into
  `b2_hardware.json`. A24 states explicitly: "B1's variable count in that
  comparison is **91** (full pair build at k=13), **not 78**, which is the
  sequential count belonging to the IEEE-CIS arm." The published documents are
  correct; only the generated artifact's prose field is wrong. Confined to that
  one string -- no computed figure is affected.

## Definition of Done

- F64 cell runs on seeds 42-51, stratified, matching its neighbours' protocol
- `Proxy cell used:` diffed; any change escalated, not published
- B.3 and proposal line 85 state the decomposition, or state why it is unchanged
- Every requirements-matrix row verified against the CURRENT documents
- Confidentiality scan: zero HIGH findings
- Suite green; every reported number resolves to `results.json`
- **Appendix stays at 3 pages with the B.3 change adding <= 2 lines** (73 pt /
  6.1 lines free on p3, measured 2026-09-12). Re-run
  `scripts/page-fill-report.py` after rendering, before the PDFs are final
- Submission uploaded by the team lead, receipt archived

## Out of scope (defined-scope rule)

F66, F48, F65, F2b B4/B5, and everything in HOLD. Not planned in by inference.
