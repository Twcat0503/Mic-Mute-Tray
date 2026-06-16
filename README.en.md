<p align="center">
  <img src="assets/mic_on.png" width="64" height="64" alt="Mic Mute Tray">
</p>

<h1 align="center">Mic Mute Tray</h1>

<p align="center">
  <b>English</b> | <a href="README.md">繁體中文</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Windows-10%20%7C%2011-brightgreen" alt="Windows">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
</p>

<p align="center">
  Lightweight Windows tray utility — toggle microphone mute with a global hotkey
</p>

---

## Features

- Toggle the default microphone mute state from a global hotkey
- Default hotkey: `F13` (ideal for custom keyboards)
- Tray icon changes between unmuted and muted states
- Custom tray icons (`.png` / `.ico` / `.bmp`) for each state
- Custom WAV sound for mute and unmute actions
- Optional startup with Windows
- Local JSON configuration
- Bundled fallback icons and sounds are auto-generated when missing

## Recommended for Custom Keyboard Users

This app is **lightweight** and designed for users with **custom mechanical
keyboards** (programmable via **QMK** / **VIA**). Assign an unused key like
`F13` to your keyboard through VIA, set the same hotkey in Mic Mute Tray,
and you get a dedicated hardware mute button with zero software conflicts.

Customize your experience:

- **Custom sounds** — replace default WAV files with your own
- **Custom tray icons** — use your own images to match your desktop theme
- **Custom hotkey** — record any key combination in the settings window

## Requirements

- Windows 10 or Windows 11
- Python 3.10 or newer
- A working microphone input device
- Python packages listed in `requirements.txt`

This app uses Windows audio APIs (`pycaw` + `comtypes`), so it is not
intended for macOS or Linux.

## Download

```powershell
git clone https://github.com/<your-user>/mic-mute-tray.git
cd mic-mute-tray
```

Or click `Code` → `Download ZIP` on the GitHub page, extract, and open the
folder.

## Install

```bat
install.bat
```

Manual install:

```powershell
python -m pip install -r requirements.txt
```

A virtual environment is recommended for development:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Start

```bat
launch.bat
```

The app starts in the background and appears in the Windows system tray.
For troubleshooting, run from a terminal:

```powershell
python main.py
```

## Usage

1. Run `launch.bat` to start
2. Press `F13` (or your configured hotkey) to toggle microphone mute
3. Check the system tray icon for the current state
4. Right-click the tray icon → `Settings` to change options

### Custom Keyboard Setup (VIA / QMK)

1. Open VIA and assign `F13` to a key on your keyboard
2. Flash the new keymap to your keyboard
3. Set the same key as the toggle hotkey in Mic Mute Tray's settings
4. Press that physical key anytime to toggle mute — no software conflict

## Settings

- **Hotkey recording** — press any key combination to capture it
- **Custom icons** — select `.png` / `.ico` / `.bmp` files
- **Custom sounds** — select `.wav` files
- **Auto-start** — launch on Windows login

Settings are saved in `config.json`. See `config.example.json` for defaults:

```json
{
  "hotkey": "F13",
  "mic_on_icon": null,
  "mic_off_icon": null,
  "mic_on_sound": null,
  "mic_off_sound": null,
  "autostart": false
}
```

## Project Structure

```text
main.py               Application entry point
tray_app.py           Tray icon, menu, hotkey flow, and state refresh
settings_window.py    Settings window (Tkinter)
mic_control.py        Windows microphone mute control
config_manager.py     JSON config loading and saving
hotkey_manager.py     Global hotkey registration
sound_manager.py      Notification sound playback
startup_manager.py    Windows startup registry helper
asset_generator.py    Default icon and WAV asset generator
assets/               Bundled default icons and sounds
```

## Troubleshooting

### Hotkey does not work

- Choose another hotkey in `Settings`
- Avoid hotkeys already used by another app
- Run `python main.py` to check for errors

### Tray icon is missing

- Check the hidden icons area in the Windows taskbar
- Restart the app
- Reinstall dependencies: `python -m pip install -r requirements.txt`

### Microphone state does not change

- Confirm Windows has a default input device
- Check Windows privacy settings for microphone access
- Confirm the input device is not disabled in sound settings

### Startup with Windows does not work

- Toggle `Start with Windows` off and on again in `Settings`
- Confirm the app folder was not moved after enabling
- Run `python main.py` to inspect errors

## License

MIT License. See [LICENSE](LICENSE).
