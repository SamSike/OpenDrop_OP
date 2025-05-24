# keymap.py
import sys

if sys.platform.startswith("win"):
    KEY_UP = [2490368]
    KEY_DOWN = [2621440]
    KEY_LEFT = [2424832]
    KEY_RIGHT = [2555904]
elif sys.platform.startswith("darwin"):  # macOS
    KEY_UP = [0]
    KEY_DOWN = [1]
    KEY_LEFT = [2]
    KEY_RIGHT = [3]
else:  # Linux default (OpenCV codes)
    KEY_UP = [82]
    KEY_DOWN = [84]
    KEY_LEFT = [81]
    KEY_RIGHT = [83]

KEY_ENTER = [13, 10]
KEY_SPACE = [32]
KEY_ESC = [27]
KEY_O = [ord('o'), ord('O')]
KEY_P = [ord('p'), ord('P')]


def key_in(k, key_group):
    return k in key_group
