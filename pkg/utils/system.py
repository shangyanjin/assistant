"""
System utilities
"""
import platform
from typing import Optional
import tkinter as tk


def check_system_compatibility(root: tk.Tk) -> Optional[str]:
    """
    Check system and software compatibility issues
    
    Args:
        root: Tk instance
        
    Returns:
        Warning message string or None
    """
    def _version_tuple(v):
        """Convert version string to tuple for comparison"""
        filled = []
        for point in v.split("."):
            filled.append(point.zfill(8))
        return tuple(filled)

    # Tcl and macOS issue: https://github.com/python/cpython/issues/110218
    if platform.system().lower() == "darwin":
        version = platform.mac_ver()[0]
        if version and 14 <= float(version) < 15:
            tcl_version = root.tk.call("info", "patchlevel")
            if _version_tuple(tcl_version) <= _version_tuple("8.6.12"):
                return (
                    "Warning: Tkinter Responsiveness Issue Detected\n\n"
                    "You may experience unresponsive GUI elements when "
                    "your cursor is inside the window during startup. "
                    "This is a known issue with Tcl/Tk versions 8.6.12 "
                    "and older on macOS Sonoma.\n\nTo resolve this:\n"
                    "Update to Python 3.11.7+ or 3.12+\n"
                    "Or install Tcl/Tk 8.6.13 or newer separately\n\n"
                    "Temporary workaround: Move your cursor out of "
                    "the window and back in if elements become unresponsive.\n\n"
                    "For more information, visit: https://github.com/python/cpython/issues/110218"
                )
    return None

