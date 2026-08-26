"""Microphone mute control for the current platform."""

import sys

if sys.platform == "darwin":
    from mac_mic_control import MicControl
elif sys.platform == "win32":
    from win_mic_control import MicControl
else:
    raise ImportError(
        f"Mic Mute Tray supports Windows and macOS; {sys.platform} is not supported."
    )

__all__ = ["MicControl"]
