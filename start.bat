@echo off
echo Starting TrackFlow...
echo.

echo [1/3] Starting AI API on port 8000...
start cmd /k "cd ai && python -m uvicorn api.main:app --reload --port 8000"
timeout /t 3 >nul

echo [2/3] Starting Backend on port 3000...
start cmd /k "cd backend && npm run dev"
timeout /t 3 >nul

echo [3/3] Starting Frontend on port 5173...
start cmd /k "cd frontend && npm run dev"

echo.
echo TrackFlow is starting!
echo - Frontend: http://localhost:5173
echo - Backend: http://localhost:3000
echo - AI API: http://localhost:8000
echo.
pause
