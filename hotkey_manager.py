"""Global hotkey registration for the current platform."""

import sys

if sys.platform == "darwin":
    from mac_hotkey import HotkeyManager
elif sys.platform == "win32":
    from win_hotkey import HotkeyManager
else:
    raise ImportError(
        f"Mic Mute Tray supports Windows and macOS; {sys.platform} is not supported."
    )

__all__ = ["HotkeyManager"]
