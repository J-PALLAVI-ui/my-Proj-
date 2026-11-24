# FujiNova 5.0 PowerShell Launcher
$ErrorActionPreference = "Stop"

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "         FUJINOVA 5.0 - Mount Fuji Travel OS            " -ForegroundColor Yellow
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ScriptDir

# 1. Detect Python / Uvicorn executable
$uvicorn = ""
if (Test-Path "$ScriptDir\..\.venv\Scripts\uvicorn.exe") {
    $uvicorn = "$ScriptDir\..\.venv\Scripts\uvicorn.exe"
} elseif (Test-Path "$ScriptDir\.venv\Scripts\uvicorn.exe") {
    $uvicorn = "$ScriptDir\.venv\Scripts\uvicorn.exe"
} else {
    $uvicorn = "uvicorn"
}

# 2. Check .env
if (-not (Test-Path "$ScriptDir\.env")) {
    if (Test-Path "$ScriptDir\.env.example") {
        Write-Host "[*] Initializing .env from template..." -ForegroundColor Gray
        Copy-Item "$ScriptDir\.env.example" "$ScriptDir\.env"
    }
}

Write-Host "[*] Launching Backend (FastAPI on http://127.0.0.1:8000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$ScriptDir'; & '$uvicorn' backend.app.main:app --host 127.0.0.1 --port 8000 --reload"

Write-Host "[*] Launching Frontend (React + Vite on http://localhost:5173)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$ScriptDir\frontend'; npm run dev"

Start-Sleep -Seconds 3

Write-Host "[*] Opening FujiNova 5.0 in browser..." -ForegroundColor Cyan
Start-Process "http://localhost:5173"

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  FujiNova 5.0 is live!" -ForegroundColor Green
Write-Host "  - UI:       http://localhost:5173" -ForegroundColor White
Write-Host "  - API Docs: http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "========================================================" -ForegroundColor Cyan
