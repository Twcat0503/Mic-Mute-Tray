"""Check that the packaged Windows app can load its Tk and runtime modules."""

import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    executable = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else root / "dist" / f"MicMuteTray-windows-x64-v{version}.exe"
    )
    if not executable.is_file():
        raise FileNotFoundError(executable)

    result = subprocess.run(
        [str(executable), "--check-windows-bundle"], timeout=30, check=False
    )
    if result.returncode:
        raise RuntimeError(f"Packaged app check failed (code {result.returncode})")
    print("Packaged app loaded Tk and Windows runtime modules.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
