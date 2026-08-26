"""Notification sound playback for the current platform."""

import sys

if sys.platform == "darwin":
    from mac_sound import SoundManager
elif sys.platform == "win32":
    from win_sound import SoundManager
else:
    raise ImportError(
        f"Mic Mute Tray supports Windows and macOS; {sys.platform} is not supported."
    )

__all__ = ["SoundManager"]
