# Troubleshooting: symptoms, causes, and where the answer already lives

**What this is.** A symptom index. Every entry names something that went wrong
in this repository, what actually caused it, and **where the authoritative
answer lives**. Created 2026-10-03 (IMP-2, Sprint 20 retrospective).

**Why it exists.** `docs/SPRINT_RETROSPECTIVE.md` category 9 has asked for a
"troubleshooting note" since Sprint 2, and no such document was ever created.
Nine retrospectives carry category-9 findings that had nowhere to go, so each
one was rediscovered by a later session.

**The rule this document follows.** It does **not** restate what another file
owns — that is the defect CLAUDE.md bans. Each entry is a pointer with just
enough symptom text to be findable by search. If an entry and its target ever
disagree, the target is right.

**How to use it.** Search this file for the symptom before debugging. That is
the whole mechanism: a one-line lookup is cheaper than a rediscovery, and
Sprint 20 spent most of a task on a rediscovery that `HARDWARE_REQUEST_B4.md`
had already answered.

---

## Environment and interpreter

**Symptom: `ModuleNotFoundError` for a package that is installed.**
A bare `python` on this machine is a different interpreter from the project's.
→ `docs/ENVIRONMENT.md` is the single place the interpreter is recorded.
Enforced by `test_interpreter_paths.py`, which also bans hardcoded venv paths
outside that document.

**Symptom: a test passes locally and fails in CI, or the reverse.**
CI runs ubuntu-latest; the workstation is Windows. Path separators, `fork`
availability and `xelatex` presence all differ.
→ `docs/VENV_PARITY.md`.

---

## Tests that pass when they should not

**Symptom: a guard is green and the thing it guards is broken.**
The repository's most frequent defect class. Presence is not correctness:
asserting a string exists is not asserting the thing it describes is true.
→ `experiments/src/injection.py` provides `Mutation`, `injected()` and
`assert_can_fail()`. Break the thing, confirm red, restore. Enforced in part by
`test_guard_discipline.py`.

Measured instances: a `--force` grep that matched the comment saying the flag
must not exist; a `"270"` presence check that passed after the figure was
deleted from the table that owned it, because seven prose mentions remained; a
figure check that passed while the value was wrong by a factor of ten.

**Symptom: a test skips instead of failing, and the suite reads green.**
"Could not check" rendering as "clean". A skip is legitimate only when the
fixture is genuinely unavailable, and the message must say nothing was checked.
→ `experiments/src/test_sent_correspondence.py::_require` is the pattern to
copy. Sprint 20 measured a case where moving one document aside turned 22
guards into silent skips with exit 0.

**Symptom: a test fails for days during planning, then passes.**
It is reading live sprint state rather than a pinned payload.
→ `experiments/src/test_phase3_artifacts.py` and its `PHASE_ORDER` gate.

---

## Escapes eaten in transit

**Symptom: a file contains a real newline where `backslash-n` was written, or
a `.replace()` reports success and changes nothing.**
Two different layers produce this, and the fix differs:

- An **unquoted** heredoc lets bash expand the body first.
- A **quoted** heredoc is safe from bash, and then Python interprets the
  escape itself because the string literal is not raw. A `b""` literal does
  this too; only `r""`, `rb""` and `br""` are exempt.

→ `.claude/hooks/block_heredoc_escape_loss.py` blocks both, with the fix list
in its block message. Preferred fix: use the Edit or Write tool and avoid the
shell layer entirely.

**Symptom: a JSON config key points at a file that does not exist, and the
hook never runs.**
A single backslash in a JSON string is an escape. `\b` is a backspace.
→ CLAUDE.md, "don't let a shell or a JSON parser eat an escape".

---

## Hooks

**Symptom: a Stop hook does not block when it should.**
A hook killed at its configured timeout produces **no exit code**, so it
cannot block — a timeout fails OPEN. Measured 2026-10-03.
→ `.claude/hooks/verify_closeout_complete.py` carries the budget arithmetic at
the point of ordering, and `test_ci_status.py` enforces that the sum of
internal subprocess timeouts fits the configured budget.

**Symptom: a hook passes on a detached HEAD and fails in a normal clone, or
the reverse.**
`git branch --show-current` returns empty on the detached HEAD that
`actions/checkout` leaves. A hook gating on the branch name returns ALLOW
before reaching any check.
→ Supply `branch_override` in the payload. `test_phase3_artifacts.py` does.

---

## Hardware and cost

**Symptom: a cost estimate disagrees with another record of the same block.**
Estimates were written at different times against different knowledge, and
none was retired when the next arrived.
→ The read list in the capability pre-flight (`docs/SPRINT_PLANNING.md`):
`HARDWARE_REQUEST_*`, `*_RESULT.md`, `*_RECONCILIATION.md`, `RESULTS_MEMO.md`,
and the frozen preregistration's sections 4 and 10. For SPECTRA specifically,
`docs/SPECTRA_BLOCK_RECONCILIATION.md`.

**Symptom: QCi rejects a job with "400 ... Must specify one and only one job
under the job_submission.problem_config field".**
The request was built by hand instead of by the library. Every block since B1
submits through `eqc_models`.
→ `experiments/src/eqc_submit.py` (`metered_fit`; `offline_solver` for a dry
run that reaches the request). The capability pre-flight lists the proven
runner to copy.

**Symptom: the cost ledger shows Dirac-3 calls nobody launched.**
A test invoked a metered runner and checked for a refusal only after the
subprocess returned; once the window opened, the run went ahead.
→ Runners refuse inside any pytest process;
`experiments/src/test_metered_runners_refuse_in_tests.py`.

**Symptom: something is reported "not defined here" or "blocked on the team
lead", and it exists.**
Absence was asserted without a search.
→ The absence rule in the capability pre-flight: search the card's earlier
bullets, the frozen preregistration, and the commits on the subject first.

**Symptom: a proxy result is read as a device result.**
The classical proxy solves the identical Hamiltonian, so it is easy to treat
its behavior as a device prediction. It is not. Rows carry
`evidence_tag: PROJ` with `metered_seconds: 0`.
→ `docs/HARDWARE_REQUEST_B4.md` line 89 explains why the SPECTRA proxy's
negative in-segment edges are expected rather than a warning sign. Sprint 20
rediscovered that at the cost of most of a task.

**Symptom: the allocation balance does not reconcile.**
Free-tier seconds before the grant, and a withdrawn run, both complicate it.
→ `docs/QPU_RECONCILIATION.md`.

---

## Shell, paths and tooling on this workstation

The two entries below are **added from the spamfilter-multi repository's own
troubleshooting document** (team lead, 2026-10-03). That repository is
read-only from here and nothing in it was modified. Both entries are
machine-level rather than project-level, which is why they apply.

Its path is deliberately not written as a backtick file reference: it resolves
on this workstation and nowhere else, and a pointer that cannot resolve is the
failure `test_troubleshooting_index.py` exists to catch.

**Symptom: a grep or ripgrep pattern containing a Windows path matches
nothing.**
Backslashes in the pattern are read as escape characters.
→ Use forward slashes in patterns on every platform, including Windows:
`grep -r "D:/Data/Harold/github" .` rather than `D:\Data\...`. Relative
paths (`grep -r "docs/SPRINT" .`) avoid the question entirely. Ripgrep
normalizes internally, so forward slashes are correct everywhere.

**Symptom: `git push` or `git fetch` fails with "SSL peer certificate or SSH
remote key was not OK", having worked the day before with no config change.**
Norton's encrypted-connections scanning intercepts the TLS connection to
GitHub and re-signs it with a Norton root. Git-for-Windows validates against a
bundled CA file that does not contain that root, so validation fails. Browsers
accept it because Norton installs its root in the Windows store. A silent
Norton LiveUpdate can re-enable interception, which is why it breaks
unpredictably.

Diagnose by reading the issuer:

```
echo | openssl s_client -connect github.com:443 -servername github.com 2>/dev/null | openssl x509 -noout -issuer
```

A Norton issuer confirms interception; Sectigo or DigiCert is GitHub's real
CA. Durable fix: `git config --global http.sslBackend schannel`, so git trusts
the Norton certificate through the Windows store and survives a LiveUpdate.
Do **not** set `http.sslVerify false` — that disables the check that would
reveal a real interception.

**NOT imported from that repository, deliberately.** Its PowerShell guidance
("always use PowerShell for Windows paths") is correct there and wrong here:
F78 removed PowerShell from this repository because CI runs ubuntu-latest, and
this repository's CLAUDE.md separately names the global PowerShell footer
script as a thing not to use. Its Flutter, Android, Gmail OAuth, emulator and
UI sections have no surface here.

---

## Documents of record

**Symptom: a submitted or sent artifact's bytes changed.**
Re-rendering a PDF changes its `/ID` trailer even when the content is
identical, so the file is no longer the one that was filed.
→ `experiments/src/test_published_artifacts.py` pins the three filed PDFs by
sha256; `test_sent_correspondence.py` pins the sent QCi correspondence, whose
hashes are recorded in `docs/QCI_CORRESPONDENCE_HASHES.md`.

**Symptom: a figure in one document disagrees with the document that owns it.**
A number restated in a second place drifts.
→ CLAUDE.md, "don't restate a number that another file owns". Suite counts are
never restated anywhere.

---

## Adding to this file

Add an entry when a category-9 finding has an authoritative home. One symptom
line, one cause line, one pointer. If there is no home yet, the entry is
premature: write the fix first, then point at it.
