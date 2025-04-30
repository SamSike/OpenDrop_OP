from enum import Enum

class FunctionType(Enum):
    PENDANT_DROP = "Pendant Drop"
    CONTACT_ANGLE = "Contact Angle"

class Stage(Enum):
    ACQUISITION = 1
    PREPARATION = 2
    ANALYSIS = 3
    OUTPUT = 4

class Move(Enum):
    Next = 1
    Back = -1

class FittingMethod(str, Enum):
    TANGENT_FIT = 'tangent fit'
    ELLIPSE_FIT = 'ellipse fit'
    POLYNOMIAL_FIT = 'polynomial fit'
    CIRCLE_FIT = 'circle fit'
    YL_FIT = 'YL fit'
    ML_MODEL = 'ML model'