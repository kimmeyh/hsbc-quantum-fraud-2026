# Sprint 13 Plan: Submit

**Dates**: 2026-09-12 to 2026-09-13 (hard deadline 2026-09-15)
**Branch**: `feature/20260912_Sprint_13`
**Scope** (DEFINED, team lead 2026-09-12): **F10 only.** F64 was selected, then
WITHDRAWN by the team lead the same day. Reasoning recorded below, because it is
a methodology decision and not a scheduling one.

Sprint numbering note: the team lead's selection message said "Sprint 12". Sprint
12 closed on 2026-09-11 (PR #75 to develop, PR #76 to main, retrospective and
summary complete). This is Sprint 13. Recorded rather than silently renumbered.

## Objective

Verify every claim against its evidence, then submit. No new evidence.

## Why F64 was withdrawn (team lead, 2026-09-12)

F64 varies ONE axis (subset order at fixed k=17) with everything else frozen at
values chosen for a different configuration -- pool family, lambda, weak-learner
type, the cardinality question. The team lead's judgment: the gain that matters
is likely a COMBINATION of these, so a one-factor-at-a-time probe measures the
axis it varies and stays silent about the interaction, which is where the
leverage is expected to sit.

The result could not become false -- a cell that scores 0.79 scores 0.79 forever
-- but it could become UNIMPORTANT: a true fact about a formulation Phase 2
abandons. A31 already established the mechanism (the device cannot spread weight
over more than ~200 learners), so F64 would decompose a result INSIDE a
formulation we already have evidence is the wrong ask of the hardware.

Decisive: proposal section 6 already presents this cell as **experiment 1 of six
in an ordered program**, each with its acceptance criterion written before it
runs, and experiment 3 is the cardinality-constrained formulation the A31 finding
points to. Running experiment 1 early and reporting it alone would convert an
ordered program into one result plus five things we did not do. The program is
the stronger artifact.

F64 stays in the backlog at Priority 1 as the first thing Phase 2 runs. Both
documents already describe it as unrun, so NO document change is needed and the
appendix's 2-line budget is not spent.

## Audience-first statement (mandatory, SPRINT_PLANNING.md)

**F10's reader is the judge assessing all five rubric criteria, plus the portal's
conformance check.** They must be able to open every cited artifact and find
every quoted number exactly as the document states it. Nothing in this sprint
adds a claim; the whole job is making the existing claims checkable.


## Capability pre-flight (run 2026-09-11/12 BEFORE estimating)

Code inventoried, not just documents (Sprint 10 improvement 6). The F64 half of
this pre-flight is retained in git history and in the backlog card; only the F10
findings are live.

| Check | Expected | Measured | Consequence |
|---|---|---|---|
| Submission PDFs current vs sources | assumed | **YES** -- all three newer than their `.md` | No re-render needed to start |
| Page limits | 6 / 3 / 1 | **6 / 3 / 1 verified** | E5 matrix row is STALE, see below |
| Confidentiality scan | unknown | **0 HIGH, 1 REVIEW** (team lead's own contact block, required by Guidelines 4.1) | Scan is clean |
| Public repo + freeze commit | assumed | **HTTP 200** both; `prereg-freeze` tag intact | Appendix C reproducibility claim holds |
| Portal slots and size cap | 5 slots, 20 MB | **3 files, ~142 KB total** | No packaging risk |
| `store.py` enforces schema at write time | per CLAUDE.md | **NO** -- `store.py` validates nothing; enforcement is CI-time in `test_row_schema.py` | CLAUDE.md overstates it; F10 must not rely on write-time validation |

### The finding that shapes the sprint

**There is no new evidence to produce.** Every remaining task is verification of
claims already published. That makes this the lowest-risk sprint of the project
and the one where a missed check is most expensive, because the next reader is a
judge rather than a reviewer we can correct.


## Tasks

| # | Task | Est | Runtime | Dominant cost | Owner / Model |
|---|---|---|---|---|---|
| A | **Evidence walk**: every number in all three documents vs `results.json`; the three known defects below | 90m | ~2m suite | 168 result rows, 3 documents | Opus |
| B | **Requirements-matrix walk**: all 92 rows against the CURRENT documents, not against intent | 60m | -- | E5 and D12 known stale | Opus |
| C | **Confidentiality scan + compliance walk** (T&C s3, Guidelines s4) | 30m | ~1m | scan is scripted | Opus + **team lead** |
| D | **Final render + page-limit re-check**; PDFs regenerated from final sources | 20m | ~2m | pandoc | Opus |
| E | **Submission**: portal upload, receipt archived | 30m | -- | portal is team-lead-only | **team lead** |

**Sequence**: A -> B -> C -> D -> E. D must follow A and B, because either can
change a source document and every page-limit figure is measured from the
rendered PDF.


## Premise falsifier (mandatory, Sprint 8 improvement 2)

**This sprint's premise**: the submission's claims are all checkable against
committed evidence, and the remaining work is verification rather than
correction.

**What would disprove it**: any document figure that resolves to NO artifact, or
any requirements-matrix row whose status contradicts the shipped document. Three
such defects are ALREADY found (below), so the premise is known to be imperfect
before the sprint starts -- the open question is how many more exist, not
whether any do.

**The check cannot merely confirm**: the evidence walk compares two independent
artifacts (prose and `results.json`) that are produced by different processes. It
found three disagreements during the pre-flight alone.


## Risks

| Risk | Mitigation |
|---|---|
| **A stale claim reaches a judge** | Tasks A and B are the whole mitigation. Three defects found already; assume more |
| **A late edit breaks a page limit** | Task D re-renders and re-runs `page-fill-report.py` AFTER all edits. Appendix p3 has only 6.1 lines of slack |
| **Class 4 edits without approval** | Any submission-document change is presented text-before / text-after / pros / cons / recommendation FIRST. Enforced by hook, not by memory |
| **Deadline 2026-09-15** | F10 is the only submission blocker and the only scope. No competing work |
| **Portal behavior on upload** | Residual unknowns recorded in matrix row A5 (size cap display, whether upload marks "submitted"). Team lead walks it; nothing is uploaded until the package is final |


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

- Every figure in all three documents resolves to `results.json` or the registry
- All 92 requirements-matrix rows verified against the CURRENT documents; E5 and
  D12 corrected
- `summarize_b2.py` comparator string corrected and `b2_hardware.json`
  regenerated
- Confidentiality scan: zero HIGH findings
- Suite green
- PDFs re-rendered from final sources; **6 / 3 / 1 confirmed by
  `page-fill-report.py` after the last edit**
- Submission uploaded by the team lead, receipt archived


## Out of scope (defined-scope rule)

F66, F48, F65, F2b B4/B5, and everything in HOLD. Not planned in by inference.
