param(
    [switch]$Quick,
    [switch]$Full,
    [switch]$SkipSmoke,
    [switch]$IncludeReleasePack
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repoRoot "venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    $python = "python"
}

if ($Quick -and $Full) {
    throw "Invalid arguments: -Quick and -Full cannot be used together."
}

$mode = if ($Full) { "Full" } else { "Quick" }
$results = New-Object System.Collections.Generic.List[object]

function Invoke-GateStep {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][scriptblock]$Action
    )

    $startedAt = Get-Date
    Write-Host ("[GATE] START  {0}  ({1:HH:mm:ss})" -f $Name, $startedAt)

    $ok = $true
    $errorText = ""
    try {
        & $Action
        if ($LASTEXITCODE -ne $null -and $LASTEXITCODE -ne 0) {
            throw "Step returned non-zero exit code: $LASTEXITCODE"
        }
    }
    catch {
        $ok = $false
        $errorText = $_.Exception.Message
    }

    $endedAt = Get-Date
    $duration = [math]::Round(($endedAt - $startedAt).TotalSeconds, 1)
    $status = if ($ok) { "PASS" } else { "FAIL" }
    Write-Host ("[GATE] END    {0}  => {1} ({2}s)" -f $Name, $status, $duration)
    if (-not $ok -and $errorText) {
        Write-Host ("[GATE] ERROR  {0}" -f $errorText)
    }

    $results.Add(
        [pscustomobject]@{
            Name = $Name
            Status = $status
            DurationSec = $duration
            Error = $errorText
        }
    ) | Out-Null

    if (-not $ok) {
        throw "Gate step failed: $Name"
    }
}

Write-Host ("[GATE] MODE={0}" -f $mode)
Write-Host ("[GATE] REPO={0}" -f $repoRoot)

Push-Location $repoRoot
try {
    if ($mode -eq "Quick") {
        Invoke-GateStep -Name "Runtime + Accounts regression" -Action {
            & $python -m pytest tests/test_runtime_api.py tests/test_runtime_ws_auth_contract.py tests/test_accounts_vertical_slice.py -v
        }

        Invoke-GateStep -Name "Python compile check" -Action {
            & $python -m compileall apps/py-runtime/src desktop_app
        }

        Invoke-GateStep -Name "Frontend typecheck" -Action {
            Push-Location (Join-Path $repoRoot "apps\desktop")
            try {
                npm run typecheck
            }
            finally {
                Pop-Location
            }
        }
    }
    else {
        Invoke-GateStep -Name "Full pytest" -Action {
            & $python -m pytest tests -q
        }

        Invoke-GateStep -Name "Python compile check" -Action {
            & $python -m compileall apps/py-runtime/src desktop_app
        }

        Invoke-GateStep -Name "Frontend typecheck" -Action {
            Push-Location (Join-Path $repoRoot "apps\desktop")
            try {
                npm run typecheck
            }
            finally {
                Pop-Location
            }
        }

        Invoke-GateStep -Name "Frontend build" -Action {
            Push-Location (Join-Path $repoRoot "apps\desktop")
            try {
                npm run build
            }
            finally {
                Pop-Location
            }
        }

        if (-not $SkipSmoke) {
            Invoke-GateStep -Name "Tauri managed runtime smoke" -Action {
                & (Join-Path $repoRoot "scripts\smoke-tauri-runtime.ps1") -SkipBuild
            }
        }

        Invoke-GateStep -Name "Release chain contract tests" -Action {
            & $python -m pytest tests/test_release_chain_single_shell.py -v
        }

        if ($IncludeReleasePack) {
            Invoke-GateStep -Name "Alpha package build (no smoke)" -Action {
                & (Join-Path $repoRoot "scripts\release.ps1") -SkipSmoke -SkipPreflight
            }
        }
    }

    Write-Host ""
    Write-Host "[GATE] Summary"
    $results | Format-Table -AutoSize | Out-String | Write-Host

    $failed = @($results | Where-Object { $_.Status -eq "FAIL" })
    if ($failed.Count -gt 0) {
        Write-Host ("[GATE] RESULT=FAIL, FAILED_STEPS={0}" -f $failed.Count)
        exit 1
    }

    Write-Host "[GATE] RESULT=PASS"
    exit 0
}
finally {
    Pop-Location
}
