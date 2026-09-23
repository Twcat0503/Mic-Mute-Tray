"""Play WAV notifications using the Windows standard library backend."""

import os
import winsound


class SoundManager:
    def play(self, path: str):
        """Play a WAV without blocking the caller."""
        if not path or not os.path.isfile(path):
            return
        try:
            winsound.PlaySound(
                path, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT
            )
        except RuntimeError:
            pass

    def cleanup(self):
        """Stop any pending notification."""
        winsound.PlaySound(None, 0)
