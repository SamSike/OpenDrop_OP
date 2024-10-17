import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../modules')))

import pytest
from unittest import mock
import numpy as np
from ExtractData import ExtractedData
from read_image import get_import_filename, import_from_source

@mock.patch("cv2.imread")
def test_image_from_harddrive(mock_imread):
    mock_imread.return_value = np.zeros((10, 10, 3))

    class MockExperimentalSetup:
        def __init__(self):
            self.import_files = ["image1.png", "image2.png"]
            self.image_source = "harddrive"

    class MockExperimentalDrop:
        def __init__(self):
            self.image = None

    experimental_setup = MockExperimentalSetup()
    experimental_drop = MockExperimentalDrop()

    import_from_source(experimental_drop, experimental_setup, 1)

    assert experimental_drop.image is not None, "Image was not loaded into experimental_drop.image"
    mock_imread.assert_called_once_with("image2.png", 1)

def test_get_import_filename():
    class MockExperimentalSetup:
        def __init__(self):
            self.import_files = ["image1.png", "image2.png"]

    experimental_setup = MockExperimentalSetup()
    filename = get_import_filename(experimental_setup, 1)

    assert filename == "image2.png", "get_import_filename did not return the expected filename"
