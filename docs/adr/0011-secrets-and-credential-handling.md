# ADR-0011: Secrets and credential handling

## Status

Accepted

## Date

2026-08-30 (records practice established Aug 29-30)

## Context

The project touches multiple credentialed services: QCi Dirac-3 (metered API key), Kaggle (OAuth), GitHub (gh CLI), and eventually the challenge portal. The repository becomes a public reproducibility package at Stage 7, and a leaked key is both a security and a budget incident (Dirac seconds are money). The employer-confidentiality constraint adds strings that must never appear in any commit. Numbering note: ADRs 0005-0010 are reserved for the F1-sprint candidates approved in the 2026-08-30 disposition; this ADR takes the next free number.

## Decision

- Credentials NEVER live in the repository. Locations of record: OS user environment or OAuth caches in the user profile (Kaggle `~/.kaggle/credentials.json`, gh keyring); project `.env` (gitignored) only for run-scoped variables, loaded via python-dotenv, following the established ForrierWall pattern for `QCI_API_KEY`.
- `.gitignore` pins the credential file names (`.env`, `kaggle.json`, `credentials.json`); the pre-commit hook hard-blocks staged `.env` files and content matching `.secrets-patterns.txt` (itself gitignored so patterns never enter history). The hook is verified working (blocked a live test secret and a real false positive, both 2026-08-30).
- Credential VALUES are never pasted into chat, logs, commit messages, or results files; scripts log key NAMES and presence booleans only.
- One credential system per service: legacy and new-style credentials must not coexist (the Kaggle env-var-shadowing incident, where legacy `KAGGLE_USERNAME`/`KAGGLE_KEY` silently overrode the working OAuth cache, cost two failed download cycles; the legacy pair was removed).
- The Stage 7 confidentiality scan re-verifies all of this repo-wide before anything goes public.

## Alternatives Considered

### Committed encrypted secrets (git-crypt or SOPS)
- **Pros**: Reproducible environments from clone.
- **Cons**: Key management burden for a solo maintainer; encrypted blobs in a to-be-public repo invite scrutiny; no need since only one machine runs the work.
- **Why Rejected**: Out-of-repo storage is simpler and strictly safer for this project's shape.

## Consequences

### Positive
- A public snapshot of the repo at any commit contains zero credential material by construction, not by cleanup.
### Negative
- Fresh-environment setup requires manual credential provisioning (documented per service in README).
### Neutral
- The hook's text patterns need occasional curation (one false positive already handled by moving filename guards to .gitignore).

## Preregistration touchpoints

None; pure engineering. The preregistration governs methodology; this ADR records engineering decisions only.

## References

`.gitignore`; `.git/hooks/pre-commit`; spamfilter-multi ADR-0008 and ADR-0027; the Dirac-3 usage constraint (hardware approvals); CHECKLIST Stage 7 confidentiality scan item.
