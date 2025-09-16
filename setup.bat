@echo off
chcp 65001 >nul
title GitHub Assistant - Setup
color 0A
echo.
echo ========================================
echo    GITHUB ASSISTANT SETUP
echo ========================================
echo.

REM Check if Python is installed
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo.
    echo Please install Python from: https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    echo After installing Python, run this setup again.
    echo.
    pause
    exit /b 1
) else (
    echo Python is installed
)

REM Check if Git is installed
echo.
echo [2/4] Checking Git installation...
git --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: Git is not installed or not in PATH.
    echo.
    echo Please install Git from: https://git-scm.com/
    echo Make sure to add Git to PATH during installation
    echo.
    echo After installing Git, run this setup again.
    echo.
    pause
    exit /b 1
) else (
    echo Git is installed
)

REM Check if Git LFS is installed (optional but recommended)
echo.
echo [3/4] Checking Git LFS installation...
git lfs version >nul 2>&1
if errorlevel 1 (
    echo Git LFS not detected. This is optional but recommended for large files.
    echo Install from: https://git-lfs.github.io/
    echo Without Git LFS, large file uploads greater than 100MB may be slow.
    echo.
    echo Enter S then Enter to skip and continue setup now.
    echo Press any other key then Enter to exit and install Git LFS first.
    set /p LFS_CHOICE="Choice (S to skip, anything else to exit): "
    if /I "%LFS_CHOICE%"=="S" (
        echo Skipping Git LFS and continuing setup...
    ) else (
        echo Exiting setup so you can install Git LFS.
        exit /b 1
    )
) else (
    echo Git LFS is installed
    git lfs install --skip-repo >nul 2>&1
    echo Git LFS user hooks initialized.
)

REM Install required packages
echo.
echo [4/4] Installing required packages...
echo This may take a few minutes...
echo.
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install packages. Please check your internet connection.
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo    SETUP COMPLETE
echo ========================================
echo.
echo Setup is complete. We'll reopen the Start Here menu.
echo Then select [2] to run the app.
echo.
echo Please read the instructions above.
set /p _CONT="Press Enter to return to the Start Here menu... "
if exist "START_HERE.bat" (
    echo Launching START_HERE.bat...
    call START_HERE.bat
) else (
    echo START_HERE.bat not found. Starting app directly...
    call run.bat
)
exit /b 0
