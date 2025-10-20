@echo off
REM SnapStudy - Windows Deployment Script
REM This is a wrapper that calls the PowerShell deployment script

echo.
echo ============================================================
echo   SnapStudy AWS Deployment Script (Windows)
echo ============================================================
echo.

REM Check if PowerShell is available
where powershell >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: PowerShell not found
    echo Please install PowerShell to run this script
    pause
    exit /b 1
)

REM Run PowerShell deployment script
powershell -ExecutionPolicy Bypass -File "%~dp0deploy.ps1"

pause
