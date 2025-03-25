import pytest
import os
import sys
import tkinter as tk

# pip install pytest-mock

# Ensure the parent directory is in the path for importing `conan`
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))
from conan import clear_screen, pause_wait_time, quit_, cheeky_pause, main


# Fixture to mock os.system (for clear_screen)
@pytest.fixture
def mock_system(mocker):
    return mocker.patch("os.system")


# Test the clear_screen function
def test_clear_screen(mock_system):
    clear_screen()
    mock_system.assert_called_once_with('cls' if os.name == 'nt' else 'clear')


# Fixture to mock time.sleep (for pause_wait_time)
@pytest.fixture
def mock_sleep(mocker):
    return mocker.patch("time.sleep")


# Test the pause_wait_time function when elapsed time is already greater than the pause time.
def test_pause_wait_time_longer_elapsed(mock_sleep):
    pause_wait_time(2, 1)
    mock_sleep.assert_not_called()


# Test the pause_wait_time function when elapsed time is less than the pause time.
def test_pause_wait_time_shorter_elapsed(mock_sleep):
    pause_wait_time(1, 2)
    mock_sleep.assert_called_once_with(1)


# Fixture to mock tkinter.Tk, Button, and Frame (for cheeky_pause)
@pytest.fixture
def mock_tkinter(mocker):
    # Mock tkinter components
    mock_tk = mocker.patch("tkinter.Tk")
    mock_button = mocker.patch("tkinter.Button")
    mock_frame = mocker.patch("tkinter.Frame")
    
    # Mock the root Tk instance
    mock_root = mocker.MagicMock()
    mock_tk.return_value = mock_root

    # Create a mock instance of Frame
    mock_frame_instance = mocker.MagicMock()
    mock_frame.return_value = mock_frame_instance

    return mock_tk, mock_button, mock_frame, mock_root, mock_frame_instance


# Test the cheeky_pause function
def test_cheeky_pause(mock_tkinter):
    mock_tk, mock_button, mock_frame, mock_root, mock_frame_instance = mock_tkinter
    cheeky_pause()

    mock_tk.assert_called_once()  # Check Tk() was called once
    mock_frame.assert_called_once_with(mock_root)  # Ensure Frame was created with root
    mock_button.assert_called_once_with(mock_frame_instance)  # Ensure Button was created with the frame instance
    mock_root.mainloop.assert_called_once()  # Check mainloop was called once


# Fixture to mock all the functions used in the main test
@pytest.fixture
def mock_main_dependencies(mocker):
    # Mock external functions used in main()
    mock_call_user_input = mocker.patch('conan.call_user_input')
    mock_get_image = mocker.patch('conan.get_image')
    mock_set_drop_region = mocker.patch('conan.set_drop_region')
    mock_extract_drop_profile = mocker.patch('conan.extract_drop_profile')
    mock_set_surface_line = mocker.patch('conan.set_surface_line')
    mock_perform_fits = mocker.patch('conan.perform_fits')
    mock_correct_tilt = mocker.patch('conan.correct_tilt')
    mock_join = mocker.patch('conan.os.path.join', return_value='/mocked/path/export.csv')

    return {
        'mock_call_user_input': mock_call_user_input,
        'mock_get_image': mock_get_image,
        'mock_set_drop_region': mock_set_drop_region,
        'mock_extract_drop_profile': mock_extract_drop_profile,
        'mock_set_surface_line': mock_set_surface_line,
        'mock_perform_fits': mock_perform_fits,
        'mock_correct_tilt': mock_correct_tilt,
        'mock_join': mock_join,
    }


# Test the main function
def test_main(mock_main_dependencies, mocker):
    # Extract mock dependencies from the fixture
    mock_call_user_input = mock_main_dependencies['mock_call_user_input']
    mock_get_image = mock_main_dependencies['mock_get_image']
    mock_set_drop_region = mock_main_dependencies['mock_set_drop_region']
    mock_extract_drop_profile = mock_main_dependencies['mock_extract_drop_profile']
    mock_set_surface_line = mock_main_dependencies['mock_set_surface_line']
    mock_perform_fits = mock_main_dependencies['mock_perform_fits']
    mock_correct_tilt = mock_main_dependencies['mock_correct_tilt']
    mock_join = mock_main_dependencies['mock_join']

    from conan import main, ExperimentalSetup, ExtractedData, DropData, Tolerances
    
    # Mock experimental setup
    user_inputs = mocker.MagicMock()
    user_inputs.number_of_frames = 2
    user_inputs.import_files = ['image1.png', 'image2.png']
    user_inputs.ML_boole = False

    mocker.patch('conan.ExperimentalSetup', return_value=user_inputs)
    mocker.patch('conan.ExtractedData', return_value=mocker.MagicMock())
    mocker.patch('conan.ExperimentalDrop')
    mocker.patch('conan.timeit.default_timer', side_effect=[0, 1, 2])
    
    main()

    # Check if key functions are called
    mock_call_user_input.assert_called_once()
    assert mock_get_image.call_count == 2
    assert mock_set_drop_region.call_count == 2
    assert mock_extract_drop_profile.call_count == 2
    assert mock_set_surface_line.call_count == 2
    assert not mock_correct_tilt.called  # Should not be called when ML_boole is False


# Example of using pytest's parametrize for a simple test
@pytest.mark.parametrize("input_val, expected", [(2, 3), (4, 5), (7, 8)])
def test_example(input_val, expected):
    assert input_val + 1 == expected
