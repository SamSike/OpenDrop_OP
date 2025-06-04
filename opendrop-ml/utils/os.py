import sys
import os


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    # If the application is frozen (e.g., using PyInstaller), use _MEIPASS
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        # Go up one directory from opendrop_ml.utils/ (directory of this file)
        base_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), ".."))
    return os.path.normpath(os.path.join(base_path, relative_path))


def is_windows():
    """Check if the current operating system is Windows."""
    return sys.platform.startswith("win32") or sys.platform.startswith("cygwin")
