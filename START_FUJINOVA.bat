@echo off
setlocal enabledelayedexpansion
title FujiNova Launcher
color 0B

echo =======================================================================
echo          FUJINOVA -- Mount Fuji Travel OS (Windows Launcher)
echo =======================================================================
echo.

cd /d "%~dp0"

:: 1. Check Python installation
echo [*] Checking Python installation...
set "PYTHON_CMD="

:: Check if local virtualenv python already exists
if exist "%~dp0.venv\Scripts\python.exe" (
    set "PYTHON_CMD=%~dp0.venv\Scripts\python.exe"
    echo [OK] Using virtualenv Python: .venv\Scripts\python.exe
) else (
    :: Try py -3.12, py -3, or python
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
                echo Please install Python 3.11, 3.12 or 3.13 from https://www.python.org/
                pause
                exit /b 1
            )
        )
    )

    :: Create virtual environment if missing
    if not exist "%~dp0.venv" (
        echo [*] Creating virtual environment (.venv)...
        !PY_LAUNCHER! -m venv "%~dp0.venv"
        if !errorlevel! neq 0 (
            echo [ERROR] Failed to create virtual environment (.venv).
            pause
            exit /b 1
        )
        echo [OK] Virtual environment (.venv) created.
    )
    set "PYTHON_CMD=%~dp0.venv\Scripts\python.exe"
)

:: 2. Check Node.js and npm
echo [*] Checking Node.js and npm...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH!
    echo Please install Node.js (LTS version) from https://nodejs.org/
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

:: 3. Check / create .env from .env.example
if not exist "%~dp0.env" (
    if exist "%~dp0.env.example" (
        echo [*] Initializing .env from .env.example...
        copy "%~dp0.env.example" "%~dp0.env" >nul
        echo [OK] Created .env (remember to configure your API keys if needed).
    ) else (
        echo [WARNING] Neither .env nor .env.example was found.
    )
) else (
    echo [OK] Environment file (.env) exists.
)

:: 4. Check backend dependencies
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

:: 5. Check frontend dependencies
echo [*] Checking frontend dependencies...
if not exist "%~dp0frontend\node_modules" (
    echo [*] Installing frontend dependencies (npm install)...
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

:: 6. Verify / Initialize Database
echo [*] Checking and initializing database...
"%PYTHON_CMD%" -c "from backend.app.core.database import init_db; from backend.data.seed_places import seed_database; init_db(); seed_database()"
if %errorlevel% neq 0 (
    echo [ERROR] Database initialization failed!
    pause
    exit /b 1
)
echo [OK] SQLite database verified and seeded.

:: 7. Check if ports 8000 and 5173 are already occupied
echo [*] Checking server ports...
netstat -ano | findstr /R /C:":8000 .*LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo [WARNING] Port 8000 is already in use! FujiNova Backend might already be running.
)

netstat -ano | findstr /R /C:":5173 .*LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo [WARNING] Port 5173 is already in use! FujiNova Frontend might already be running.
)

:: 8. Start Backend Service
echo [*] Starting Backend (FastAPI on http://127.0.0.1:8000)...
start "FujiNova_Backend" /min cmd /c ""%PYTHON_CMD%" -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000"

:: 9. Start Frontend Service
echo [*] Starting Frontend (React/Vite on http://localhost:5173)...
cd /d "%~dp0frontend"
start "FujiNova_Frontend" /min cmd /c "npm run dev"
cd /d "%~dp0"

:: 10. Wait for services and perform health check
echo [*] Waiting for services to become healthy...
set /a ATTEMPTS=0
:WAIT_LOOP
set /a ATTEMPTS+=1
timeout /t 2 /nobreak >nul

powershell -Command "try { $res = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/health' -TimeoutSec 2; if ($res.status -eq 'ok') { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
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
