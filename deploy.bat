@echo off
echo SnapStudy Deployment Launcher
echo ============================
echo.

REM Check if PowerShell is available
powershell -Command "Write-Host 'PowerShell is available'" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: PowerShell is not available or not in PATH
    echo Please install PowerShell and try again
    pause
    exit /b 1
)

echo Select deployment option:
echo 1. Deploy everything (Backend + Frontend)
echo 2. Deploy backend only
echo 3. Deploy frontend only
echo 4. Exit
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo Deploying complete SnapStudy platform...
    powershell -ExecutionPolicy Bypass -File "%~dp0deploy-snapstudy.ps1"
) else if "%choice%"=="2" (
    echo Deploying backend only...
    powershell -ExecutionPolicy Bypass -File "%~dp0deploy-snapstudy.ps1" -BackendOnly
) else if "%choice%"=="3" (
    echo Deploying frontend only...
    powershell -ExecutionPolicy Bypass -File "%~dp0deploy-snapstudy.ps1" -FrontendOnly
) else if "%choice%"=="4" (
    echo Exiting...
    exit /b 0
) else (
    echo Invalid choice. Please try again.
    pause
    goto :eof
)

echo.
echo Deployment completed. Check the output above for results.
pause