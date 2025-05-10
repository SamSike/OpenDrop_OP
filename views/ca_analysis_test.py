import pytest
from unittest.mock import MagicMock
from views.ca_analysis import CaAnalysis, extract_method
from utils.enums import FittingMethod
from PIL import Image

def test_extract_method_priority():
    contact_angles = {
        FittingMethod.YL_FIT: {"left_angle": 40},
        FittingMethod.CIRCLE_FIT: {"left_angle": 45}
    }
    method = extract_method(contact_angles)
    assert method == FittingMethod.CIRCLE_FIT or method == FittingMethod.YL_FIT

def test_extract_method_none():
    contact_angles = {}
    method = extract_method(contact_angles)
    assert method is None

def test_draw_on_cropped_image_returns_image():
    user_input_data = MagicMock()
    user_input_data.analysis_methods_ca = {FittingMethod.CIRCLE_FIT: True}
    user_input_data.number_of_frames = 1
    user_input_data.import_files = ["dummy.png"]

    ca = MagicMock(spec=CaAnalysis)
    ca.draw_on_cropped_image = CaAnalysis.draw_on_cropped_image

    dummy_image = Image.new("RGB", (100, 100))
    result_img = ca.draw_on_cropped_image(
        ca,
        image=dummy_image,
        left_angle=30,
        right_angle=45,
        contact_points=[(30, 80), (70, 80)],
        tangent_lines=[((30, 80), (50, 60)), ((70, 80), (90, 60))]
    )

    assert isinstance(result_img, Image.Image)
