@echo off
title WiFi File Server
echo Starting WiFi File Server...
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Install dependencies if needed
echo Installing/checking dependencies...
python -m pip install flask werkzeug pillow qrcode netifaces --quiet

REM Run the application
echo.
echo Starting server...
python FileServer.pyz

pause
