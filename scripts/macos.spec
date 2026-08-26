# PyInstaller spec for the macOS menu bar agent.
# Build:  uvx --python "$(which python3)" --from pyinstaller pyinstaller scripts/macos.spec
import os

ROOT = os.path.abspath(os.path.join(SPECPATH, ".."))

with open(os.path.join(ROOT, "VERSION"), encoding="utf-8") as fh:
    VERSION = fh.read().strip()

a = Analysis(
    [os.path.join(ROOT, "main.py")],
    pathex=[ROOT],
    binaries=[],
    datas=[(os.path.join(ROOT, "assets"), "assets")],
    # These are reached through lazy imports and platform dispatch, so the
    # static analysis needs them spelled out.
    hiddenimports=[
        "mac_app", "mac_objc", "mac_mic_control", "mac_hotkey",
        "mac_keycodes", "mac_sound", "mac_startup",
        "tkinter", "tkinter.ttk", "tkinter.filedialog", "tkinter.messagebox",
    ],
    hookspath=[],
    runtime_hooks=[],
    # The Windows backend and its dependencies never load on macOS.
    excludes=[
        "win_tray_app", "win_mic_control", "win_hotkey", "win_sound",
        "win_startup", "pystray", "PIL", "pygame", "keyboard", "pycaw",
        "comtypes", "numpy", "pytest",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Mic Mute Tray",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="Mic Mute Tray",
)

app = BUNDLE(
    coll,
    name="Mic Mute Tray.app",
    icon=None,
    bundle_identifier="com.micmutetray.app",
    version=VERSION,
    info_plist={
        # A menu bar extra has no Dock icon and no app menu.
        "LSUIElement": True,
        "LSMinimumSystemVersion": "12.0",
        "CFBundleName": "Mic Mute Tray",
        "CFBundleDisplayName": "Mic Mute Tray",
        "CFBundleShortVersionString": VERSION,
        "CFBundleVersion": VERSION,
        "NSHumanReadableCopyright": "MIT License",
        # The app only flips a Core Audio mute property and never records,
        # but the description is declared in case the API is ever gated.
        "NSMicrophoneUsageDescription":
            "Mic Mute Tray toggles the mute state of your input device.",
        "NSHighResolutionCapable": True,
    },
)
