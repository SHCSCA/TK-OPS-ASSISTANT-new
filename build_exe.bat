@echo off
setlocal
chcp 65001 >nul

cd /d "%~dp0"

set "PY=venv\Scripts\python.exe"
if not exist "%PY%" (
  echo [!] 未找到 venv\Scripts\python.exe，将回退到系统 python
  set "PY=python"
)

if /I "%~1"=="-h" goto :help
if /I "%~1"=="--help" goto :help
if /I "%~1"=="/?" goto :help

set "BAT_ARGS_RAW=%*"
set "PS_FILE=%TEMP%\tkops_build_progress_%RANDOM%%RANDOM%.ps1"

>"%PS_FILE%" (
  echo $ErrorActionPreference = 'Stop'
  echo $py = $env:PY
  echo $repo = Get-Location
  echo $raw = $env:BAT_ARGS_RAW
  echo $logOut = Join-Path $env:TEMP 'tkops_build_runtime.log'
  echo $logErr = Join-Path $env:TEMP 'tkops_build_runtime.err.log'
  echo if ^(Test-Path $logOut^) { Remove-Item $logOut -Force }
  echo if ^(Test-Path $logErr^) { Remove-Item $logErr -Force }
  echo $cmd = "`"$py`" build.py $raw"
  echo Write-Host "[RUN] Python: $py"
  echo Write-Host "[RUN] Command: $cmd"
  echo Write-Host "[INFO] Stdout log: $logOut"
  echo Write-Host "[INFO] Stderr log: $logErr"
  echo $proc = Start-Process -FilePath 'cmd.exe' -ArgumentList "/c $cmd" -WorkingDirectory $repo -RedirectStandardOutput $logOut -RedirectStandardError $logErr -PassThru
  echo $percent = 3
  echo while ^(-not $proc.HasExited^) {
  echo ^    if ^($percent -lt 95^) { $percent = $percent + 1 }
  echo ^    Write-Progress -Activity 'TK-OPS EXE Build' -Status ^("Progress " + $percent + "%%"^) -PercentComplete $percent
  echo ^    Start-Sleep -Milliseconds 350
  echo }
  echo $proc.WaitForExit^(
  echo ^)
  echo $exitCode = [int]$proc.ExitCode
  echo if ^($exitCode -eq 0^) {
  echo ^    Write-Progress -Activity 'TK-OPS EXE Build' -Status 'Progress 100%%' -PercentComplete 100 -Completed
  echo ^    Write-Host "[OK] Build completed: dist\\TK-OPS\\TK-OPS.exe"
  echo ^    if ^(Test-Path $logOut^) {
  echo ^        Write-Host "[INFO] Last build output:"
  echo ^        Get-Content $logOut -Tail 20
  echo ^    }
  echo ^    if ^(Test-Path $logErr^) {
  echo ^        Write-Host "[INFO] Last error output:"
  echo ^        Get-Content $logErr -Tail 20
  echo ^    }
  echo ^    exit 0
  echo }
  echo Write-Progress -Activity 'TK-OPS EXE Build' -Status 'Failed' -PercentComplete 100 -Completed
  echo Write-Host "[ERR] Build failed, exit code: $exitCode"
  echo if ^(Test-Path $logOut^) {
  echo ^    Write-Host "[INFO] Stdout log (last 80 lines):"
  echo ^    Get-Content $logOut -Tail 80
  echo }
  echo if ^(Test-Path $logErr^) {
  echo ^    Write-Host "[INFO] Stderr log (last 80 lines):"
  echo ^    Get-Content $logErr -Tail 80
  echo }
  echo exit $exitCode
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%PS_FILE%"
set "EXIT_CODE=%ERRORLEVEL%"
del "%PS_FILE%" >nul 2>nul
exit /b %EXIT_CODE%

:help
echo.
echo TK-OPS 一键打包脚本 build_exe.bat
echo ====================================
echo 用法:
echo   build_exe.bat [参数]
echo.
echo 参数会透传给 build.py，常用参数:
echo   --clean      构建前清理 build 和 dist
echo   --ico-only   仅生成图标，不打包 EXE
echo   --help       显示帮助
echo.
echo 示例:
echo   build_exe.bat
echo   build_exe.bat --clean
echo   build_exe.bat --ico-only
echo.
echo 输出:
echo   EXE 文件: dist\TK-OPS\TK-OPS.exe
echo   构建日志: %%TEMP%%\tkops_build_runtime.log
echo.
exit /b 0
