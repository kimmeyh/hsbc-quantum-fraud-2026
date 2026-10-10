<#
.SYNOPSIS
    Stop hook blocking a turn that CLAIMS sprint/phase close-out completion
    while machine-checkable artifacts contradict it. Ported 2026-09-02 from
    spamfilter-multi (Sprint 50 escape lesson), adapted to this repo's
    sprint_status schema (current_sprint.pr, updated) and doc paths.

.DESCRIPTION
    Fires ONLY when the final assistant message claims close-out completion
    AND an artifact contradicts it. Checks: sprint_status currency and sprint
    number; PR recorded once plan_approved; previous sprint SUMMARY exists
    (three-doc rule); uncommitted 0* team-lead files; open sprint-labeled
    issues AFTER the sprint PR merged (post-merge precondition -- spamfilter
    Sprint 51 false-positive lesson).

.NOTES
    Exit 0 = allow stop. Exit 2 = block with guidance.
    Bypass: branch name containing allow_stop_hook_bypass.
#>

$ErrorActionPreference = 'Stop'

try {
    $raw = [Console]::In.ReadToEnd()
    if (-not $raw) { exit 0 }
    $payload = $raw | ConvertFrom-Json
} catch { exit 0 }

$cwd = [string]$payload.cwd
if (-not $cwd) { $cwd = (Get-Location).Path }
if ($payload.repo_override) { $cwd = [string]$payload.repo_override }

$lastMessage = ''
try {
    if ($payload.last_assistant_message) {
        $lastMessage = [string]$payload.last_assistant_message
    } elseif ($payload.messages) {
        $assistantMsgs = @($payload.messages | Where-Object { $_.role -eq 'assistant' })
        if ($assistantMsgs.Count -gt 0) { $lastMessage = [string]$assistantMsgs[-1].content }
    }
} catch { $lastMessage = '' }
if (-not $lastMessage) { exit 0 }

# Gate 1: sprint feature branch only.
$branchOverride = [string]$payload.branch_override
if ($branchOverride) { $branch = $branchOverride.Trim() }
else {
    try { $branch = (& git -C $cwd branch --show-current 2>$null).Trim() } catch { $branch = '' }
}
if (-not $branch) { exit 0 }
if ($branch -match 'allow_stop_hook_bypass') { exit 0 }
if ($branch -notmatch '^feature/\d+_Sprint_(\d+)') { exit 0 }
$sprintNum = [int]$Matches[1]

# Gate 2: does the message CLAIM close-out completion? (narrow, anchored)
$claimPatterns = @(
    '(?i)\b(the\s+)?(sprint|phase\s*[78]|close[- ]?out|post[- ]?merge)\s+(work\s+|process\s+)?(is|was)\s+(now\s+)?(fully\s+|genuinely\s+)?(complete|closed|done|finished)\b'
    '(?i)\bclose[- ]?out\b[^.\n]{0,40}\b(is|was)\s+(now\s+)?(complete|done|finished)\b'
    '(?i)\ball\s+(the\s+)?(post[- ]?merge|checklist|close[- ]?out)\s+(items|steps)\b[^.\n]{0,40}\b(are\s+)?(now\s+)?(complete|done)\b'
    '(?i)\bready\s+for\s+(the\s+)?next\s+sprint\b'
    '(?i)\bsprint\s+\d+\s+is\s+(fully\s+)?(closed|complete)\b'
)
$midSprintPatterns = @(
    '(?i)\b(task|tier|sub[- ]?task)\s+\w+\b[^.\n]{0,40}\b(blocked|in progress|not started|remaining|pending)\b'
    '(?i)\bstopping criterion\s*\d'
    '(?i)\b(is|remains)\s+blocked\b'
    '(?i)\bstill\s+(executing|in\s+flight|running)\b'
)
$claims = $false
foreach ($pat in $claimPatterns) { if ($lastMessage -match $pat) { $claims = $true; break } }
if ($claims) {
    foreach ($pat in $midSprintPatterns) { if ($lastMessage -match $pat) { $claims = $false; break } }
}
if (-not $claims) { exit 0 }

# Gate 3: machine-checkable artifacts.
$violations = @()
$status = $null

$statusPath = Join-Path $cwd '.claude/sprint_status.json'
if (-not (Test-Path -LiteralPath $statusPath)) {
    $violations += ".claude/sprint_status.json is MISSING."
} else {
    try {
        $status = Get-Content -LiteralPath $statusPath -Raw | ConvertFrom-Json
        $statusSprint = [int]$status.current_sprint.number
        if ($statusSprint -ne $sprintNum) {
            $violations += ".claude/sprint_status.json current_sprint.number is $statusSprint but the branch is Sprint $sprintNum -- stale state file misleads the next session."
        }
    } catch { $violations += ".claude/sprint_status.json is not valid JSON." }
}

# PR recorded once plan approved (workflow 3.3.1; precondition per spamfilter F170).
if ($status -and $status.current_sprint -and $status.current_sprint.plan_approved -eq $true) {
    $prNum = $status.current_sprint.pr
    if ($null -eq $prNum -or [string]$prNum -eq '') {
        $violations += "plan_approved is true but current_sprint.pr is null -- workflow 3.3.1 requires the draft PR recorded."
    }
}

# Uncommitted 0* team-lead working files at close-out (commit neutrally, never read).
try {
    $dirty = & git -C $cwd status --porcelain -- '0*' 2>$null
    if ($dirty) {
        $names = @($dirty | ForEach-Object { ($_ -replace '^..\s*', '').Trim() }) -join ', '
        $violations += "Uncommitted team-lead 0* working file(s): $names. Commit with a neutral message (never read them)."
    }
} catch { }

# Previous sprint SUMMARY (three-doc rule, workflow 3.2.1).
$prevSprint = $sprintNum - 1
if ($prevSprint -gt 0) {
    $prevSummary = Join-Path $cwd ("docs/sprints/SPRINT_{0}_SUMMARY.md" -f $prevSprint)
    $prevRetro = Join-Path $cwd ("docs/sprints/SPRINT_{0}_RETROSPECTIVE.md" -f $prevSprint)
    if ((Test-Path -LiteralPath $prevRetro) -and -not (Test-Path -LiteralPath $prevSummary)) {
        $violations += "docs/sprints/SPRINT_${prevSprint}_SUMMARY.md is missing (three-doc rule, workflow 3.2.1)."
    }
}

# Open sprint issues -- POST-MERGE precondition only.
try {
    $prMerged = $false
    $prJson = & gh pr list --head $branch --state all --json state,mergedAt 2>$null
    if ($LASTEXITCODE -eq 0 -and $prJson) {
        foreach ($pr in ($prJson | ConvertFrom-Json)) {
            if ($pr.state -eq 'MERGED' -or $pr.mergedAt) { $prMerged = $true }
        }
    }
    if ($prMerged) {
        $ghOut = & gh issue list --label sprint --state open --json number 2>$null
        if ($LASTEXITCODE -eq 0 -and $ghOut) {
            $open = $ghOut | ConvertFrom-Json
            if ($open.Count -gt 0) {
                $nums = ($open | ForEach-Object { "#$($_.number)" }) -join ', '
                $violations += "Sprint PR MERGED but sprint-labeled issues still OPEN: $nums ('Closes #N' does not fire on feature->develop merges; close manually, workflow 2.3)."
            }
        }
    }
} catch { }

if ($violations.Count -eq 0) { exit 0 }

$msg = @"
[BLOCKED by verify-closeout-complete hook]

The final message claims close-out completion, but these artifacts contradict it:

$($violations | ForEach-Object { "  - $_" } | Out-String)
Open docs/SPRINT_CHECKLIST.md, walk the close-out section line by line, and fix
each violation. Verify by CHECKING the artifact, not by recalling. Do not
re-assert completion until every item is verified done.

Bypass (only if a violation is genuinely not applicable): rename the branch to
include allow_stop_hook_bypass, or state explicitly which item does not apply and why.
"@
[Console]::Error.WriteLine($msg)
exit 2
