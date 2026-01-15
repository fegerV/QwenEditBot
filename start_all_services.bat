@echo off
REM Start all QwenEditBot services in a single window (without ngrok) - FINAL SAFE VERSION
REM This version does NOT kill existing Python processes, including ComfyUI
REM Migrations are NOT performed - run them manually when needed
REM Usage: double-click this file or run from cmd: start_all_services.bat

REM Ensure script runs from the repository folder where this file is located
cd /d "%~dp0"

echo ======================================
echo Starting QwenEditBot services in single window (without ngrok) - FINAL SAFE MODE
echo Repository: %CD%
echo ======================================

echo NOTE: This script will NOT terminate any existing Python processes.
echo NOTE: Migrations are NOT performed - run them manually when needed.
echo Make sure database schema is up-to-date before running this script.
echo.

echo Verifying ComfyUI is running...
ping -n 1 localhost >nul
curl -s --connect-timeout 5 http://localhost:8188/system_stats >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ ComfyUI is running and responsive
) else (
    echo ⚠ Warning: ComfyUI is not responding at http://localhost:8188
    echo Please ensure ComfyUI is running before proceeding.
    echo To start ComfyUI manually:
    echo   cd C:\ComfyUI
    echo   python main.py --listen --port 8188
    echo.
    echo Press any key to continue anyway or Ctrl+C to abort...
    pause >nul
)

echo Checking if Redis is running...
ping -n 1 localhost >nul
tasklist /FI "IMAGENAME eq redis-server.exe" 2>NUL | find /I /N "redis-server.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo ✓ Redis is already running
) else (
    echo Starting Redis server...
    start "Redis Server" cmd /c ""C:\Program Files\Redis\redis-server.exe" --port 6379"
    
    echo Waiting for Redis to start...
    timeout /t 5 /nobreak >nul
    
    REM Verify Redis is running
    tasklist /FI "IMAGENAME eq redis-server.exe" 2>NUL | find /I /N "redis-server.exe">NUL
    if "%ERRORLEVEL%"=="0" (
        echo ✓ Redis server started successfully
    ) else (
        echo ⚠ Warning: Could not verify Redis server started
        echo Make sure Redis is properly installed in C:\Program Files\Redis
    )
)

echo Verifying database is accessible...
cd /d "%~dp0backend" && python -c "from app.database import engine; print('Database connection OK')"
if %errorlevel% neq 0 (
    echo Database connection failed!
    pause
    exit /b 1
)

REM Start backend first
echo Starting backend (uvicorn)...
start "QwenEditBot Backend" cmd /c "cd /d "%~dp0backend" && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo Waiting for backend to initialize...
timeout /t 15 /nobreak >nul

echo Starting Telegram bot...
start "QwenEditBot Bot" cmd /c "cd /d "%~dp0" && python -m bot.run"

echo Waiting for bot to initialize...
timeout /t 15 /nobreak >nul

echo Waiting for services to fully stabilize before starting worker...
echo This delay helps prevent ComfyUI from crashing due to intensive polling by the worker
timeout /t 30 /nobreak >nul

echo Starting worker (job processor)...
start "QwenEditBot Worker" cmd /c "cd /d "%~dp0" && python -m worker.run"

echo All services started in background processes. Check individual windows for logs and errors.
echo If a service fails to start, open its window and inspect the error message.
echo Note: This script runs services WITHOUT ngrok tunneling for external access.

REM Optional: Wait for a keypress before exiting to allow viewing startup messages
echo Press any key to exit...
pause >nul
exit /b 0
