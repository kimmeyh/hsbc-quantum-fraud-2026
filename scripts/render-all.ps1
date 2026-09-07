<#
.SYNOPSIS
    Render every submission PDF with its correct per-document settings.
.DESCRIPTION
    Sprint 5 retrospective, improvement 4. The appendix needs a 0.9in margin: at
    the 1in default it spills 230 characters onto a fourth page against a HARD
    3-page limit, and nothing in render-pdf.ps1 knows that. The margin lived
    only in an ADR paragraph, so any rebuild that did not read the ADR produced
    a silently over-limit appendix.

    This script is the single source of truth for how each document renders.
    Use it instead of calling render-pdf.ps1 directly.
.EXAMPLE
    .\scripts\render-all.ps1
    .\scripts\render-all.ps1 -QciPackage
#>
param(
    [switch]$QciPackage,
    [ValidateSet('letter','a4')][string]$Paper = 'letter'
)
$ErrorActionPreference = 'Stop'
$render = Join-Path $PSScriptRoot 'render-pdf.ps1'
$root = Split-Path -Parent $PSScriptRoot

# source, output, margin. The margin is part of the document's identity here.
$docs = @(
    @{ Source = 'docs\paper\proposal.md';     Out = 'docs\paper\out\proposal.pdf';     Margin = '1in'   }
    @{ Source = 'docs\paper\appendix.md';     Out = 'docs\paper\out\appendix.pdf';     Margin = '0.9in' }
    @{ Source = 'docs\paper\team_profile.md'; Out = 'docs\paper\out\team_profile.pdf'; Margin = '1in'   }
)

if ($QciPackage) {
    $docs += @(
        @{ Source = 'docs\paper\proposal.md';            Out = 'docs\paper\out\qci_package\DRAFT_proposal.pdf';        Margin = '1in'   }
        @{ Source = 'docs\paper\appendix.md';            Out = 'docs\paper\out\qci_package\DRAFT_appendix.pdf';        Margin = '0.9in' }
        @{ Source = 'docs\paper\qci_cover.md';           Out = 'docs\paper\out\qci_package\DRAFT_qci_cover.pdf';       Margin = '1in'   }
        @{ Source = 'experiments\PREREGISTRATION.md';    Out = 'docs\paper\out\qci_package\DRAFT_preregistration.pdf'; Margin = '1in'   }
        @{ Source = 'experiments\results\gate_report.md';Out = 'docs\paper\out\qci_package\DRAFT_gate_report.pdf';     Margin = '1in'   }
        @{ Source = 'docs\HARDWARE_REQUEST_B1_G0b.md';   Out = 'docs\paper\out\qci_package\DRAFT_hardware_plan.pdf';   Margin = '1in'   }
        @{ Source = 'docs\QCI_EQC_MODELS_FEEDBACK.md'; Out = 'docs\paper\out\qci_package\DRAFT_eqc_models_feedback.pdf'; Margin = '1in' }
    )
}

foreach ($d in $docs) {
    & $render -Source (Join-Path $root $d.Source) -Out (Join-Path $root $d.Out) `
              -Paper $Paper -Margin $d.Margin |
        Where-Object { $_ -match 'PDF written|WRONG|LOCKED' }
}

# The renders are not the verification. Read the finished PDFs back.
Write-Host ''
& (Join-Path $root '.venv\Scripts\python.exe') -m pytest (Join-Path $root 'experiments\src\test_submission_artifacts.py') -q
