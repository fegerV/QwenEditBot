@echo off
echo Setting up ngrok tunnel and Telegram webhook...

REM Проверяем, установлен ли ngrok
if not exist "ngrok.exe" (
    echo Error: ngrok.exe not found in current directory!
    echo Please download ngrok from https://ngrok.com/download and place it in this directory.
    pause
    exit /b 1
)

REM Проверяем, установлен ли токен для ngrok
echo Checking ngrok authtoken...
ngrok config check-authtoken >nul 2>&1
if errorlevel 1 (
    echo Please set your ngrok authtoken first:
    echo ngrok config add-authtoken YOUR_AUTHTOKEN_HERE
    pause
    exit /b 1
)

REM Запускаем backend если еще не запущен
echo Starting backend server...
start "FastAPI Backend" cmd /k "cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

REM Ждем немного пока backend запускается
timeout /t 5 /nobreak >nul

REM Запускаем ngrok
echo Starting ngrok tunnel...
start "Ngrok Tunnel" cmd /k "ngrok http 8000"

REM Ждем пока пользователь скопирует URL из ngrok
echo.
echo Please wait for ngrok to generate the URL and copy it.
echo Then press any key to continue and set up the Telegram webhook.
pause >nul

REM Запрашиваем токен бота и URL от пользователя
set /p BOT_TOKEN="Enter your Telegram bot token: "
set /p NGROK_URL="Enter your ngrok HTTPS URL (e.g., https://abc123.ngrok-free.app): "

REM Устанавливаем webhook для Telegram
echo Setting up Telegram webhook...
curl -X POST "https://api.telegram.org/bot%BOT_TOKEN%/setWebhook?url=%NGROK_URL%/api/telegram/webhook"

echo.
echo Webhook setup complete!
echo Your bot should now receive updates via ngrok.
echo.
echo Note: The webhook endpoint is at /api/telegram/webhook, not just /webhook
echo as the backend API is structured with prefixes.

pause