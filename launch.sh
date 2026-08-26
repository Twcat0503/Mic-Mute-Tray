#!/bin/bash
# Mic Mute Tray - start the menu bar agent in the background.
cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"
SCRIPT="$(pwd)/main.py"

# Launch with the absolute path so this check can tell our agent apart from
# any other main.py running on the machine.
if pgrep -f "$SCRIPT" >/dev/null 2>&1; then
  echo "[Mic Mute Tray] Already running."
  exit 0
fi

nohup "$PYTHON" "$SCRIPT" >/dev/null 2>&1 &
echo "[Mic Mute Tray] Started. Look for the microphone icon in the menu bar."
