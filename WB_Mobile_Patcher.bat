@echo off
setlocal enabledelayedexpansion

title WB Mobile Patcher v1.0
echo ======================================================================
echo              WB Mobile Patcher v1.0 - Portable Suite
echo ======================================================================
echo.

cd /d "%~dp0"
set PYTHONDONTWRITEBYTECODE=1

if "%~1"=="" goto no_args
python -B WB_Mobile_Patcher.py %*
goto end

:no_args
python -B WB_Mobile_Patcher.py "input"

:end
echo.
echo ======================================================================
echo All built APKs and files are located in the "output\" folder.
echo ======================================================================
echo.
pause
