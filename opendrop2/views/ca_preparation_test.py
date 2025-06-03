from opendrop2.views.ca_preparation import CaPreparation

from unittest.mock import patch, MagicMock
import pytest


@pytest.fixture
def dummy_user_input_data():
    return MagicMock()


@pytest.fixture
def dummy_experimental_drop():
    return MagicMock()


@pytest.fixture
def dummy_parent():
    return MagicMock()


@pytest.fixture
def fake_frame():
    return MagicMock()


def test_create_user_input_fields():
    with patch("opendrop2.views.ca_preparation.create_user_inputs_cm") as mock_create:
        mock_create.return_value = MagicMock()
        instance = MagicMock(spec=CaPreparation)
        instance.user_input_data = MagicMock()
        CaPreparation.create_user_input_fields(
            instance, parent_frame=mock_create.return_value
        )
        mock_create.assert_called_once()


def test_create_analysis_method_fields():
    with patch("opendrop2.views.ca_preparation.create_analysis_checklist_cm") as mock_create:
        mock_create.return_value = MagicMock()
        instance = MagicMock(spec=CaPreparation)
        instance.user_input_data = MagicMock()
        CaPreparation.create_analysis_method_fields(
            instance, parent_frame=mock_create.return_value
        )
        mock_create.assert_called_once()


def test_create_fitting_view_fields():
    with patch("opendrop2.views.ca_preparation.create_plotting_checklist") as mock_create:
        mock_create.return_value = MagicMock()
        instance = MagicMock(spec=CaPreparation)
        instance.user_input_data = MagicMock()
        CaPreparation.create_fitting_view_fields(
            instance, parent_frame=mock_create.return_value
        )
        mock_create.assert_called_once()
