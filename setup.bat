@echo off
title GitHub Assistant - Setup
color 0A
echo.
echo ========================================
echo    🚀 GITHUB ASSISTANT SETUP 🚀
echo ========================================
echo.

REM Check if Python is installed
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH.
    echo.
    echo 📥 Please install Python from: https://python.org
    echo    Make sure to check "Add Python to PATH" during installation
    echo.
    echo After installing Python, run this setup again.
    echo.
    pause
    exit /b 1
) else (
    echo ✅ Python is installed
)

REM Check if Git is installed
echo.
echo [2/4] Checking Git installation...
git --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Git is not installed or not in PATH.
    echo.
    echo 📥 Please install Git from: https://git-scm.com/
    echo    Make sure to add Git to PATH during installation
    echo.
    echo After installing Git, run this setup again.
    echo.
    pause
    exit /b 1
) else (
    echo ✅ Git is installed
)

REM Check if Git LFS is installed (optional but recommended)
echo.
echo [3/4] Checking Git LFS installation...
git lfs version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Git LFS is not installed (optional but recommended for large files)
    echo.
    echo 📥 Install Git LFS from: https://git-lfs.github.io/
    echo    Or run: winget install Git.Git-LFS
    echo.
    echo You can continue without Git LFS, but large files may cause issues.
    echo.
    pause
) else (
    echo ✅ Git LFS is installed
)

REM Install required packages
echo.
echo [4/4] Installing required packages...
echo This may take a few minutes...
echo.
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Failed to install packages. Please check your internet connection.
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo    ✅ SETUP COMPLETE! ✅
echo ========================================
echo.
echo 🎉 GitHub Assistant is ready to use!
echo.
echo 📋 Next steps:
echo    1. Double-click "run.bat" to start the app
echo    2. Get a GitHub token from: https://github.com/settings/tokens/new
echo    3. Connect to GitHub in the app
echo    4. Start uploading your projects!
echo.
echo 💡 Tip: Keep this folder - you'll need it to run the app
echo.
pause
