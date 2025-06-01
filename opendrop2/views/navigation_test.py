from opendrop2.views.navigation import create_navigation

from unittest.mock import MagicMock, patch
import pytest


@pytest.fixture
def app():
    with patch("views.navigation.CTk", return_value=MagicMock(name="MockCTk")), patch(
        "views.navigation.CTkFrame", return_value=MagicMock(name="MockFrame")
    ), patch(
        "views.navigation.CTkLabel", return_value=MagicMock(name="MockLabel")
    ), patch(
        "views.navigation.CTkProgressBar",
        return_value=MagicMock(name="MockProgressBar"),
    ):
        yield MagicMock(name="App")


def test_navigation_component_creation(app):
    next_stage, prev_stage = create_navigation(app)
    assert callable(next_stage)
    assert callable(prev_stage)


def test_navigation_stage_changes(app):
    next_stage, prev_stage = create_navigation(app)
    for _ in range(3):
        next_stage()
    for _ in range(2):
        prev_stage()
