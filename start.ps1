<#
  Windows PowerShell one-click starter for Premium YouTube AI Auto Blogger
  - Kills existing python servers
  - Ensures venv exists and dependencies are installed
  - Starts Flask app and opens browser
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

function Initialize-Venv {
  if (-not (Test-Path ".venv/Scripts/python.exe")) {
    Write-Host "[+] Creating virtual environment..." -ForegroundColor Cyan
    py -3 -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -U pip
    if (Test-Path "requirements.txt") {
      .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    }
  }
}

function Start-App {
  Write-Host "[+] Stopping old python processes (if any)..." -ForegroundColor Yellow
  try {
    # 백그라운드 좀비 프로세스만 선별 종료 (현재 세션 보호)
    Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -eq 0 } | ForEach-Object { $_.Kill() } | Out-Null
  } catch { }

  Write-Host "[+] Activating venv..." -ForegroundColor Cyan
  if (Test-Path ".venv/Scripts/Activate.ps1") {
    & .\.venv\Scripts\Activate.ps1
  }

  Write-Host "[+] Starting Flask app (foreground, live logs below)..." -ForegroundColor Green
  $env:FLASK_ENV = 'development'
  $env:PYTHONIOENCODING = 'utf-8'

  # 브라우저는 백그라운드로 지연 실행
  try { Start-Job -ScriptBlock { Start-Sleep -Seconds 3; Start-Process "http://localhost:5000" } | Out-Null } catch {}

  # 서버를 포그라운드로 실행하여 창이 유지되고 로그가 바로 표시되도록 처리
  # 표준출력/표준에러를 통합해 화면에 표시하면서 파일로도 저장
  $python = Join-Path $root ".venv\Scripts\python.exe"
  if (-not (Test-Path $python)) {
    $pyCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pyCmd) { $python = $pyCmd.Source } else { $python = "python" }
  }
  # 파이썬 경고(stderr)로 인한 PowerShell NativeCommandError가 종료를 유발하지 않도록 임시로 완화
  $prevErrPref = $ErrorActionPreference
  $ErrorActionPreference = 'Continue'
  try {
    & $python "premium_auto_blogger_web.py" 2>&1 | Tee-Object -FilePath (Join-Path $root "server.out.log")
  } finally {
    $ErrorActionPreference = $prevErrPref
  }
}

try {
  Initialize-Venv
  Start-App
} catch {
  Write-Host "[!] Failed to start. See server.err.log for details." -ForegroundColor Red
}

# 창이 자동으로 닫히지 않도록 유지 (배경 대기 루프)
while ($true) {
  Start-Sleep -Seconds 3600
}



