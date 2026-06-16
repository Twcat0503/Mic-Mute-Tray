"""Global hotkey registration."""

from typing import Callable, Optional

import keyboard


class HotkeyManager:
    def __init__(self):
        self._hotkey: Optional[str] = None
        self._callback: Optional[Callable] = None

    def register(self, hotkey: str, callback: Callable):
        """Register a global hotkey, replacing the previous one if needed."""
        self.unregister()
        self._hotkey = hotkey
        self._callback = callback
        keyboard.add_hotkey(hotkey, callback, suppress=True)

    def unregister(self):
        """Remove the active global hotkey."""
        if self._hotkey:
            try:
                keyboard.remove_hotkey(self._hotkey)
            except (KeyError, ValueError):
                pass
            self._hotkey = None

    @property
    def current(self) -> Optional[str]:
        return self._hotkey
