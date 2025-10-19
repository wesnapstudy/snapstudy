@echo off
echo ========================================
echo   SnapStudy Frontend Setup
echo ========================================
echo.

cd frontend

echo Installing frontend dependencies...
call npm install

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install dependencies
    echo Please make sure Node.js and npm are installed
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo To start the application:
echo   1. Start the backend: cd backend && python start_server.py
echo   2. Start the frontend: cd frontend && npm start
echo.
echo Or use the start scripts:
echo   - Backend: backend\start_server.py
echo   - Frontend: frontend\start.bat
echo.
echo Frontend will be available at: http://localhost:3000
echo Backend API docs at: http://localhost:8000/docs
echo.
pause