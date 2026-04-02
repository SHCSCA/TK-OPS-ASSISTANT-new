param(
    [switch]$TypecheckOnly,
    [switch]$SmokeRuntime
)

$repoRoot = Split-Path -Parent $PSScriptRoot

Push-Location (Join-Path $repoRoot "apps\desktop")
try {
    if ($TypecheckOnly) {
        npm run typecheck
    }
    else {
        npm run build
    }
}
finally {
    Pop-Location
}

if ($SmokeRuntime -and -not $TypecheckOnly) {
    & (Join-Path $repoRoot "scripts\smoke-tauri-runtime.ps1") -SkipBuild
}
