# Quantum-Enhanced Credit Card Fraud Detection

Phase 1 concept proposal to the **2026 Global Quantum + AI Challenge**
(Resonance Alliance / The Quantum Insider), HSBC track. Submitted **2026-09-12**
by team *Claude Shannon's Fraud Catchers*.

This repository is the evidence behind that submission. Every figure in the
proposal traces to a row in a results store here, and the experiments that
produced them are runnable.

**The headline result is a null, and it is reported as one.** A quantum-inspired
training step (CVQBoost on QCi's Dirac-3) trails a tuned gradient-boosted
classical detector on the ULB benchmark. One configuration is positive at scale
and still trails full-feature CatBoost. No quantum advantage is claimed.

The figures behind that paragraph are not restated here. They live in
[`experiments/results/gate_report.md`](experiments/results/gate_report.md),
regenerated from the row store by `python experiments/src/score_gates.py`, and
in the proposal's own results table. A number copied into a README is a number
that goes stale.

## What was submitted

| Document | Pages | Source |
|---|---|---|
| Concept proposal | 6 | [`docs/paper/proposal.md`](docs/paper/proposal.md) |
| Appendices | 3 | [`docs/paper/appendix.md`](docs/paper/appendix.md) |
| Team profile | 1 | [`docs/paper/team_profile.md`](docs/paper/team_profile.md) |

The rendered PDFs are build outputs and are not committed. Rebuild them with
`scripts/render-all.ps1`; per-file SHA-256 of the submitted versions is recorded
in [`docs/submission/PACKAGE.md`](docs/submission/PACKAGE.md).

### Retrieving the repository exactly as submitted

The submission was built from the state tagged below. To see what a judge sees:

```bash
git clone https://github.com/kimmeyh/hsbc-quantum-fraud-2026.git
cd hsbc-quantum-fraud-2026
git log --oneline --until="2026-09-12"     # the submission commit and earlier
```

The **preregistration freeze** is the anchor for every methodological claim:

```bash
git show prereg-freeze          # tag
git show 95751b9                # the freeze commit, cited by hash in Appendix B
```

Both resolve anonymously. Appendix C's claim that every figure regenerates from
this repository depends on it, so **history is never rewritten and those
references never move**; a hook refuses force-pushes and tag moves.

## Key documents

| Path | What it is |
|---|---|
| [`experiments/PREREGISTRATION.md`](experiments/PREREGISTRATION.md) | **FROZEN** methodology: hypotheses, gates with numeric pass criteria, splits, seeds, budget. Changes only by dated amendment; the log at the top of that file is the count |
| [`experiments/results/results.json`](experiments/results/results.json) | The row store. Every reported number originates here with a config hash and an evidence tag |
| [`experiments/results/gate_report.md`](experiments/results/gate_report.md) | Regenerated gate scoring, verdicts included. Rebuild with `python experiments/src/score_gates.py` |
| [`docs/requirements-matrix.md`](docs/requirements-matrix.md) | The acceptance checklist, walked row by row against the four official challenge PDFs before submission |
| [`docs/submission/`](docs/submission/) | Submission receipt, package manifest, compliance walk |
| [`docs/sprints/`](docs/sprints/) | Plan, retrospective and summary for every sprint |
| `CHECKLIST-Phase1.md` | The Phase 1 record. **CLOSED 2026-09-12 and never updated** |
| `CHECKLIST-Phase2-pre.md` | Live work during the review window |
| `CHECKLIST-Phase2.md` | Dormant until selection; the six committed experiments |
| [`docs/adr/`](docs/adr/) | Architecture decision records |
| [`docs/research/`](docs/research/) | Primary-source research behind design decisions, each recording what could NOT be established alongside what could |

**Evidence tags** appear on every figure: **[HW]** measured on Dirac-3
hardware, **[SIM]** classical or simulated, **[PROJ]** projected. The
distinction is load-bearing and is never blurred.

## How to reproduce

These steps were executed against a fresh clone on 2026-09-12, and the numbers
below are what that clone actually printed.

### 1. Clone and create an environment

```bash
git clone https://github.com/kimmeyh/hsbc-quantum-fraud-2026.git
cd hsbc-quantum-fraud-2026
python -m venv .venv
```

Activate it: `.venv\Scripts\activate` (Windows) or
`source .venv/bin/activate` (Linux/macOS).

**Windows: clone to a short path** such as `C:\src\hqf`. Some dependencies ship
deeply nested files and `pip install` fails with `OSError [Errno 2]` on a long
path unless Windows long-path support is enabled. This is an operating-system
limit, not a repository one.

### 2. Install

```bash
pip install -r experiments/requirements-lock.txt
```

Use the **lock** file, not `requirements.txt`. The lock holds the exact resolved
versions that produced the reported figures; `requirements.txt` states ranges
and resolves differently today (xgboost 2.1 to 3.4 is a major version). The
interpreter used was Python 3.12.10, recorded as a comment in the lock file.

### 3. Run a quick test

```bash
python -m pytest experiments/src/test_metrics.py -q
```

These are known-answer tests over the statistical primitives and need no data,
so they run in seconds. The counts are whatever the suite reports; this file
deliberately does not restate them.

### 4. Run the full suite

```bash
python -m pytest experiments/src/ -q
```

**Expect zero failures and some skips.** The exact counts are whatever pytest
reports, and they are not restated here: this paragraph was written with one set
of numbers and was wrong within the same sprint, which is precisely the failure
one-source-of-truth avoids.

**The skips are correct and expected.** They are the tests that need raw
datasets, which are not redistributed here because their licences do not permit
it. A fresh clone cannot run them, and they skip rather than fail so that a red
suite always means a real defect. Each skip states its own reason; run with
`-rs` to see them.

The pool-mechanism guard is deliberately NOT among them: it runs against a
committed fixture (`experiments/results/pool_mechanism_fixture.npz`) so the
mechanism claim in appendix A.4 is checked on a fresh clone rather than only on
a machine that happens to have the pools.

To skip the one long-running test during iteration:

```bash
python -m pytest experiments/src/ -q -m "not slow"
```

### 5. Optional: stage the datasets

Only needed to run the data-dependent tests and regenerate figures from raw
inputs. `experiments/data/` is gitignored apart from `MANIFEST.json`, which
carries the SHA-256 of every file the frozen loaders read.

| Dataset | Place at | Source |
|---|---|---|
| ULB credit card | `experiments/data/ulb/creditcard.csv` | Kaggle, "Credit Card Fraud Detection" (ULB) |
| IEEE-CIS | `experiments/data/ieee-cis/` | Kaggle, "IEEE-CIS Fraud Detection" |
| SPECTRA | `experiments/data/spectra/spectra_<name>.csv` | see [`docs/references.md`](docs/references.md) |

Then verify against the frozen checksums:

```bash
python scripts/manifest.py verify
```

`VERIFY OK` means every file matches what the results were produced from. Any
other output means the data differs and figures will not reproduce.

Set `HSBC_ULB_CSV` to override the ULB location.

### What you cannot reproduce, and why

**The hardware rows**, tagged **[HW]**. They ran on QCi's Dirac-3 against a
grant to this project and need a funded account. Campaign totals -- fits, metered
seconds, and how many carry a retained job identifier -- are in the appendix and
in [`experiments/results/hw_job_ids.json`](experiments/results/hw_job_ids.json),
not restated here.

`qpu_cost_ledger.json` is a PARTIAL record and is deliberately not named first:
it was last regenerated on 2026-09-09 and predates blocks B2 and B3, so its
totals understate the campaign. It remains accurate for the calls it covers.

What IS reproducible is their classical counterpart: every hardware fit solves a
Hamiltonian that `experiments/src/mechanism_controls.py` solves exactly, and the
agreement between them is itself a reported result. Raw device responses and job
identifiers are committed under `experiments/results/`.

## Repository layout

```
docs/
  paper/          the three submitted documents (sources)
  submission/     receipt, package manifest, compliance walk
  sprints/        plan / retrospective / summary per sprint
  adr/            architecture decision records
  source/         the four official challenge PDFs
experiments/
  src/            runners, analysis, and the test suite
  results/        the row store, artifacts, gate report
  data/           gitignored; MANIFEST.json only
scripts/          rendering, manifest, confidentiality scan
```

## How this project works

Methodology was **frozen before any result was observed** and changes only by
dated amendment. Gates are scored as committed even when they fail: G0 missed
its 0.85 AUPRC floor at 0.8296, and that is reported as a failure along with the
fact that the stopping rule attached to it was not honoured.

Three published claims were found false during external review and withdrawn
(A26, A27) rather than quietly corrected. The amendment log carries them,
including one correction that was itself wrong.

Development ran in sprints with retrospectives; `docs/sprints/` holds the
record.

## Status

Phase 1 submitted 2026-09-12. Review runs 16 Sep to 14 Nov 2026, with finalist
notification mid-November. Work continues on tooling and Phase 2 preparation;
the submitted documents are a record and are not edited.

## Licence and contact

Team lead: Harold Kimmey, independent researcher. Contact details are in the
team profile. All IP remains with the author per the Challenge Terms &
Conditions section 4.1.
