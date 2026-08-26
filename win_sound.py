"""Play notification sounds."""

import os
import threading

import pygame


class SoundManager:
    def __init__(self):
        try:
            pygame.mixer.pre_init(44100, -16, 1, 512)
            pygame.mixer.init()
        except Exception:
            pass
        self._lock = threading.Lock()

    def play(self, path: str):
        """Play a WAV sound asynchronously when the path exists."""
        if not path or not os.path.isfile(path):
            return

        def _worker():
            with self._lock:
                try:
                    sound = pygame.mixer.Sound(path)
                    sound.play()
                    pygame.time.wait(max(1, int(sound.get_length() * 1000)))
                except Exception:
                    pass

        threading.Thread(target=_worker, daemon=True).start()

    def cleanup(self):
        """Release pygame mixer resources."""
        try:
            pygame.mixer.quit()
        except Exception:
            pass
