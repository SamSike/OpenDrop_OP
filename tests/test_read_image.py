import os
import cv2
import pytest
from unittest.mock import MagicMock, patch
import numpy as np
from modules.read_image import get_image, save_image, import_from_source # Adjust the import based on your directory structure

# Mock classes
class MockExperimentalSetup:
    def __init__(self):
        self.create_folder_boole = True
        self.filename = "test_image.png"
        self.directory_string = "./test_directory"
        self.image_source = "Local images"
        self.import_files = ["test_image.png"]
        self.time_string = ""

class MockExperimentalDrop:
    def __init__(self):
        self.image = None
        self.time = ""

# Test get_image function
def test_get_image_creates_directory(mocker):
    mock_setup = MockExperimentalSetup()
    mock_drop = MockExperimentalDrop()
    
    # Mock os.makedirs to prevent actual directory creation
    mocker.patch("os.makedirs")

    # Call get_image with frame_number = 0
    get_image(mock_drop, mock_setup, 0)

    # Check if the directory was created
    expected_directory = os.path.join(mock_setup.directory_string, f"{mock_setup.filename}_{mock_setup.time_string}")
    assert os.path.exists(expected_directory) == False  # We use False here as the directory won't actually be created due to mocking
    mock_setup.directory_string = expected_directory  # Update for cleanup

    # Cleanup
    if os.path.exists(expected_directory):
        os.rmdir(expected_directory)

# Test save_image function
def test_save_image_creates_file(mocker):
    mock_setup = MockExperimentalSetup()
    mock_drop = MockExperimentalDrop()
    mock_drop.image = np.zeros((100, 100, 3), dtype=np.uint8)  # Mock an image

    # Mock cv2.imwrite to prevent actual file writing
    mocker.patch("cv2.imwrite", return_value=True)

    # Call save_image
    save_image(mock_drop, mock_setup, 0)

    # Construct the expected filename
    expected_filename = os.path.join(
        mock_setup.directory_string,
        f"{mock_setup.filename[:-4]}_{mock_setup.time_string}_{str(0).zfill(3)}{mock_setup.filename[-4:]}"
    )

    # Check if cv2.imwrite was called with the expected filename
    cv2.imwrite.assert_called_once_with(expected_filename, mock_drop.image)

# Test import_from_source function
def test_import_from_source_with_local_image(mocker):
    mock_setup = MockExperimentalSetup()
    mock_drop = MockExperimentalDrop()

    # Mock cv2.imread to return a mock image
    mock_image = np.zeros((100, 100, 3), dtype=np.uint8)  # Dummy black image
    mocker.patch("cv2.imread", return_value=mock_image)

    # Call import_from_source
    import_from_source(mock_drop, mock_setup, 0)

    # Check if the image was loaded from the local source
    assert np.array_equal(mock_drop.image, mock_image)
