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
    echo WARNING: Git LFS is not installed (recommended for large files)
    echo.
    echo Attempting to detect winget to auto-install Git LFS...
    where winget >nul 2>&1
    if errorlevel 1 (
        echo winget not found. Please install Git LFS manually:
        echo   https://git-lfs.github.io/
        echo Or install via Git for Windows installer.
        echo.
        echo You can continue without Git LFS, but large files (>100MB) may upload slowly.
        echo.
    ) else (
        echo winget found. Trying: winget install Git.Git-LFS -e --source winget --silent
        winget install Git.Git-LFS -e --source winget --silent
        if errorlevel 1 (
            echo Could not auto-install Git LFS. Please install manually:
            echo   https://git-lfs.github.io/
            echo.
        ) else (
            echo Git LFS installation attempted. Opening a NEW terminal may be required.
        )
    )
    echo After installing Git LFS, REOPEN this window and rerun setup.
    echo.
    echo You can bypass Git LFS for now. Large files (>100MB) may upload slowly.
    echo.
    echo Choose an option:
    echo   [C] Continue without Git LFS (recommended if you don't use large files)
    echo   [X] Exit setup and install Git LFS first
    set /p LFS_BYPASS="Select (C/X): "
    if /I "%LFS_BYPASS%"=="X" (
        echo Exiting setup. Install Git LFS, then run setup again.
        exit /b 1
    )
    echo Continuing without Git LFS...
) else (
    echo Git LFS is installed
    echo Initializing Git LFS user hooks...
    for /f "tokens=*" %%I in ('git lfs install --skip-repo 2^>^&1') do set LFS_INSTALL_OUT=%%I
    echo %LFS_INSTALL_OUT%
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
echo On the next screen, select [2] to run the app.
echo.
if exist "START_HERE.bat" (
    echo Launching START_HERE.bat...
    timeout /t 2 >nul
    call START_HERE.bat
) else (
    echo START_HERE.bat not found. Starting app directly...
    timeout /t 2 >nul
    call run.bat
)
exit /b 0
