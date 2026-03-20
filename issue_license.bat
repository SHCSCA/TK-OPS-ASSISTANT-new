@echo off
setlocal
chcp 65001 >nul
set "INTERACTIVE=0"

cd /d "%~dp0"
set "PY=venv\Scripts\python.exe"
if not exist "%PY%" (
  echo [!] 未找到 venv\Scripts\python.exe，将回退到系统 python
  set "PY=python"
)

if /I "%~1"=="-h" goto :help
if /I "%~1"=="--help" goto :help
if /I "%~1"=="/?" goto :help

if "%~1"=="" goto :interactive
if /I "%~1"=="self" (
  echo [RUN] 输出本机机器码信息...
  "%PY%" tools\issue_license.py --self
  goto :end
)

echo [RUN] 执行签发命令: tools\issue_license.py %*
"%PY%" tools\issue_license.py %*
if "%ERRORLEVEL%"=="0" echo [OK] 命令执行成功
goto :end

:interactive
set "INTERACTIVE=1"
echo TK-OPS 许可证签发工具
echo.
echo 支持的 machine_id 格式:
echo   1^) 复合机器码 ^(推荐^): cpu16:board16:disk16:mac16
echo   2^) 完整机器码: 64 位十六进制
echo   3^) 短机器码: XXXX-XXXX-XXXX-XXXX ^(仅本机匹配场景^)
echo.
set /p MID=请输入 machine_id: 
if "%MID%"=="" (
  echo [!] machine_id 不能为空
  goto :end
)
set /p DAYS=请输入有效天数 ^(0=永久^) [0]: 
if "%DAYS%"=="" set "DAYS=0"
set /p TIER=请输入授权等级 ^(free/pro/enterprise^) [pro]: 
if "%TIER%"=="" set "TIER=pro"

echo.
echo [RUN] 正在签发许可证...
"%PY%" tools\issue_license.py "%MID%" --days %DAYS% --tier %TIER%
if "%ERRORLEVEL%"=="0" echo [OK] 签发成功

:end
if "%INTERACTIVE%"=="1" (
  echo.
  pause
)
exit /b %ERRORLEVEL%

:help
echo.
echo TK-OPS 许可证签发脚本 issue_license.bat
echo ========================================
echo 用法:
echo   issue_license.bat
echo   issue_license.bat self
echo   issue_license.bat machine_id [--days N] [--tier T]
echo   issue_license.bat machine_id --verify license_key
echo.
echo 参数说明:
echo   machine_id   机器码 ^(复合/64位完整/短码^)
echo   --days N     有效天数，0 表示永久
echo   --tier T     授权等级: free / pro / enterprise
echo   --verify     按 machine_id 校验许可证是否有效
echo.
echo 示例:
echo   issue_license.bat self
echo   issue_license.bat 829D-598A-6587-A85A --days 365 --tier enterprise
echo   issue_license.bat e797d9f475dcb607:1e58a774e4e64f1c:e6f43d01e54f91eb:3cf5e8a99e6311fc --days 0 --tier pro
echo   issue_license.bat 829d598a6587a85af34840fb263396fde56120f86293f5bedf93490c582aae22 --verify license_key
echo.
exit /b 0
