param(
    [switch]$SkipSmoke
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$desktopRoot = Join-Path $repoRoot "apps\desktop"
$tauriRoot = Join-Path $desktopRoot "src-tauri"
$alphaRoot = Join-Path $repoRoot "dist-alpha"
$stageRoot = Join-Path $alphaRoot "TK-OPS-Alpha"
$frontendDist = Join-Path $desktopRoot "dist\\index.html"
$hostSource = Join-Path $tauriRoot "target\release\tk_ops_desktop.exe"
$hostTarget = Join-Path $stageRoot "TK-OPS.exe"
$vsDevCmd = "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\VsDevCmd.bat"
$cargo = Join-Path $env:USERPROFILE ".cargo\bin\cargo.exe"

if (-not (Test-Path $vsDevCmd)) {
    throw "VsDevCmd.bat not found: $vsDevCmd"
}

if (-not (Test-Path $cargo)) {
    throw "cargo.exe not found: $cargo"
}

if (-not (Test-Path $frontendDist)) {
    Push-Location $desktopRoot
    try {
        npm run build
        if ($LASTEXITCODE -ne 0) {
            throw "npm run build failed with exit code $LASTEXITCODE"
        }
    }
    finally {
        Pop-Location
    }
}
else {
    Write-Host "FRONTEND_BUILD=skip_existing_dist"
}

if (-not (Test-Path $hostSource)) {
    Push-Location $tauriRoot
    try {
        cmd /c "call `"$vsDevCmd`" -arch=x64 -host_arch=x64 >nul && `"$cargo`" build --release"
        if ($LASTEXITCODE -ne 0) {
            throw "cargo build --release failed with exit code $LASTEXITCODE"
        }
    }
    finally {
        Pop-Location
    }
}
else {
    Write-Host "HOST_BUILD=skip_existing_release_exe"
}

if (Test-Path $stageRoot) {
    Remove-Item -LiteralPath $stageRoot -Recurse -Force
}

New-Item -ItemType Directory -Force $stageRoot | Out-Null
New-Item -ItemType Directory -Force (Join-Path $stageRoot "runtime\src") | Out-Null

Copy-Item -LiteralPath $hostSource -Destination $hostTarget -Force
Copy-Item -Path (Join-Path $repoRoot "apps\py-runtime\src\*") -Destination (Join-Path $stageRoot "runtime\src") -Recurse -Force
Copy-Item -LiteralPath (Join-Path $repoRoot "desktop_app") -Destination (Join-Path $stageRoot "desktop_app") -Recurse -Force
Copy-Item -LiteralPath (Join-Path $repoRoot "VERSION") -Destination (Join-Path $stageRoot "VERSION") -Force

$alphaReadme = @(
    "TK-OPS Alpha package",
    "",
    "1. Host entry: TK-OPS.exe",
    "2. Runtime entry: runtime\\src\\main.py",
    "3. This payload only keeps the new desktop host and Python runtime chain.",
    "4. desktop_app is copied only for runtime dependency reuse and migration reference."
) -join [Environment]::NewLine
$alphaReadme | Set-Content -Path (Join-Path $stageRoot "README-alpha.txt") -Encoding UTF8

if (-not $SkipSmoke) {
    & (Join-Path $repoRoot "scripts\smoke-tauri-runtime.ps1") -SkipBuild -ExecutablePath $hostTarget
}

Write-Host ("ALPHA_STAGE={0}" -f $stageRoot)
