@echo off
echo Starting QwenEditBot system with ngrok...

REM Check if ngrok is installed
if not exist "ngrok.exe" (
    echo Error: ngrok.exe not found in current directory!
    echo Please download ngrok from https://ngrok.com/download and place it in this directory.
    pause
    exit /b 1
)

REM Check if ngrok authtoken is set
echo Checking ngrok authtoken...
ngrok config check-authtoken >nul 2>&1
if errorlevel 1 (
    echo Please set your ngrok authtoken first:
    echo ngrok config add-authtoken YOUR_AUTHTOKEN_HERE
    pause
    exit /b 1
)

REM Start Redis if not already running (optional)
echo Checking if Redis is running...
redis-cli ping >nul 2>&1
if errorlevel 1 (
    echo Redis is not running. Please start Redis server manually.
    echo redis-server
    pause
    exit /b 1
) else (
    echo Redis is running.
)

REM Start backend server
echo Starting backend server...
start "QwenEditBot Backend" cmd /c "cd backend && venv\Scripts\activate && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

REM Wait for backend to start
echo Waiting for backend to start...
timeout /t 10 /nobreak >nul

REM Start worker
echo Starting worker...
start "QwenEditBot Worker" cmd /c "cd worker && venv\Scripts\activate && python run.py"

REM Wait for worker to start
echo Waiting for worker to start...
timeout /t 5 /nobreak >nul

REM Start ngrok tunnel
echo Starting ngrok tunnel...
start "Ngrok Tunnel" cmd /c "ngrok http 8000"

REM Wait for ngrok to initialize
echo Ngrok tunnel started. Please wait for the URL to appear in the ngrok window.
echo After ngrok generates the URL, you will need to set up the Telegram webhook.
echo.
echo Press any key to continue to webhook setup when ready...
pause >nul

REM Get bot token and ngrok URL from user
set /p BOT_TOKEN="Enter your Telegram bot token: "
set /p NGROK_URL="Enter your ngrok HTTPS URL (e.g., https://abc123.ngrok-free.app): "

REM Set up Telegram webhook
echo Setting up Telegram webhook...
curl -X POST "https://api.telegram.org/bot%BOT_TOKEN%/setWebhook?url=%NGROK_URL%/api/telegram/webhook"

echo.
echo Webhook setup complete!
echo Your QwenEditBot system is now running with ngrok tunnel.
echo.
echo Important URLs:
echo - Backend Health: %NGROK_URL%/health
echo - Backend Docs: %NGROK_URL%/docs
echo - Ngrok Inspector: http://localhost:4040
echo.
echo To stop the system, close all command windows.
echo.

pause