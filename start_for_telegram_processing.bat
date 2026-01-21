@echo off
setlocal enabledelayedexpansion
title QwenEditBot Service Manager
chcp 65001 >nul

:: Configuration
set "BACKEND_URL=http://localhost:8000"
set "COMFYUI_URL=http://localhost:8188"
set "REDIS_PATH=C:\Program Files\Redis\redis-server.exe"
set "LOG_DIR=%~dp0logs"
set "BACKEND_LOG=%LOG_DIR%\backend.log"
set "DIAGNOSTIC_LOG=%LOG_DIR%\diagnostic.log"

:: Create logs directory
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo ================================================================ > "%~dp0startup.log"
echo           QwenEditBot - Telegram Processing Services           >> "%~dp0startup.log"
echo ================================================================ >> "%~dp0startup.log"
echo [INFO] Запуск от %DATE% %TIME% >> "%~dp0startup.log"

cls
echo ================================================================
echo           QwenEditBot - Telegram Processing Services
echo ================================================================
echo.

:: 0. Pre-flight diagnostics
echo [0/7] Запуск диагностики...
echo [0/7] Запуск диагностики... > "%DIAGNOSTIC_LOG%"
echo Diagnostic run at %DATE% %TIME% > "%DIAGNOSTIC_LOG%"
echo ================================= >> "%DIAGNOSTIC_LOG%"

:: Check Python and modules
echo   - Проверка Python и зависимостей...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo ❌ ОШИБКА: Python не найден в PATH.
    echo [FATAL] Python not in PATH >> "%DIAGNOSTIC_LOG%"
    pause
    exit /b 1
)

:: Test backend imports
cd /d "%~dp0backend"
echo [DIAG] Testing backend imports... >> "%DIAGNOSTIC_LOG%"
python -c "import sys; print('Python version:', sys.version)" 2>&1 >> "%DIAGNOSTIC_LOG%"
python -c "import fastapi, sqlalchemy, alembic, redis" 2>&1 >> "%DIAGNOSTIC_LOG%"
if %errorlevel% neq 0 (
    color 0E
    echo ⚠ ВНИМАНИЕ: Ошибка импорта зависимостей backend
    echo [WARNING] Backend dependency import failed >> "%DIAGNOSTIC_LOG%"
    echo Смотрите %DIAGNOSTIC_LOG% для деталей
) else (
    echo ✓ Зависимости backend проверены.
)
cd /d "%~dp0"
echo.
echo [1/7] Проверка Python...
echo ✓ Python найден.
echo.

:: 2. Check Environment Files
echo [2/7] Проверка файлов конфигурации...
set "ENV_MISSING=0"
if not exist "backend\.env" (echo   - ВНИМАНИЕ: backend\.env отсутствует & set "ENV_MISSING=1")
if not exist "bot\.env" (echo   - ВНИМАНИЕ: bot\.env отсутствует & set "ENV_MISSING=1")
if not exist "worker\.env" (echo   - ВНИМАНИЕ: worker\.env отсутствует & set "ENV_MISSING=1")

if "%ENV_MISSING%"=="1" (
    echo.
    echo ⚠ Некоторые файлы .env отсутствуют. Убедитесь, что вы их создали на основе .env.example
    echo [WARNING] Missing .env files >> "%DIAGNOSTIC_LOG%"
) else (
    echo ✓ Все файлы .env на месте.
    echo [INFO] All .env files present >> "%DIAGNOSTIC_LOG%"
)
echo.

:: 3. Check ComfyUI (Must be started manually as per instructions)
echo [3/7] Проверка ComfyUI (%COMFYUI_URL%)...
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
echo [5/7] Запуск Backend (Uvicorn)...
echo [5/7] Starting Backend... >> "%~dp0startup.log"

:: Create backend log directory
if not exist "%LOG_DIR%\backend" mkdir "%LOG_DIR%\backend"

:: Start backend with logging and error capture
start "QwenEditBot Backend" cmd /c "cd /d "%~dp0backend" && title Backend && echo [Backend] Starting at %TIME% > "%~dp0logs\backend\startup.log" && (python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > "%~dp0logs\backend\runtime.log" 2>&1 || (echo ERROR: Backend crashed! Check logs && echo [Backend crashed at %TIME%] >> "%~dp0logs\backend\crash.log" && type "%~dp0logs\backend\runtime.log" >> "%~dp0logs\backend\crash.log" && pause))"

echo Ожидание инициализации Backend...
echo Waiting for backend to initialize... >> "%~dp0startup.log"
set "retries=0"
:check_backend
set /a retries+=1
if %retries% gtr 30 (
    color 0C
    echo ❌ ОШИБКА: Backend не запустился за 30 секунд.
    echo [ERROR] Backend failed to start in 30 seconds >> "%~dp0startup.log"
    echo Проверьте логи: %~dp0logs\backend\
    pause
    exit /b 1
)

:: Comprehensive health checks
echo   ... ожидание (%retries%/30)
curl -s %BACKEND_URL%/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Backend health endpoint responding.
    curl -s %BACKEND_URL%/api/webhooks/test >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✓ Backend webhook endpoint responding.
        echo [INFO] Backend fully operational at %TIME% >> "%~dp0startup.log"
        goto backend_ready
    )
)

timeout /t 2 /nobreak >nul
goto check_backend

:backend_ready
echo ✓ Backend запущен.
echo.

:: 6. Start Bot and Worker
echo [6/7] Запуск Bot и Worker...
echo [6/7] Starting Bot and Worker... >> "%~dp0startup.log"
start "QwenEditBot Bot" cmd /c "cd /d "%~dp0" && title Bot && python -m bot.run"
timeout /t 2 /nobreak >nul
start "QwenEditBot Worker" cmd /c "cd /d "%~dp0" && title Worker && python -m worker.run"

echo.
echo [7/7] Завершение...
echo [7/7] Finalizing startup... >> "%~dp0startup.log"
echo ================================================================
echo           ВСЕ СЕРВИСЫ ЗАПУЩЕНЫ УСПЕШНО
echo ================================================================
echo.
echo Теперь вы можете использовать бота в Telegram.
echo Логи доступны в отдельных окнах:
echo   - Backend (порт 8000) - Логи: %~dp0logs\backend\
echo   - Bot (Telegram API)
echo   - Worker (Обработка задач)
echo.
echo Диагностическая информация: %DIAGNOSTIC_LOG%
echo Общий лог запуска: %~dp0startup.log
echo.
echo Нажмите любую клавишу, чтобы закрыть это окно (сервисы продолжат работу).
pause >nul
echo [INFO] Service manager closed at %TIME% >> "%~dp0startup.log"
exit /b 0
