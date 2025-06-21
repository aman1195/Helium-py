@echo off
echo Installing required packages...
pip install -r requirements.txt

if %ERRORLEVEL% neq 0 (
    echo Failed to install requirements. Please check the error messages above.
    pause
    exit /b
)

echo.
echo Starting Helium AI...
echo.

set PYTHONPATH=%CD%
python -m src.web_app

if %ERRORLEVEL% neq 0 (
    echo.
    echo Failed to start Helium AI. Please check the error messages above.
    pause
)
