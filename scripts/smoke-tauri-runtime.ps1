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

function Find-VsDevCmd {
    # Use vswhere to detect Visual Studio installation (most reliable)
    $vswhere = "C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe"
    if (Test-Path $vswhere) {
        $installationPath = & $vswhere -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -latest -property installationPath 2>$null
        if ($installationPath) {
            $detected = Join-Path $installationPath "Common7\Tools\VsDevCmd.bat"
            if (Test-Path $detected) {
                return $detected
            }
        }
    }

    # Fallback candidates (in order of likelihood)
    $candidates = @(
        "C:\Program Files\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\VsDevCmd.bat",
        "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\VsDevCmd.bat",
        "C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\Tools\VsDevCmd.bat",
        "C:\Program Files\Microsoft Visual Studio\2019\BuildTools\Common7\Tools\VsDevCmd.bat"
    )

    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }

    return $null
}

function Find-CargoExe {
    $candidates = @()

    # Respect CARGO_HOME environment variable if set
    if ($env:CARGO_HOME) {
        $candidates += (Join-Path $env:CARGO_HOME "bin\cargo.exe")
    }

    # Standard user-level Rust installation
    $candidates += (Join-Path $env:USERPROFILE ".cargo\bin\cargo.exe")

    # System-level Rust installation (common locations)
    $candidates += "C:\Program Files\Rust\.cargo\bin\cargo.exe"
    $candidates += "C:\Rust\.cargo\bin\cargo.exe"

    foreach ($candidate in $candidates) {
        if ($candidate -and (Test-Path $candidate)) {
            return $candidate
        }
    }

    return $null
}

$vsDevCmd = Find-VsDevCmd
$cargo = Find-CargoExe

if (-not $vsDevCmd) {
    throw "VsDevCmd.bat not found in known locations."
}

if (-not $cargo) {
    throw "cargo.exe not found in CARGO_HOME/known locations."
}

function Get-RuntimeProcesses {
    # Default runtime port to help identify the correct process
    $defaultPort = "8765"

    Get-CimInstance Win32_Process |
        Where-Object {
            $_.Name -like "python*.exe" -and
            $_.CommandLine -like "*main.py*"
        } |
        Where-Object {
            $cmd = $_.CommandLine
            # Match by path patterns (case-insensitive via -clike would need -like with wildcards)
            $cmdLower = $cmd.ToLower()
            (
                $cmdLower -like "*py-runtime*" -or
                $cmdLower -like "*\runtime\src\*" -or
                $cmdLower -like "*/runtime/src/*" -or
                $cmd -like "*:$defaultPort*" -or
                $cmd -like "*localhost:$defaultPort*"
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
