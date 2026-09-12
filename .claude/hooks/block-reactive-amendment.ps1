<#
.SYNOPSIS
    Require amendments to the FROZEN preregistration to be deliberate
    (workflow "VERIFY BEFORE AMENDING", team lead 2026-09-11).

.DESCRIPTION
    In Sprint 12 a reviewer's finding was accepted and a correction to the
    preregistration published within hours. The correction was itself FALSE --
    the convexity claim, withdrawn the next day in A27 -- and two independent
    external reviews caught it. Amending under time pressure reproduced the
    exact defect class the amendment protocol exists to record.

    The rule that came out of it: a review finding is not actionable until
    independently verified against the code or artifact it describes, and
    corrections are BATCHED behind a completed analysis rather than written
    while the review is still arriving.

    A rule in a workflow document depends on the model reading the document.
    This hook makes the preregistration edit itself require a deliberate act.

    HOW TO PROCEED. Record the verification before amending:

        .claude/.amendment-verified

    Its content should name what was checked and how -- the code path, the
    artifact, the recomputation. Claude may create it ONLY after that
    verification has actually been done. Creating it to unblock an edit is the
    evasion this hook exists to prevent, and the whole point is that the
    verification is cheap and skipping it is what went wrong.

    Scope: experiments/PREREGISTRATION.md only. It is the one frozen document
    where "amendments only" is the governing rule, and the one where a hasty
    correction is itself a protocol violation rather than an ordinary edit.
#>
$ErrorActionPreference = 'Stop'

try { $raw = [Console]::In.ReadToEnd() } catch { exit 0 }
if (-not $raw) { exit 0 }

try { $payload = $raw | ConvertFrom-Json } catch { exit 0 }

if ($payload.tool_name -notin @('Edit', 'Write', 'NotebookEdit')) { exit 0 }

$path = $payload.tool_input.file_path
if (-not $path) { exit 0 }

$norm = ($path -replace '\\', '/')
if ($norm -notlike '*experiments/PREREGISTRATION.md') { exit 0 }

$root = $env:CLAUDE_PROJECT_DIR
if (-not $root) { $root = (Get-Location).Path }
$token = Join-Path $root '.claude/.amendment-verified'

if (Test-Path $token) { exit 0 }

$msg = @"
[BLOCKED] PREREGISTRATION.md is FROZEN. Amendments only, and only after the
finding behind them has been independently verified (workflow: VERIFY BEFORE
AMENDING, team lead 2026-09-11).

Before amending:

  1. Verify the finding against the CODE or the ARTIFACT it describes.
     Not against the reviewer's description of it.
  2. If a review is still arriving, WAIT and batch. Do not amend per finding.
  3. Record what you checked:

     Set-Content .claude/.amendment-verified "<what was checked, and how>"

Do NOT create that file to unblock yourself.

Why this is a hook: in Sprint 12 a correction was written in response to a
review finding and published within hours. The correction was false. Two
external reviews caught it the same day, and A27 records the withdrawal. The
verification that would have prevented it took four minutes when it was finally
done.
"@

[Console]::Error.WriteLine($msg)
exit 2
