#!/bin/bash
# Mic Mute Tray - macOS setup check.
set -e
cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"

if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "[Mic Mute Tray] python3 was not found. Install Python 3.10 or newer."
  exit 1
fi

"$PYTHON" - <<'PY'
import sys
if sys.version_info < (3, 10):
    sys.exit(f"[Mic Mute Tray] Python 3.10 or newer is required (found {sys.version.split()[0]}).")
print(f"[Mic Mute Tray] Python {sys.version.split()[0]} OK")
PY

# The menu bar agent never loads Tkinter, but the settings dialog is a Tk
# window. Homebrew's Python omits it unless the python-tk formula is
# installed, so say what to do rather than letting the dialog fail later.
if "$PYTHON" -c "import tkinter" >/dev/null 2>&1; then
  echo "[Mic Mute Tray] tkinter OK"
else
  echo "[Mic Mute Tray] WARNING: this Python has no Tkinter."
  echo "[Mic Mute Tray] The menu bar icon and the hotkey will work, but the"
  echo "[Mic Mute Tray] settings window cannot open."
  echo "[Mic Mute Tray] Using Homebrew? Install the matching formula, e.g.:"
  echo "[Mic Mute Tray]     brew install python-tk@3.13"
  echo "[Mic Mute Tray] Interpreter: $("$PYTHON" -c 'import sys; print(sys.executable)')"
fi

echo "[Mic Mute Tray] No third-party packages are needed on macOS."
echo "[Mic Mute Tray] Run ./launch.sh to start the app."
