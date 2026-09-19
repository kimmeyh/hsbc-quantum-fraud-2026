# Sprint 17 Summary: Clear the Deck for Phase 2

**Sprint**: 17
**Branch**: `feature/20260919_Sprint_17`
**Dates**: 2026-09-19
**Scope**: F86 (new), F82, F83, F84. F85 closed into F86, F81 closed.
**Metered Dirac-3 seconds**: ZERO, as planned.

## What shipped

All nine tasks. The QCi package is assembled and waiting for the team lead to
send; the three tooling cards are closed with their guards proven by injection.

**F86, the QCi post-submission package.** Seven files: three submitted PDFs at
their filed bytes, three refreshed documents, one plain-text memo. It asks QCi
for nothing except their thoughts, deliberately -- the 30,000-second request
was the previous letter and re-asking inside a thank-you would undercut both.

**F82, the escape-eaten class.** `block_heredoc_escape_loss.py` blocks an
unquoted heredoc whose body carries a backslash escape on its way into a file.

**F83, cross-platform parity.** Measured rather than argued, on both platforms
at the same commit.

**F84, A33.** Every new results row records its execution environment.

## The numbers

| | |
|---|---|
| Tests | 1,031 -> **1,043**, no xfails |
| Windows | 1,043 passed, 71 skipped, 0 failed |
| Linux | 1,043 passed, 71 skipped, 0 failed |
| Amendments | A32 -> **A33** |
| Metered seconds | 0 |
| Grant position | 1,039 of 3,000 drawn, **1,961 remaining** |

The two suite results being identical is itself the F83 result. They differed
by 15 at the start of the sprint.

## The QPU arithmetic, which does not subtract

The sprint plan's own pre-flight said the figures "do not reconcile". They do,
exactly. The trap is that `3,000 - 1,141 = 1,859` is wrong in both directions
at once:

- the campaign total **includes 163 pre-grant free-tier seconds** that never
  touched the allocation
- the campaign total **excludes 61 seconds** of the withdrawn first B3 run,
  which drew on it anyway

Drawn is 1,039. Remaining is **1,961**, endpoint-confirmed in Sprint 12 against
QCi's own API. A reviewer made this same subtraction in Sprint 12 and reported
our figure as an error; it was not. Recorded at `docs/QPU_RECONCILIATION.md`
so the next reader does not re-derive it a third time.

## Three defects found in this sprint's own work

Each was found by verification rather than by review, and each is the same
family this repository keeps paying for.

**The renderer rebuilt the submitted PDFs, twice.** `render_all.py` re-rendered
all three filed artifacts on any invocation. The first fix added an
`--allow-overwrite-submitted` escape hatch; the very next command passed it,
not to rebuild a submission but because it was the quickest way to get an
unrelated test running. The flag is gone and there is no override. An escape
hatch easier to reach than the correct path is not a guard.

**The cross-repository guard had never run in CI.** 15 of its 17 cases skipped
on non-Windows with "powershell not on PATH", but the hook under test is a
Python file invoked through `sys.executable`. CI runs ubuntu-latest. So the
guard enforcing the team lead's cross-repository boundary -- the rule added
after a session wrote into EvidenceBasedDB -- passed by being skipped, and the
boundary was protected on one workstation and nowhere else.

**Two vacuous tests in the new F82 guard**, caught by injection and not by the
green suite that preceded it. A `delim in quoted` branch was dead code, and
`test_bypass_token_allows` passed for two separate wrong reasons in succession.
Three rounds of injection were needed; the first two found defects in the
verification rather than in the thing verified.

## One finding withdrawn

Task D reported that A31 (16.0) and the appendix (28.0) disagreed on the
linear-term span and that `device_resolution.json` recorded neither. **Wrong on
both counts.** The artifact has a `per_pool` array carrying every figure; I
read only the summary block. Max `linear_spread` is 28.0, exactly what the
appendix says, and **A32 had already corrected this on the day of submission**.
Withdrawn the same day, before it reached any outward document. Two things
worth keeping: "not in the artifact" requires reading the whole artifact, and
check the amendment log before reporting a contradiction between documents.

## Deliberately not done

- **The package was not sent.** Assembled for the team lead; Claude never
  sends.
- **No submitted document was edited.** `docs/paper/*` and
  `PREREGISTRATION.md` section content are frozen records of a filing made
  2026-09-12, verified byte-identical at close.
- **`results.json` and `gate_report.md` were not regenerated.** Task H tested
  whether the post-results record reproduces; it did not edit it.
- **The 168 existing rows were not retrofitted** with the new environment
  field. Back-filling provenance that was never observed would be inventing it.
- **No second permanent venv was built.** The Linux environment used for the
  measurement lives outside the repository and nothing depends on it.

## Open for the team lead

**One question, deferred to the end of the sprint deliberately so that nothing
waited on it: the submission date.** The Sprint 17 request says "note on
submission 9/14". `SUBMISSION_RECEIPT.md` records **2026-09-12**, with the
portal confirmation quoted, and the memo is written with that date throughout.
If 9/14 is right, the memo needs one edit before sending.
