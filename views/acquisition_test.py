from views.acquisition import Acquisition

from unittest.mock import patch, MagicMock
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
def component(mock_user_input):
    with patch("views.acquisition.Acquisition.__init__", return_value=None):
        component = Acquisition.__new__(Acquisition)
        component.image_source = MagicMock()
        component.frame_interval = MagicMock()
        component.edgefinder = MagicMock()
        component.choose_files_button = MagicMock()
        component.initialize_image_display = MagicMock()
        component.load_image = MagicMock()
        component.update_index_entry = MagicMock()
        component.name_label = MagicMock()
        component.current_index = 0
        component.current_image = None
        component.user_input_data = mock_user_input
        component.images_frame = MagicMock()
        component.display_image = MagicMock()
        return component


def test_component_initialization(component):
    assert hasattr(component, "image_source")
    assert hasattr(component, "frame_interval")
    assert hasattr(component, "edgefinder")
    assert hasattr(component, "choose_files_button")


def test_update_frame_interval(component, mock_user_input):
    component.frame_interval.get_value = MagicMock(return_value=5)
    component.update_frame_interval()
    assert mock_user_input.frame_interval == 5


def test_change_image_updates_index(component, mock_user_input):
    mock_user_input.import_files = ["img1", "img2", "img3"]
    mock_user_input.number_of_frames = 3
    component.current_index = 0
    component.load_image = MagicMock()
    component.update_index_entry = MagicMock()
    component.name_label = MagicMock()

    component.change_image(1)
    assert component.current_index == 1
    component.load_image.assert_called_once_with("img2")
