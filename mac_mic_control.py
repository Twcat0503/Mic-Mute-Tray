"""Microphone mute control through the macOS Core Audio HAL.

The default input device is resolved on every call so that swapping headsets
or changing the input in System Settings is picked up without a restart.
"""

import ctypes
import threading
from ctypes import POINTER, byref, c_char_p, c_float, c_uint32, c_void_p

_core_audio = ctypes.CDLL("/System/Library/Frameworks/CoreAudio.framework/CoreAudio")
_core_foundation = ctypes.CDLL(
    "/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation"
)


def _fourcc(code: str) -> int:
    """Convert a Core Audio four-character code into its integer selector."""
    return int.from_bytes(code.encode("ascii"), "big")


kAudioObjectSystemObject = 1
kAudioHardwarePropertyDefaultInputDevice = _fourcc("dIn ")
kAudioObjectPropertyScopeInput = _fourcc("inpt")
kAudioObjectPropertyElementMain = 0
kAudioDevicePropertyMute = _fourcc("mute")
kAudioDevicePropertyVolumeScalar = _fourcc("volm")
kAudioObjectPropertyName = _fourcc("lnam")
kCFStringEncodingUTF8 = 0x08000100

# Some interfaces expose mute per channel instead of on the main element.
_ELEMENTS = (kAudioObjectPropertyElementMain, 1, 2)


class _PropertyAddress(ctypes.Structure):
    _fields_ = [
        ("mSelector", c_uint32),
        ("mScope", c_uint32),
        ("mElement", c_uint32),
    ]


_core_audio.AudioObjectGetPropertyData.argtypes = [
    c_uint32, POINTER(_PropertyAddress), c_uint32, c_void_p, POINTER(c_uint32), c_void_p,
]
_core_audio.AudioObjectGetPropertyData.restype = c_uint32
_core_audio.AudioObjectSetPropertyData.argtypes = [
    c_uint32, POINTER(_PropertyAddress), c_uint32, c_void_p, c_uint32, c_void_p,
]
_core_audio.AudioObjectSetPropertyData.restype = c_uint32
_core_audio.AudioObjectHasProperty.argtypes = [c_uint32, POINTER(_PropertyAddress)]
_core_audio.AudioObjectHasProperty.restype = ctypes.c_ubyte
_core_audio.AudioObjectIsPropertySettable.argtypes = [
    c_uint32, POINTER(_PropertyAddress), POINTER(ctypes.c_ubyte),
]
_core_audio.AudioObjectIsPropertySettable.restype = c_uint32

_core_foundation.CFStringGetCString.argtypes = [
    c_void_p, c_char_p, ctypes.c_long, c_uint32,
]
_core_foundation.CFStringGetCString.restype = ctypes.c_ubyte
_core_foundation.CFRelease.argtypes = [c_void_p]


def _address(selector: int, scope: int, element: int) -> _PropertyAddress:
    return _PropertyAddress(selector, scope, element)


def _default_input_device() -> int:
    """Return the Core Audio object ID of the default input device."""
    address = _address(
        kAudioHardwarePropertyDefaultInputDevice,
        _fourcc("glob"),
        kAudioObjectPropertyElementMain,
    )
    device = c_uint32(0)
    size = c_uint32(ctypes.sizeof(device))
    status = _core_audio.AudioObjectGetPropertyData(
        kAudioObjectSystemObject, byref(address), 0, None, byref(size), byref(device)
    )
    if status != 0 or device.value == 0:
        raise RuntimeError("No default microphone input device was found.")
    return device.value


def _writable_mute_element(device: int):
    """Return the first element exposing a settable mute property."""
    for element in _ELEMENTS:
        address = _address(
            kAudioDevicePropertyMute, kAudioObjectPropertyScopeInput, element
        )
        if not _core_audio.AudioObjectHasProperty(device, byref(address)):
            continue
        settable = ctypes.c_ubyte(0)
        _core_audio.AudioObjectIsPropertySettable(
            device, byref(address), byref(settable)
        )
        if settable.value:
            return address
    return None


def _volume_elements(device: int):
    """Return every element exposing a settable input volume property."""
    found = []
    for element in _ELEMENTS:
        address = _address(
            kAudioDevicePropertyVolumeScalar, kAudioObjectPropertyScopeInput, element
        )
        if not _core_audio.AudioObjectHasProperty(device, byref(address)):
            continue
        settable = ctypes.c_ubyte(0)
        _core_audio.AudioObjectIsPropertySettable(
            device, byref(address), byref(settable)
        )
        if settable.value:
            found.append(address)
    return found


def _get_uint32(device: int, address: _PropertyAddress) -> int:
    value = c_uint32(0)
    size = c_uint32(ctypes.sizeof(value))
    status = _core_audio.AudioObjectGetPropertyData(
        device, byref(address), 0, None, byref(size), byref(value)
    )
    if status != 0:
        raise OSError(f"AudioObjectGetPropertyData failed with status {status}")
    return value.value


def _set_uint32(device: int, address: _PropertyAddress, value: int):
    payload = c_uint32(value)
    status = _core_audio.AudioObjectSetPropertyData(
        device, byref(address), 0, None, ctypes.sizeof(payload), byref(payload)
    )
    if status != 0:
        raise OSError(f"AudioObjectSetPropertyData failed with status {status}")


def _get_float(device: int, address: _PropertyAddress) -> float:
    value = c_float(0)
    size = c_uint32(ctypes.sizeof(value))
    status = _core_audio.AudioObjectGetPropertyData(
        device, byref(address), 0, None, byref(size), byref(value)
    )
    if status != 0:
        raise OSError(f"AudioObjectGetPropertyData failed with status {status}")
    return value.value


def _set_float(device: int, address: _PropertyAddress, value: float):
    payload = c_float(value)
    status = _core_audio.AudioObjectSetPropertyData(
        device, byref(address), 0, None, ctypes.sizeof(payload), byref(payload)
    )
    if status != 0:
        raise OSError(f"AudioObjectSetPropertyData failed with status {status}")


def device_name() -> str:
    """Return the human readable name of the default input device."""
    device = _default_input_device()
    address = _address(
        kAudioObjectPropertyName, _fourcc("glob"), kAudioObjectPropertyElementMain
    )
    ref = c_void_p()
    size = c_uint32(ctypes.sizeof(ref))
    status = _core_audio.AudioObjectGetPropertyData(
        device, byref(address), 0, None, byref(size), byref(ref)
    )
    if status != 0 or not ref:
        return "Unknown input device"
    buffer = ctypes.create_string_buffer(256)
    _core_foundation.CFStringGetCString(ref, buffer, 256, kCFStringEncodingUTF8)
    _core_foundation.CFRelease(ref)
    return buffer.value.decode("utf-8", "replace")


class MicControl:
    """Read and update the mute state of the default microphone.

    Devices that expose a real mute switch use it. The rest fall back to
    driving the input volume to zero, which is how macOS itself degrades for
    interfaces without a hardware mute.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._restore_volume: float = 1.0
        # Fail loudly here so TrayApp can report the microphone as unavailable.
        _default_input_device()

    def _supports_mute(self, device: int):
        return _writable_mute_element(device)

    def is_muted(self) -> bool:
        """Return True when the microphone is muted."""
        try:
            device = _default_input_device()
            address = self._supports_mute(device)
            if address is not None:
                return bool(_get_uint32(device, address))
            volumes = _volume_elements(device)
            if volumes:
                return _get_float(device, volumes[0]) <= 0.0001
        except Exception:
            pass
        return False

    def set_mute(self, state: bool):
        """Set the microphone mute state."""
        with self._lock:
            try:
                device = _default_input_device()
                address = self._supports_mute(device)
                if address is not None:
                    _set_uint32(device, address, 1 if state else 0)
                    return
                volumes = _volume_elements(device)
                if not volumes:
                    return
                if state:
                    current = _get_float(device, volumes[0])
                    if current > 0.0001:
                        self._restore_volume = current
                    for element in volumes:
                        _set_float(device, element, 0.0)
                else:
                    for element in volumes:
                        _set_float(device, element, self._restore_volume)
            except Exception as e:
                print(f"[ERROR] Failed to set microphone mute state: {e}")

    def toggle(self) -> bool:
        """Toggle mute state and return True when the new state is muted."""
        target = not self.is_muted()
        self.set_mute(target)
        return self.is_muted()
