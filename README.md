# Quantum-Enhanced Credit Card Fraud Detection

Phase 1 concept proposal to the **2026 Global Quantum + AI Challenge**
(Resonance Alliance / The Quantum Insider), HSBC track. Submitted **2026-09-12**
by team *Claude Shannon's Fraud Catchers*.

This repository is the evidence behind that submission. Every figure in the
proposal traces to a row in a results store here, and the experiments that
produced them are runnable.

**The headline result is a null, and it is reported as one.** A quantum-inspired
training step (CVQBoost on QCi's Dirac-3) trails a tuned gradient-boosted
classical detector by 0.0399 AUPRC on the ULB benchmark, on nine of ten seeds.
One configuration is positive at scale: an 833-variable arm gains +0.0256 AUPRC
on ten of ten seeds, and it still trails full-feature CatBoost. No quantum
advantage is claimed.

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
| [`experiments/PREREGISTRATION.md`](experiments/PREREGISTRATION.md) | **FROZEN** methodology: hypotheses, gates with numeric pass criteria, splits, seeds, budget. Changes only by dated amendment (32 so far, A1-A32) |
| [`experiments/results/results.json`](experiments/results/results.json) | The row store. Every reported number originates here with a config hash and an evidence tag |
| [`experiments/results/gate_report.md`](experiments/results/gate_report.md) | Regenerated gate scoring: G0 FAIL, G0b PASS, H1b NULL, H4 PARTIAL |
| [`docs/requirements-matrix.md`](docs/requirements-matrix.md) | 92-row acceptance checklist against the four official challenge PDFs |
| [`docs/submission/`](docs/submission/) | Submission receipt, package manifest, compliance walk |
| [`docs/sprints/`](docs/sprints/) | Plan, retrospective and summary for each of 14 sprints |
| `CHECKLIST-Phase1.md` | The Phase 1 record. **CLOSED 2026-09-12 and never updated** |
| `CHECKLIST-Phase2-pre.md` | Live work during the review window |
| `CHECKLIST-Phase2.md` | Dormant until selection; the six committed experiments |
| [`docs/adr/`](docs/adr/) | Architecture decision records |

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

Expected: **12 passed in about 5 seconds**. These are known-answer tests over
the statistical primitives and need no data.

### 4. Run the full suite

```bash
python -m pytest experiments/src/ -q
```

Expected on a fresh clone: **296 passed, 16 skipped, 0 failed**, in about 35
seconds.

**The 16 skips are correct and expected.** They are the tests that need raw
datasets, which are not redistributed here because their licences do not permit
it. A fresh clone cannot run them, and they skip rather than fail so that a red
suite always means a real defect.

One group that used to skip no longer does: the pool-mechanism guard runs
against a committed fixture (`experiments/results/pool_mechanism_fixture.npz`,
0.83 MB) so that the mechanism claim in appendix A.4 is checked on a fresh
clone rather than only on a machine that has the pools.

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

**The hardware rows.** 61 metered fits on QCi's Dirac-3 over 1,141 device
seconds, tagged **[HW]**. They need a funded QCi account, and the allocation was
a grant to this project. What IS reproducible is their classical counterpart:
every hardware fit solves a Hamiltonian that `experiments/src/mechanism_controls.py`
solves exactly, and the agreement between them is itself a reported result.

Raw device responses for 48 of the 61 fits, and job identifiers for 60, are
committed under `experiments/results/`.

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

Development ran as 14 sprints with retrospectives; `docs/sprints/` holds the
record.

## Status

Phase 1 submitted 2026-09-12. Review runs 16 Sep to 14 Nov 2026, with finalist
notification mid-November. Work continues on tooling and Phase 2 preparation;
the submitted documents are a record and are not edited.

## Licence and contact

Team lead: Harold Kimmey, independent researcher. Contact details are in the
team profile. All IP remains with the author per the Challenge Terms &
Conditions section 4.1.
