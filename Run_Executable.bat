@echo off
echo ========================================
echo Evony Active Generals Tracker - Run Script
echo ========================================
echo.

REM Check if the executable exists
if not exist "dist\EvonyActiveGenerals.exe" (
    echo ERROR: Executable not found!
    echo.
    echo Please run Build_Executable.bat first to create the executable.
    echo Expected location: dist\EvonyActiveGenerals.exe
    echo.
    pause
    exit /b 1
)

echo Starting Evony Active Generals Tracker...
echo.
echo The application includes all resources embedded - no external files needed.
echo.

REM Run the executable
start "" "dist\EvonyActiveGenerals.exe"

echo Application launched successfully!
echo.
echo If the application doesn't start, check for any error messages.
echo.