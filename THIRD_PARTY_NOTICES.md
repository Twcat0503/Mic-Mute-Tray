# Third-party notices

Mic Mute Tray's own source code is licensed under MIT; see [LICENSE](LICENSE).
Standalone downloads also bundle Python and other components that retain their
own licenses. Each release provides a `MicMuteTray-<platform>-licenses-vX.Y.Z.zip`
archive containing the license files and exact package versions collected from
the corresponding build environment.

The Windows runtime uses these direct dependencies:

| Component | License | Upstream source |
|---|---|---|
| pycaw | MIT | [AndreMiras/pycaw](https://github.com/AndreMiras/pycaw) |
| pystray | LGPL-3.0 | [moses-palmer/pystray](https://github.com/moses-palmer/pystray) |
| Pillow | MIT-CMU | [python-pillow/Pillow](https://github.com/python-pillow/Pillow) |
| keyboard | MIT | [boppreh/keyboard](https://github.com/boppreh/keyboard) |
| comtypes | MIT | [enthought/comtypes](https://github.com/enthought/comtypes) |

The Windows license archive also covers installed transitive packages such as
`six`, `psutil`, and `pywin32-ctypes`. The standalone builds include CPython and
the PyInstaller bootloader. Their license files are included in the platform
license archives. The archive contents are generated from installed packages
at build time, so they reflect the versions used for that release.
