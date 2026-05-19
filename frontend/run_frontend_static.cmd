@echo off
cd /d D:\WORK\presentation-coach\frontend\static
D:\WORK\presentation-coach\backend\.venv\Scripts\python.exe -m http.server 5173 --bind 127.0.0.1 > ..\frontend-server.log 2>&1
