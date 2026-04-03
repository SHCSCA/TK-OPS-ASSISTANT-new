param(
    [switch]$RuntimeOnly,
    [switch]$DesktopOnly,
    [switch]$BrowserOnly,
    [string]$RuntimeHost = "127.0.0.1",
    [int]$RuntimePort = 8765,
    [string]$RuntimeToken = "dev-token"
)

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
