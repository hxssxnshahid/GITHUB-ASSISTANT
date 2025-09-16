@echo off
echo Installing GitHub Assistant...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH.
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Install required packages
echo Installing required packages...
pip install -r requirements.txt

echo.
echo Setup complete! You can now run the GitHub Assistant.
echo.
echo To run the application, double-click run.bat or run:
echo python github_assistant.py
echo.
pause
