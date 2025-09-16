@echo off
setlocal ENABLEDELAYEDEXPANSION
chcp 65001 >nul
title GitHub Assistant
color 0B
echo.
echo ========================================
echo    STARTING GITHUB ASSISTANT
echo ========================================
echo.

REM Check if Python is installed
echo Checking Python...
where python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo.
    echo Please install Python from: https://python.org
    echo Then run setup.bat first
    echo.
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking required Python packages...
python -c "import github" >nul 2>&1
if errorlevel 1 (
    echo WARNING: Required packages not installed.
    echo.
    echo Running setup first...
    echo.
    call setup.bat
    if errorlevel 1 (
        echo ERROR: Setup failed. Please check the error messages above.
        pause
        exit /b 1
    )
)

REM Check if Git is available
echo Checking Git...
git --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: Git is not installed or not in PATH.
    echo.
    echo Please install Git from: https://git-scm.com/
    echo Then run setup.bat again
    echo.
    pause
    exit /b 1
)

REM Optional: Warn if Git LFS is missing and offer diagnostics
git lfs version >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Git LFS not detected. Large files greater than 100MB may upload slowly.
    if exist "check_git_lfs.bat" (
        echo Press Y then Enter to run a quick Git LFS diagnostic now, or any other key to skip.
        set /p RUNLFS="Run diagnostic? (Y/N): "
        if /I "%RUNLFS%"=="Y" (
            call check_git_lfs.bat
        )
    ) else (
        echo You can install Git LFS from: https://git-lfs.github.io/
    )
)

echo All requirements met. Starting GitHub Assistant...
echo.
echo First time? Get a GitHub token from: https://github.com/settings/tokens/new
echo.

REM Start the application
if not exist "github_assistant.py" (
    echo ERROR: github_assistant.py not found in %CD%
    echo Ensure you are running this from the project folder.
    pause
    exit /b 1
)

set LOGFILE=run_log.txt
echo [%date% %time%] Launching app >> "%LOGFILE%"
python github_assistant.py 1>>"%LOGFILE%" 2>>&1
set APP_EXIT=%ERRORLEVEL%

REM If we get here, the app has closed
echo.
echo GitHub Assistant has closed.
echo Exit code: %APP_EXIT%
echo Log saved to %LOGFILE%
echo.
pause
endlocal
