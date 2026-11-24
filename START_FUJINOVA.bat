@echo off
setlocal enabledelayedexpansion
title FujiNova Launcher
color 0B

echo =======================================================================
echo          FUJINOVA -- Mount Fuji Travel OS (Windows Launcher)
echo =======================================================================
echo.

cd /d "%~dp0"

:: 1. Clear any lingering processes on ports 8000 and 5173
echo [*] Ensuring ports 8000 and 5173 are free...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr /R ":8000.*LISTENING"') do (
    echo [*] Clearing previous process on port 8000: PID %%a
    taskkill /F /T /PID %%a >nul 2>&1
)
for /f "tokens=4,5" %%a in ('netstat -ano ^| findstr /R ":5173.*LISTENING"') do (
    taskkill /F /T /PID %%a >nul 2>&1
    taskkill /F /T /PID %%b >nul 2>&1
)
taskkill /F /FI "WINDOWTITLE eq FujiNova_Backend*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq FujiNova_Frontend*" >nul 2>&1

:: 2. Check Python installation
echo [*] Checking Python installation...
set "PYTHON_CMD="

if exist "%~dp0.venv\Scripts\python.exe" (
    set "PYTHON_CMD=%~dp0.venv\Scripts\python.exe"
    echo [OK] Using virtualenv Python: .venv\Scripts\python.exe
) else (
    py -3.12 --version >nul 2>&1
    if !errorlevel! equ 0 (
        set "PY_LAUNCHER=py -3.12"
    ) else (
        py -3 --version >nul 2>&1
        if !errorlevel! equ 0 (
            set "PY_LAUNCHER=py -3"
        ) else (
            python --version >nul 2>&1
            if !errorlevel! equ 0 (
                set "PY_LAUNCHER=python"
            ) else (
                echo [ERROR] Python is not installed or not in PATH!
                echo Please install Python 3.11 or 3.12 from python.org
                pause
                exit /b 1
            )
        )
    )

    if not exist "%~dp0.venv" (
        echo [*] Creating virtual environment...
        !PY_LAUNCHER! -m venv "%~dp0.venv"
        if !errorlevel! neq 0 (
            echo [ERROR] Failed to create virtual environment.
            pause
            exit /b 1
        )
        echo [OK] Virtual environment created.
    )
    set "PYTHON_CMD=%~dp0.venv\Scripts\python.exe"
)

:: 3. Check Node.js and npm
echo [*] Checking Node.js and npm...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH!
    echo Please install Node.js LTS version from https://nodejs.org/
    pause
    exit /b 1
)

npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] npm is not installed or not in PATH!
    pause
    exit /b 1
)
echo [OK] Node.js and npm detected.

:: 4. Check / create .env
if not exist "%~dp0.env" (
    if exist "%~dp0.env.example" (
        echo [*] Initializing .env from .env.example...
        copy "%~dp0.env.example" "%~dp0.env" >nul
        echo [OK] Created .env file.
    )
) else (
    echo [OK] Environment file .env exists.
)

:: 5. Check backend dependencies
echo [*] Checking backend dependencies...
"%PYTHON_CMD%" -c "import fastapi, uvicorn, pydantic, langgraph" >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] Installing backend dependencies from backend\requirements.txt...
    "%PYTHON_CMD%" -m pip install -r "%~dp0backend\requirements.txt"
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to install backend dependencies!
        pause
        exit /b 1
    )
    echo [OK] Backend dependencies installed.
) else (
    echo [OK] Backend dependencies verified.
)

:: 6. Check frontend dependencies
echo [*] Checking frontend dependencies...
if not exist "%~dp0frontend\node_modules" (
    echo [*] Installing frontend dependencies via npm install...
    cd /d "%~dp0frontend"
    call npm install
    cd /d "%~dp0"
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to install frontend dependencies!
        pause
        exit /b 1
    )
    echo [OK] Frontend dependencies installed.
) else (
    echo [OK] Frontend dependencies verified.
)

:: 7. Verify / Initialize Database
echo [*] Checking and initializing database...
"%PYTHON_CMD%" -c "from backend.app.core.database import init_db; from backend.data.seed_places import seed_database; init_db(); seed_database()"
if %errorlevel% neq 0 (
    echo [ERROR] Database initialization failed!
    pause
    exit /b 1
)
echo [OK] SQLite database verified and seeded.

:: 8. Start Backend Service
echo [*] Starting Backend (FastAPI on http://127.0.0.1:8000)...
start "FujiNova_Backend" /min cmd /c ""%PYTHON_CMD%" -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000"

:: 9. Start Frontend Service
echo [*] Starting Frontend (React/Vite on http://localhost:5173)...
cd /d "%~dp0frontend"
start "FujiNova_Frontend" /min cmd /c "npm run dev"
cd /d "%~dp0"

:: 10. Wait for services and perform health check using Python
echo [*] Waiting for services to become healthy...
set /a ATTEMPTS=0
:WAIT_LOOP
set /a ATTEMPTS+=1
ping -n 3 127.0.0.1 >nul

"%PYTHON_CMD%" -c "import urllib.request; res = urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health', timeout=2); exit(0 if res.status == 200 else 1)" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Backend is healthy at http://127.0.0.1:8000/api/v1/health
    goto BACKEND_READY
)

if !ATTEMPTS! geq 15 (
    echo [WARNING] Backend health probe timed out. Please check the FujiNova_Backend window for details.
    goto BACKEND_READY
)
goto WAIT_LOOP

:BACKEND_READY
echo.
echo =======================================================================
echo   FujiNova is up and running!
echo   -------------------------------------------------------------------
echo   - Web App:      http://localhost:5173
echo   - API Health:   http://127.0.0.1:8000/api/v1/health
echo   - API Swagger:  http://127.0.0.1:8000/docs
echo =======================================================================
echo.
echo [*] Opening FujiNova in your default web browser...
start http://localhost:5173

echo.
echo Leave this window open or minimize it.
echo To safely stop FujiNova, double-click STOP_FUJINOVA.bat.
echo.
pause
