"""Login item registration through a launchd user agent.

A LaunchAgent in `~/Library/LaunchAgents` is the supported way for an app that
is not a signed bundle to start at login. macOS lists it under System Settings
> General > Login Items > Allow in the Background.
"""

import os
import plistlib
import subprocess
import sys

APP_NAME = "Mic Mute Tray"
LABEL = "com.micmutetray.agent"

_AGENTS_DIR = os.path.expanduser("~/Library/LaunchAgents")
PLIST_PATH = os.path.join(_AGENTS_DIR, f"{LABEL}.plist")


def _script_path() -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")


def _program_arguments() -> list:
    """Return the argv launchd should run at login."""
    if getattr(sys, "frozen", False):
        return [sys.executable]
    return [sys.executable, _script_path()]


def _launchctl(*args) -> bool:
    """Run launchctl, returning True on success."""
    try:
        result = subprocess.run(
            ["launchctl", *args],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def is_enabled() -> bool:
    """Return True when the login item is installed."""
    return os.path.isfile(PLIST_PATH)


def enable(exe_path=None):
    """Install and load the launchd agent for the current user."""
    try:
        os.makedirs(_AGENTS_DIR, exist_ok=True)
        plist = {
            "Label": LABEL,
            "ProgramArguments": _program_arguments(),
            "RunAtLoad": True,
            # Aqua-only keeps the agent out of ssh and other non-GUI sessions,
            # where a menu bar extra makes no sense.
            "LimitLoadToSessionType": "Aqua",
            "ProcessType": "Interactive",
        }
        with open(PLIST_PATH, "wb") as fh:
            plistlib.dump(plist, fh)

        domain = f"gui/{os.getuid()}"
        _launchctl("bootout", f"{domain}/{LABEL}")
        if not _launchctl("bootstrap", domain, PLIST_PATH):
            # Older syntax as a fallback; the agent still loads at next login.
            _launchctl("load", "-w", PLIST_PATH)
    except OSError as e:
        print(f"[WARN] Failed to enable login item: {e}")


def disable():
    """Unload and remove the launchd agent."""
    domain = f"gui/{os.getuid()}"
    if not _launchctl("bootout", f"{domain}/{LABEL}"):
        _launchctl("unload", "-w", PLIST_PATH)
    try:
        if os.path.isfile(PLIST_PATH):
            os.remove(PLIST_PATH)
    except OSError as e:
        print(f"[WARN] Failed to remove login item: {e}")
