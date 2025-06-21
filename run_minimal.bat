@echo off
echo Installing minimal requirements...
pip install -r minimal_requirements.txt

if %ERRORLEVEL% neq 0 (
    echo Failed to install requirements. Please check the error messages above.
    pause
    exit /b
)

echo.
echo Starting Helium AI (Minimal Version)...
echo.

python minimal_web.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo Failed to start Helium AI. Please check the error messages above.
    pause
)
