@echo off
chcp 65001 >nul
setlocal ENABLEDELAYEDEXPANSION

echo.
echo ========================================
echo    CHECKING GIT LFS AVAILABILITY
echo ========================================
echo.

REM Exit codes:
REM   0 = Git LFS detected and usable
REM   2 = Git is not installed or not in PATH
REM   3 = Git LFS is not installed or not in PATH
REM   4 = Unexpected error

REM 1) Check Git
where git >nul 2>&1
if errorlevel 1 (
	echo ERROR: Git is not installed or not in PATH.
	echo Install from https://git-scm.com/ and open a NEW terminal.
	set EXITCODE=2 & goto :END
)

for /f "tokens=*" %%G in ('git --version 2^>^&1') do set GIT_VER=%%G
echo %GIT_VER%

REM 2) Check Git LFS binary
REM    We call via "git lfs version" so it resolves the extension correctly
for /f "tokens=*" %%L in ('git lfs version 2^>^&1') do set LFS_VER=%%L
if errorlevel 1 (
	echo WARNING: Git LFS not detected by this session.
	echo If you just installed it, CLOSE this window and open a NEW one.
	echo Otherwise install from https://git-lfs.github.io/ or run:
	echo   winget install Git.Git-LFS
	set EXITCODE=3 & goto :END
)

echo %LFS_VER%

REM 3) Show LFS environment for diagnostics (does not affect result)
call :PrintHeader "Git LFS Environment"
 git lfs env 2>nul | findstr /R /C:"^git-lfs/" /C:"^LocalGit" /C:"^Process" /C:"^Repo:" /C:"^Endpoint:" 

REM 4) Ensure user-level install of hooks (safe if already installed)
REM    This does NOT modify current repo; it just sets up user hooks
for /f "tokens=*" %%I in ('git lfs install --skip-repo 2^>^&1') do set LFS_INSTALL_OUT=%%I
echo %LFS_INSTALL_OUT%


echo.
echo Git LFS appears to be installed and callable from this shell.
echo You can now retry your upload or run your app.
set EXITCODE=0 & goto :END

:PrintHeader
set HDR=%~1
echo.
echo ---------------- %HDR% ----------------
exit /b 0

:END
echo.
echo Press any key to close this window...
pause >nul
exit /b %EXITCODE%
