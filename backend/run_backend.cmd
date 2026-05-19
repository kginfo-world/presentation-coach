@echo off
cd /d D:\WORK\presentation-coach\backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 > backend-server.log 2>&1
