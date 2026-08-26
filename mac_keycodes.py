"""Translate hotkey strings into macOS virtual key codes and modifiers.

Hotkey strings use the same lowercase `key+key` shape as the Windows build so
one `config.json` value stays readable on both platforms.
"""

# Virtual key codes from Carbon's Events.h.
VIRTUAL_KEYS = {
    "a": 0x00, "s": 0x01, "d": 0x02, "f": 0x03, "h": 0x04, "g": 0x05,
    "z": 0x06, "x": 0x07, "c": 0x08, "v": 0x09, "b": 0x0B, "q": 0x0C,
    "w": 0x0D, "e": 0x0E, "r": 0x0F, "y": 0x10, "t": 0x11, "o": 0x1F,
    "u": 0x20, "i": 0x22, "p": 0x23, "l": 0x25, "j": 0x26, "k": 0x28,
    "n": 0x2D, "m": 0x2E,
    "1": 0x12, "2": 0x13, "3": 0x14, "4": 0x15, "5": 0x17, "6": 0x16,
    "7": 0x1A, "8": 0x1C, "9": 0x19, "0": 0x1D,
    "=": 0x18, "-": 0x1B, "]": 0x1E, "[": 0x21, "'": 0x27, ";": 0x29,
    "\\": 0x2A, ",": 0x2B, "/": 0x2C, ".": 0x2F, "`": 0x32,
    "enter": 0x24, "return": 0x24, "tab": 0x30, "space": 0x31,
    "backspace": 0x33, "esc": 0x35, "escape": 0x35,
    "home": 0x73, "page up": 0x74, "pageup": 0x74, "delete": 0x75,
    "end": 0x77, "page down": 0x79, "pagedown": 0x79,
    "left": 0x7B, "right": 0x7C, "down": 0x7D, "up": 0x7E,
    "f1": 0x7A, "f2": 0x78, "f3": 0x63, "f4": 0x76, "f5": 0x60, "f6": 0x61,
    "f7": 0x62, "f8": 0x64, "f9": 0x65, "f10": 0x6D, "f11": 0x67, "f12": 0x6F,
    "f13": 0x69, "f14": 0x6B, "f15": 0x71, "f16": 0x6A, "f17": 0x40,
    "f18": 0x4F, "f19": 0x50, "f20": 0x5A,
}

# Carbon modifier masks from MacTypes.h.
CMD_KEY = 0x0100
SHIFT_KEY = 0x0200
OPTION_KEY = 0x0800
CONTROL_KEY = 0x1000

MODIFIERS = {
    "cmd": CMD_KEY, "command": CMD_KEY, "windows": CMD_KEY, "win": CMD_KEY,
    "super": CMD_KEY, "meta": CMD_KEY,
    "shift": SHIFT_KEY,
    "alt": OPTION_KEY, "option": OPTION_KEY, "opt": OPTION_KEY,
    "ctrl": CONTROL_KEY, "control": CONTROL_KEY,
}

# Shown in the settings window so the recorded hotkey reads like a Mac shortcut.
MODIFIER_SYMBOLS = [
    (CONTROL_KEY, "⌃"),
    (OPTION_KEY, "⌥"),
    (SHIFT_KEY, "⇧"),
    (CMD_KEY, "⌘"),
]


def parse(hotkey: str):
    """Return `(key_code, modifier_mask)` for a hotkey string.

    Raises ValueError when the string names a key macOS cannot register.
    """
    if not hotkey or not hotkey.strip():
        raise ValueError("Hotkey is empty.")

    parts = [part.strip().lower() for part in hotkey.split("+") if part.strip()]
    if not parts:
        raise ValueError(f"Unsupported hotkey: {hotkey}")

    modifiers = 0
    key_code = None
    for part in parts:
        if part in MODIFIERS:
            modifiers |= MODIFIERS[part]
            continue
        if part not in VIRTUAL_KEYS:
            raise ValueError(f"Unsupported key for macOS: {part}")
        if key_code is not None:
            raise ValueError(f"Hotkey has more than one non-modifier key: {hotkey}")
        key_code = VIRTUAL_KEYS[part]

    if key_code is None:
        raise ValueError(f"Hotkey needs a non-modifier key: {hotkey}")
    return key_code, modifiers


def describe(hotkey: str) -> str:
    """Return a Mac-style label such as `⌃⌥M` for a hotkey string."""
    try:
        key_code, modifiers = parse(hotkey)
    except ValueError:
        return hotkey

    label = "".join(sym for mask, sym in MODIFIER_SYMBOLS if modifiers & mask)
    name = next(
        (n for n, code in VIRTUAL_KEYS.items() if code == key_code and len(n) > 1),
        None,
    )
    if name is None:
        name = next(n for n, code in VIRTUAL_KEYS.items() if code == key_code)
    return label + name.upper()


# Ordered for the settings window: the default first, then function keys,
# letters, digits, and the named keys that make sensible shortcuts.
_NAMED_KEYS = [
    ("Space", "space"), ("Return", "return"), ("Tab", "tab"),
    ("Escape", "esc"), ("Delete", "backspace"), ("Forward Delete", "delete"),
    ("Home", "home"), ("End", "end"), ("Page Up", "pageup"),
    ("Page Down", "pagedown"),
    ("Left", "left"), ("Right", "right"), ("Up", "up"), ("Down", "down"),
]


def selectable_keys():
    """Return ordered `(display, token)` pairs for the settings window."""
    keys = [(f"F{n}", f"f{n}") for n in range(13, 21)]
    keys += [(f"F{n}", f"f{n}") for n in range(1, 13)]
    keys += [(c.upper(), c) for c in "abcdefghijklmnopqrstuvwxyz" if c in VIRTUAL_KEYS]
    keys += [(d, d) for d in "0123456789"]
    keys += _NAMED_KEYS
    return [(label, token) for label, token in keys if token in VIRTUAL_KEYS]


def build(key_token: str, control: bool, option: bool, shift: bool, command: bool) -> str:
    """Build a hotkey string from a key plus modifier flags."""
    parts = []
    if control:
        parts.append("ctrl")
    if option:
        parts.append("option")
    if shift:
        parts.append("shift")
    if command:
        parts.append("cmd")
    parts.append(key_token)
    return "+".join(parts)


def split(hotkey: str):
    """Return `(key_token, control, option, shift, command)` for a hotkey."""
    key_code, modifiers = parse(hotkey)
    token = next(
        (n for n, code in VIRTUAL_KEYS.items() if code == key_code and len(n) > 1),
        None,
    ) or next(n for n, code in VIRTUAL_KEYS.items() if code == key_code)
    return (
        token,
        bool(modifiers & CONTROL_KEY),
        bool(modifiers & OPTION_KEY),
        bool(modifiers & SHIFT_KEY),
        bool(modifiers & CMD_KEY),
    )
