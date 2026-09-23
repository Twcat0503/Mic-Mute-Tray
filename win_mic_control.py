"""Microphone mute control through the Windows Core Audio API."""

import comtypes


def _get_mic_volume():
    """Return the pycaw IAudioEndpointVolume interface for the default mic."""
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

    device = AudioUtilities.GetMicrophone()
    if device is None:
        raise RuntimeError("No default microphone input device was found.")

    interface = device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return interface.QueryInterface(IAudioEndpointVolume)


def _with_mic_volume(operation):
    """Balance COM initialization on the thread performing the operation."""
    comtypes.CoInitialize()
    volume = None
    try:
        volume = _get_mic_volume()
        return operation(volume)
    finally:
        volume = None
        comtypes.CoUninitialize()


class MicControl:
    """Read and update the mute state of the default microphone."""

    def is_muted(self) -> bool:
        """Return True when the microphone is muted."""
        return _with_mic_volume(lambda volume: bool(volume.GetMute()))

    def toggle(self) -> bool:
        """Toggle mute state and return True when the new state is muted."""
        def toggle_volume(volume):
            muted = bool(volume.GetMute())
            volume.SetMute(not muted, None)
            return not muted
        return _with_mic_volume(toggle_volume)

    def set_mute(self, state: bool):
        """Set the microphone mute state."""
        _with_mic_volume(lambda volume: volume.SetMute(int(state), None))
