"""JSON configuration storage."""

import json
import os
from typing import Any

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

DEFAULT_CONFIG: dict = {
    "hotkey": "F13",
    "mic_on_icon": None,
    "mic_off_icon": None,
    "mic_on_sound": None,
    "mic_off_sound": None,
    "autostart": False,
}


class ConfigManager:
    def __init__(self):
        self._data: dict = dict(DEFAULT_CONFIG)
        self._load()

    def _load(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as fh:
                    saved = json.load(fh)
                    for key in DEFAULT_CONFIG:
                        if key in saved:
                            self._data[key] = saved[key]
            except (json.JSONDecodeError, OSError):
                pass

    def save(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as fh:
                json.dump(self._data, fh, indent=2, ensure_ascii=True)
        except OSError:
            pass

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any):
        self._data[key] = value
        self.save()

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any):
        self.set(key, value)
