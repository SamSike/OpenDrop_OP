from modules.image.select_regions import (
    set_drop_region,
    set_surface_line,
    correct_tilt,
    user_line,
    draw_rectangle,
    draw_line,
    optimized_path,
    intersection,
    ML_prepare_hydrophobic,
)
from modules.core.classes import ExperimentalSetup, ExperimentalDrop
from modules.preprocessing.preprocessing import prepare_hydrophobic
from modules.fitting.fits import perform_fits
from utils.enums import RegionSelect, ThresholdSelect

from itertools import cycle
from unittest.mock import patch, MagicMock
from numpy.testing import assert_array_equal
import numpy as np
import unittest
import cv2
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class TestSelectRegions(unittest.TestCase):

    @patch("modules.preprocessing.preprocessing.auto_crop")
    def test_set_drop_region_auto(self, mock_auto_crop: MagicMock):
        # Create mock return value
        # Simulate a blank image of size 100x100
        mock_image = np.zeros((100, 100, 3))
        mock_auto_crop.return_value = (
            mock_image,
            (10, 90, 20, 80),
        )  # Simulate cropping result

        # Simulate experimental_drop and experimental_setup objects
        experimental_drop = ExperimentalDrop()
        experimental_drop.image = mock_image
        experimental_setup = ExperimentalSetup()
        experimental_setup.drop_id_method = RegionSelect.AUTOMATED
        experimental_setup.screen_resolution = [1, 1]

        # Call the function to be tested
        set_drop_region(experimental_drop, experimental_setup, index=0)

        # Check if auto_crop was called correctly
        mock_auto_crop.assert_called_once_with(mock_image)

        # Verify if experimental_drop handled auto_crop's return value correctly
        self.assertTrue(np.array_equal(experimental_drop.cropped_image, mock_image))
        self.assertEqual(experimental_setup.drop_region, [(10, 20), (90, 80)])

    @patch("modules.image.select_regions.user_roi")
    @patch("modules.image.select_regions.image_crop")
    def test_set_drop_region_user_selected(
        self, mock_image_crop: MagicMock, mock_user_roi: MagicMock
    ):
        # Create mock return value
        # Simulate a blank image of size 100x100
        mock_image = np.zeros((100, 100, 3))
        # Simulate the user-selected region
        mock_user_roi.return_value = [(10, 20), (90, 80)]

        # Simulate the cropped image as a 3D array
        # Assume the cropped result is still 3D
        mock_cropped_image = np.zeros((60, 80, 3))
        mock_image_crop.return_value = mock_cropped_image

        # Simulate experimental_drop and experimental_setup objects
        experimental_drop = ExperimentalDrop()
        experimental_drop.image = mock_image
        experimental_setup = ExperimentalSetup()
        experimental_setup.drop_id_method = RegionSelect.USER_SELECTED
        experimental_setup.screen_resolution = [1, 1]

        # Call the function to be tested
        set_drop_region(experimental_drop, experimental_setup, index=1)

        # Check if user_roi was called correctly
        mock_user_roi.assert_called_once_with(
            mock_image, "Select drop region for Image 1", 0.008, [0, 0]
        )

        # Verify if image_crop was called correctly
        mock_image_crop.assert_called_once_with(mock_image, [(10, 20), (90, 80)])

        # Check if experimental_drop and experimental_setup handled user_roi's return value correctly
        self.assertEqual(experimental_setup.drop_region, [(10, 20), (90, 80)])
        self.assertEqual(
            experimental_drop.cropped_image.shape, (60, 80, 3)
        )  # Verify the cropped image size


class TestSurfaceLine(unittest.TestCase):

    @patch("modules.image.select_regions.prepare_hydrophobic")
    @patch("modules.preprocessing.preprocessing.optimized_path")
    def test_set_surface_line_auto(self, mock_optimized_path, mock_prepare_hydrophobic):
        # Simulate optimized_path return value to ensure enough data points for distance calculation
        mock_optimized_path.return_value = np.array(
            [[0, 0], [1, 2], [2, 4], [3, 6], [4, 8], [5, 10]]
        )

        # Create mock return values
        mock_contour = np.array(
            [[0, 0], [1, 2], [2, 4], [3, 6], [4, 8], [5, 10]]
        )  # Using more contour points
        mock_contact_points = {0: [0, 0], 1: [5, 10]}
        mock_prepare_hydrophobic.return_value = (mock_contour, mock_contact_points)

        # Simulate experimental_drop and experimental_setup objects
        experimental_drop = MagicMock()
        experimental_drop.contour = mock_contour
        experimental_setup = MagicMock()
        experimental_setup.baseline_method = ThresholdSelect.AUTOMATED

        # Call the function to be tested
        set_surface_line(experimental_drop, experimental_setup)

        # Check if prepare_hydrophobic was called correctly
        mock_prepare_hydrophobic.assert_called_once_with(mock_contour)

        # Verify if the return values were handled correctly
        self.assertTrue(np.array_equal(experimental_drop.drop_contour, mock_contour))
        self.assertEqual(experimental_drop.contact_points, mock_contact_points)


class TestCorrectTilt(unittest.TestCase):

    @patch("modules.image.select_regions.tilt_correction")
    def test_correct_tilt_auto(self, mock_tilt_correction):
        # Create mock return value
        mock_cropped_image = np.zeros((100, 100, 3))
        mock_tilt_correction.return_value = mock_cropped_image

        # Simulate experimental_drop and experimental_setup objects
        experimental_drop = MagicMock()
        experimental_drop.cropped_image = mock_cropped_image
        experimental_drop.contact_points = [(10, 20), (90, 80)]
        experimental_setup = MagicMock()
        experimental_setup.baseline_method = ThresholdSelect.AUTOMATED

        # Call the function to be tested
        correct_tilt(experimental_drop, experimental_setup)

        # Check if tilt_correction was called correctly
        mock_tilt_correction.assert_called_once_with(
            mock_cropped_image, [(10, 20), (90, 80)]
        )

        # Verify if the return values were handled correctly
        self.assertTrue(
            np.array_equal(experimental_drop.cropped_image, mock_cropped_image)
        )


class TestDrawRectangle(unittest.TestCase):

    @patch("modules.image.select_regions.cv2.rectangle")
    @patch.dict(
        "modules.image.select_regions.__dict__",
        {"image_TEMP": np.zeros((100, 100, 3)), "img": np.zeros((100, 100, 3))},
    )
    def test_draw_rectangle(self, mock_rectangle):
        global drawing, ix, iy, fx, fy
        # Initialize local variables
        drawing = False
        ix, iy = 0, 0
        fx, fy = 0, 0

        # Simulate mouse button down event
        draw_rectangle(cv2.EVENT_LBUTTONDOWN, 10, 20, None, None)
        # No rectangle should be drawn when mouse is pressed down
        mock_rectangle.assert_not_called()

        # Simulate mouse move event, cv2.rectangle should be called
        draw_rectangle(cv2.EVENT_MOUSEMOVE, 30, 40, None, None)
        called_args = mock_rectangle.call_args
        assert np.array_equal(
            called_args[0][0], np.zeros((100, 100, 3))
        )  # Manually compare numpy arrays
        assert called_args[0][1] == (10, 20)
        assert called_args[0][2] == (30, 40)
        assert called_args[0][3] == (0, 0, 255)
        assert called_args[0][4] == 2

        # Simulate mouse button release event, cv2.rectangle should be called again
        draw_rectangle(cv2.EVENT_LBUTTONUP, 50, 60, None, None)
        called_args = mock_rectangle.call_args
        assert np.array_equal(
            called_args[0][0], np.zeros((100, 100, 3))
        )  # Manually compare numpy arrays
        assert called_args[0][1] == (10, 20)
        assert called_args[0][2] == (50, 60)
        assert called_args[0][3] == (0, 255, 0)
        assert called_args[0][4] == 2


class TestDrawLine(unittest.TestCase):

    @patch("modules.image.select_regions.cv2.line")
    @patch.dict(
        "modules.image.select_regions.__dict__",
        {"image_TEMP": np.zeros((100, 100, 3)), "img": np.zeros((100, 100, 3))},
    )
    def test_draw_line(self, mock_line):
        global drawing, ix, iy, fx, fy
        # Initialize local variables
        drawing = False
        ix, iy = 0, 0
        fx, fy = 0, 0

        # Simulate mouse button down event
        draw_line(cv2.EVENT_LBUTTONDOWN, 10, 20, None, None)
        mock_line.assert_not_called()  # No line should be drawn when mouse is pressed down

        # Simulate mouse move event, cv2.line should be called
        draw_line(cv2.EVENT_MOUSEMOVE, 30, 40, None, None)
        args, kwargs = mock_line.call_args
        # Compare first argument
        assert_array_equal(args[0], np.zeros((100, 100, 3)))
        self.assertEqual(args[1], (10, 20))  # Compare start point
        self.assertEqual(args[2], (30, 40))  # Compare end point
        self.assertEqual(args[3], (0, 0, 255))  # Compare color
        self.assertEqual(args[4], 2)  # Compare line thickness

        # Simulate mouse button release event, cv2.line should be called again
        draw_line(cv2.EVENT_LBUTTONUP, 50, 60, None, None)
        args, kwargs = mock_line.call_args
        # Compare first argument
        assert_array_equal(args[0], np.zeros((100, 100, 3)))
        self.assertEqual(args[1], (10, 20))  # Compare start point
        self.assertEqual(args[2], (50, 60))  # Compare end point
        self.assertEqual(args[3], (0, 255, 0))  # Compare color
        self.assertEqual(args[4], 2)  # Compare line thickness


class TestOptimizedPath(unittest.TestCase):

    def test_optimized_path_with_mock_distance(self):
        coords = [(0, 0), (1, 2), (3, 4), (5, 6)]
        start = (0, 0)

        # Use patch to mock the behavior of distance function
        with patch(
            "modules.image.select_regions.distance", side_effect=cycle([1])
        ) as mock_distance:
            result = optimized_path(coords, start)

            # Add debug output
            print("Distance call count:", mock_distance.call_count)

            # Expected call count is 6 times
            self.assertEqual(mock_distance.call_count, 6)

    def test_optimized_path_without_start(self):
        coords = [(0, 0), (1, 2), (3, 4), (5, 6)]

        # Verify when start is not provided, it defaults to the first point
        result = optimized_path(coords)
        expected_result = np.array([(0, 0), (1, 2), (3, 4), (5, 6)])
        np.testing.assert_array_equal(result, expected_result)

    def test_optimized_path_with_single_point(self):
        coords = [(0, 0)]

        # Handle the case of a single point, the result should return the input single point
        result = optimized_path(coords)
        expected_result = np.array([(0, 0)])
        np.testing.assert_array_equal(result, expected_result)


if __name__ == "__main__":
    unittest.main()
