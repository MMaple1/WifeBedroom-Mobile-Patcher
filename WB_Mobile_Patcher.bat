@echo off
setlocal enabledelayedexpansion

title WB Mobile Patcher v1.0
cd /d "%~dp0"
set PYTHONDONTWRITEBYTECODE=1

echo ======================================================================
echo              WB Mobile Patcher v1.0 - Portable Suite
echo ======================================================================
echo.

where python >nul 2>nul
if errorlevel 1 goto :no_python

where java >nul 2>nul
if errorlevel 1 goto :no_java

goto :run_tool

:no_python
echo ======================================================================
echo [ERROR] Python is required to run WB Mobile Patcher!
echo ======================================================================
echo Python was not found in your system PATH.
echo.
echo Please install Python 3.8 or higher from: https://www.python.org/
echo IMPORTANT: During installation, make sure to check the box:
echo           "Add python.exe to PATH"
echo ======================================================================
echo.
pause
exit /b 1

:no_java
echo ======================================================================
echo [ERROR] Java Runtime is required to sign Android APKs!
echo ======================================================================
echo Java was not found in your system PATH. Android devices will refuse
echo to install unsigned APKs.
echo.
echo Quick Solution (Choose one, free and takes 1 minute):
echo   1. Install OpenJDK (Recommended): https://adoptium.net/ (Temurin 17 or 21)
echo   2. Or install Oracle Java: https://www.java.com/
echo.
echo IMPORTANT: During installation, ensure "Set JAVA_HOME" / "Add to PATH"
echo           is checked.
echo ======================================================================
echo.
pause
exit /b 1

:run_tool
if "%~1"=="" goto :no_args
python -B WB_Mobile_Patcher.py %*
goto :end

:no_args
python -B WB_Mobile_Patcher.py "input"

:end
echo.
echo ======================================================================
echo Finished! Check the "output\" folder for your completed APK.
echo ======================================================================
echo.
pause
