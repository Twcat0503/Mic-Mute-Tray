"""Collect build-environment license files for standalone release artifacts."""

import argparse
import importlib.metadata
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIRED = {
    "windows": {"pycaw", "pystray", "pillow", "keyboard", "comtypes"},
    "macos": {"pyinstaller"},
}


def _license_files(distribution):
    """Return files that carry a package's license or copyright notice."""
    for relative in distribution.files or ():
        name = Path(str(relative)).name.upper()
        if name.startswith(("LICENSE", "LICENCE", "COPYING", "NOTICE")):
            path = Path(distribution.locate_file(relative))
            if path.is_file():
                yield relative, path


def build(platform: str) -> Path:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    output = ROOT / "dist" / f"MicMuteTray-{platform}-licenses-v{version}.zip"
    output.parent.mkdir(exist_ok=True)
    manifest = [
        f"Mic Mute Tray {version} - {platform} build license files",
        "Package versions and license texts come from the build environment.",
        "The project source license is included at MicMuteTray/LICENSE.",
        "",
    ]
    seen = set()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.write(ROOT / "LICENSE", "MicMuteTray/LICENSE")
        archive.write(ROOT / "THIRD_PARTY_NOTICES.md", "THIRD_PARTY_NOTICES.md")
        for distribution in sorted(
            importlib.metadata.distributions(),
            key=lambda item: (item.metadata["Name"] or "").lower(),
        ):
            name = distribution.metadata["Name"] or "unknown"
            safe_name = re.sub(r"[^A-Za-z0-9_.-]", "-", name)
            files = list(_license_files(distribution))
            if not files:
                continue
            seen.add(name.lower())
            manifest.append(f"{name} {distribution.version}")
            for relative, path in files:
                # Keep only the path inside dist-info, never the local build path.
                parts = Path(str(relative)).parts
                inner = "/".join(parts[1:]) if len(parts) > 1 else parts[0]
                archive.write(
                    path, f"packages/{safe_name}-{distribution.version}/{inner}"
                )

        missing = REQUIRED[platform] - seen
        if missing:
            raise RuntimeError(f"Missing required dependency licenses: {sorted(missing)}")

        python_license = next(
            (path for name in ("LICENSE.txt", "LICENSE", "LICENSE.md")
             if (path := Path(sys.base_prefix) / name).is_file()),
            ROOT / "licenses" / "CPython-LICENSE.txt",
        )
        if python_license.is_file():
            archive.write(python_license, "CPython/LICENSE.txt")
            manifest.append(f"CPython {sys.version.split()[0]}")
        else:
            raise RuntimeError("CPython license file was not found in the build environment")

        archive.writestr("MANIFEST.txt", "\n".join(manifest) + "\n")
    print(f"[licenses] {output.name}: {len(seen)} packages")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platform", choices=sorted(REQUIRED), required=True)
    args = parser.parse_args()
    build(args.platform)


if __name__ == "__main__":
    main()
