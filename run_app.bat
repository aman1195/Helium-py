@echo off
REM Run the Helium AI application

echo Installing/updating requirements...
pip install -r requirements.txt

if %ERRORLEVEL% neq 0 (
    echo Failed to install requirements. Please check the error messages above.
    pause
    exit /b
)

echo.
echo Starting Helium AI...
echo.

echo Open your web browser and go to: http://localhost:5000
echo.

python app.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo Failed to start Helium AI. Please check the error messages above.
    pause
)
