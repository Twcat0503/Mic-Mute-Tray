@echo off
setlocal
cd /d "%~dp0"
echo [Mic Mute Tray] Installing dependencies...
if exist ".venv\Scripts\python.exe" goto install
where py >nul 2>&1
if not errorlevel 1 (
  py -3 -m venv .venv
  if not errorlevel 1 goto check_venv
)
where python >nul 2>&1
if not errorlevel 1 (
  python -m venv .venv
  if not errorlevel 1 goto check_venv
)
where uv >nul 2>&1
if not errorlevel 1 (
  uv venv --seed .venv
  if not errorlevel 1 goto check_venv
)
echo Python 3.10 or newer is required. Install Python and try again.
pause
exit /b 1
:check_venv
if not exist ".venv\Scripts\python.exe" (
  echo Could not create the Python environment.
  pause
  exit /b 1
)
:install
".venv\Scripts\python.exe" -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)"
if errorlevel 1 (
  echo Python 3.10 or newer is required.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -c "import tkinter as tk; root = tk.Tk(); root.withdraw(); root.destroy()"
if errorlevel 1 (
  echo Python is missing working Tkinter resources. Install Python with Tcl/Tk support.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo Installation failed.
  pause
  exit /b 1
)
echo Installation complete. Run launch.bat to start the app.
pause
