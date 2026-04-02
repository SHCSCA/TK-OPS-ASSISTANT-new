$repoRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repoRoot "venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    throw "未找到虚拟环境 Python：$python"
}

Push-Location $repoRoot
try {
    & $python -m compileall apps\py-runtime\src
}
finally {
    Pop-Location
}
