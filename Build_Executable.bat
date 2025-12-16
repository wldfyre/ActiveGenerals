@echo off
echo ========================================
echo Evony Active Generals Tracker - Build Script
echo ========================================
echo.
echo This script builds the single-file executable with embedded resources.
echo Make sure PyInstaller is installed: pip install pyinstaller
echo.

REM Check if PyInstaller is available
pyinstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: PyInstaller is not installed or not in PATH.
    echo Please install it with: pip install pyinstaller
    pause
    exit /b 1
)

echo Building executable with embedded resources...
echo This may take several minutes depending on your system...

REM Build the executable using the spec file
pyinstaller EvonyActiveGenerals.spec

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo Build completed successfully!
    echo ========================================
    echo.
    echo Executable created: dist\EvonyActiveGenerals.exe
    echo Size: 
    dir /b dist\EvonyActiveGenerals.exe | for %%A in (*) do echo   %%~zA bytes
    echo.
    echo The executable is now ready for distribution.
    echo No external files (Resources folder or config.json) are needed.
) else (
    echo.
    echo ========================================
    echo Build failed!
    echo ========================================
    echo Please check the error messages above.
)

echo.
pause