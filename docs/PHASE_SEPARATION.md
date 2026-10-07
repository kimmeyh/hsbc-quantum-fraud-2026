# Phase 1 / Phase 2 Separation: the Decision Document (F123)

**Sprint 22 Task A** (#160). Written 2026-10-06. **Status: approved in
principle by the team lead at Sprint 22 planning ("generally approve
recommendation - could be adjusted during Manual Validation"). Nothing listed
for MOVE below has been moved; every move waits for his approval of this
document.**

The team lead's question (2026-10-06): "since we are no longer in phase 1 and
now in phase 2, there should be a separate set of files (JSON, .md...) and
reports for phase 2 so that we are not updating phase 1 files ... separate
what we do and learn in phase 2 without affecting phase 1 files (primarily the
locked down files and files that these files were based on)."

## 1. The boundary: the filing, not the freeze

**The preregistration freeze cannot be the boundary.** At `prereg-freeze`
(`95751b9`) the source tree held four files: `data.py`, `metrics.py`,
`smoke_test.py`, `tune.py`. Every other Phase 1 module -- `qubo_proxy`,
`score_gates`, `store`, `spectra_segment`, the hardware runners -- was written
after the freeze under dated amendments, and produced the evidence that was
filed.

**The boundary is the filing, 2026-09-12** (the last commit that day,
`f35699c`). A Phase 1 file is a tracked file that existed at `f35699c` in one
of the groups below. Anything created after it is Phase 2 by default.

## 2. Inventory

### Group L -- LOCKED (documents of record; never edited)

- `experiments/PREREGISTRATION.md` -- FROZEN; tag `prereg-freeze`
- `docs/paper/` and `docs/submission/`, including the three submitted PDFs
  (hashes pinned by `test_published_artifacts.py`)
- The sent QCi package (`docs/qci_package/`, gitignored, hashes pinned in
  `docs/QCI_CORRESPONDENCE_HASHES.md`), and the four package documents the
  team lead declared FINAL on 2026-09-27

These are already guarded: the submission-edit hook, the frozen-history hook,
and the hash tests.

### Group B -- BUILT-FROM (the evidence chain behind group L; not yet guarded)

- **Evidence**: everything under `experiments/results/` at `f35699c`:
  `results.json`, `gate_report.md`, `qpu_cost_ledger.json` and the other
  result artifacts
- **Code**: the non-test modules under `experiments/src/` at `f35699c` --
  the loaders, `data`, `metrics`, `store`, `qubo_proxy`, `score_gates`,
  `spectra_segment`, the `run_*` runners and the rest
- Tests under `experiments/src/test_*.py` are NOT in group B: they verify
  both phases and stay where CI finds them (`pytest.ini: testpaths`)

## 3. What has already changed since the filing

Measured with `git log f35699c..HEAD`. **Not only Sprint 21**: group B has
been changing for weeks.

| Kind | Files | When | Recorded? |
|---|---|---|---|
| Mechanical: interpreter path | `h6_twin_preflight.py`, `pilot_variance.py`, `smoke_test.py` | Sprint 16 (#117) | in commit only |
| Report layout | `score_gates.py`, `gate_report.md` | Sprint 17 | in commit only |
| Row stamping | `store.py` (environment on every new row) | Sprint 17 | **amendment A33** |
| New evidence, frozen-grid follow-ups | `qubo_proxy.py`, `results.json`, `gate_report.md` | Sprint 18 (F64, F91) | in commits |
| Review fixes | `run_hardware_b3.py`, `store.py` | Sprints 14 and 18 | in commits |
| Hardware evidence B4/B5 | `results.json`, `gate_report.md`, `qpu_cost_ledger.json` | Sprint 21 | `docs/B4_B5_HARDWARE_RESULT.md` |
| **Analysis code, no amendment** | `spectra_segment.py` (feasibility gate) | Sprint 21 | **none** |
| Correction to a Phase 1 doc | `docs/HARDWARE_REQUEST_B4.md` (additive) | Sprint 21 | dated in the text |
| New post-filing files in Phase 1 directories | `run_hardware_b4.py`, `run_hardware_b5.py`, `eqc_submit.py`, `run_f100_classical_bar.py`, `f100_lane_pilot.py`; `f100_*.json`, `f101_*.json`, `b4_hardware.json`, `b5_hardware.json` | Sprint 21 | in commits |

## 4. Recommendation

### 4.1 Freeze group B now; route everything new to Phase 2

**Recommended.** From approval onward, nothing new is written into group B.
Phase 2 code and evidence live in their own tree (section 5). Phase 2 code
reaches Phase 1 code by IMPORTING it, never by editing it; where Phase 2 needs
different behavior, it wraps.

**Why not also move the past changes out:** every move rewrites group B files
again -- regenerating `gate_report.md`, rewriting `results.json`, updating
every document that cites a row -- which is the very churn this card exists to
stop. Freezing in place stops it today; relocating repeats it once more. The
filed paper's figures resolve against `results.json` either way
(`test_document_figures_resolve.py`), so leaving the post-filing rows in place
does not touch any submitted figure.

### 4.2 Disposition of each past change (for the team lead)

- **Mechanical, layout, A33, review fixes**: **KEEP.** No evidence changed, or
  the change is a recorded amendment.
- **Sprint 18 rows (F64, F91) and Sprint 21 B4/B5 rows**: **KEEP in place.**
  B4 and B5 are blocks of the frozen Phase 1 grid (PREREGISTRATION section
  10), run after the filing; the Phase 1 store is a legitimate home for
  completing the committed grid. They are marked by date and block, and every
  new row from approval onward goes to the Phase 2 store.
- **`spectra_segment.py` feasibility gate**: **KEEP, with a decision needed.**
  Reverting it would make the B4 rows unreproducible from the code that scored
  them. But it is Phase 1 analysis code changed without the dated amendment
  section 11 requires, and the team lead has ruled out Phase 1 amendments. The
  honest record is a dated note in a Phase 2 document (this one), saying what
  changed and why, rather than an amendment to the frozen file.
- **`HARDWARE_REQUEST_B4.md` correction**: **KEEP.** It is additive and
  dated, and the sent text stands beneath it.
- **New post-filing files in Phase 1 directories**: **MOVE at approval** to the
  Phase 2 tree. They were never Phase 1 files; they are Phase 2 work that
  landed in the wrong place because no Phase 2 place existed.

### 4.3 The alternative, if the team lead prefers it

**Relocate all post-filing evidence** (the Sprint 18 and 21 rows, B4/B5 and
their reports) to the Phase 2 store, and restore group B evidence to its
filing-day content. Cleaner boundary, one more round of churn, and every
document citing those rows needs its paths updated.

## 5. The Phase 2 layout

```
experiments/phase2/
  src/       Phase 2 modules. Import Phase 1 code read-only; never edit it.
  results/   Phase 2 evidence: its own results.json (same row schema, plus
             "phase": 2), its own cost ledger, its own reports.
docs/phase2/ Phase 2 documents: research, results, the Phase 2
             preregistration (F102) when it is written.
```

Tests stay in `experiments/src/test_*.py`, where CI already runs them.

**Provisional use this sprint** (approved at planning): Sprint 22 Tasks C, D
and E write only into these locations. Nothing that already exists moves.

## 6. The guard design

A rule in a document has failed in this repository every time it was the only
control. Three mechanisms, each extending one that already exists:

1. **Edit guard (IMP-4, carded).** Extend `block_unapproved_submission_edit.py`
   from group L to group B: a PreToolUse block on editing any group B path.
   The path list is generated from `git ls-tree f35699c`, not typed. No
   override token ships with it (CLAUDE.md, Sprint 17); a genuine exception
   arrives later, in its own commit, with its own reason.
2. **Evidence immutability in the suite (IMP-3, Task B this sprint).**
   Tracked results files are hashed when the suite starts and when it ends; any
   change fails the run and names the file.
3. **Placement check (new, small).** A test that fails when a file created
   after `f35699c` sits in a group B directory, with an allowlist holding the
   files section 4.2 lists for MOVE, so the list can only shrink.

## 7. Premise falsifier

The premise is that Phase 2 work can run without changing a Phase 1 file.
**Falsifier**: a Phase 2 task that cannot run unless a group B file changes.
None was found during this sprint's planning or execution; any that appears is
recorded here, not worked around.

## 8. What the team lead decides at Manual Validation

1. Approve section 4.1 (freeze group B in place), or choose section 4.3
   (relocate post-filing evidence)
2. Approve the MOVE of the post-filing files listed in section 3 into the
   Phase 2 tree
3. The `spectra_segment.py` record: the dated note in this document, as
   recommended, or something else
4. IMP-4 and the placement check as designed in section 6

## 9. Decision, 2026-10-07: Phase 2 moves to its own repository

Team lead, Sprint 22 Manual Validation. **This supersedes sections 4 to 6.**
Phase 2 continues in a new, PRIVATE repository, started from this
repository's `develop` with full history. This repository is then restored
to its as-filed state and archived on GitHub (read-only).

Why: the filed proposal and appendix cite
`github.com/kimmeyh/hsbc-quantum-fraud-2026`, a public repository. A reader
following that link should see what was filed, not the post-filing work.
An archived repository refuses every push, which is a stronger guard than
any hook. And a separate repository keeps every Phase 2 path unchanged.

Sequence (card F127): close Sprint 22 here on the current layout; the team
lead creates the new repository; push `develop` there with history; copy
the untracked files (`.env`, datasets, predictions, the private QCi
package) with their ignore rules written first; CI green there; one restore
commit here to `f35699c`, tagged `as-filed`; the team lead archives this
repository.

Exceptions to the restore, kept at their current content:

- `docs/paper/qci_cover.md` stays OUT. It was in the tree at the filing and
  was moved out on 2026-09-17 because it is private commercial
  correspondence.
- The three filed PDFs (`docs/paper/out/`, committed 2026-09-18) stay IN.
  They are the filed bytes, hashes pinned.
- `docs/submission/PACKAGE.md` and `SUBMISSION_RECEIPT.md` keep their
  post-filing text, which says the PDFs are tracked and why. Restoring the
  filing text would say the PDFs are not tracked, beside the tracked PDFs.
  (Proposed; confirmed by the team lead before the restore.)
