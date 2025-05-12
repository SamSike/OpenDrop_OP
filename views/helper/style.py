# style.py

from views.helper.theme import *

# This is for light mode. In dark mode, use the default color
APP_COLORS = {
    "PRIMARY": "#2C68F6",
    "BACKGROUND": "#F5F7FA",
    "OUTERFRAME": "#E2E6EC",
    "INNERFRAME": "#F5F7FA",
    "ENTRY": "#FFFFFF",
    "TEXT": "#1C1C1C",
    "SECONDARY": "#7DA3F5",
    "ACCENT": "#00A3D9",
    "ERROR": "#D64545",
    "SUCCESS": "#4BB543",
    "BORDER": "#C4CBD4",
}

def get_color(name: str) -> str:
    """Get a named color from the scientific colorboard."""
    return APP_COLORS.get(name.upper(), "#000000")  # fallback to black


def set_light_only_color(widget, name):
    if get_appearance_mode() == LIGHT_MODE:
        widget.configure(fg_color=get_color(name))
