from opendrop2.views.ift_analysis import IftAnalysis

from unittest.mock import patch, MagicMock
import pytest
import matplotlib

matplotlib.use("Agg")


@pytest.fixture
def dummy_data():
    from opendrop2.modules.core.classes import ExperimentalSetup

    data = ExperimentalSetup()
    data.import_files = ["img1.bmp", "img2.bmp"]
    data.number_of_frames = 2
    return data


@pytest.fixture
def instance(dummy_data):
    with patch("opendrop2.views.ift_analysis.IftAnalysis.__init__", return_value=None):
        obj = IftAnalysis()
        obj.user_input_data = dummy_data
        obj.output = []
        obj.preformed_methods = {}
        obj.table_data = []
        return obj


def test_create_results_tab(instance):
    instance.create_results_tab = MagicMock()
    instance.create_results_tab(MagicMock())
    instance.create_results_tab.assert_called()


def test_create_table(instance):
    instance.create_table = MagicMock()
    instance.create_table(MagicMock())
    instance.create_table.assert_called()


def test_create_image_frame(instance):
    instance.create_image_frame = MagicMock()
    instance.create_image_frame(MagicMock())
    instance.create_image_frame.assert_called()


def test_create_residuals_frame(instance):
    instance.create_residuals_frame = MagicMock()
    instance.create_residuals_frame(MagicMock())
    instance.create_residuals_frame.assert_called()


def test_create_graph_tab(instance):
    instance.create_graph_tab = MagicMock()
    instance.create_graph_tab(MagicMock())
    instance.create_graph_tab.assert_called()
