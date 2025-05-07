import pytest
import tkinter as tk
from PIL import Image
from unittest.mock import patch, MagicMock
from views.ift_acquisition import IftAcquisition



@pytest.fixture
def dummy_user_input_data(tmp_path):
    class DummyData:
        import_files = [str(tmp_path / "test_image.png")]
        number_of_frames = 1
        frame_interval = ""
        cv2_capture_num = ""
        genlcam_capture_num = ""
        image_source = "Local images"

    img = Image.new("RGB", (100, 100), color='white')
    img.save(tmp_path / "test_image.png")
    return DummyData()



@pytest.fixture
def ift_acquisition_instance(dummy_user_input_data):
    root = tk.Tk()
    root.withdraw()

    with patch("views.ift_acquisition.CTkImage", MagicMock()), \
         patch("views.ift_acquisition.CTkLabel", MagicMock()), \
         patch("views.ift_acquisition.CTkEntry", MagicMock()), \
         patch("views.ift_acquisition.CTkButton", MagicMock()), \
         patch("views.ift_acquisition.CTkOptionMenu", MagicMock()), \
         patch("views.ift_acquisition.CTkFrame", MagicMock()), \
         patch("views.ift_acquisition.set_light_only_color", MagicMock()):

        app = IftAcquisition(root, dummy_user_input_data)


        app.index_entry = MagicMock()
        app.index_entry.get.return_value = "1"
        app.index_entry.delete = MagicMock()
        app.index_entry.insert = MagicMock()
        app.image_label = MagicMock()
        app.tk_image = MagicMock()
        app.current_image = Image.new("RGB", (100, 100))
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
