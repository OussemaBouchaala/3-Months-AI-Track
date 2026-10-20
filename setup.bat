@echo off
REM One-time setup: creates .venv here and installs everything Bench and the labs need.
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  python -m venv .venv
)
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
echo.
echo Done. Double-click start.bat to open Bench.
pause
