"""System tray controller."""

import threading
import tkinter as tk
from typing import Optional

import pystray
from PIL import Image
from pystray import Menu, MenuItem

import asset_generator
from config_manager import ConfigManager
from hotkey_manager import HotkeyManager
from mic_control import MicControl
from sound_manager import SoundManager


class TrayApp:
    APP_NAME = "Mic Mute Tray"

    def __init__(self, root: tk.Tk):
        """Initialize tray state, assets, hotkeys, and microphone access."""
        self._root = root
        self._config = ConfigManager()
        self._sound = SoundManager()
        self._hotkey_mgr = HotkeyManager()
        self._assets = asset_generator.ensure_assets()
        self._mic_available = False
        self._muted = False
        self._poll_id = None
        self._last_status = None
        self._mic = MicControl()

        try:
            self._muted = self._mic.is_muted()
            self._mic_available = True
        except Exception as e:
            print(f"[WARN] Microphone control is unavailable: {e}")

        self._icon: Optional[pystray.Icon] = None
        self._settings_win = None
        self._settings_lock = threading.Lock()

        self._create_icon()
        self._register_hotkey()
        self._poll_microphone()

    def _pick_image(self, muted: bool) -> Image.Image:
        """Choose the custom or bundled icon for the current mute state."""
        default = self._assets["mic_off"] if muted else self._assets["mic_on"]
        path = asset_generator.custom_icon_path(self._config, muted) or default
        try:
            return Image.open(path).convert("RGBA")
        except Exception:
            return Image.open(default).convert("RGBA")

    def _get_icon_image(self) -> Image.Image:
        """Return the current tray icon image."""
        return self._pick_image(self._muted)

    def _update_icon(self):
        """Refresh tray icon image and tooltip text."""
        if not self._icon:
            return
        if self._mic_available and self._mic:
            muted = self._muted
            status = "Muted" if muted else "Unmuted"
        else:
            muted = False
            status = "Unavailable"
        self._icon.icon = self._pick_image(muted)
        self._icon.title = f"{self.APP_NAME} - {status}"
        self._icon.update_menu()

    def _poll_microphone(self):
        """Synchronize external changes and recover when a mic reconnects."""
        try:
            self._muted = self._mic.is_muted()
            self._mic_available = True
        except Exception:
            self._mic_available = False
        status = (self._mic_available, self._muted)
        if status != self._last_status:
            self._last_status = status
            self._update_icon()
        self._poll_id = self._root.after(1000, self._poll_microphone)

    def _register_hotkey(self):
        """Register the configured hotkey."""
        hotkey = self._config.get("hotkey", "F13")
        try:
            self._hotkey_mgr.register(
                hotkey, lambda: self._root.after(0, self._on_toggle)
            )
        except Exception as e:
            print(f"[WARN] Failed to register hotkey ({hotkey}): {e}")

    def _on_toggle(self):
        """Toggle microphone mute state and play a notification sound."""
        if not self._mic_available or not self._mic:
            return

        try:
            muted = self._mic.toggle()
            self._muted = muted
            self._update_icon()

            self._sound.play(
                asset_generator.resolve_sound_path(self._config, self._assets, muted)
            )
        except Exception as e:
            print(f"[ERROR] Failed to toggle microphone: {e}")

    def _create_icon(self):
        """Create the tray icon and menu."""

        def _status_text(_item):
            if self._mic_available and self._mic:
                return "Microphone muted" if self._muted else "Microphone unmuted"
            return "Microphone unavailable"

        menu_items = [
            MenuItem(_status_text, None, enabled=False),
            Menu.SEPARATOR,
            MenuItem("Toggle Mute", lambda _icon, _item: self._root.after(0, self._on_toggle),
                     enabled=lambda _item: self._mic_available),
            MenuItem("Settings", lambda _icon, _item: self._root.after(0, self._show_settings)),
            Menu.SEPARATOR,
        ]
        menu_items.append(MenuItem("Quit", lambda _icon, _item: self._root.after(0, self._quit)))

        menu = Menu(*menu_items)
        self._icon = pystray.Icon(
            self.APP_NAME,
            self._get_icon_image(),
            self.APP_NAME,
            menu,
        )

    def _show_settings(self):
        """Open the settings window on the Tk main thread."""
        from settings_window import SettingsWindow

        with self._settings_lock:
            if self._settings_win is not None:
                try:
                    if self._settings_win.winfo_exists():
                        self._settings_win.lift()
                        self._settings_win.focus_force()
                        return
                except tk.TclError:
                    pass

            self._hotkey_mgr.unregister()

            self._settings_win = SettingsWindow(
                self._root,
                self._config,
                self._hotkey_mgr,
                on_close=self._on_settings_closed,
            )

    def _on_settings_closed(self):
        """Restore hotkey and tray state after settings closes."""
        self._settings_win = None
        self._register_hotkey()
        self._update_icon()

    def _quit(self):
        if self._poll_id is not None:
            self._root.after_cancel(self._poll_id)
            self._poll_id = None
        self._hotkey_mgr.unregister()
        self._sound.cleanup()
        if self._icon:
            threading.Thread(target=self._icon.stop, daemon=True).start()
        self._root.after(100, self._root.destroy)

    def run(self):
        """Start the blocking pystray event loop."""
        self._icon.run()
