"""Windows startup registration."""

import os
import sys
from typing import Optional
import winreg

APP_NAME = "Mic Mute Tray"
_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def is_enabled() -> bool:
    """Return True when the app is registered in HKCU Run."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY, 0, winreg.KEY_READ) as key:
            winreg.QueryValueEx(key, APP_NAME)
            return True
    except OSError:
        return False


def enable(exe_path: Optional[str] = None):
    """Register the app to start with the current Windows user."""
    if exe_path is None:
        exe_path = _resolve_exe_path()
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            _RUN_KEY,
            0,
            winreg.KEY_SET_VALUE,
        ) as key:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, exe_path)
    except OSError:
        pass


def disable():
    """Remove the app from the current user's Windows startup entries."""
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            _RUN_KEY,
            0,
            winreg.KEY_SET_VALUE,
        ) as key:
            winreg.DeleteValue(key, APP_NAME)
    except OSError:
        pass


def _resolve_exe_path() -> str:
    """Return the command used for Windows startup."""
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'

    pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    if not os.path.isfile(pythonw):
        pythonw = sys.executable

    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
    return f'"{pythonw}" "{script}"'
