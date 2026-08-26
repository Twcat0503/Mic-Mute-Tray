"""Application entry point."""

import sys


def _report_startup_error(error: Exception) -> bool:
    """Show a dialog when startup fails, falling back to stderr."""
    try:
        import tkinter as tk
        import tkinter.messagebox as mb

        root_err = tk.Tk()
        root_err.withdraw()
        mb.showerror("Startup Error", f"Failed to start Mic Mute Tray:\n{error}")
        root_err.destroy()
    except Exception:
        print(f"[ERROR] Startup failed: {error}", file=sys.stderr)
    return False


def run_settings() -> bool:
    """Open the settings dialog on its own.

    The macOS menu bar agent runs this as a child process: AppKit owns the
    main thread there, and Tk needs a main loop of its own.
    """
    import tkinter as tk

    from config_manager import ConfigManager
    from settings_window import SettingsWindow

    root = tk.Tk()
    root.withdraw()

    if sys.platform == "darwin":
        import mac_objc

        mac_objc.activate_app()

    SettingsWindow(root, ConfigManager(), None, on_close=root.quit)
    root.mainloop()
    try:
        root.destroy()
    except tk.TclError:
        pass
    return True


def run_macos() -> bool:
    """Run the macOS menu bar agent."""
    from mac_app import MenuBarApp

    MenuBarApp().run()
    return True


def run_windows() -> bool:
    """Start the hidden Tk root window and the system tray app."""
    import threading
    import tkinter as tk

    try:
        import ctypes

        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    root = tk.Tk()
    root.withdraw()
    root.wm_attributes("-toolwindow", True)
    root.title("Mic Mute Tray")

    from win_tray_app import TrayApp

    app = TrayApp(root)

    tray_thread = threading.Thread(target=app.run, daemon=True, name="pystray")
    tray_thread.start()

    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
    return True


def main():
    """Dispatch to the settings dialog or the platform's tray front end."""
    try:
        if "--settings" in sys.argv:
            return run_settings()
        if sys.platform == "darwin":
            return run_macos()
        if sys.platform == "win32":
            return run_windows()
        raise RuntimeError(
            f"Mic Mute Tray supports Windows and macOS; {sys.platform} is not supported."
        )
    except Exception as e:
        return _report_startup_error(e)


if __name__ == "__main__":
    main()
