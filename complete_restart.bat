@echo off
echo Completely restarting services...

REM Kill the known processes using their commands
FOR /F "tokens=2" %%i IN ('tasklist /FI "IMAGENAME eq python.exe" /FO CSV ^| findstr :5000') DO taskkill /PID %%i /F 2>nul
FOR /F "tokens=2" %%i IN ('tasklist /FI "IMAGENAME eq python.exe" /FO CSV ^| findstr bot/run.py') DO taskkill /PID %%i /F 2>nul

REM Alternative: Kill using port occupation
netstat -ano | findstr :8000
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do taskkill /PID %%a /F 2>nul

REM Give a moment for processes to terminate
timeout /t 3 /nobreak

echo Starting backend service...
start "Backend Service" cmd /k "cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

echo Starting bot service...
start "Bot Service" cmd /k "cd bot && python run.py"

echo All services have been restarted!
pause