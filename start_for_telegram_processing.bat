@echo off
setlocal enabledelayedexpansion
title QwenEditBot Service Manager
chcp 65001 >nul

:: Configuration
set "BACKEND_URL=http://localhost:8000"
set "COMFYUI_URL=http://localhost:8188"
set "REDIS_PATH=C:\Program Files\Redis\redis-server.exe"

cls
echo ================================================================
echo           QwenEditBot - Telegram Processing Services
echo ================================================================
echo.

:: 1. Check Python
echo [1/6] Проверка Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo ❌ ОШИБКА: Python не найден в PATH.
    pause
    exit /b 1
)
echo ✓ Python найден.
echo.

:: 2. Check Environment Files
echo [2/6] Проверка файлов конфигурации...
set "ENV_MISSING=0"
if not exist "backend\.env" (echo   - ВНИМАНИЕ: backend\.env отсутствует & set "ENV_MISSING=1")
if not exist "bot\.env" (echo   - ВНИМАНИЕ: bot\.env отсутствует & set "ENV_MISSING=1")
if not exist "worker\.env" (echo   - ВНИМАНИЕ: worker\.env отсутствует & set "ENV_MISSING=1")

if "%ENV_MISSING%"=="1" (
    echo.
    echo ⚠ Некоторые файлы .env отсутствуют. Убедитесь, что вы их создали на основе .env.example
) else (
    echo ✓ Все файлы .env на месте.
)
echo.

:: 3. Check ComfyUI (Must be started manually as per instructions)
echo [3/6] Проверка ComfyUI (%COMFYUI_URL%)...
curl -s --connect-timeout 2 %COMFYUI_URL%/system_stats >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ ComfyUI запущен и отвечает.
) else (
    color 0E
    echo ⚠ ВНИМАНИЕ: ComfyUI не отвечает.
    echo Пожалуйста, запустите ComfyUI: C:\ComfyUI\run_nvidia_gpu.bat
    echo.
    set /p "choice=Продолжить запуск остальных сервисов? (y/n): "
    if /i "!choice!" neq "y" exit /b 1
)
echo.

:: 4. Check Redis
echo [4/6] Проверка Redis...
tasklist /FI "IMAGENAME eq redis-server.exe" 2>NUL | find /I /N "redis-server.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo ✓ Redis уже запущен.
) else (
    echo Redis не запущен. Попытка запуска...
    if exist "%REDIS_PATH%" (
        start "Redis Server" cmd /c ""%REDIS_PATH%" --port 6379"
        timeout /t 3 /nobreak >nul
        echo ✓ Redis запущен.
    ) else (
        color 0E
        echo ⚠ ОШИБКА: Redis не найден по пути %REDIS_PATH%
        echo Пожалуйста, запустите Redis вручную.
        echo.
    )
)
echo.

:: 5. Start Backend
echo [5/6] Запуск Backend (Uvicorn)...
start "QwenEditBot Backend" cmd /c "cd /d "%~dp0backend" && title Backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

echo Ожидание инициализации Backend...
set "retries=0"
:check_backend
set /a retries+=1
if %retries% gtr 30 (
    color 0C
    echo ❌ ОШИБКА: Backend не запустился за 30 секунд.
    pause
    exit /b 1
)
curl -s %BACKEND_URL%/api/webhooks/test >nul 2>&1
if %errorlevel% neq 0 (
    echo   ... ожидание (%retries%/30)
    timeout /t 2 /nobreak >nul
    goto check_backend
)
echo ✓ Backend запущен.
echo.

:: 6. Start Bot and Worker
echo [6/6] Запуск Bot и Worker...
start "QwenEditBot Bot" cmd /c "cd /d "%~dp0" && title Bot && python -m bot.run"
timeout /t 2 /nobreak >nul
start "QwenEditBot Worker" cmd /c "cd /d "%~dp0" && title Worker && python -m worker.run"

echo.
echo ================================================================
echo           ВСЕ СЕРВИСЫ ЗАПУЩЕНЫ УСПЕШНО
echo ================================================================
echo.
echo Теперь вы можете использовать бота в Telegram.
echo Логи доступны в отдельных окнах:
echo   - Backend (порт 8000)
echo   - Bot (Telegram API)
echo   - Worker (Обработка задач)
echo.
echo Нажмите любую клавишу, чтобы закрыть это окно (сервисы продолжат работу).
pause >nul
exit /b 0
