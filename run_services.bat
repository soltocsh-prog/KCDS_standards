@echo off
title KCS Automation Services Bootstrapper
echo ===================================================
echo  KCS Automation 서비스를 부팅합니다...
echo ===================================================

echo 1. 백엔드 서버(FastAPI)를 시작합니다...
start "KCS Backend Server" cmd /k "cd backend && .\venv\Scripts\python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000"

echo 2. 프론트엔드 개발 서버(Vite)를 시작합니다...
start "KCS Frontend Server" cmd /k "npm run dev"

echo.
echo ===================================================
echo  모든 서비스 구동 명령이 전송되었습니다.
echo  - 백엔드 주소: http://127.0.0.1:8000
echo  - 프론트엔드 주소: http://localhost:5173
echo ===================================================
pause
