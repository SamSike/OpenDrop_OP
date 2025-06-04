from opendrop_ml.utils.enums import RegionSelect, ThresholdSelect

import os
import cv2

VERSION = "1.0"
CV2_VERSION = tuple(map(int, cv2.__version__.split(".")))

AUTO_MANUAL_OPTIONS = [RegionSelect.AUTOMATED, RegionSelect.USER_SELECTED]
DROP_ID_OPTIONS = [RegionSelect.AUTOMATED, RegionSelect.USER_SELECTED]
THRESHOLD_OPTIONS = [ThresholdSelect.AUTOMATED, ThresholdSelect.USER_SELECTED]
BASELINE_OPTIONS = [ThresholdSelect.AUTOMATED, ThresholdSelect.USER_SELECTED]
NEEDLE_OPTIONS = ["0.7176", "1.270", "1.651"]
FILE_SOURCE_OPTIONS_CA = ["Local images", "Flea3", "USB camera"]
FILE_SOURCE_OPTIONS_IFT = ["Local images", "cv2.VideoCapture", "GenlCam"]
EDGEFINDER_OPTIONS = ["OpenCV", "Subpixel", "Both"]

# OPENDROP
INTERFACIAL_TENSION = "Interfacial Tension"

LEFT_ANGLE = "left angle"
RIGHT_ANGLE = "right angle"

# CA ANALYSIS
BASELINE_INTERCEPTS = "baseline intercepts"
CONTACT_POINTS = "contact points"
TANGENT_LINES = "tangent lines"
FIT_SHAPE = "fit shape"
BASELINE = "baseline"

PATH_TO_SCRIPT = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "..")
PATH_TO_FILE = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "parameters.csv"
)

# FONT_FRAME_LABEL = ("Helvetica", 16, "BOLD")
FONT_FRAME_LABEL = "*-*-medium-r-normal--*-160-*"

LABEL_WIDTH = 29
ENTRY_WIDTH = 11

DELTA_TOL = 1.0e-6
GRADIENT_TOL = 1.0e-6
MAXIMUM_FITTING_STEPS = 10
OBJECTIVE_TOL = 1.0e-4
ARCLENGTH_TOL = 1.0e-6
MAXIMUM_ARCLENGTH_STEPS = 10
NEEDLE_TOL = 1.0e-4
NEEDLE_STEPS = 20
MAX_ARCLENGTH = 100

IMAGE_TYPE = [
    ("Image Files", "*.png"),
    ("Image Files", "*.jpg"),
    ("Image Files", "*.jpeg"),
    ("Image Files", "*.gif"),
    ("Image Files", "*.bmp"),
]
