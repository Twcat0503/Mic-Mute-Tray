@echo off
setlocal
cd /d "%~dp0"
if exist "%~dp0.venv\Scripts\pythonw.exe" (
  start "" "%~dp0.venv\Scripts\pythonw.exe" "%~dp0main.py"
  exit /b 0
)
where pythonw >nul 2>&1
if not errorlevel 1 (
  start "" pythonw "%~dp0main.py"
  exit /b 0
)
echo Python was not found. Run install.bat first.
pause
exit /b 1
