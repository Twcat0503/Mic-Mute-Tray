@echo off
setlocal
cd /d "%~dp0"
echo [Mic Mute Tray] Installing dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo Installation failed.
  pause
  exit /b 1
)
echo Installation complete. Run launch.bat to start the app.
pause
