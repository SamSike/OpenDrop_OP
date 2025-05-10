import pytest
import tkinter as tk
from unittest.mock import patch, MagicMock
from views.ift_acquisition import IftAcquisition


@pytest.fixture
def dummy_user_input_data():
    class DummyData:
        import_files = ["dummy/path/image.png"]
        number_of_frames = 1
        frame_interval = "0"
        cv2_capture_num = ""
        genlcam_capture_num = ""
        image_source = "Local images"
    return DummyData()




@pytest.fixture
def ift_acquisition_instance(dummy_user_input_data):
    with patch("views.ift_acquisition.IftAcquisition.__init__", return_value=None), \
         patch("views.ift_acquisition.Image.open", return_value=MagicMock()):

        app = IftAcquisition.__new__(IftAcquisition)

        app.user_input_data = dummy_user_input_data
        app.current_index = 0
        app.index_entry = MagicMock()
        app.index_entry.get.return_value = "1"
        app.index_entry.delete = MagicMock()
        app.index_entry.insert = MagicMock()
        app.image_label = MagicMock()
        app.tk_image = MagicMock()
        app.current_image = MagicMock()
        return app





def test_update_index_entry(ift_acquisition_instance):
    ift_acquisition_instance.current_index = 0
    ift_acquisition_instance.update_index_entry()
    ift_acquisition_instance.index_entry.delete.assert_called_once()
    ift_acquisition_instance.index_entry.insert.assert_called_once_with(0, "1")


def test_update_index_from_entry_valid(ift_acquisition_instance):
    ift_acquisition_instance.index_entry.get.return_value = "1"
    ift_acquisition_instance.update_index_from_entry()
    assert ift_acquisition_instance.current_index == 0


def test_update_index_from_entry_invalid(ift_acquisition_instance, capsys):
    ift_acquisition_instance.index_entry.get.return_value = "abc"
    ift_acquisition_instance.update_index_from_entry()
    captured = capsys.readouterr()
    assert "Invalid input" in captured.out
