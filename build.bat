@echo off
echo Building Assistant executable...
echo.

REM Check if PyInstaller is installed
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
)

echo.
echo Building executable...
pyinstaller build.spec

echo.
echo Build complete!
echo Executable location: dist\assistant.exe
pause

