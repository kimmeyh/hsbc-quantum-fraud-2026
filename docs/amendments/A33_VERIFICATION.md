A33 (F84): environment fields on new results.json rows.
Verified 2026-09-19, Sprint 17 Task I.

WHAT WAS CHECKED, and against what:

1. The claim "no row records which OS produced it" -- verified against the
   ARTIFACT, not against the card. Loaded all 168 rows of
   experiments/results/results.json and searched every key on every row for
   os / platform / python / blas / thread / env / machine / host.
   Result: NONE. Zero environment-bearing fields on zero rows.

2. Field coverage across the 168 rows was enumerated to confirm what IS
   recorded: arm, dataset, protocol, seed, config_hash, metrics, evidence_tag
   and metered_seconds on all 168; features_used, retry_count and timestamps
   on 158. None of these identifies a machine.

3. The section-11 required-keys line was read directly
   (experiments/PREREGISTRATION.md:148). It lists the schema and does not
   include any environment field, so adding one is an amendment rather than an
   edit. Confirmed the row schema is stated there and nowhere else that
   conflicts.

4. requirements-lock.txt was read: it pins 18 package versions and records the
   interpreter as a COMMENT (Python 3.12.10), with no platform. So the lock
   file cannot answer the question either. This is what makes the gap real
   rather than cosmetic.

5. The justification was tested rather than assumed. Task H measured the suite
   on Windows and Linux at the same commit: 1,031 passed / 0 failed and
   1,018 passed / 0 failed. There is NO measured behavioral divergence, so
   this amendment is explicitly NOT a fix for a known difference. It is
   provenance. The amendment text says so in those words rather than implying
   a problem that was not observed.

6. The field was shown to carry real information, on both platforms:
     Windows: {"os":"Windows","os_release":"11","python":"3.12.10",
               "threads":32,"blas":"numpy-1.26.4"}
     Linux:   {"os":"Linux","os_release":"5.15.167.4-microsoft-standard-WSL2",
               "python":"3.12.14","threads":32,"blas":"numpy-2.5.3"}
   The Linux reading also exposed a real drift -- that venv resolved numpy
   2.5.3 against the locked 1.26.4 -- which is precisely the class of thing a
   row with no environment cannot show.

7. The guards were proven to FAIL before the amendment was written. Five
   injections into store.py (no stamp, empty stamp, dropped os field,
   overwriting a caller-supplied environment, mutating the caller's dict);
   all five turned test_row_environment.py red, and it restored green.

NOT verified against a reviewer's description of anything. No review is
outstanding; this came from the F84 card and was checked against the store.

NO GATE IS RESCORED. NO PROTOCOL CONTENT CHANGES. No existing row is modified:
the 168 historical rows are deliberately not retrofitted, and a test asserts
they stay that way.
