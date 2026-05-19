$ErrorActionPreference = "Stop"

Set-Location (Join-Path $PSScriptRoot "static")
& "D:\WORK\presentation-coach\backend\.venv\Scripts\python.exe" -m http.server 5173 --bind 127.0.0.1
