<p align="center">
  <img src="assets/mic_on.png" width="64" height="64" alt="Mic Mute Tray">
</p>

<h1 align="center">Mic Mute Tray</h1>

<p align="center">
  <b>English</b> | <a href="README.md">繁體中文</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Windows-10%20%7C%2011-brightgreen" alt="Windows">
  <img src="https://img.shields.io/badge/macOS-12%2B-black" alt="macOS">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
</p>

<p align="center">
  Lightweight tray and menu bar utility — toggle microphone mute with a global hotkey
</p>

---

## Features

- Toggle the default microphone mute state from a global hotkey
- Default hotkey: `F13` (ideal for custom keyboards)
- Tray / menu bar icon changes between unmuted and muted states
- Custom icons (`.png` / `.ico` / `.bmp`) for each state
- Custom WAV sound for mute and unmute actions
- Optional startup at login
- Local JSON configuration
- Bundled fallback icons and sounds are auto-generated when missing
- The icon follows along when the mute state is changed from System Settings or another app

## Platform Support

| | Windows | macOS |
|---|---|---|
| Microphone control | Core Audio API (`pycaw`) | Core Audio HAL (`ctypes`) |
| Global hotkey | `keyboard` package | Carbon `RegisterEventHotKey` |
| Tray / menu bar | `pystray` | `NSStatusItem` (AppKit) |
| Sound playback | `pygame` | `NSSound` |
| Start at login | Registry `HKCU\...\Run` | launchd LaunchAgent |
| Third-party dependencies | 6 packages | **None, standard library only** |

## Recommended for Custom Keyboard Users

This app is **lightweight** and designed for users with **custom mechanical
keyboards** (programmable via **QMK** / **VIA**). Assign an unused key like
`F13` to your keyboard through VIA, set the same hotkey in Mic Mute Tray,
and you get a dedicated hardware mute button with zero software conflicts.

Customize your experience:

- **Custom sounds** — replace default WAV files with your own
- **Custom icons** — use your own images to match your desktop theme
- **Custom hotkey** — pick any key combination in the settings window

## Requirements

**Common**

- Python 3.10 or newer
- A working microphone input device

**Windows**

- Windows 10 or Windows 11
- Python packages listed in `requirements.txt`

**macOS**

- macOS 12 Monterey or newer (the menu bar icons use SF Symbols)
- **No third-party packages required**
- The settings window needs Tkinter. The system `python3` and the
  python.org installers include it; **Homebrew's Python does not** unless
  you install the matching `python-tk` formula. Without it the menu bar
  icon and hotkey still work and only the settings window is unavailable,
  which the app reports with an alert.
- **No Accessibility permission required** — the global hotkey uses Carbon
  `RegisterEventHotKey`, the one system-wide hotkey API on macOS that works
  without granting access

## Download

Head to **[Releases](https://github.com/twcat0503/Mic-Mute-Tray/releases/latest)**. Every version ships two forms for each
platform, and **the two platforms are kept completely separate**.

### Standalone executables (no Python needed)

| Platform | File |
|---|---|
| Windows 10 / 11 | `MicMuteTray-windows-x64-vX.Y.Z.exe` |
| macOS (Apple Silicon) | `MicMuteTray-macos-arm64-vX.Y.Z.zip` |

> **macOS blocks the first launch**
>
> The app is not signed or notarized with an Apple Developer account, so
> Gatekeeper reports "cannot be opened because the developer cannot be
> verified". **Control-click the app in Finder and choose Open**, or run:
>
> ```bash
> xattr -d com.apple.quarantine "Mic Mute Tray.app"
> ```
>
> Removing the warning entirely requires an Apple Developer account
> ($99/year) to sign and notarize the bundle.

### Source archives (requires Python 3.10 or newer)

| Platform | File | Contents |
|---|---|---|
| Windows | `mic-mute-tray-windows-vX.Y.Z.zip` | Windows backend and `.bat` scripts only |
| macOS | `mic-mute-tray-macos-vX.Y.Z.zip` | macOS backend and `.sh` scripts only |

The Windows archive contains no `mac_*` files, and the macOS archive contains
no `win_*` files.

### From source

```bash
git clone https://github.com/twcat0503/Mic-Mute-Tray.git
cd Mic-Mute-Tray
```

Or click `Code` → `Download ZIP` on the GitHub page (that is the full source,
covering both platforms).

## Install

**Windows**

```bat
install.bat
```

Manual install:

```powershell
python -m pip install -r requirements.txt
```

**macOS**

```bash
./install.sh
```

Nothing needs to be installed on macOS; `install.sh` only checks the Python
version and that `tkinter` is available.

## Start

**Windows**

```bat
launch.bat
```

**macOS**

```bash
./launch.sh
```

The app starts in the background and appears in the Windows system tray or on
the right side of the macOS menu bar. On macOS it does not appear in the Dock.

For troubleshooting, run it directly from a terminal:

```bash
python3 main.py
```

## Usage

1. Run `launch.bat` (Windows) or `./launch.sh` (macOS) to start
2. Press `F13` (or your configured hotkey) to toggle microphone mute
3. Check the tray / menu bar icon for the current state
4. Click the icon → `Settings…` to change options

On macOS, clicking the menu bar icon opens a menu — as the Apple Human
Interface Guidelines prescribe for a menu bar extra — containing the current
state, `Toggle Mute`, `Settings…`, and `Quit`.

### Custom Keyboard Setup (VIA / QMK)

1. Open VIA and assign `F13` to a key on your keyboard
2. Flash the new keymap to your keyboard
3. Set the same key as the toggle hotkey in Mic Mute Tray's settings
4. Press that physical key anytime to toggle mute — no software conflict

## Settings

- **Hotkey** — on Windows, press any key combination to record it; on macOS,
  pick a key from the list and tick `⌃` `⌥` `⇧` `⌘`
- **Custom icons** — select `.png` / `.ico` / `.bmp` files
- **Custom sounds** — select `.wav` files
- **Start at login** — launch when you log in

Configuration file location:

- Windows: `config.json` in the app folder
- macOS: `~/Library/Application Support/Mic Mute Tray/config.json`

See `config.example.json` for defaults:

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

## macOS Design Notes

The macOS build follows Apple's Human Interface Guidelines:

- **Template images** — the default icons are the SF Symbols `mic.fill` and
  `mic.slash.fill`, which the system tints automatically so they read
  correctly on light and dark menu bars and while selected
- **A menu, not a popover** — clicking the icon opens a standard `NSMenu`
- **Menu bar agent** — the app sets
  `NSApplicationActivationPolicyAccessory` at runtime, so it takes no Dock
  space and creates no app menu
- **Configuration location** — stored under
  `~/Library/Application Support/`, where Apple expects per-user app data
- **Start at login** — a launchd agent in `~/Library/LaunchAgents`. Once
  enabled it appears under System Settings → General → Login Items → Allow in
  the Background

AppKit and Tkinter both insist on owning the main thread, so on macOS AppKit
owns the main loop and the settings window opens as a separate child process.
The resident menu bar agent therefore never loads Tkinter at all.

## Building the Downloads

`scripts/` holds the packaging script and the PyInstaller specs.

**Per-platform source archives** (runs anywhere):

```bash
python3 scripts/package.py --clean
# writes dist/mic-mute-tray-windows-vX.Y.Z.zip
#        dist/mic-mute-tray-macos-vX.Y.Z.zip
```

The script fails the build if either archive picks up the other platform's
files.

**macOS `.app`** (must run on macOS):

```bash
uvx --python "$(which python3)" --from pyinstaller pyinstaller \
  --noconfirm --distpath dist --workpath build/pyi scripts/macos.spec
```

**Windows `.exe`** (must run on Windows): install the dependencies and
`pyinstaller` via `install.bat` first, then:

```bat
pyinstaller --noconfirm --distpath dist --workpath build/pyi scripts/windows.spec
```

PyInstaller cannot cross-compile, so `.github/workflows/release.yml` builds
each platform on its own GitHub Actions runner when a `v*` tag is pushed, then
gathers everything into one draft release.

## Project Structure

```text
main.py               Application entry point and platform dispatch
config_manager.py     JSON config loading and saving
asset_generator.py    Default icon and WAV generator, asset path resolution
settings_window.py    Settings window (Tkinter)

mic_control.py        Microphone control — platform dispatch
hotkey_manager.py     Global hotkey — platform dispatch
sound_manager.py      Notification sounds — platform dispatch
startup_manager.py    Start at login — platform dispatch

win_tray_app.py       Windows system tray (pystray)
win_mic_control.py    Windows microphone control (pycaw)
win_hotkey.py         Windows global hotkey (keyboard)
win_sound.py          Windows sound playback (pygame)
win_startup.py        Windows startup registry helper

mac_app.py            macOS menu bar agent (NSStatusItem)
mac_objc.py           ctypes bridge to the Objective-C runtime and AppKit
mac_mic_control.py    macOS microphone control (Core Audio HAL)
mac_hotkey.py         macOS global hotkey (Carbon RegisterEventHotKey)
mac_keycodes.py       Hotkey string to macOS virtual key code translation
mac_sound.py          macOS sound playback (NSSound)
mac_startup.py        macOS login item (launchd LaunchAgent)

assets/               Bundled default icons and sounds
scripts/              Packaging script and PyInstaller specs
.github/workflows/    Release CI (per-platform builds)
```

## Troubleshooting

### Hotkey does not work

- Choose another hotkey in `Settings`
- Avoid hotkeys already used by another app
- macOS: if the combination is already registered by the system or another
  app, `RegisterEventHotKey` fails and a warning is printed to the terminal
- Run `python3 main.py` to check for errors

### Icon is missing

- Windows: check the hidden icons area in the taskbar
- macOS: the system hides menu bar extras when space runs short; quit another
  menu bar app to make room
- Restart the app

### Microphone state does not change

- Confirm the system has a default input device
- Windows: check privacy settings for microphone access
- macOS: some external audio interfaces expose no mute property; the app then
  drives the input volume to zero instead and restores the previous level on
  unmute
- Confirm the input device is not disabled

### The settings window does not open

- Usually the Python running the app has no Tkinter, most often a
  Homebrew Python
- `./install.sh` checks for this and says what is missing
- Install the matching `python-tk` formula, or run the app with the
  system `python3`
- The standalone `.app` download is unaffected; it bundles Tkinter

### Start at login does not work

- Toggle the option off and on again in `Settings`
- Confirm the app folder was not moved after enabling
- macOS: check System Settings → General → Login Items and confirm Mic Mute
  Tray is allowed to run in the background
- Run `python3 main.py` to inspect errors

## License

MIT License. See [LICENSE](LICENSE).
