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

if (-not (Test-Path $python)) {
    throw "未找到虚拟环境 Python：$python"
}

Push-Location $repoRoot
try {
    if (-not $DesktopOnly) {
        Write-Host "启动 Python runtime..."
        $env:TKOPS_RUNTIME_HOST = $RuntimeHost
        $env:TKOPS_RUNTIME_PORT = "$RuntimePort"
        $env:TKOPS_RUNTIME_TOKEN = $RuntimeToken
        $env:TKOPS_RUNTIME_MANAGED = "0"
        Start-Process -FilePath $python -ArgumentList "apps\py-runtime\src\main.py" -WorkingDirectory $repoRoot
    }

    if (-not $RuntimeOnly) {
        Write-Host "启动桌面前端开发服务器..."
        $env:VITE_RUNTIME_URL = "http://${RuntimeHost}:${RuntimePort}"
        $env:VITE_RUNTIME_TOKEN = $RuntimeToken
        Push-Location (Join-Path $repoRoot "apps\desktop")
        try {
            if ($BrowserOnly) {
                Write-Host "鍚姩娴忚鍣ㄨ皟璇曢〉..."
                npm run dev:web -- --host 127.0.0.1 --port 4173
            }
            else {
                Write-Host "鍚姩 Tauri 妗岄潰瀹夸富..."
                npm run dev:desktop
            }
        }
        finally {
            Pop-Location
        }
    }
}
finally {
    Pop-Location
}
