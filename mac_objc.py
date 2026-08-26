"""Minimal ctypes bridge to the Objective-C runtime and AppKit.

Only the handful of calls Mic Mute Tray needs are wrapped here so the macOS
build stays dependency free. Every Objective-C message goes through `msg()`,
which builds a correctly typed `objc_msgSend` prototype: on arm64 the ABI
passes arguments by prototype, so an untyped call would corrupt the stack.
"""

import ctypes
import ctypes.util
from ctypes import CFUNCTYPE, c_bool, c_char_p, c_double, c_int64, c_uint64, c_void_p

_objc = ctypes.CDLL(ctypes.util.find_library("objc"))
_libc = ctypes.CDLL(None)

# Loading the frameworks registers their classes with the runtime.
ctypes.CDLL("/System/Library/Frameworks/Foundation.framework/Foundation")
ctypes.CDLL("/System/Library/Frameworks/AppKit.framework/AppKit")

_objc.objc_getClass.restype = c_void_p
_objc.objc_getClass.argtypes = [c_char_p]
_objc.sel_registerName.restype = c_void_p
_objc.sel_registerName.argtypes = [c_char_p]
_objc.objc_allocateClassPair.restype = c_void_p
_objc.objc_allocateClassPair.argtypes = [c_void_p, c_char_p, ctypes.c_size_t]
_objc.objc_registerClassPair.argtypes = [c_void_p]
_objc.class_addMethod.restype = c_bool
_objc.class_addMethod.argtypes = [c_void_p, c_void_p, c_void_p, c_char_p]

_MSG_SEND = ctypes.cast(_libc.objc_msgSend, c_void_p).value

_class_cache: dict = {}
_sel_cache: dict = {}
_msg_cache: dict = {}

# Objective-C objects and callbacks created here must outlive the call that
# made them; ctypes would otherwise free the trampolines.
_keep_alive: list = []

# Each target needs a class name the runtime has not seen before.
_target_serial = 0


class NSSize(ctypes.Structure):
    _fields_ = [("width", c_double), ("height", c_double)]


class NSPoint(ctypes.Structure):
    _fields_ = [("x", c_double), ("y", c_double)]


def cls(name: str) -> c_void_p:
    """Return the Objective-C class object for `name`."""
    if name not in _class_cache:
        handle = _objc.objc_getClass(name.encode())
        if not handle:
            raise LookupError(f"Objective-C class not found: {name}")
        _class_cache[name] = handle
    return _class_cache[name]


def sel(name: str) -> c_void_p:
    """Return the selector for `name`."""
    if name not in _sel_cache:
        _sel_cache[name] = _objc.sel_registerName(name.encode())
    return _sel_cache[name]


def msg(restype, *argtypes):
    """Return a typed objc_msgSend callable for one method signature."""
    key = (restype, argtypes)
    if key not in _msg_cache:
        proto = CFUNCTYPE(restype, c_void_p, c_void_p, *argtypes)
        _msg_cache[key] = proto(_MSG_SEND)
    return _msg_cache[key]


def send(receiver, selector: str, restype=c_void_p, *args):
    """Send `selector` to `receiver`; args are (ctype, value) pairs."""
    argtypes = tuple(a[0] for a in args)
    values = tuple(a[1] for a in args)
    return msg(restype, *argtypes)(receiver, sel(selector), *values)


def nsstring(text: str) -> c_void_p:
    """Return an autoreleased NSString for `text`."""
    return msg(c_void_p, c_char_p)(
        cls("NSString"), sel("stringWithUTF8String:"), text.encode("utf-8")
    )


def keep_alive(obj):
    """Hold a Python reference so a ctypes trampoline is not collected.

    This is for callbacks, not Objective-C objects: sending them a message
    would crash.
    """
    _keep_alive.append(obj)
    return obj


def retain(obj):
    """Send `retain` so an autoreleased object survives the next pool drain.

    Class methods such as `imageWithSystemSymbolName:` and
    `statusItemWithLength:` hand back autoreleased objects. The AppKit run
    loop drains the pool on every pass, so anything held past the current
    call has to be retained or it becomes a dangling pointer.
    """
    if obj:
        msg(c_void_p)(obj, sel("retain"))
    return obj


def make_target(callback) -> c_void_p:
    """Create an Objective-C object whose `invoke:` calls `callback(tag)`.

    AppKit menu items need an Objective-C target/action pair. A class is
    registered once per target with a single `invoke:` method that reads the
    sender's tag, which is how one Python callback can serve every menu item.
    """
    global _target_serial
    _target_serial += 1
    name = f"MMTTarget{_target_serial}"
    handle = _objc.objc_allocateClassPair(cls("NSObject"), name.encode(), 0)
    if not handle:
        raise RuntimeError(f"Failed to allocate Objective-C class {name}")

    imp_type = CFUNCTYPE(None, c_void_p, c_void_p, c_void_p)

    def _trampoline(_self, _cmd, sender):
        try:
            # NSTimer and NSMenuItem both land here; only menu items carry a tag.
            tag = -1
            if sender and msg(c_bool, c_void_p)(
                sender, sel("respondsToSelector:"), sel("tag")
            ):
                tag = int(msg(c_int64)(sender, sel("tag")))
            callback(tag)
        except Exception as e:  # never let an exception unwind into ObjC
            print(f"[ERROR] Action handler failed: {e}")

    imp = imp_type(_trampoline)
    _objc.class_addMethod(handle, sel("invoke:"), ctypes.cast(imp, c_void_p), b"v@:@")
    _objc.objc_registerClassPair(handle)

    instance = msg(c_void_p)(msg(c_void_p)(handle, sel("alloc")), sel("init"))
    keep_alive(imp)
    # `instance` came from alloc/init, so it is already owned.
    return instance


def shared_application() -> c_void_p:
    """Return the process-wide NSApplication instance."""
    return msg(c_void_p)(cls("NSApplication"), sel("sharedApplication"))


# NSApplicationActivationPolicyAccessory: the app runs without a Dock icon or
# app menu, which is what the macOS Human Interface Guidelines describe for a
# utility that lives only in the menu bar.
ACTIVATION_POLICY_ACCESSORY = 1


def become_menu_bar_agent():
    """Hide the Dock icon so the app is a menu bar extra only."""
    app = shared_application()
    return bool(
        msg(c_bool, c_int64)(
            app, sel("setActivationPolicy:"), ACTIVATION_POLICY_ACCESSORY
        )
    )


def activate_app():
    """Bring the app forward so its windows appear above other apps."""
    msg(None, c_bool)(shared_application(), sel("activateIgnoringOtherApps:"), True)


def symbol_image(symbol_name: str, description: str, point_size: float = 16.0):
    """Return an SF Symbol NSImage sized for the menu bar, or None."""
    image = msg(c_void_p, c_void_p, c_void_p)(
        cls("NSImage"),
        sel("imageWithSystemSymbolName:accessibilityDescription:"),
        nsstring(symbol_name),
        nsstring(description),
    )
    if not image:
        return None
    config = msg(c_void_p, c_double, c_int64)(
        cls("NSImageSymbolConfiguration"),
        sel("configurationWithPointSize:weight:"),
        point_size,
        5,  # NSFontWeightRegular
    )
    if config:
        configured = msg(c_void_p, c_void_p)(
            image, sel("imageWithSymbolConfiguration:"), config
        )
        if configured:
            image = configured
    msg(None, c_bool)(image, sel("setTemplate:"), True)
    return image


def image_from_file(path: str, height: float = 18.0):
    """Load an image file and scale it to the menu bar height, or None."""
    image = msg(c_void_p, c_void_p)(
        msg(c_void_p)(cls("NSImage"), sel("alloc")),
        sel("initWithContentsOfFile:"),
        nsstring(path),
    )
    if not image:
        return None
    size = msg(NSSize)(image, sel("size"))
    if size.width > 0 and size.height > 0:
        scaled = NSSize(height * (size.width / size.height), height)
        msg(None, NSSize)(image, sel("setSize:"), scaled)
    return image


def run_event_loop():
    """Run the AppKit main loop; returns when the app is told to terminate."""
    msg(None)(shared_application(), sel("run"))


def stop_event_loop():
    """Make `run_event_loop` return so Python shutdown runs normally.

    `stop:` only takes effect once AppKit finishes handling an event, so a
    dummy event is posted to wake the loop. Calling `terminate:` instead would
    exit through C and skip Python cleanup and stdout flushing.
    """
    app = shared_application()
    msg(None, c_void_p)(app, sel("stop:"), None)

    NSEventTypeApplicationDefined = 15
    event = msg(
        c_void_p, c_uint64, NSPoint, c_uint64, c_double, c_int64, c_void_p,
        ctypes.c_short, c_int64, c_int64,
    )(
        cls("NSEvent"),
        sel(
            "otherEventWithType:location:modifierFlags:timestamp:"
            "windowNumber:context:subtype:data1:data2:"
        ),
        NSEventTypeApplicationDefined,
        NSPoint(0.0, 0.0),
        0,
        0.0,
        0,
        None,
        0,
        0,
        0,
    )
    if event:
        msg(None, c_void_p, c_bool)(app, sel("postEvent:atStart:"), event, True)


def schedule_timer(interval: float, target, repeats: bool = True) -> c_void_p:
    """Schedule an NSTimer that sends `invoke:` to `target`."""
    return msg(c_void_p, c_double, c_void_p, c_void_p, c_void_p, c_bool)(
        cls("NSTimer"),
        sel("scheduledTimerWithTimeInterval:target:selector:userInfo:repeats:"),
        interval,
        target,
        sel("invoke:"),
        None,
        repeats,
    )


def invalidate_timer(timer):
    """Stop a scheduled NSTimer."""
    if timer:
        msg(None)(timer, sel("invalidate"))
