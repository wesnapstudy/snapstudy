@echo off
echo SnapStudy AI Services Setup and Test
echo =====================================

echo.
echo Step 1: Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Step 2: Installing additional dependencies...
pip install uvicorn[standard]

echo.
echo Step 3: Running AI services test...
python test_ai_services.py

echo.
echo Setup complete! 
echo.
echo To start the server, run:
echo   python start_server.py
echo.
echo To test the API endpoints (after starting server), run:
echo   python test_api_endpoints.py
echo.
pause