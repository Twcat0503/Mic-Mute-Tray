# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.0.0] - 2026-08-26

First tagged release. Ships both platforms and downloadable builds.

### Added

- **macOS support.** The app runs as a menu bar agent with no Dock icon,
  built entirely on the standard library:
  - Microphone mute through the Core Audio HAL, with a fallback to driving
    input volume to zero for devices that expose no mute property
  - Global hotkey through the Carbon `RegisterEventHotKey` API, which needs
    no Accessibility permission
  - `NSStatusItem` menu bar extra using the SF Symbols `mic.fill` and
    `mic.slash.fill` as template images, so it tracks light and dark menu bars
  - Notification sounds through `NSSound`
  - Start at login through a launchd agent in `~/Library/LaunchAgents`
  - Configuration stored in `~/Library/Application Support/Mic Mute Tray/`
- The icon now follows mute changes made outside the app, such as from the
  system's own sound settings or another application.
- `install.sh` and `launch.sh` for macOS.
- Per-platform downloads on GitHub Releases: a source archive and a
  standalone build for each of Windows and macOS. The two platforms' files
  are kept entirely separate.
- `scripts/package.py` to build the source archives, which fails the build if
  either archive picks up the other platform's files.
- `.github/workflows/release.yml` to build every artifact on its own runner
  when a `v*` tag is pushed.

### Changed

- Platform-specific code moved into `win_*` and `mac_*` modules. The modules
  named after each feature are now thin dispatchers that select a backend, so
  `pycaw` never loads on macOS and AppKit is never touched on Windows.
- `requirements.txt` marks every package as Windows-only. macOS installs
  nothing.
- Pillow is optional; it is only needed to generate the default Windows tray
  icons.

### Notes

- The settings window needs Tkinter. Homebrew's Python omits it unless
  the `python-tk` formula is installed; the app detects this and says so
  instead of failing silently. The menu bar agent itself never loads
  Tkinter, so the icon and hotkey work either way.

- The macOS build is not signed or notarized, so Gatekeeper blocks the first
  launch of the standalone app. See the README for how to open it.
- On macOS the settings dialog opens as a separate process, because AppKit and
  Tkinter cannot share a main thread. The resident agent never loads Tkinter.

[Unreleased]: https://github.com/twcat0503/Mic-Mute-Tray/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/twcat0503/Mic-Mute-Tray/releases/tag/v1.0.0
