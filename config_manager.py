"""JSON configuration storage."""

import json
import os
import sys
from typing import Any

APP_NAME = "Mic Mute Tray"

# Config has always lived beside the script. macOS keeps it in Application
# Support instead, which is where Apple expects per-user app data, but an
# existing side-by-side file is still read so upgrades lose nothing.
_LOCAL_CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def _default_config_file() -> str:
    if sys.platform == "darwin":
        support = os.path.expanduser(
            os.path.join("~/Library/Application Support", APP_NAME)
        )
        return os.path.join(support, "config.json")
    return _LOCAL_CONFIG


CONFIG_FILE = _default_config_file()

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
        for path in (CONFIG_FILE, _LOCAL_CONFIG):
            if not os.path.exists(path):
                continue
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    saved = json.load(fh)
                    for key in DEFAULT_CONFIG:
                        if key in saved:
                            self._data[key] = saved[key]
                return
            except (json.JSONDecodeError, OSError):
                continue

    def save(self):
        try:
            os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
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
