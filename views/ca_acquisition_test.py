import pytest
import os
from unittest.mock import patch, MagicMock
from customtkinter import CTk
from views.ca_acquisition import CaAcquisition
from unittest import mock
import pytest


@pytest.fixture(autouse=True)
def mock_ctk():
    with mock.patch("customtkinter.CTk"):
        yield

@pytest.fixture
def mock_user_input():
    class MockUserInput:
        image_source = "Local images"
        import_files = []
        frame_interval = 0
        edgefinder = ""
        number_of_frames = 0
    return MockUserInput()

@pytest.fixture
def root():
    app = CTk()
    app.withdraw()
    yield app
    app.destroy()

@pytest.fixture
def ca_component(root, mock_user_input):
    return CaAcquisition(root, mock_user_input)

def test_component_initialization(ca_component):
    assert hasattr(ca_component, 'image_source')
    assert hasattr(ca_component, 'frame_interval')
    assert hasattr(ca_component, 'edgefinder')
    assert hasattr(ca_component, 'choose_files_button')

def test_update_image_source_enables_button(ca_component):
    ca_component.choose_files_button.configure = MagicMock()
    ca_component.update_image_source("Local images")
    ca_component.choose_files_button.configure.assert_called_with(state="normal")

def test_update_frame_interval(ca_component, mock_user_input):
    ca_component.frame_interval.get_value = MagicMock(return_value=5)
    ca_component.update_frame_interval()
    assert mock_user_input.frame_interval == 5

def test_update_edgefinder(ca_component, mock_user_input):
    ca_component.edgefinder.get_value = MagicMock(return_value="sobel")
    ca_component.update_edgefinder()
    assert mock_user_input.edgefinder == "sobel"

@patch("views.ca_acquisition.filedialog.askopenfilenames")
def test_select_files_and_display(mock_askopen, ca_component, mock_user_input):
    mock_askopen.return_value = ["image1.png", "image2.png"]
    ca_component.initialize_image_display = MagicMock()
    ca_component.select_files()

    assert mock_user_input.import_files == ["image1.png", "image2.png"]
    assert mock_user_input.number_of_frames == 2
    assert ca_component.choose_files_button.cget("text") == "2 File(s) Selected"
    ca_component.initialize_image_display.assert_called_once()

def test_change_image_updates_index(ca_component, mock_user_input):
    mock_user_input.import_files = ["img1", "img2", "img3"]
    mock_user_input.number_of_frames = 3
    ca_component.current_index = 0
    ca_component.load_image = MagicMock()
    ca_component.update_index_entry = MagicMock()
    ca_component.name_label = MagicMock()

    ca_component.change_image(1)
    assert ca_component.current_index == 1
    ca_component.load_image.assert_called_once_with("img2")

@patch("views.ca_acquisition.Image.open")
def test_load_image_success(mock_open, ca_component):
    mock_open.return_value = MagicMock(size=(100, 100))
    ca_component.display_image = MagicMock()
    ca_component.load_image("fake_path.png")
    ca_component.display_image.assert_called_once()

@patch("views.ca_acquisition.Image.open", side_effect=FileNotFoundError)
def test_load_image_file_not_found(mock_open, ca_component):
    ca_component.load_image("missing.png")
    assert ca_component.current_image is None
