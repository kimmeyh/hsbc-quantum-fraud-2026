<#
.SYNOPSIS
    Render a Markdown source to submission-grade PDF (ADR-0012 toolchain).
.DESCRIPTION
    Markdown -> docx (pandoc) -> PDF (Word COM). Chosen after a Sprint 5
    pre-flight found pandoc present but with NO PDF engine (no xelatex or
    pdflatex) and WeasyPrint unusable (missing GTK libraries). Word is
    installed, produces reliable A4/Letter output with tables intact, and
    embeds fonts, which the portal requires.
.EXAMPLE
    .\scripts\render-pdf.ps1 -Source docs\paper\proposal.md -Out docs\paper\out\proposal.pdf
#>
param(
    [Parameter(Mandatory)][string]$Source,
    [Parameter(Mandatory)][string]$Out,
    [string]$Reference,                       # optional reference.docx for styling
    [ValidateSet('letter','a4')][string]$Paper = 'letter'
)
$ErrorActionPreference = 'Stop'
$src = (Resolve-Path $Source).Path
$outDir = Split-Path -Parent $Out
if ($outDir -and -not (Test-Path $outDir)) { New-Item -ItemType Directory -Force $outDir | Out-Null }
$docx = [System.IO.Path]::ChangeExtension([System.IO.Path]::GetTempFileName(), '.docx')

$pandocArgs = @($src, '-o', $docx, '--standalone')
if ($Reference) { $pandocArgs += @('--reference-doc', (Resolve-Path $Reference).Path) }
& pandoc @pandocArgs
if ($LASTEXITCODE -ne 0) { throw "pandoc failed on $Source" }

$word = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $doc = $word.Documents.Open($docx)
    $doc.PageSetup.PaperSize = if ($Paper -eq 'a4') { 7 } else { 1 }   # wdPaperA4 / wdPaperLetter
    $full = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $Out))
    $doc.SaveAs([ref]$full, [ref]17)                                   # wdFormatPDF
    $pages = $doc.ComputeStatistics(2)                                 # wdStatisticPages
    $doc.Close($false)
    Write-Host "PDF written: $full ($pages pages)"
} finally {
    if ($word) { $word.Quit() }
    Remove-Item $docx -ErrorAction SilentlyContinue
}
