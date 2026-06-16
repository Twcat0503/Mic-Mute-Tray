"""Application entry point."""

import sys
import threading
import tkinter as tk


try:
    import ctypes

    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass


def main():
    """Start the hidden Tk root window and the system tray app."""
    try:
        root = tk.Tk()
        root.withdraw()
        root.wm_attributes("-toolwindow", True)
        root.title("Mic Mute Tray")

        from tray_app import TrayApp

        app = TrayApp(root)

        tray_thread = threading.Thread(target=app.run, daemon=True, name="pystray")
        tray_thread.start()

        try:
            root.mainloop()
        except KeyboardInterrupt:
            pass
    except Exception as e:
        try:
            import tkinter.messagebox as mb

            root_err = tk.Tk()
            root_err.withdraw()
            mb.showerror("Startup Error", f"Failed to start Mic Mute Tray:\n{e}")
            root_err.destroy()
        except Exception:
            print(f"[ERROR] Startup failed: {e}", file=sys.stderr)
        return False
    return True


if __name__ == "__main__":
    main()
