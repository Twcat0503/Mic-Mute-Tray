# PyInstaller spec for the Windows tray app.
# Build:  pyinstaller scripts/windows.spec
import os

ROOT = os.path.abspath(os.path.join(SPECPATH, ".."))

with open(os.path.join(ROOT, "VERSION"), encoding="utf-8") as fh:
    VERSION = fh.read().strip()

a = Analysis(
    [os.path.join(ROOT, "main.py")],
    pathex=[ROOT],
    binaries=[],
    datas=[(os.path.join(ROOT, "assets"), "assets")],
    # Reached through lazy imports and platform dispatch.
    hiddenimports=[
        "win_tray_app", "win_mic_control", "win_hotkey", "win_sound",
        "win_startup", "pystray._win32",
        "tkinter", "tkinter.ttk", "tkinter.filedialog", "tkinter.messagebox",
    ],
    hookspath=[],
    runtime_hooks=[],
    # The macOS backend never loads on Windows.
    excludes=[
        "mac_app", "mac_objc", "mac_mic_control", "mac_hotkey",
        "mac_keycodes", "mac_sound", "mac_startup", "numpy", "pytest",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

# One file keeps the download to a single .exe, matching how the batch
# scripts present the app today.
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="MicMuteTray",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=False,
    icon=os.path.join(ROOT, "assets", "mic_on.png"),
    version_file=None,
)
