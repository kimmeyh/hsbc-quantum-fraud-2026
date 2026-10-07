# Sprint 22 Plan: Separate the Phases, Then Look for Better Numbers

**Sprint**: 22 | **Branch**: `feature/20261006_Sprint_22`
**Planned**: 2026-10-06 | **Status**: awaiting team-lead approval
**Scope**: F123, IMP-3, F124, F17, F20 (the team lead's selection list,
complete, in his stated order)
**Metered Dirac-3 seconds**: **0**. Nothing in this sprint touches the device.
Any Dirac-3 fit F20 or F124 might justify waits for the team lead's approval
of F124's ranked list, which is the gate he set on 2026-10-06.

## Objective

Decide how Phase 2 work stays out of Phase 1's locked files, then search
everything we know for what could improve SPECTRA predictions -- and test the
two cheapest levers already in hand on the classical proxy.

Sprint 21 showed the device returns its classical proxy's answer, so a better
number has to come from the problem (features, the weak-learner pool,
regularization, the vote itself), not from the solve. This sprint is about
finding those levers and ordering them, not spending device seconds on them.

## What the capability pre-flight found, before any estimate

Mandatory per `SPRINT_PLANNING.md`. Each finding changes a task.

1. **EmuCore is not a Dirac-3 emulator.** The `emucore-direct package not
   available` warning `eqc_models` prints on every run refers to a QCi
   **reservoir-computing** device: `eqc_models.ml.forecast` and `ml.reservoir`
   name EmuCore as their only supported device. That is a lead for F124's QCi
   NeuraWave question, not a tool for F17.
2. **`eqc_models` has no local Dirac-3 stand-in.** Its solvers are cloud
   (`Dirac3CloudSolver` and variants) or direct-to-hardware
   (`Dirac3DirectSolver`). So F17 is an investigation: whether QCi offers a
   simulator (**unverified**), or whether one is worth building.
3. **Soft votes are reachable but not by the library's builders.** The proxy's
   vote matrix is built from hard `predict` votes. Each `WeakClassifier` wraps
   an sklearn model in `.clf` (decision tree, logistic regression, LDA, KNN,
   Gaussian NB, Gaussian process), and every one of those has
   `predict_proba`. F20 can build a soft-vote matrix, but only by reaching into
   that internal attribute, which a future `eqc_models` version could rename.
4. **F17's value is narrower than its card assumed.** The card was written
   when device behavior was unknown. B4 then measured the device matching its
   exact classical proxy within 0.0072 in-pocket AUPRC on every cell. A
   simulator's remaining value is in what the proxy does NOT model: the ~200
   distinguishable coefficient levels (A31), sampling spread across
   `num_samples`, and cost. Task D is shaped around that.

## Tasks

| Task | Card | What | Est | Runtime | Depends on |
|---|---|---|---|---|---|
| A | F123 | Phase 1 / Phase 2 separation: locked-file inventory, Phase 2 layout, disposition of Sprint 21's five Phase 1 changes, guard design | 120 | n/a | nothing |
| B | IMP-3 | The test suite may not change committed evidence: hash tracked results files at session start and end; card updated first if A changes it | 30 | +~1 s per suite | A |
| C | F124 | SPECTRA prediction research: ranked list of levers, each with a proxy test plan; QCi NeuraWave from primary sources | 240 | n/a | A, B |
| D | F17 | Dirac-3 simulator investigation and go / no-go recommendation | 150 | n/a | A, B; parallel to C |
| E | F20 | Soft votes and multi-sample ensembling on the classical proxy | 180 | see runtime | A, B; parallel to C and D |

**Derived total: 720 minutes implementation, 828 with allowances**, computed
from the card estimates above, not asserted.

**Allowances, named rather than absorbed** (`SPRINT_PLANNING.md`):
- **30% sourcing allowance on Task C, 72 min, and on Task A, 36 min.** Both
  produce prose that makes factual claims, and F124 spans more sources than
  any card so far.
- If every claim sources cleanly, the allowance is returned.

**Calibration note.** Sprint 21 came in at 454 against 750, with its
investigative tasks well under estimate. These card estimates are kept as
written because C and D search sources this repository has not read before
(EvidenceBasedDB, QCi primary sources).

### Runtime, estimated separately

- **Task E is the only task that computes.** Its dominant term is the
  sequential weak-learner pool build, **measured in Sprint 21: 41.9 s of a
  44.0 s cell at 560 variables, about 38-90 s at 816.** One pool build serves
  both the hard-vote and the soft-vote matrix, so the side-by-side costs about
  one build per cell: roughly 19 minutes for 15 cells. The multi-sample half
  re-scores samples B4 already stored, so it needs no new device runs.
- Any run expected to exceed 30 minutes emits heartbeat progress first.

## Sequencing

Your order, kept:

1. **A (F123) first.**
2. **B (IMP-3) after A**, with its card updated first if A changes it.
3. **C (F124) after A and B; D (F17) in parallel with C.**
4. **E (F20)**: you gave no position, so I propose **after A and B, in
   parallel with C and D, with its results fed into C's ranked list.** F20 is
   itself one of the levers F124 should rank, and measuring it first gives F124
   real data instead of a guess. Its device half stays out of this sprint.

## The one mid-sprint gate, and a proposal for it

F123's acceptance says nothing is moved until you approve its decision. Tasks
C, D and E all write new files. **Proposal:** they write only to the Phase 2
location F123's document proposes, never into a Phase 1 file. Nothing that
already exists moves. You review the layout at Manual Validation. That keeps
the sprint moving without either guessing your decision or stopping for it.

## Premise falsifiers

Required for any card justified by a measurement.

- **F123**: the premise is that Phase 2 work can run without touching Phase 1
  files. **Falsifier**: a Phase 2 task cannot run unless a locked Phase 1 file
  changes. Then the layout has to name that dependency, not hide it.
- **IMP-3**: proven red with a mutation, a test that writes a tracked results
  file, before it is trusted.
- **F124**: the premise is that untried levers exist. **Falsifier**: every
  candidate turns out to be tested already, in this repository or off it. That
  is a reportable outcome: it says the gap is the method, not the setup.
- **F17**: the premise is that a simulator adds information beyond the exact
  proxy. **Falsifier**: on B4's 10 cells, a resolution- and sampling-aware
  simulator reproduces the proxy as closely as the device did (within 0.0072
  in-pocket AUPRC). Then the recommendation is no-go.
- **F20**: the premise is that hard-vote quantization loses information.
  **Falsifier**: soft votes move proxy AUPRC by less than the seed-to-seed
  spread (about 0.05 in-pocket on oilgas). Multi-sample ensembling is judged
  the same way against single-best.

## Risks

- **Allocation.** None spent; the balance stays 1,022 s. An unexplained 6 s
  gap before Sprint 21 remains on record.
- **F124's breadth.** EvidenceBasedDB is read-only from here: read, never
  written. QCi NeuraWave must come from primary sources. Anything unverified is
  labeled unverified.
- **F20 depends on a library internal** (`WeakClassifier.clf`). The installed
  `eqc_models` version is recorded with the results.
- **The close-out hook's false positive (F125, not in scope).** Once this
  sprint has its PR and issues, the stale-`develop` count can't trigger it
  falsely during the sprint. It can again at the next planning window.
- **Context and session continuity.** Task actuals are recorded as each task
  finishes.

## Model assignments

All tasks on the top tier in the main loop. A and C are architecture and
research decisions; D and E touch the method. No subagents planned.

## Definition of Done

Per `SPRINT_PLANNING.md`: acceptance met with evidence, suite green, every
number in a results file with its evidence tag, docs updated in the same
commit, committed with the issue number. Sprint-specific:

- No Phase 1 file is changed by this sprint's tasks. IMP-3 enforces that for
  results files from Task B onward.
- Every new results file lives where F123's proposed layout says.
- Zero metered seconds.
