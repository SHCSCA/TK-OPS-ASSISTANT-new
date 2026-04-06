param(
    [switch]$RuntimeOnly,
    [switch]$DesktopOnly,
    [switch]$BrowserOnly,
    [string]$RuntimeHost = "127.0.0.1",
    [int]$RuntimePort = 8765,
    [string]$RuntimeToken = "dev-token"
)

function Find-VsDevCmd {
    $candidates = @(
        "F:\VS\BuildTools\Common7\Tools\VsDevCmd.bat",
        "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\VsDevCmd.bat",
        "C:\Program Files\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\VsDevCmd.bat",
        "C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\Tools\VsDevCmd.bat"
    )

    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }

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

    return $null
}

function Import-VsDevEnvironment {
    param(
        [Parameter(Mandatory = $true)]
        [string]$VsDevCmdPath
    )

    $envLines = cmd /c "call `"$VsDevCmdPath`" -arch=x64 -host_arch=x64 >nul && set"
    foreach ($line in $envLines) {
        if ($line -match '^(.*?)=(.*)$') {
            Set-Item -Path ("Env:{0}" -f $matches[1]) -Value $matches[2]
        }
    }
}

function Ensure-DesktopBuildEnv {
    if ($BrowserOnly) {
        return
    }

    if (-not $env:RUSTUP_HOME -and (Test-Path "F:\rust\rustup")) {
        $env:RUSTUP_HOME = "F:\rust\rustup"
    }

    if (-not $env:CARGO_HOME -and (Test-Path "F:\rust\cargo")) {
        $env:CARGO_HOME = "F:\rust\cargo"
    }

    if (-not (gcm cargo -ErrorAction SilentlyContinue)) {
        $cargoCandidates = @(
            "F:\rust\cargo\bin",
            (Join-Path $env:USERPROFILE ".cargo\bin")
        )

        foreach ($candidate in $cargoCandidates) {
            if (Test-Path (Join-Path $candidate "cargo.exe")) {
                if ($env:Path -notlike "*$candidate*") {
                    $env:Path = "$candidate;$env:Path"
                }
                break
            }
        }
    }

    if (-not (gcm cargo -ErrorAction SilentlyContinue)) {
        if ($env:CARGO_HOME) {
            $cargoBin = Join-Path $env:CARGO_HOME "bin"
            if (Test-Path (Join-Path $cargoBin "cargo.exe")) {
                if ($env:Path -notlike "*$cargoBin*") {
                    $env:Path = "$cargoBin;$env:Path"
                }
            }
        }
    }

    if (-not (gcm cargo -ErrorAction SilentlyContinue)) {
        throw "cargo not found. Install Rust and ensure CARGO_HOME\\bin is in PATH."
    }

    if (gcm rustup -ErrorAction SilentlyContinue) {
        $activeToolchain = & rustup show active-toolchain 2>$null
        if (-not $activeToolchain) {
            & rustup default stable | Out-Null
        }
    }

    if (-not (gcm link.exe -ErrorAction SilentlyContinue)) {
        $vsDevCmd = Find-VsDevCmd
        if (-not $vsDevCmd) {
            throw "MSVC build environment not found. Install Visual Studio Build Tools (C++)."
        }
        Write-Host "Loading MSVC toolchain env: $vsDevCmd"
        Import-VsDevEnvironment -VsDevCmdPath $vsDevCmd
    }

    if (-not (gcm link.exe -ErrorAction SilentlyContinue)) {
        throw "MSVC linker (link.exe) is unavailable. Cannot start Tauri desktop host."
    }
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repoRoot "venv\Scripts\python.exe"
$runtimeProcess = $null

if (-not (Test-Path $python)) {
    throw "Python executable not found in venv: $python"
}

if ($RuntimeOnly -and $DesktopOnly) {
    throw "Invalid args: -RuntimeOnly and -DesktopOnly cannot be used together."
}

if ($RuntimeOnly -and $BrowserOnly) {
    throw "Invalid args: -RuntimeOnly and -BrowserOnly cannot be used together."
}

if ($DesktopOnly -and $BrowserOnly) {
    throw "Invalid args: -DesktopOnly and -BrowserOnly cannot be used together."
}

Push-Location $repoRoot
try {
    $runRuntimeOnly = $RuntimeOnly
    $runBrowserOnly = $BrowserOnly

    if ($runRuntimeOnly) {
        Write-Host "Starting runtime only..."
        $env:TKOPS_RUNTIME_HOST = $RuntimeHost
        $env:TKOPS_RUNTIME_PORT = "$RuntimePort"
        $env:TKOPS_RUNTIME_TOKEN = $RuntimeToken
        $env:TKOPS_RUNTIME_MANAGED = "0"
        & $python "apps\py-runtime\src\main.py"
        return
    }

    if ($runBrowserOnly) {
        Write-Host "Starting external runtime for browser dev..."
        $env:TKOPS_RUNTIME_HOST = $RuntimeHost
        $env:TKOPS_RUNTIME_PORT = "$RuntimePort"
        $env:TKOPS_RUNTIME_TOKEN = $RuntimeToken
        $env:TKOPS_RUNTIME_MANAGED = "0"
        $runtimeProcess = Start-Process -FilePath $python -ArgumentList "apps\py-runtime\src\main.py" -WorkingDirectory $repoRoot -PassThru
    }

    Write-Host "Starting desktop host..."
    Ensure-DesktopBuildEnv
    $env:VITE_RUNTIME_URL = "http://${RuntimeHost}:${RuntimePort}"
    $env:VITE_RUNTIME_TOKEN = $RuntimeToken
    $env:TKOPS_RUNTIME_HOST = $RuntimeHost
    $env:TKOPS_RUNTIME_PORT = "$RuntimePort"
    $env:TKOPS_RUNTIME_TOKEN = $RuntimeToken
    $env:TKOPS_RUNTIME_MANAGED = if ($runBrowserOnly) { "0" } else { "1" }

    Push-Location (Join-Path $repoRoot "apps\desktop")
    try {
        if ($runBrowserOnly) {
            Write-Host "Starting browser debug page..."
            npm run dev:web -- --host 127.0.0.1 --port 4173
        }
        else {
            Write-Host "Starting Tauri desktop host..."
            npm run dev:desktop
        }
    }
    finally {
        Pop-Location
    }
}
finally {
    if ($runtimeProcess -and -not $runtimeProcess.HasExited) {
        Stop-Process -Id $runtimeProcess.Id -Force -ErrorAction SilentlyContinue
    }
    Pop-Location
}
