@echo off
title FujiNova - Stop Services
color 0C

echo =======================================================================
echo                 FUJINOVA -- Stopping All Services
echo =======================================================================
echo.

cd /d "%~dp0"

echo [*] Finding and terminating processes on port 8000 (Backend)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr /R ":8000.*LISTENING"') do (
    echo [*] Terminating process tree for port 8000: PID %%a
    taskkill /F /T /PID %%a >nul 2>&1
)

echo [*] Finding and terminating processes on port 5173 (Frontend)...
for /f "tokens=4,5" %%a in ('netstat -ano ^| findstr /R ":5173.*LISTENING"') do (
    taskkill /F /T /PID %%a >nul 2>&1
    taskkill /F /T /PID %%b >nul 2>&1
)

:: Terminate any named windows
taskkill /F /FI "WINDOWTITLE eq FujiNova_Backend*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq FujiNova_Frontend*" >nul 2>&1

:: Pause 1 second using ping
ping -n 2 127.0.0.1 >nul

:: Verification
netstat -ano | findstr /R ":8000.*LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr /R ":8000.*LISTENING"') do taskkill /F /T /PID %%a >nul 2>&1
)
netstat -ano | findstr /R ":5173.*LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=4,5" %%a in ('netstat -ano ^| findstr /R ":5173.*LISTENING"') do taskkill /F /T /PID %%a >nul 2>&1
)

echo.
echo =======================================================================
echo   All FujiNova services have been stopped successfully!
echo =======================================================================
echo.
ping -n 3 127.0.0.1 >nul
exit /b 0
