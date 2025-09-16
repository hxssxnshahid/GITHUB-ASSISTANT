@echo off
echo Building GitHub Assistant executable...
echo.

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Build the executable
echo Building executable...
pyinstaller --onefile --windowed --name "GitHub Assistant" --icon=icon.ico github_assistant.py

if exist "dist\GitHub Assistant.exe" (
    echo.
    echo Build successful! Executable created in dist\ folder
    echo You can now distribute GitHub Assistant.exe
) else (
    echo.
    echo Build failed. Check the output above for errors.
)

echo.
pause
