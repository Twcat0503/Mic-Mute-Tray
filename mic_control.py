"""Microphone mute control through the Windows Core Audio API."""

import comtypes


def _get_mic_volume():
    """Return the pycaw IAudioEndpointVolume interface for the default mic."""
    try:
        comtypes.CoInitialize()
    except OSError:
        pass

    from ctypes import POINTER, cast

    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

    device = AudioUtilities.GetMicrophone()
    if device is None:
        raise RuntimeError("No default microphone input device was found.")

    interface = device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return cast(interface, POINTER(IAudioEndpointVolume))


class MicControl:
    """Read and update the mute state of the default microphone."""

    def is_muted(self) -> bool:
        """Return True when the microphone is muted."""
        try:
            return bool(_get_mic_volume().GetMute())
        except Exception:
            return False

    def toggle(self) -> bool:
        """Toggle mute state and return True when the new state is muted."""
        try:
            volume = _get_mic_volume()
            muted = bool(volume.GetMute())
            volume.SetMute(not muted, None)
            return not muted
        except Exception:
            return False

    def set_mute(self, state: bool):
        """Set the microphone mute state."""
        try:
            _get_mic_volume().SetMute(int(state), None)
        except Exception:
            pass
