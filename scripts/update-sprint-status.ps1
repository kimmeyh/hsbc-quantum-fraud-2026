# Update .claude/sprint_status.json safely via parsed JSON (Sprint 2 retro improvement 4).
# Usage:
#   .\scripts\update-sprint-status.ps1 -Set status=phase_4_execution
#   .\scripts\update-sprint-status.ps1 -Set plan_approved=true -Set pr=3
#   .\scripts\update-sprint-status.ps1 -NewSprint 3 -Name "Classical Evidence" -Branch feature/20260901_Sprint_3 -PlanDoc docs/sprints/SPRINT_3_PLAN.md
# Keys in -Set target current_sprint.<key>; booleans and integers are typed automatically.
param(
    [string[]]$Set = @(),
    [int]$NewSprint = 0,
    [string]$Name,
    [string]$Branch,
    [string]$PlanDoc
)
$path = Join-Path $PSScriptRoot "..\.claude\sprint_status.json"
$j = Get-Content $path -Raw | ConvertFrom-Json

if ($NewSprint -gt 0) {
    $j.last_completed_sprint = [PSCustomObject]@{
        number = $j.current_sprint.number
        merged_pr = $j.current_sprint.pr
        main_merge_pr = $null
        docs_triad_complete = $false
    }
    $j.current_sprint = [PSCustomObject]@{
        number = $NewSprint; name = $Name; branch = $Branch
        status = "phase_1_backlog_refinement"; plan_doc = $PlanDoc
        pr = $null; plan_approved = $false; github_issues = @()
    }
}

foreach ($kv in $Set) {
    $k, $v = $kv -split '=', 2
    $typed = switch -Regex ($v) {
        '^(true|false)$' { [bool]::Parse($v); break }
        '^\d+$'          { [int]$v; break }
        default          { $v }
    }
    if ($j.current_sprint.PSObject.Properties.Name -contains $k) {
        $j.current_sprint.$k = $typed
    } else {
        $j.current_sprint | Add-Member -NotePropertyName $k -NotePropertyValue $typed
    }
}

$j.updated = Get-Date -Format "yyyy-MM-dd"
$j | ConvertTo-Json -Depth 6 | Set-Content $path -Encoding utf8
Write-Host "sprint_status.json updated: sprint $($j.current_sprint.number), status $($j.current_sprint.status)"
