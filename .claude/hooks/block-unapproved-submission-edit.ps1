<#
.SYNOPSIS
    Block edits to the three submission documents without recorded Product
    Owner approval (workflow Class 4, team lead 2026-09-12).

.DESCRIPTION
    By Sprint 12 proposal.md, appendix.md and team_profile.md had become the
    product. Edits to them were still being made at the speed of edits to code:
    apply first, report after. The Class 4 rule says the opposite -- present
    text-before / text-after / pros / cons / recommendation, and WAIT.

    A rule that lives only in a workflow document depends on the model reading
    it. This hook makes it deterministic: the edit fails unless approval for the
    current session has been recorded.

    HOW TO APPROVE. The team lead's approval is recorded by writing the token
    file, which is gitignored and per-session:

        .claude/.submission-edit-approved

    Claude may create it ONLY after the team lead has approved the specific
    changes in conversation. Creating it pre-emptively to unblock an edit is the
    exact evasion this hook exists to prevent, and it is a process violation
    whether or not anyone notices.

    The file's CONTENT should be the approved change summary, so the record
    survives the session and the next reader can see what was approved.

    Scope: proposal.md, appendix.md, team_profile.md under docs/paper/ only.
    Their -OLD and -min variants are excluded: those are working copies, not the
    submitted artifacts. The rendered PDFs are outputs and are not matched --
    the source is where approval belongs.
#>
$ErrorActionPreference = 'Stop'

try { $raw = [Console]::In.ReadToEnd() } catch { exit 0 }
if (-not $raw) { exit 0 }

try { $payload = $raw | ConvertFrom-Json } catch { exit 0 }

$toolName = $payload.tool_name
if ($toolName -notin @('Edit', 'Write', 'NotebookEdit')) { exit 0 }

$path = $payload.tool_input.file_path
if (-not $path) { exit 0 }

# Normalise separators so the match works from either shell.
$norm = ($path -replace '\\', '/')

# Only the three SUBMITTED documents. Working copies are deliberately exempt.
$guarded = @(
    'docs/paper/proposal.md',
    'docs/paper/appendix.md',
    'docs/paper/team_profile.md'
)
$hit = $guarded | Where-Object { $norm -like "*$_" }
if (-not $hit) { exit 0 }

# -OLD / -min variants share the stem; make sure we did not match one.
$leaf = Split-Path $norm -Leaf
if ($leaf -notin @('proposal.md', 'appendix.md', 'team_profile.md')) { exit 0 }

$root = $env:CLAUDE_PROJECT_DIR
if (-not $root) { $root = (Get-Location).Path }
$token = Join-Path $root '.claude/.submission-edit-approved'

if (Test-Path $token) { exit 0 }

$msg = @"
[BLOCKED] $leaf is a SUBMITTED document. Class 4 (workflow, team lead 2026-09-12)
requires Product Owner approval BEFORE the edit, not after.

Present the change for approval first:

  - text BEFORE
  - text AFTER
  - pros
  - cons
  - recommendation, and why

Then, once the team lead has approved, record it:

  Set-Content .claude/.submission-edit-approved "<what was approved>"

Do NOT create that file to unblock yourself. It records an approval that
happened; creating it without one is the evasion this hook exists to prevent.

Why this is a hook and not a note: by Sprint 12 these three files were the
product, and they were still being edited at the speed of code. A rule in a
document depends on someone reading the document.
"@

# Write to stderr and exit 2 deliberately. `Write-Error` under
# $ErrorActionPreference = 'Stop' TERMINATES the script before `exit 2` runs, so
# the hook exits 1 -- a generic failure rather than the blocking signal Claude
# Code reads from exit 2, and the message never reaches the model as a reason.
# Caught by testing the hook rather than trusting it.
[Console]::Error.WriteLine($msg)
exit 2
