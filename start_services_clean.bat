@echo off
echo Starting services with clean environment...

REM First, let's make sure we have the right working directory
cd /d "c:\QwenEditBot"

REM Kill any existing Python processes related to our services
echo Terminating existing processes...
taskkill /f /im python.exe 2>nul

REM Wait a bit for processes to terminate
timeout /t 3 /nobreak >nul

REM Start backend service in a new window
echo Starting backend service...
start "QwenEditBot Backend" cmd /k "cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

REM Wait a few seconds for backend to start
timeout /t 5 /nobreak >nul

REM Start bot service in another window
echo Starting bot service...
start "QwenEditBot Bot" cmd /k "cd bot && python run.py"

echo Both services have been started in separate windows.
echo Please check the respective windows to verify they are running properly.
pause