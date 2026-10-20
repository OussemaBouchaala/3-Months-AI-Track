@echo off
REM Starts Bench. Uses the .venv next to platform\ (run setup.bat once), or your old lab venv until then.
cd /d "%~dp0"
if exist "..\.venv\Scripts\python.exe" (
  "..\.venv\Scripts\python.exe" server.py
) else if exist "..\..\ml-fundamentals-lab\.venv\Scripts\python.exe" (
  "..\..\ml-fundamentals-lab\.venv\Scripts\python.exe" server.py
) else (
  python server.py
)
pause
