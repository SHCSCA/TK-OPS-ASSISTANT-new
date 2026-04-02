param(
    [switch]$SkipBuild,
    [int]$WaitSeconds = 8,
    [string]$ExecutablePath
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$tauriRoot = Join-Path $repoRoot "apps\desktop\src-tauri"
$defaultExePath = Join-Path $tauriRoot "target\debug\tk_ops_desktop.exe"
$exePath = if ($ExecutablePath) { $ExecutablePath } else { $defaultExePath }
$runtimeLog = Join-Path $env:APPDATA "TK-OPS-ASSISTANT\logs\runtime.log"
$vsDevCmd = "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\VsDevCmd.bat"
$cargo = Join-Path $env:USERPROFILE ".cargo\bin\cargo.exe"

if (-not (Test-Path $vsDevCmd)) {
    throw "VsDevCmd.bat not found: $vsDevCmd"
}

if (-not (Test-Path $cargo)) {
    throw "cargo.exe not found: $cargo"
}

function Get-RuntimeProcesses {
    Get-CimInstance Win32_Process |
        Where-Object {
            $_.Name -like "python*.exe" -and
            $_.CommandLine -like "*main.py*" -and
            (
                $_.CommandLine -like "*py-runtime*" -or
                $_.CommandLine -like "*\\runtime\\src\\*" -or
                $_.CommandLine -like "*/runtime/src/*"
            )
        } |
        Select-Object ProcessId, Name, CommandLine
}

if (-not $SkipBuild) {
    Push-Location $tauriRoot
    try {
        cmd /c "call `"$vsDevCmd`" -arch=x64 -host_arch=x64 >nul && `"$cargo`" build"
        if ($LASTEXITCODE -ne 0) {
            throw "cargo build failed with exit code $LASTEXITCODE"
        }
    }
    finally {
        Pop-Location
    }
}

if (-not (Test-Path $exePath)) {
    throw "Host executable not found: $exePath"
}

$beforeLogWrite = $null
if (Test-Path $runtimeLog) {
    $beforeLogWrite = (Get-Item $runtimeLog).LastWriteTimeUtc
}

$beforeRuntimeIds = @(Get-RuntimeProcesses | Select-Object -ExpandProperty ProcessId)
$hostProcess = $null
$newRuntimeProcesses = @()

try {
    $hostProcess = Start-Process -FilePath $exePath -WorkingDirectory (Split-Path $exePath) -PassThru
    Start-Sleep -Seconds $WaitSeconds

    $afterRuntimeProcesses = @(Get-RuntimeProcesses)
    $newRuntimeProcesses = @(
        $afterRuntimeProcesses | Where-Object { $_.ProcessId -notin $beforeRuntimeIds }
    )

    $hostAlive = $false
    try {
        $hostAlive = -not $hostProcess.HasExited
    }
    catch {
        $hostAlive = $false
    }

    $logUpdated = $false
    if (Test-Path $runtimeLog) {
        $afterLogWrite = (Get-Item $runtimeLog).LastWriteTimeUtc
        $logUpdated = $beforeLogWrite -eq $null -or $afterLogWrite -gt $beforeLogWrite
    }

    Write-Host ("HOST_ALIVE={0}" -f $hostAlive)
    Write-Host ("NEW_RUNTIME_COUNT={0}" -f @($newRuntimeProcesses).Count)
    Write-Host ("RUNTIME_LOG_UPDATED={0}" -f $logUpdated)

    if (-not $hostAlive) {
        throw "Host process did not stay alive."
    }

    if ((@($newRuntimeProcesses).Count -eq 0) -and (-not $logUpdated)) {
        throw "No new managed runtime evidence was observed."
    }

    Write-Host "Tauri managed runtime smoke passed."
}
finally {
    if ($hostProcess -and -not $hostProcess.HasExited) {
        Stop-Process -Id $hostProcess.Id -Force -ErrorAction SilentlyContinue
    }

    $newRuntimeProcesses | ForEach-Object {
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }
}
