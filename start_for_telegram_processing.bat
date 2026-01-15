@echo off
REM Start QwenEditBot services for Telegram processing (ComfyUI already running)
REM Use this when ComfyUI is already running and you want to process Telegram requests
REM Usage: double-click this file or run from cmd: start_for_telegram_processing.bat

REM Ensure script runs from the repository folder where this file is located
cd /d "%~dp0"

echo ======================================
echo Starting QwenEditBot services for Telegram processing
echo Assuming ComfyUI is already running
echo Repository: %CD%
echo ======================================

echo Verifying ComfyUI is running...
ping -n 1 localhost >nul
curl -s --connect-timeout 5 http://localhost:8188/system_stats >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ ComfyUI is running and responsive
) else (
    echo ⚠ ERROR: ComfyUI is not responding at http://localhost:8188
    echo ComfyUI must be running for processing to work.
    echo To start ComfyUI:
    echo   cd C:\ComfyUI
    echo   python main.py --listen --port 8188
    echo.
    echo Exiting...
    pause
    exit /b 1
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

echo Starting worker (job processor)...
echo The worker will connect to the running ComfyUI and process jobs from Telegram
start "QwenEditBot Worker" cmd /c "cd /d "%~dp0" && python -m worker.run"

echo.
echo All services started for Telegram processing.
echo You can now send photos from Telegram for processing.
echo.
echo Check individual windows for logs and errors.
echo If a service fails to start, open its window and inspect the error message.

REM Optional: Wait for a keypress before exiting to allow viewing startup messages
echo Press any key to exit...
pause >nul
exit /b 0