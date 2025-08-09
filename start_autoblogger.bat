@echo off
setlocal
cd /d "%~dp0"

set "PS_EXE=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
if exist "%PS_EXE%" (
  start "Premium Auto Blogger" "%PS_EXE%" -NoProfile -NoLogo -ExecutionPolicy Bypass -NoExit -File "%~dp0start.ps1"
  goto :EOF
)

set FLASK_ENV=development
set PYTHONIOENCODING=utf-8
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" premium_auto_blogger_web.py
) else (
  python premium_auto_blogger_web.py
)

pause


