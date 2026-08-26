"""Start-at-login registration for the current platform."""

import sys

if sys.platform == "darwin":
    from mac_startup import APP_NAME, disable, enable, is_enabled
elif sys.platform == "win32":
    from win_startup import APP_NAME, disable, enable, is_enabled
else:
    raise ImportError(
        f"Mic Mute Tray supports Windows and macOS; {sys.platform} is not supported."
    )

__all__ = ["APP_NAME", "disable", "enable", "is_enabled"]
