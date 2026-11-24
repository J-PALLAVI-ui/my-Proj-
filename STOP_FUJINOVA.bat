@echo off
title Stop FujiNova
color 0C

echo =======================================================================
echo                 Stopping FujiNova Services...
echo =======================================================================
echo.

cd /d "%~dp0"

echo [*] Finding and terminating processes listening on ports 8000 and 5173...

:: Find and terminate process on port 8000 (Backend)
powershell -Command "$pids = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique; foreach ($p in $pids) { if ($p) { Stop-Process -Id $p -Force -ErrorAction SilentlyContinue; Write-Host \"[OK] Terminated backend process on port 8000 (PID $p)\" } }"

:: Find and terminate process on port 5173 (Frontend Vite)
powershell -Command "$pids = Get-NetTCPConnection -LocalPort 5173 -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique; foreach ($p in $pids) { if ($p) { Stop-Process -Id $p -Force -ErrorAction SilentlyContinue; Write-Host \"[OK] Terminated frontend process on port 5173 (PID $p)\" } }"

echo.
echo =======================================================================
echo   FujiNova services have been stopped.
echo =======================================================================
echo.
