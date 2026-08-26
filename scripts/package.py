"""Build the per-platform source archives published on GitHub Releases.

Each archive holds only the files its platform runs, so a Windows download
carries no macOS backend and a macOS download carries no Windows backend.
"""

import argparse
import os
import shutil
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")

# Modules both front ends load, including the dispatchers that pick a backend.
SHARED = [
    "main.py",
    "config_manager.py",
    "asset_generator.py",
    "settings_window.py",
    "mic_control.py",
    "hotkey_manager.py",
    "sound_manager.py",
    "startup_manager.py",
    "config.example.json",
    "README.md",
    "README.en.md",
    "LICENSE",
    "VERSION",
]

PLATFORMS = {
    "windows": {
        "files": SHARED + [
            "win_tray_app.py",
            "win_mic_control.py",
            "win_hotkey.py",
            "win_sound.py",
            "win_startup.py",
            "install.bat",
            "launch.bat",
            "requirements.txt",
        ],
        # A file matching this prefix must never reach the other platform's zip.
        "forbidden_prefix": "mac_",
    },
    "macos": {
        "files": SHARED + [
            "mac_app.py",
            "mac_objc.py",
            "mac_mic_control.py",
            "mac_hotkey.py",
            "mac_keycodes.py",
            "mac_sound.py",
            "mac_startup.py",
            "install.sh",
            "launch.sh",
        ],
        "forbidden_prefix": "win_",
    },
}

ASSET_DIR = "assets"


def read_version() -> str:
    with open(os.path.join(ROOT, "VERSION"), "r", encoding="utf-8") as fh:
        return fh.read().strip()


def build(platform: str, version: str) -> str:
    """Write one platform archive and return its path."""
    spec = PLATFORMS[platform]
    name = f"mic-mute-tray-{platform}-v{version}"
    archive = os.path.join(DIST, f"{name}.zip")

    missing = [f for f in spec["files"] if not os.path.exists(os.path.join(ROOT, f))]
    if missing:
        raise SystemExit(f"[package] Missing files for {platform}: {missing}")

    os.makedirs(DIST, exist_ok=True)
    if os.path.exists(archive):
        os.remove(archive)

    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
        for relative in spec["files"]:
            zf.write(os.path.join(ROOT, relative), os.path.join(name, relative))

        asset_root = os.path.join(ROOT, ASSET_DIR)
        for entry in sorted(os.listdir(asset_root)):
            path = os.path.join(asset_root, entry)
            if os.path.isfile(path):
                zf.write(path, os.path.join(name, ASSET_DIR, entry))

        # launch.sh and install.sh must stay executable after unzipping.
        if platform == "macos":
            for info in zf.infolist():
                if info.filename.endswith(".sh"):
                    info.external_attr = (0o755 << 16) | (info.external_attr & 0xFFFF)

    return archive


def verify(archive: str, platform: str):
    """Fail loudly if an archive leaked the other platform's backend."""
    forbidden = PLATFORMS[platform]["forbidden_prefix"]
    with zipfile.ZipFile(archive) as zf:
        names = zf.namelist()

    leaked = [n for n in names if os.path.basename(n).startswith(forbidden)]
    if leaked:
        raise SystemExit(f"[package] {platform} archive leaked {forbidden}* files: {leaked}")

    for required in ("main.py", f"{ASSET_DIR}/mic_on.png", "LICENSE"):
        if not any(n.endswith(required) for n in names):
            raise SystemExit(f"[package] {platform} archive is missing {required}")

    print(f"[package] {os.path.basename(archive)}")
    print(f"           {len(names)} entries, {os.path.getsize(archive) / 1024:.0f} KB")
    print(f"           no {forbidden}* files present")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", default=None, help="defaults to the VERSION file")
    parser.add_argument(
        "--platform",
        choices=[*PLATFORMS, "all"],
        default="all",
    )
    parser.add_argument("--clean", action="store_true", help="empty dist/ first")
    args = parser.parse_args()

    version = args.version or read_version()
    if args.clean and os.path.isdir(DIST):
        shutil.rmtree(DIST)

    targets = list(PLATFORMS) if args.platform == "all" else [args.platform]
    for platform in targets:
        verify(build(platform, version), platform)
    return 0


if __name__ == "__main__":
    sys.exit(main())
