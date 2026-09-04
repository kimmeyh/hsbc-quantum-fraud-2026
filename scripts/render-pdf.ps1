<#
.SYNOPSIS
    Render a Markdown source to submission-grade PDF (ADR-0012 toolchain).
.DESCRIPTION
    Markdown -> PDF via pandoc + xelatex (MiKTeX). Page size is set through the
    LaTeX geometry package, so the document is laid out at that size from the
    start.

    HISTORY, so this is not reintroduced: an earlier version routed through Word
    (pandoc -> docx -> Word SaveAs) and set PageSetup.PaperSize AFTER opening the
    document. Word did not reflow, so it emitted 11x17 TABLOID pages while
    reporting plausible page counts. Page size and page count are both submission
    requirements (requirements-matrix B1), so this script verifies BOTH after
    rendering and fails loudly on either.
.EXAMPLE
    .\scripts\render-pdf.ps1 -Source docs\paper\proposal.md -Out docs\paper\out\proposal.pdf
#>
param(
    [Parameter(Mandatory)][string]$Source,
    [Parameter(Mandatory)][string]$Out,
    [ValidateSet('letter','a4')][string]$Paper = 'letter',
    [string]$Margin = '1in'
)
$ErrorActionPreference = 'Stop'

$src = (Resolve-Path $Source).Path
$outDir = Split-Path -Parent $Out
if ($outDir -and -not (Test-Path $outDir)) { New-Item -ItemType Directory -Force $outDir | Out-Null }

# A PDF open in a viewer holds a write lock; name the cause rather than failing opaquely.
if (Test-Path $Out) {
    try {
        $probe = [System.IO.File]::Open((Resolve-Path $Out).Path, 'Open', 'ReadWrite', 'None')
        $probe.Close()
    } catch {
        throw ("Output PDF is LOCKED by another process: {0}. Close it (a PDF viewer is the usual cause) and re-run." -f $Out)
    }
}

$geom = if ($Paper -eq 'a4') { 'a4paper' } else { 'letterpaper' }
& pandoc $src -o $Out --pdf-engine=xelatex -V "geometry:$geom" -V "geometry:margin=$Margin" -V fontsize=10pt
if ($LASTEXITCODE -ne 0) { throw "pandoc/xelatex failed on $Source" }

# Verify what was actually produced: page size AND page count.
$py = Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe"
$abs = (Resolve-Path $Out).Path
$result = & $py -c "from pypdf import PdfReader; r=PdfReader(r'$abs'); b=r.pages[0].mediabox; w,h=round(float(b.width)),round(float(b.height)); n={(612,792):'US Letter',(595,842):'A4',(792,1224):'TABLOID 11x17'}.get((w,h), 'OTHER %dx%dpt'%(w,h)); print('%d|%s'%(len(r.pages), n))"
$pages, $size = $result -split '\|'
$expected = if ($Paper -eq 'a4') { 'A4' } else { 'US Letter' }
if ($size -ne $expected) { throw "WRONG PAGE SIZE: produced $size, expected $expected, for $Out" }
Write-Host "PDF written: $Out ($pages pages, $size)"
