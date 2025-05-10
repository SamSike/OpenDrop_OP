import pytest
from unittest.mock import patch, MagicMock
from unittest import mock
from views.ca_acquisition import CaAcquisition


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
def ca_component(mock_user_input):
    with patch("views.ca_acquisition.CaAcquisition.__init__", return_value=None):
        component = CaAcquisition.__new__(CaAcquisition)
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


def test_component_initialization(ca_component):
    assert hasattr(ca_component, 'image_source')
    assert hasattr(ca_component, 'frame_interval')
    assert hasattr(ca_component, 'edgefinder')
    assert hasattr(ca_component, 'choose_files_button')


def test_update_frame_interval(ca_component, mock_user_input):
    ca_component.frame_interval.get_value = MagicMock(return_value=5)
    ca_component.update_frame_interval()
    assert mock_user_input.frame_interval == 5


def test_update_edgefinder(ca_component, mock_user_input):
    ca_component.edgefinder.get_value = MagicMock(return_value="sobel")
    ca_component.update_edgefinder()
    assert mock_user_input.edgefinder == "sobel"


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
