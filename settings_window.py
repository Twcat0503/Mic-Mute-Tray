"""Settings window."""

import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Callable, Optional

import startup_manager
from config_manager import ConfigManager
from hotkey_manager import HotkeyManager

IS_MACOS = sys.platform == "darwin"

if IS_MACOS:
    import mac_keycodes
else:
    import keyboard

# macOS registers global hotkeys through Carbon, which only accepts a key code
# plus modifier flags. Picking them explicitly keeps the dialog to shortcuts
# the system can actually register.
HEADING_FONT = ("SF Pro Text", 12, "bold") if IS_MACOS else ("Segoe UI", 10, "bold")
AUTOSTART_LABEL = "Start at login" if IS_MACOS else "Start with Windows"
_ANY_FILE = "*" if IS_MACOS else "*.*"

IMAGE_FILETYPES = [
    ("Image files", ("*.png", "*.ico", "*.bmp")),
    ("All files", _ANY_FILE),
]
SOUND_FILETYPES = [("WAV files", "*.wav"), ("All files", _ANY_FILE)]


class SettingsWindow(tk.Toplevel):
    """Tkinter settings dialog."""

    def __init__(
        self,
        parent: tk.Misc,
        config: ConfigManager,
        hotkey_mgr: Optional[HotkeyManager] = None,
        on_close: Optional[Callable] = None,
    ):
        super().__init__(parent)
        self._config = config
        self._hotkey_mgr = hotkey_mgr
        self._on_close = on_close
        self._recording = False

        self.title("Mic Mute Tray Settings")
        self.resizable(False, False)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._cancel)

        self._build_ui()
        self._load_values()
        self._center()

    def _build_ui(self):
        pad = {"padx": 10, "pady": 4}
        main = ttk.Frame(self, padding=16)
        main.pack(fill=tk.BOTH, expand=True)

        row = 0

        ttk.Label(main, text="Hotkey", font=HEADING_FONT).grid(
            row=row,
            column=0,
            columnspan=3,
            sticky="w",
            pady=(0, 4),
        )
        row += 1

        row = self._build_hotkey_rows(main, row, pad)

        ttk.Separator(main, orient="horizontal").grid(
            row=row,
            column=0,
            columnspan=3,
            sticky="ew",
            pady=8,
        )
        row += 1

        ttk.Label(main, text="Tray Icons", font=HEADING_FONT).grid(
            row=row,
            column=0,
            columnspan=3,
            sticky="w",
            pady=(0, 4),
        )
        row += 1

        self._on_icon_var = tk.StringVar()
        self._off_icon_var = tk.StringVar()
        self._add_file_row(main, row, "Unmuted icon", self._on_icon_var, IMAGE_FILETYPES)
        row += 1
        self._add_file_row(main, row, "Muted icon", self._off_icon_var, IMAGE_FILETYPES)
        row += 1

        if IS_MACOS:
            ttk.Label(
                main,
                text="Leave empty to use the system microphone symbol.",
                foreground="gray40",
            ).grid(row=row, column=0, columnspan=3, sticky="w", padx=10)
            row += 1

        ttk.Separator(main, orient="horizontal").grid(
            row=row,
            column=0,
            columnspan=3,
            sticky="ew",
            pady=8,
        )
        row += 1

        ttk.Label(main, text="Sounds", font=HEADING_FONT).grid(
            row=row,
            column=0,
            columnspan=3,
            sticky="w",
            pady=(0, 4),
        )
        row += 1

        self._on_sound_var = tk.StringVar()
        self._off_sound_var = tk.StringVar()
        self._add_file_row(main, row, "Unmute sound", self._on_sound_var, SOUND_FILETYPES)
        row += 1
        self._add_file_row(main, row, "Mute sound", self._off_sound_var, SOUND_FILETYPES)
        row += 1

        ttk.Separator(main, orient="horizontal").grid(
            row=row,
            column=0,
            columnspan=3,
            sticky="ew",
            pady=8,
        )
        row += 1

        self._autostart_var = tk.BooleanVar()
        ttk.Checkbutton(
            main,
            text=AUTOSTART_LABEL,
            variable=self._autostart_var,
        ).grid(row=row, column=0, columnspan=3, sticky="w", **pad)
        row += 1

        ttk.Separator(main, orient="horizontal").grid(
            row=row,
            column=0,
            columnspan=3,
            sticky="ew",
            pady=8,
        )
        row += 1

        btn_frame = ttk.Frame(main)
        btn_frame.grid(row=row, column=0, columnspan=3, sticky="e", pady=(0, 2))
        ttk.Button(btn_frame, text="Save", width=8, command=self._save).pack(
            side=tk.LEFT,
            padx=4,
        )
        ttk.Button(btn_frame, text="Cancel", width=8, command=self._cancel).pack(
            side=tk.LEFT,
            padx=4,
        )

        main.columnconfigure(1, weight=1)

    def _build_hotkey_rows(self, main, row: int, pad: dict) -> int:
        """Build the platform's hotkey controls and return the next row."""
        self._hotkey_var = tk.StringVar()

        if not IS_MACOS:
            ttk.Label(main, text="Toggle microphone").grid(
                row=row,
                column=0,
                sticky="w",
                **pad,
            )
            self._hotkey_entry = ttk.Entry(
                main,
                textvariable=self._hotkey_var,
                width=22,
                state="readonly",
            )
            self._hotkey_entry.grid(row=row, column=1, sticky="ew", **pad)
            self._record_btn = ttk.Button(
                main,
                text="Record",
                width=8,
                command=self._start_record,
            )
            self._record_btn.grid(row=row, column=2, **pad)
            return row + 1

        self._key_choices = mac_keycodes.selectable_keys()
        self._key_var = tk.StringVar()
        ttk.Label(main, text="Toggle microphone").grid(
            row=row,
            column=0,
            sticky="w",
            **pad,
        )
        combo = ttk.Combobox(
            main,
            textvariable=self._key_var,
            values=[label for label, _ in self._key_choices],
            state="readonly",
            width=18,
        )
        combo.grid(row=row, column=1, columnspan=2, sticky="ew", **pad)
        combo.bind("<<ComboboxSelected>>", lambda _e: self._update_preview())
        row += 1

        self._mod_vars = {
            "control": tk.BooleanVar(),
            "option": tk.BooleanVar(),
            "shift": tk.BooleanVar(),
            "command": tk.BooleanVar(),
        }
        mods = ttk.Frame(main)
        mods.grid(row=row, column=1, columnspan=2, sticky="w", padx=10, pady=4)
        for text, key in (
            ("⌃ Control", "control"),
            ("⌥ Option", "option"),
            ("⇧ Shift", "shift"),
            ("⌘ Command", "command"),
        ):
            ttk.Checkbutton(
                mods,
                text=text,
                variable=self._mod_vars[key],
                command=self._update_preview,
            ).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Label(main, text="Modifiers").grid(row=row, column=0, sticky="w", **pad)
        row += 1

        ttk.Label(main, text="Shortcut").grid(row=row, column=0, sticky="w", **pad)
        self._preview = ttk.Label(main, textvariable=self._hotkey_var, font=HEADING_FONT)
        self._preview.grid(row=row, column=1, columnspan=2, sticky="w", **pad)
        return row + 1

    def _current_hotkey(self) -> str:
        """Return the hotkey string described by the macOS controls."""
        label = self._key_var.get()
        token = next(
            (tok for lab, tok in self._key_choices if lab == label),
            self._key_choices[0][1],
        )
        return mac_keycodes.build(
            token,
            self._mod_vars["control"].get(),
            self._mod_vars["option"].get(),
            self._mod_vars["shift"].get(),
            self._mod_vars["command"].get(),
        )

    def _update_preview(self):
        """Show the selected shortcut in Mac notation."""
        self._hotkey_var.set(mac_keycodes.describe(self._current_hotkey()))

    def _add_file_row(
        self,
        parent,
        row: int,
        label: str,
        var: tk.StringVar,
        filetypes: list,
    ):
        ttk.Label(parent, text=label).grid(
            row=row,
            column=0,
            sticky="w",
            padx=10,
            pady=4,
        )
        ttk.Entry(parent, textvariable=var, width=28).grid(
            row=row,
            column=1,
            sticky="ew",
            padx=10,
            pady=4,
        )
        ttk.Button(
            parent,
            text="Browse",
            width=8,
            command=lambda v=var, ft=filetypes: self._browse(v, ft),
        ).grid(row=row, column=2, padx=10, pady=4)

    def _load_values(self):
        saved = self._config.get("hotkey", "F13")
        if IS_MACOS:
            try:
                token, control, option, shift, command = mac_keycodes.split(saved)
            except ValueError:
                token, control, option, shift, command = "f13", False, False, False, False
            label = next(
                (lab for lab, tok in self._key_choices if tok == token),
                self._key_choices[0][0],
            )
            self._key_var.set(label)
            self._mod_vars["control"].set(control)
            self._mod_vars["option"].set(option)
            self._mod_vars["shift"].set(shift)
            self._mod_vars["command"].set(command)
            self._update_preview()
        else:
            self._hotkey_var.set(saved)

        self._on_icon_var.set(self._config.get("mic_on_icon") or "")
        self._off_icon_var.set(self._config.get("mic_off_icon") or "")
        self._on_sound_var.set(self._config.get("mic_on_sound") or "")
        self._off_sound_var.set(self._config.get("mic_off_sound") or "")
        self._autostart_var.set(startup_manager.is_enabled())

    def _browse(self, var: tk.StringVar, filetypes: list):
        path = filedialog.askopenfilename(
            parent=self,
            title="Select file",
            filetypes=filetypes,
        )
        if path:
            var.set(path)

    def _start_record(self):
        """Capture the next hotkey pressed by the user."""
        if self._recording:
            return
        self._recording = True
        self._record_btn.configure(text="Listening", state="disabled")
        self._hotkey_entry.configure(state="normal")
        self._hotkey_var.set("Press keys... (Esc to cancel)")
        self._hotkey_entry.configure(state="readonly")

        if self._hotkey_mgr:
            self._hotkey_mgr.unregister()

        def capture():
            current_hotkey = self._config.get("hotkey", "F13")
            try:
                hotkey = keyboard.read_hotkey(suppress=False)
            except (KeyboardInterrupt, Exception):
                hotkey = current_hotkey

            if not hotkey or hotkey.lower() in {"esc", "escape"}:
                hotkey = current_hotkey

            self.after(0, lambda: self._finish_record(hotkey))

        threading.Thread(target=capture, daemon=True).start()

    def _finish_record(self, hotkey: str):
        """Update the UI after hotkey capture completes."""
        self._recording = False
        self._hotkey_entry.configure(state="normal")
        self._hotkey_var.set(hotkey)
        self._hotkey_entry.configure(state="readonly")
        self._record_btn.configure(text="Record", state="normal")
        messagebox.showinfo("Hotkey captured", f"Hotkey: {hotkey}", parent=self)

    def _save(self):
        """Validate and save settings."""
        if IS_MACOS:
            hotkey = self._current_hotkey()
            try:
                mac_keycodes.parse(hotkey)
            except ValueError as e:
                messagebox.showwarning("Warning", str(e), parent=self)
                return
        else:
            hotkey = self._hotkey_var.get().strip()
            if not hotkey or "Press keys" in hotkey:
                messagebox.showwarning(
                    "Warning", "Please record a hotkey first.", parent=self
                )
                return

        on_icon = self._on_icon_var.get().strip()
        off_icon = self._off_icon_var.get().strip()
        if on_icon and not os.path.isfile(on_icon):
            messagebox.showwarning(
                "Warning",
                f"Unmuted icon file does not exist:\n{on_icon}",
                parent=self,
            )
            return
        if off_icon and not os.path.isfile(off_icon):
            messagebox.showwarning(
                "Warning",
                f"Muted icon file does not exist:\n{off_icon}",
                parent=self,
            )
            return

        on_sound = self._on_sound_var.get().strip()
        off_sound = self._off_sound_var.get().strip()
        if on_sound and not os.path.isfile(on_sound):
            messagebox.showwarning(
                "Warning",
                f"Unmute sound file does not exist:\n{on_sound}",
                parent=self,
            )
            return
        if off_sound and not os.path.isfile(off_sound):
            messagebox.showwarning(
                "Warning",
                f"Mute sound file does not exist:\n{off_sound}",
                parent=self,
            )
            return

        try:
            self._config.set("hotkey", hotkey)
            self._config.set("mic_on_icon", on_icon or None)
            self._config.set("mic_off_icon", off_icon or None)
            self._config.set("mic_on_sound", on_sound or None)
            self._config.set("mic_off_sound", off_sound or None)

            if self._autostart_var.get():
                startup_manager.enable()
            else:
                startup_manager.disable()

            self._config.set("autostart", self._autostart_var.get())

            messagebox.showinfo("Saved", "Settings saved.", parent=self)
            self._close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings:\n{e}", parent=self)

    def _cancel(self):
        if self._recording:
            self._recording = False
        self._close()

    def _close(self):
        if self._on_close:
            self._on_close()
        self.destroy()

    def _center(self):
        self.update_idletasks()
        width, height = self.winfo_width(), self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"+{(screen_width - width) // 2}+{(screen_height - height) // 2}")
