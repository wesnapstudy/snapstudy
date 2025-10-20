@echo off
echo Testing frontend build...
cd frontend
echo Current directory: %CD%
echo.
echo Checking if App.tsx exists:
if exist "src\App.tsx" (
    echo ✓ App.tsx found
) else (
    echo ✗ App.tsx not found
)
echo.
echo Checking if tsconfig.json exists:
if exist "tsconfig.json" (
    echo ✓ tsconfig.json found
) else (
    echo ✗ tsconfig.json not found
)
echo.
echo Running npm run build...
npm run build
echo.
echo Build completed with exit code: %ERRORLEVEL%
pause