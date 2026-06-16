# Mic Mute Tray

Mic Mute Tray is a small Windows tray utility for toggling the default
microphone mute state with a global hotkey. It shows the current microphone
state in the system tray and can play a short sound when the state changes.

The former working name was `MicInAndOut`. The public project name is now
`Mic Mute Tray`, and the recommended GitHub repository slug is
`mic-mute-tray`.

## Features

- Toggle the default microphone mute state from a global hotkey.
- Default hotkey: `F13`.
- Tray icon changes between unmuted and muted states.
- Optional custom tray icons for each state.
- Optional custom WAV sound for mute and unmute actions.
- Optional startup registration for the current Windows user.
- Local JSON configuration.
- Bundled fallback icons and sounds are generated automatically when missing.

## Requirements

- Windows 10 or Windows 11.
- Python 3.10 or newer.
- A working microphone input device.
- Python packages listed in `requirements.txt`.

This app uses Windows audio APIs through `pycaw` and `comtypes`, so it is not
intended for macOS or Linux.

## Download

After this project is published on GitHub, users can get it in either way:

```powershell
git clone https://github.com/<your-user>/mic-mute-tray.git
cd mic-mute-tray
```

Or use GitHub's `Code` button, choose `Download ZIP`, extract the ZIP, and open
the extracted folder.

## Install

Run:

```bat
install.bat
```

Manual install:

```powershell
python -m pip install -r requirements.txt
```

Using a virtual environment is recommended for development:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Start

Run:

```bat
launch.bat
```

The app starts in the background and appears in the Windows system tray.

For troubleshooting, start it with a console so errors are visible:

```powershell
python main.py
```

## Usage

1. Start the app with `launch.bat`.
2. Press `F13` to toggle microphone mute.
3. Check the system tray icon for the current state.
4. Right-click the tray icon and choose `Settings` to change options.

## Settings

The settings window supports:

- Hotkey recording.
- Custom unmuted and muted tray icons (`.png`, `.ico`, `.bmp`).
- Custom unmute and mute sounds (`.wav`).
- Start with Windows.

When settings are saved, the app writes `config.json` in the project folder.
That file is local user data and is ignored by Git. Use
`config.example.json` as the clean reference file for the repository.

Example:

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

## Project Files

```text
main.py              Application entry point.
tray_app.py          System tray icon, menu, hotkey flow, and state refresh.
settings_window.py   Tkinter settings window.
mic_control.py       Windows microphone mute control.
config_manager.py    JSON config loading and saving.
hotkey_manager.py    Global hotkey registration.
sound_manager.py     Notification sound playback.
startup_manager.py   Windows startup registry helper.
asset_generator.py   Default icon and WAV asset generation.
assets/              Bundled default icons and sounds.
```

## Repository Hygiene

The repository is prepared to exclude local and generated files:

- `.venv/`
- `__pycache__/`
- `*.pyc`
- `config.json`
- build output
- local editor files
- local development notes

Before the first GitHub push, initialize Git if needed:

```powershell
git init
git add .
git status
git commit -m "Initial open-source release"
```

If a file such as `config.json` was already tracked before `.gitignore` was
added, remove it from the Git index without deleting the local file:

```powershell
git rm --cached config.json
```

## Troubleshooting

### The hotkey does not work

- Choose another hotkey in `Settings`.
- Avoid hotkeys already used by another app.
- Try running from a normal console with `python main.py` and check errors.

### The tray icon is missing

- Open the hidden icons area in the Windows taskbar.
- Restart the app.
- Reinstall dependencies with `python -m pip install -r requirements.txt`.

### The microphone state does not change

- Confirm Windows has a default input device.
- Check Windows privacy settings for microphone access.
- Confirm the input device is not disabled in Windows sound settings.

### Startup with Windows does not work

- Toggle `Start with Windows` off and on again in `Settings`.
- Confirm the app folder was not moved after enabling startup.
- Start once with `python main.py` to inspect errors.

## Development Verification

Run a syntax check before committing:

```powershell
python -m py_compile asset_generator.py config_manager.py hotkey_manager.py main.py mic_control.py settings_window.py sound_manager.py startup_manager.py tray_app.py
```

The app needs Windows tray and audio access for full manual testing.

## License

MIT License. See `LICENSE`.
