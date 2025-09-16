@echo off
title GitHub Assistant
color 0B
echo.
echo ========================================
echo    🚀 STARTING GITHUB ASSISTANT 🚀
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH.
    echo.
    echo 📥 Please install Python from: https://python.org
    echo    Then run setup.bat first
    echo.
    pause
    exit /b 1
)

REM Check if required packages are installed
python -c "import github" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Required packages not installed.
    echo.
    echo 🔧 Running setup first...
    echo.
    call setup.bat
    if errorlevel 1 (
        echo ❌ Setup failed. Please check the error messages above.
        pause
        exit /b 1
    )
)

REM Check if Git is available
git --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Git is not installed or not in PATH.
    echo.
    echo 📥 Please install Git from: https://git-scm.com/
    echo    Then run setup.bat again
    echo.
    pause
    exit /b 1
)

echo ✅ All requirements met. Starting GitHub Assistant...
echo.
echo 💡 First time? Get a GitHub token from: https://github.com/settings/tokens/new
echo.

REM Start the application
python github_assistant.py

REM If we get here, the app has closed
echo.
echo 👋 GitHub Assistant has closed.
echo.
pause
