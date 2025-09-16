@echo off
chcp 65001 >nul
title GitHub Assistant - Start Here
color 0E

:menu
cls
echo.
echo ========================================
echo    GITHUB ASSISTANT - START HERE
echo ========================================
echo.
echo Welcome to GitHub Assistant!
echo.
echo This is your first time? Let's get you set up:
echo.
echo [1] First time setup (recommended)
echo [2] Run the app (choose this after completing setup)
echo [3] View quick start guide
echo [4] Exit
echo.
set /p choice="Choose an option (1-4): "

if /I "%choice%"=="1" goto do_setup
if /I "%choice%"=="2" goto run_app
if /I "%choice%"=="3" goto open_quickstart
if /I "%choice%"=="4" goto bye

echo.
echo Invalid choice. Please try again.
echo.
pause
goto menu

:do_setup
echo.
echo Running first-time setup...
set FROM_START_HERE=1
call setup.bat
set FROM_START_HERE=
echo.
echo Returning to menu...
pause
goto menu

:run_app
echo.
echo Starting GitHub Assistant...
call run.bat
echo.
echo Returning to menu...
pause
goto menu

:open_quickstart
echo.
echo Opening quick start guide...
start QUICK_START.md
echo.
echo Press any key to return to menu...
pause >nul
goto menu

:bye
echo.
echo Goodbye!
exit /b 0
