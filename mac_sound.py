"""Play notification sounds through NSSound.

Sounds are cached per path and reused, which keeps playback allocation free on
the hot path and avoids leaking Objective-C objects that nothing releases.
"""

import os
from ctypes import c_bool, c_void_p

import mac_objc as objc

_CACHE_LIMIT = 8


class SoundManager:
    def __init__(self):
        self._sounds: dict = {}

    def _load(self, path: str):
        """Return a cached NSSound for `path`, or None when it cannot load."""
        if path in self._sounds:
            return self._sounds[path]

        sound = objc.msg(c_void_p, c_void_p, c_bool)(
            objc.msg(c_void_p)(objc.cls("NSSound"), objc.sel("alloc")),
            objc.sel("initWithContentsOfFile:byReference:"),
            objc.nsstring(path),
            True,
        )
        if not sound:
            return None

        if len(self._sounds) >= _CACHE_LIMIT:
            self._sounds.clear()
        self._sounds[path] = sound
        objc.retain(sound)
        return sound

    def play(self, path: str):
        """Play a sound file asynchronously when the path exists."""
        if not path or not os.path.isfile(path):
            return
        try:
            sound = self._load(path)
            if not sound:
                return
            # Restart from the beginning if the previous toggle is still playing.
            if objc.msg(c_bool)(sound, objc.sel("isPlaying")):
                objc.msg(c_bool)(sound, objc.sel("stop"))
            objc.msg(c_bool)(sound, objc.sel("play"))
        except Exception as e:
            print(f"[WARN] Failed to play sound {path}: {e}")

    def cleanup(self):
        """Stop any sound that is still playing."""
        for sound in self._sounds.values():
            try:
                objc.msg(c_bool)(sound, objc.sel("stop"))
            except Exception:
                pass
        self._sounds.clear()
