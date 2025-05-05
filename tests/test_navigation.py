import pytest
import sys
import os
from customtkinter import CTk, CTkFrame, CTkProgressBar
# Add project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from views.navigation import create_navigation

@pytest.fixture
def app():
    app = CTk()
    app.withdraw()  # Hide main window to avoid popup interference during tests
    yield app
    app.destroy()

def test_navigation_component_creation(app):
    next_stage, prev_stage = create_navigation(app)

    # Get all child widgets of the navigation frame
    navigation_frame = app.winfo_children()[0]
    children = navigation_frame.winfo_children()

    # Should contain one progress bar and four labels
    progress_bars = [c for c in children if isinstance(c, CTkProgressBar)]
    assert len(progress_bars) == 1, "There should be one progress bar"

    labels = [c for c in children if c.__class__.__name__ == "CTkLabel"]
    assert len(labels) == 4, "There should be four stage labels"

def test_navigation_stage_changes(app):
    next_stage, prev_stage = create_navigation(app)

    # Call next_stage and prev_stage multiple times to verify no errors (behavioral check only)
    for _ in range(3):
        next_stage()
    for _ in range(2):
        prev_stage()
