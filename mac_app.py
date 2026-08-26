"""macOS menu bar agent.

AppKit owns the main run loop here, which is what `NSStatusItem` and the
Carbon hot key API both expect. The settings window is a Tk dialog and Tk
insists on owning a main loop of its own, so it runs as a short lived child
process instead of fighting AppKit for the main thread.
"""

import os
import subprocess
import sys
from ctypes import c_bool, c_double, c_int64, c_void_p

import asset_generator
import mac_keycodes
import mac_objc as objc
import mac_startup
from config_manager import ConfigManager
from mac_hotkey import HotkeyManager
from mac_mic_control import MicControl, device_name
from mac_sound import SoundManager

# NSStatusItem length that sizes itself to the image.
_VARIABLE_STATUS_ITEM_LENGTH = -1.0

# The menu bar is 24 pt tall; an 18 pt glyph is the usual fit.
_MENU_BAR_ICON_HEIGHT = 18.0
_SYMBOL_POINT_SIZE = 15.0

_STATE_POLL_SECONDS = 1.0

_TAG_TOGGLE = 1
_TAG_SETTINGS = 2
_TAG_QUIT = 3


class MenuBarApp:
    APP_NAME = "Mic Mute Tray"

    def __init__(self):
        """Set up the status item, microphone access, and the global hotkey."""
        self._config = ConfigManager()
        self._sound = SoundManager()
        self._hotkey_mgr = HotkeyManager()
        self._assets = asset_generator.ensure_assets()
        self._settings_process = None
        self._last_muted = None
        self._mic_available = False
        self._image_cache: dict = {}

        try:
            self._mic = MicControl()
            self._mic_available = True
        except Exception as e:
            print(f"[WARN] Microphone control is unavailable: {e}")
            self._mic = None

        objc.become_menu_bar_agent()
        # One target serves both the menu items and the timer: menu items carry
        # a tag, the timer does not.
        self._target = objc.make_target(self._on_action)
        self._build_status_item()
        self._register_hotkey()

        self._timer = objc.schedule_timer(_STATE_POLL_SECONDS, self._target)
        self._refresh(force=True)

    # -- status item ------------------------------------------------------

    def _build_status_item(self):
        """Create the menu bar extra and its menu."""
        status_bar = objc.msg(c_void_p)(
            objc.cls("NSStatusBar"), objc.sel("systemStatusBar")
        )
        self._status_bar = status_bar
        self._status_item = objc.msg(c_void_p, c_double)(
            status_bar,
            objc.sel("statusItemWithLength:"),
            _VARIABLE_STATUS_ITEM_LENGTH,
        )
        objc.retain(self._status_item)
        self._button = objc.msg(c_void_p)(self._status_item, objc.sel("button"))

        menu = objc.msg(c_void_p)(
            objc.msg(c_void_p)(objc.cls("NSMenu"), objc.sel("alloc")), objc.sel("init")
        )
        # The app updates titles itself; automatic enabling would fight that.
        objc.msg(None, c_bool)(menu, objc.sel("setAutoenablesItems:"), False)

        self._status_line = self._add_item(menu, "Microphone", None, enabled=False)
        self._add_separator(menu)
        self._toggle_item = self._add_item(
            menu, "Toggle Mute", _TAG_TOGGLE, enabled=self._mic_available
        )
        self._add_separator(menu)
        self._add_item(menu, "Settings…", _TAG_SETTINGS, key=",")
        self._add_separator(menu)
        self._add_item(menu, f"Quit {self.APP_NAME}", _TAG_QUIT, key="q")

        objc.msg(None, c_void_p)(self._status_item, objc.sel("setMenu:"), menu)
        objc.retain(menu)
        self._menu = menu

    def _add_item(self, menu, title: str, tag, enabled: bool = True, key: str = ""):
        """Append a menu item and return it."""
        action = objc.sel("invoke:") if tag is not None else None
        item = objc.msg(c_void_p, c_void_p, c_void_p, c_void_p)(
            objc.msg(c_void_p)(objc.cls("NSMenuItem"), objc.sel("alloc")),
            objc.sel("initWithTitle:action:keyEquivalent:"),
            objc.nsstring(title),
            action,
            objc.nsstring(key),
        )
        if tag is not None:
            objc.msg(None, c_void_p)(item, objc.sel("setTarget:"), self._target)
            objc.msg(None, c_int64)(item, objc.sel("setTag:"), tag)
        objc.msg(None, c_bool)(item, objc.sel("setEnabled:"), enabled)
        objc.msg(None, c_void_p)(menu, objc.sel("addItem:"), item)
        objc.retain(item)
        return item

    def _add_separator(self, menu):
        separator = objc.msg(c_void_p)(
            objc.cls("NSMenuItem"), objc.sel("separatorItem")
        )
        objc.msg(None, c_void_p)(menu, objc.sel("addItem:"), separator)

    # -- state ------------------------------------------------------------

    def _image_for(self, muted: bool):
        """Return the status item image for the current state.

        A custom file wins when one is configured. Otherwise the app uses an
        SF Symbol, which the system renders as a template image so it tracks
        light and dark menu bars automatically.
        """
        custom = asset_generator.custom_icon_path(self._config, muted)
        key = custom or ("muted" if muted else "unmuted")
        if key in self._image_cache:
            return self._image_cache[key]

        image = None
        if custom:
            image = objc.image_from_file(custom, _MENU_BAR_ICON_HEIGHT)
        if image is None:
            symbol = "mic.slash.fill" if muted else "mic.fill"
            description = "Microphone muted" if muted else "Microphone on"
            image = objc.symbol_image(symbol, description, _SYMBOL_POINT_SIZE)
            key = "muted" if muted else "unmuted"

        if image:
            self._image_cache[key] = image
            objc.retain(image)
        return image

    def _refresh(self, force: bool = False):
        """Sync the status item with the microphone state."""
        if not self._mic_available or not self._mic:
            objc.msg(None, c_void_p)(
                self._status_line, objc.sel("setTitle:"),
                objc.nsstring("Microphone unavailable"),
            )
            if force:
                image = objc.symbol_image(
                    "mic.slash", "Microphone unavailable", _SYMBOL_POINT_SIZE
                )
                if image:
                    objc.msg(None, c_void_p)(
                        self._button, objc.sel("setImage:"), image
                    )
                objc.msg(None, c_void_p)(
                    self._button, objc.sel("setToolTip:"),
                    objc.nsstring(f"{self.APP_NAME} — Unavailable"),
                )
            return

        muted = self._mic.is_muted()
        if not force and muted == self._last_muted:
            return
        self._last_muted = muted

        image = self._image_for(muted)
        if image:
            objc.msg(None, c_void_p)(self._button, objc.sel("setImage:"), image)

        status = "Muted" if muted else "Unmuted"
        objc.msg(None, c_void_p)(
            self._button, objc.sel("setToolTip:"),
            objc.nsstring(f"{self.APP_NAME} — {status}"),
        )
        objc.msg(None, c_void_p)(
            self._status_line, objc.sel("setTitle:"),
            objc.nsstring(
                "Microphone muted" if muted else "Microphone unmuted"
            ),
        )

        hotkey = self._config.get("hotkey", "F13")
        objc.msg(None, c_void_p)(
            self._toggle_item, objc.sel("setTitle:"),
            objc.nsstring(f"Toggle Mute  ({mac_keycodes.describe(hotkey)})"),
        )

    # -- actions ----------------------------------------------------------

    def _register_hotkey(self):
        """Register the configured hotkey."""
        if not self._mic_available:
            return
        hotkey = self._config.get("hotkey", "F13")
        try:
            self._hotkey_mgr.register(hotkey, self._on_toggle)
        except Exception as e:
            print(f"[WARN] Failed to register hotkey ({hotkey}): {e}")

    def _on_toggle(self):
        """Toggle microphone mute state and play a notification sound."""
        if not self._mic_available or not self._mic:
            return
        try:
            muted = self._mic.toggle()
            self._refresh(force=True)
            self._sound.play(
                asset_generator.resolve_sound_path(self._config, self._assets, muted)
            )
        except Exception as e:
            print(f"[ERROR] Failed to toggle microphone: {e}")

    def _on_action(self, tag: int):
        """Handle both menu selections and the state poll timer."""
        if tag == _TAG_TOGGLE:
            self._on_toggle()
        elif tag == _TAG_SETTINGS:
            self._open_settings()
        elif tag == _TAG_QUIT:
            self._quit()
        else:
            # The repeating NSTimer arrives with no tag.
            self._poll()

    def _poll(self):
        """Refresh state and pick up settings changes once the dialog closes."""
        if self._settings_process is not None:
            if self._settings_process.poll() is None:
                return
            self._settings_process = None
            self._config = ConfigManager()
            self._image_cache.clear()
            self._register_hotkey()
            self._refresh(force=True)
            return
        self._refresh()

    def _open_settings(self):
        """Open the settings dialog in its own process."""
        if self._settings_process is not None and self._settings_process.poll() is None:
            objc.activate_app()
            return

        if getattr(sys, "frozen", False):
            # A bundled app has no main.py on disk, so it re-invokes itself.
            command = [sys.executable, "--settings"]
        else:
            script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
            command = [sys.executable, script, "--settings"]

        # Releasing the hotkey avoids toggling the mic while settings is open.
        self._hotkey_mgr.unregister()
        try:
            self._settings_process = subprocess.Popen(command)
        except OSError as e:
            print(f"[ERROR] Failed to open settings: {e}")
            self._register_hotkey()

    def _quit(self):
        """Tear down and leave the run loop."""
        self._hotkey_mgr.unregister()
        self._sound.cleanup()
        # Do not strand the settings dialog without an agent to return to.
        if self._settings_process is not None and self._settings_process.poll() is None:
            self._settings_process.terminate()
        objc.invalidate_timer(self._timer)
        if self._status_item:
            objc.msg(None, c_void_p)(
                self._status_bar, objc.sel("removeStatusItem:"), self._status_item
            )
        objc.stop_event_loop()

    def run(self):
        """Run the AppKit main loop."""
        if self._mic_available:
            try:
                print(f"[INFO] Default input device: {device_name()}")
            except Exception:
                pass
        objc.run_event_loop()
