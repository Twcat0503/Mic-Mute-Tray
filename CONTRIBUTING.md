# Contributing

Thanks for taking an interest in Mic Mute Tray. This is a small utility, so
the process is deliberately light.

## Reporting a problem

Open an issue and include:

- Your OS and version (e.g. Windows 11 23H2, macOS 15.2)
- Your Python version (`python3 --version`)
- The output of running the app from a terminal: `python3 main.py`
- Your input device, if the problem involves muting

## Project layout

The app runs on Windows and macOS from one source tree. Platform code lives in
files prefixed `win_` and `mac_`, and the modules named after the feature are
thin dispatchers that pick a backend at import time:

```text
mic_control.py  ->  win_mic_control.py  |  mac_mic_control.py
hotkey_manager.py -> win_hotkey.py      |  mac_hotkey.py
sound_manager.py  -> win_sound.py       |  mac_sound.py
startup_manager.py-> win_startup.py     |  mac_startup.py
```

`config_manager.py`, `asset_generator.py`, and `settings_window.py` are shared.
`win_tray_app.py` and `mac_app.py` are the two front ends.

When you add a feature, put the platform-specific half in the `win_`/`mac_`
file and keep the shared half in the dispatcher or a shared module. Do not let
one platform's imports run on the other — the dispatchers exist so that
`pycaw` is never imported on macOS and AppKit is never touched on Windows.

## Running from source

```bash
python3 main.py          # runs the tray app / menu bar agent
python3 main.py --settings   # opens just the settings dialog
```

macOS needs no third-party packages. Windows needs the packages in
`requirements.txt`; `install.bat` sets them up.

## Style

- Follow the surrounding code: 4-space indent, double quotes, type hints where
  the existing code uses them, and a short docstring on public functions.
- Comments explain *why*, not *what*. The `mac_objc.py` bridge and the Core
  Audio code are the places where a comment usually earns its keep.
- Identifiers, comments, log messages, and commit messages are in English.
- Keep the app lightweight. New runtime dependencies need a reason that
  explains why the standard library and the platform APIs are not enough.

## Commits

Use [Conventional Commits](https://www.conventionalcommits.org/):

```text
feat: add mute state polling for external changes
fix: retain autoreleased NSImage before caching it
docs: document the macOS Gatekeeper prompt
```

Keep one concern per commit.

## Testing

There is no automated test suite. Before opening a pull request, check by hand
on the platform you changed:

1. The tray / menu bar icon appears and switches between both states
2. The global hotkey toggles mute
3. The settings dialog opens, saves, and the new hotkey takes effect
4. Start at login can be turned on and off
5. Changing mute from the system's own sound settings updates the icon

If you touched packaging, run `python3 scripts/package.py --clean` — it fails
the build if either archive picks up the other platform's files.

## Releases

Maintainers only: bump `VERSION`, then push a `v*` tag. The workflow in
`.github/workflows/release.yml` builds the source archives, the macOS app
bundle, and the Windows executable on their own runners, then opens a draft
release to review before publishing.
