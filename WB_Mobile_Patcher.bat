@echo off
setlocal

title WB Mobile Patcher v1.2
cd /d "%~dp0"
set PYTHONDONTWRITEBYTECODE=1

echo ======================================================================
echo              WB Mobile Patcher v1.2 - Portable Suite
echo ======================================================================
echo.

rem Prefer the Python launcher (py -3); plain "python" can be the Microsoft Store placeholder.
set "PYEXE="
py -3 --version >nul 2>nul && set "PYEXE=py -3"
if not defined PYEXE python --version >nul 2>nul && set "PYEXE=python"
if not defined PYEXE goto :no_python

java -version >nul 2>nul
if errorlevel 1 goto :no_java

goto :run_tool

:no_python
echo ======================================================================
echo [ERROR] Python is required to run WB Mobile Patcher!
echo ======================================================================
echo Python 3.8 or newer was not found ("py -3" and "python" both failed).
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
if "%~1"=="" (
    %PYEXE% -B WB_Mobile_Patcher.py "input"
) else (
    %PYEXE% -B WB_Mobile_Patcher.py %*
)
set "RC=%ERRORLEVEL%"

echo.
echo ======================================================================
if "%RC%"=="0" (
    echo Finished! Check the "output\" folder for your completed APK.
    echo If any mod packs were skipped, see the *_skipped_packs.md report there.
) else (
    echo [ERROR] The build did not finish ^(exit code %RC%^).
    echo See patch_overlay_latest_error.log in this folder for details.
)
echo ======================================================================
echo.
pause
exit /b %RC%
