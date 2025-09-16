@echo off
title GitHub Assistant - Start Here
color 0E
echo.
echo ========================================
echo    🚀 GITHUB ASSISTANT - START HERE 🚀
echo ========================================
echo.
echo Welcome to GitHub Assistant!
echo.
echo This is your first time? Let's get you set up:
echo.
echo [1] First time setup (recommended)
echo [2] Skip setup and run app
echo [3] View quick start guide
echo [4] Exit
echo.
set /p choice="Choose an option (1-4): "

if "%choice%"=="1" (
    echo.
    echo 🔧 Running first-time setup...
    call setup.bat
    if not errorlevel 1 (
        echo.
        echo ✅ Setup complete! Starting app...
        call run.bat
    )
) else if "%choice%"=="2" (
    echo.
    echo 🚀 Starting GitHub Assistant...
    call run.bat
) else if "%choice%"=="3" (
    echo.
    echo 📖 Opening quick start guide...
    start QUICK_START.md
    echo.
    echo Press any key to continue...
    pause >nul
    goto :start
) else if "%choice%"=="4" (
    echo.
    echo 👋 Goodbye!
    exit /b 0
) else (
    echo.
    echo ❌ Invalid choice. Please try again.
    echo.
    goto :start
)

:start
echo.
echo Press any key to return to menu...
pause >nul
goto :start
