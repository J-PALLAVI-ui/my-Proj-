@echo off
setlocal enabledelayedexpansion
title FujiNova - Configure Gemini API Key
color 0A

echo =======================================================================
echo              FUJINOVA -- Quick Gemini API Key Setup
echo =======================================================================
echo.
echo This tool lets you configure your Google Gemini API key easily.
echo If you don't have a key yet, get a free one from:
echo https://aistudio.google.com/app/apikey
echo.
echo -----------------------------------------------------------------------

set /p "USER_KEY=Paste your Gemini API key here (AIza...): "

if "%USER_KEY%"=="" (
    echo.
    echo [ERROR] No API key entered!
    pause
    exit /b 1
)

cd /d "%~dp0"

:: Check if .env exists, if not copy from .env.example
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
    ) else (
        echo [ERROR] Neither .env nor .env.example exists!
        pause
        exit /b 1
    )
)

:: Run PowerShell script to safely update or insert GEMINI_API_KEY and FUJINOVA_PRIMARY_PROVIDER in .env
powershell -Command ^
    "$key = '%USER_KEY%'.Trim();" ^
    "$envFile = Join-Path $pwd '.env';" ^
    "$content = Get-Content $envFile;" ^
    "$hasKey = $false;" ^
    "$hasProvider = $false;" ^
    "$newLines = @();" ^
    "foreach ($line in $content) {" ^
    "    if ($line -match '^\s*GEMINI_API_KEY=') {" ^
    "        $newLines += 'GEMINI_API_KEY=' + $key;" ^
    "        $hasKey = $true;" ^
    "    } elseif ($line -match '^\s*FUJINOVA_PRIMARY_PROVIDER=') {" ^
    "        $newLines += 'FUJINOVA_PRIMARY_PROVIDER=google';" ^
    "        $hasProvider = $true;" ^
    "    } else {" ^
    "        $newLines += $line;" ^
    "    }" ^
    "};" ^
    "if (-not $hasKey) { $newLines += 'GEMINI_API_KEY=' + $key };" ^
    "if (-not $hasProvider) { $newLines += 'FUJINOVA_PRIMARY_PROVIDER=google' };" ^
    "Set-Content -Path $envFile -Value $newLines -Encoding utf8;"

echo.
echo =======================================================================
echo [SUCCESS] Your Gemini API key has been saved to .env!
echo Provider set to: google
echo Model set to: gemini-2.0-flash / gemini-3.8-flash
echo =======================================================================
echo.
echo To apply changes:
echo 1. If FujiNova is currently running, run STOP_FUJINOVA.bat
echo 2. Run START_FUJINOVA.bat to launch with your Gemini API key!
echo.
pause
