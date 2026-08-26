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

"$PYTHON" - <<'PY'
import tkinter  # noqa: F401
print("[Mic Mute Tray] tkinter OK")
PY

echo "[Mic Mute Tray] No third-party packages are needed on macOS."
echo "[Mic Mute Tray] Run ./launch.sh to start the app."
