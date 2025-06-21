@echo off
echo Installing required packages...
pip install -r simple_requirements.txt

if %ERRORLEVEL% neq 0 (
    echo Failed to install requirements. Please check the error messages above.
    pause
    exit /b
)

echo.
echo Starting Helium AI (Simple Web Interface)...
echo.

set FLASK_APP=simple_web.py
set FLASK_DEBUG=1
set PYTHONPATH=%CD%
python -m flask run --host=0.0.0.0 --port=5000

if %ERRORLEVEL% neq 0 (
    echo.
    echo Failed to start Helium AI. Please check the error messages above.
    pause
)
