# M6/Phase-2 review - surface played-and-unreviewed decisions (result set, reviewed empty) with the
# 3-way scoring (us vs B1 vs B2). Mirrors src/decisionlog.played_unreviewed.
# Usage:
#   pwsh predictions/review.ps1            # display only (read-only)
#   pwsh predictions/review.ps1 -Mark      # display, then stamp each as reviewed via the Python writer
# -Mark delegates the CSV write to `python -m src.decision_score mark <fixture>` (F7: the free-text
# `reasoning` field is CSV-quoted in Python, never re-quoted by PowerShell).
param([string]$Path = "$PSScriptRoot/decisions.csv", [switch]$Mark)

if (-not (Test-Path $Path)) {
    Write-Host "no decisions.csv yet ($Path) - nothing logged."
    exit 0
}

$rows = Import-Csv $Path | Where-Object { $_.result -and -not $_.reviewed }
if (-not $rows) {
    Write-Host "nothing to review (no played-and-unreviewed matches)."
    exit 0
}

Write-Host "PLAYED & UNREVIEWED ($($rows.Count))  -  points under the corrected rubric (exact=3):"
$rows | Format-Table home, away, @{N='pick';E={$_.pick}}, @{N='modal(B2)';E={$_.modal}},
    @{N='fav(B1)';E={$_.favorite_pick}}, @{N='result';E={$_.result}},
    @{N='us';E={$_.points_actual}}, @{N='B1';E={$_.points_b1}}, @{N='B2';E={$_.points_b2}},
    @{N='brier_model';E={$_.brier_model}} -AutoSize

if ($Mark) {
    $repoRoot = Split-Path $PSScriptRoot -Parent
    Push-Location $repoRoot
    try {
        foreach ($r in $rows) {
            Write-Host "  marking reviewed: $($r.home) vs $($r.away) [$($r.fixture_id)]"
            python -m src.decision_score mark $r.fixture_id
        }
    } finally {
        Pop-Location
    }
    Write-Host "done - re-run without -Mark to confirm nothing remains."
} else {
    Write-Host "(read-only; pass -Mark to stamp these reviewed)"
}
