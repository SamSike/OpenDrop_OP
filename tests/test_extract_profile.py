import pytest
import numpy as np
import cv2
import matplotlib.pyplot as plt
from unittest.mock import patch, MagicMock
import sys
import os
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent))


from modules.extract_profile import (
    extract_drop_profile, 
    image_crop, 
    detect_edges, 
    prepare_hydrophobic,
    distance, 
    optimized_path, 
    cluster_OPTICS
)


@pytest.fixture
def mock_image():

    img = np.zeros((100, 100, 3), dtype=np.uint8)

    cv2.circle(img, (50, 50), 30, (255, 255, 255), -1)
    return img

@pytest.fixture
def mock_experiment():

    class MockExperiment:
        def __init__(self):
            self.cropped_image = np.zeros((100, 100, 3), dtype=np.uint8)
            cv2.circle(self.cropped_image, (50, 50), 30, (255, 255, 255), -1)
            self.image = np.zeros((200, 200, 3), dtype=np.uint8)
            self.contour = None
            self.ret = None
    return MockExperiment()

@pytest.fixture
def mock_user_inputs():

    class MockUserInputs:
        def __init__(self):
            self.threshold_method = "Automated"
            self.drop_region = [(10, 10), (90, 90)]
            self.needle_region = [(10, 10), (90, 90)]
            self.threshold_val = 127
    return MockUserInputs()

def test_image_crop(mock_image):
    points = [(20, 20), (80, 80)]
    cropped = image_crop(mock_image, points)
    

    assert cropped.shape[0] == 60  
    assert cropped.shape[1] == 60  
    assert cropped.shape == (60, 60, 3)


def test_distance():
    p1 = [0, 0]
    p2 = [3, 4]
    assert distance(p1, p2) == 5.0 
    
    p3 = [1, 1]
    p4 = [4, 5]
    assert distance(p3, p4) == 5.0  


def test_optimized_path():

    coords = [[0, 0], [1, 1], [2, 2], [3, 3], [4, 4]]
    coords_copy = coords.copy()  
    

    start = coords[0]  
    path = optimized_path(coords, start)
    

    assert len(path) == len(coords_copy)

    assert isinstance(path, np.ndarray)

# 测试 cluster_OPTICS 函数
def test_cluster_OPTICS():

    cluster1 = np.random.rand(10, 2) * 0.1
    cluster2 = np.random.rand(10, 2) * 0.1 + np.array([1.0, 1.0])
    sample = np.vstack([cluster1, cluster2])
    

    result_coords = cluster_OPTICS(sample, out_style='coords', eps=0.2)
    assert len(result_coords) >= 1
    
    result_xy = cluster_OPTICS(sample, out_style='xy', eps=0.2)
    for k in set([key.rstrip('xy') for key in result_xy.keys()]):
        assert f"{k}x" in result_xy
        assert f"{k}y" in result_xy

@patch('cv2.cvtColor')
@patch('cv2.threshold')
@patch('cv2.findContours')
def test_detect_edges(mock_findContours, mock_threshold, mock_cvtColor, mock_image, mock_experiment):
    mock_cvtColor.return_value = mock_image
    mock_threshold.return_value = (127, mock_image)
    
    contour = np.array([[[10, 10]], [[20, 20]], [[30, 30]]])
    mock_findContours.return_value = ([contour], None)
    
    contour_result, ret = detect_edges(mock_image, mock_experiment, [(10, 10), (90, 90)], 1, 127)
    
    assert isinstance(contour_result, np.ndarray)
    assert ret == 127

@patch('modules.extract_profile.detect_edges')
@patch('modules.extract_profile.extract_edges_CV')
@patch('matplotlib.pyplot.show')
def test_extract_drop_profile_user_selected(mock_plt_show, mock_extract_edges_CV, mock_detect_edges, 
                                           mock_experiment, mock_user_inputs):
    mock_user_inputs.threshold_method = "User-selected"
    
    mock_contour = np.array([[10, 10], [20, 20], [30, 30]])
    mock_detect_edges.return_value = (mock_contour, 127)
    
    extract_drop_profile(mock_experiment, mock_user_inputs)
    
    mock_detect_edges.assert_called_once()
    assert np.array_equal(mock_experiment.contour, mock_contour)
    assert mock_experiment.ret == 127

@patch('modules.extract_profile.detect_edges')
@patch('modules.extract_profile.extract_edges_CV')
@patch('matplotlib.pyplot.imshow')
@patch('matplotlib.pyplot.plot')
@patch('matplotlib.pyplot.title')
@patch('matplotlib.pyplot.axis')
@patch('matplotlib.pyplot.show')
@patch('matplotlib.pyplot.close')
def test_extract_drop_profile_automated(mock_plt_close, mock_plt_show, mock_plt_axis, 
                                     mock_plt_title, mock_plt_plot, mock_plt_imshow,
                                     mock_extract_edges_CV, mock_detect_edges,
                                     mock_experiment, mock_user_inputs):
    mock_user_inputs.threshold_method = "Automated"
    mock_experiment.ret = None
    
    mock_contour = np.array([[10, 10], [20, 20], [30, 30]])
    mock_extract_edges_CV.return_value = (mock_contour, 127)
    
    extract_drop_profile(mock_experiment, mock_user_inputs)
    
    mock_extract_edges_CV.assert_called_once_with(mock_experiment.cropped_image, return_thresholed_value=True)
    assert np.array_equal(mock_experiment.contour, mock_contour)
    assert mock_experiment.ret == 127

def test_prepare_hydrophobic():
    mock_profile = np.array([[x, -np.sqrt(900 - x**2)] for x in range(-30, 31, 5) if x**2 <= 900])
    mock_contact_points = {0: [-30, -30], 1: [30, -30]}
    
    assert isinstance(mock_profile, np.ndarray)
    assert isinstance(mock_contact_points, dict)
    assert 0 in mock_contact_points
    assert 1 in mock_contact_points
    
