"""Create default tray icons and notification sounds."""

import math
import os
import struct
import wave

from PIL import Image, ImageDraw

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def ensure_assets() -> dict:
    """Create bundled assets when they are missing and return their paths."""
    os.makedirs(ASSETS_DIR, exist_ok=True)

    paths = {
        "mic_on": os.path.join(ASSETS_DIR, "mic_on.png"),
        "mic_off": os.path.join(ASSETS_DIR, "mic_off.png"),
        "on_sound": os.path.join(ASSETS_DIR, "on.wav"),
        "off_sound": os.path.join(ASSETS_DIR, "off.wav"),
    }

    try:
        if not os.path.exists(paths["mic_on"]):
            _create_mic_icon(paths["mic_on"], active=True)
    except Exception as e:
        print(f"[WARN] Failed to create unmuted icon: {e}")

    try:
        if not os.path.exists(paths["mic_off"]):
            _create_mic_icon(paths["mic_off"], active=False)
    except Exception as e:
        print(f"[WARN] Failed to create muted icon: {e}")

    try:
        if not os.path.exists(paths["on_sound"]):
            _create_tone(paths["on_sound"], freq=880, duration=0.12)
    except Exception as e:
        print(f"[WARN] Failed to create unmute sound: {e}")

    try:
        if not os.path.exists(paths["off_sound"]):
            _create_tone(paths["off_sound"], freq=440, duration=0.12)
    except Exception as e:
        print(f"[WARN] Failed to create mute sound: {e}")

    return paths


def _create_mic_icon(path: str, active: bool, size: int = 64):
    """Create a simple microphone icon."""
    try:
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        bg = (34, 197, 94, 255) if active else (239, 68, 68, 255)
        draw.ellipse([2, 2, size - 2, size - 2], fill=bg)

        cx = size // 2
        s = size / 64

        white = (255, 255, 255, 255)
        white_dim = (255, 255, 255, 200)

        mic_width = int(10 * s)
        mic_height = int(16 * s)
        mic_x1, mic_y1 = cx - mic_width, int(10 * s)
        mic_x2, mic_y2 = cx + mic_width, int(10 * s) + mic_height * 2
        draw.rounded_rectangle(
            [mic_x1, mic_y1, mic_x2, mic_y2],
            radius=mic_width,
            fill=white,
        )

        arc_radius = int(13 * s)
        arc_x1, arc_y1 = cx - arc_radius, int(22 * s)
        arc_x2, arc_y2 = cx + arc_radius, int(22 * s) + arc_radius * 2
        line_width = max(1, int(2 * s))
        draw.arc(
            [arc_x1, arc_y1, arc_x2, arc_y2],
            start=0,
            end=180,
            fill=white_dim,
            width=line_width,
        )

        stem_top = int(22 * s) + arc_radius
        stem_bottom = int(52 * s)
        draw.line([cx, stem_top, cx, stem_bottom], fill=white_dim, width=line_width)

        base_width = int(10 * s)
        draw.line(
            [cx - base_width, stem_bottom, cx + base_width, stem_bottom],
            fill=white_dim,
            width=line_width,
        )

        if not active:
            slash_width = max(2, int(3 * s))
            draw.line(
                [10, 10, size - 10, size - 10],
                fill=(255, 255, 255, 210),
                width=slash_width,
            )

        img.save(path, "PNG")
    except Exception as e:
        raise OSError(f"Failed to create icon {path}: {e}")


def _create_tone(
    path: str,
    freq: float,
    duration: float = 0.12,
    sample_rate: int = 44100,
    volume: float = 0.4,
):
    """Create a short WAV tone with a small fade in and fade out."""
    try:
        frame_count = int(sample_rate * duration)
        fade = int(sample_rate * 0.02)

        with wave.open(path, "wb") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(sample_rate)
            for i in range(frame_count):
                t = i / sample_rate
                amp = volume
                if i < fade:
                    amp *= i / fade
                elif i > frame_count - fade:
                    amp *= (frame_count - i) / fade
                sample = amp * math.sin(2 * math.pi * freq * t)
                f.writeframes(struct.pack("<h", int(sample * 32767)))
    except Exception as e:
        raise OSError(f"Failed to create sound {path}: {e}")
