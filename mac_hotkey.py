"""Global hotkey registration through the Carbon hot key API.

`RegisterEventHotKey` is the only system-wide hotkey mechanism on macOS that
does not require Accessibility permission, so the app works the moment it is
launched instead of sending the user to System Settings first.
"""

import ctypes
from ctypes import CFUNCTYPE, POINTER, byref, c_uint32, c_void_p
from typing import Callable, Optional

import mac_keycodes

_carbon = ctypes.CDLL("/System/Library/Frameworks/Carbon.framework/Carbon")


def _fourcc(code: str) -> int:
    return int.from_bytes(code.encode("ascii"), "big")


kEventClassKeyboard = _fourcc("keyb")
kEventHotKeyPressed = 5
kEventParamDirectObject = _fourcc("----")
typeEventHotKeyID = _fourcc("hkid")
_SIGNATURE = _fourcc("MMTr")


class _EventHotKeyID(ctypes.Structure):
    _fields_ = [("signature", c_uint32), ("id", c_uint32)]


class _EventTypeSpec(ctypes.Structure):
    _fields_ = [("eventClass", c_uint32), ("eventKind", c_uint32)]


_HandlerProc = CFUNCTYPE(c_uint32, c_void_p, c_void_p, c_void_p)

_carbon.GetApplicationEventTarget.restype = c_void_p
_carbon.RegisterEventHotKey.argtypes = [
    c_uint32, c_uint32, _EventHotKeyID, c_void_p, c_uint32, POINTER(c_void_p),
]
_carbon.RegisterEventHotKey.restype = c_uint32
_carbon.UnregisterEventHotKey.argtypes = [c_void_p]
_carbon.UnregisterEventHotKey.restype = c_uint32
_carbon.InstallEventHandler.argtypes = [
    c_void_p, c_void_p, ctypes.c_ulong, POINTER(_EventTypeSpec), c_void_p,
    POINTER(c_void_p),
]
_carbon.InstallEventHandler.restype = c_uint32
_carbon.GetEventParameter.argtypes = [
    c_void_p, c_uint32, c_uint32, POINTER(c_uint32), c_uint32, POINTER(c_uint32),
    c_void_p,
]
_carbon.GetEventParameter.restype = c_uint32


class HotkeyManager:
    """Register one global hotkey at a time."""

    def __init__(self):
        self._hotkey: Optional[str] = None
        self._callback: Optional[Callable] = None
        self._hotkey_ref = c_void_p()
        self._handler_ref = c_void_p()
        self._handler_proc = None

    def _install_handler(self):
        """Install the process-wide Carbon handler once."""
        if self._handler_proc is not None:
            return

        def _on_hotkey(_call_ref, event, _user_data):
            try:
                hotkey_id = _EventHotKeyID()
                _carbon.GetEventParameter(
                    event,
                    kEventParamDirectObject,
                    typeEventHotKeyID,
                    None,
                    ctypes.sizeof(hotkey_id),
                    None,
                    byref(hotkey_id),
                )
                if hotkey_id.signature == _SIGNATURE and self._callback:
                    self._callback()
            except Exception as e:
                print(f"[ERROR] Hotkey handler failed: {e}")
            return 0  # noErr

        # The trampoline must outlive the handler registration.
        self._handler_proc = _HandlerProc(_on_hotkey)
        spec = _EventTypeSpec(kEventClassKeyboard, kEventHotKeyPressed)
        status = _carbon.InstallEventHandler(
            _carbon.GetApplicationEventTarget(),
            ctypes.cast(self._handler_proc, c_void_p),
            1,
            byref(spec),
            None,
            byref(self._handler_ref),
        )
        if status != 0:
            self._handler_proc = None
            raise OSError(f"InstallEventHandler failed with status {status}")

    def register(self, hotkey: str, callback: Callable):
        """Register a global hotkey, replacing the previous one if needed."""
        key_code, modifiers = mac_keycodes.parse(hotkey)
        self.unregister()
        self._install_handler()
        self._callback = callback

        hotkey_id = _EventHotKeyID(_SIGNATURE, 1)
        ref = c_void_p()
        status = _carbon.RegisterEventHotKey(
            key_code,
            modifiers,
            hotkey_id,
            _carbon.GetApplicationEventTarget(),
            0,
            byref(ref),
        )
        if status != 0:
            self._callback = None
            raise OSError(
                f"RegisterEventHotKey failed with status {status}. "
                "Another app may already own this shortcut."
            )
        self._hotkey_ref = ref
        self._hotkey = hotkey

    def unregister(self):
        """Remove the active global hotkey."""
        if self._hotkey_ref:
            _carbon.UnregisterEventHotKey(self._hotkey_ref)
            self._hotkey_ref = c_void_p()
        self._hotkey = None
        self._callback = None

    @property
    def current(self) -> Optional[str]:
        return self._hotkey
