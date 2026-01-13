@echo off
echo Stopping services...

REM Kill existing service processes
taskkill /f /im uvicorn.exe 2>nul
taskkill /f /im python.exe /fi "memusage gt 10000" 2>nul

echo Starting backend service...
start cmd /k "cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

echo Starting bot service...
start cmd /k "cd bot && python run.py"

echo Services restarted!
pause