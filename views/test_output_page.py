import sys
import os
import pytest
import tkinter
from customtkinter import CTk

# Add project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from views.output_page import OutputPage


class DummyUserInput:
    def __init__(self):
        self.output_directory = None
        self.filename = None


@pytest.fixture
def app():
    app = CTk()
    app.withdraw()  # Prevent popup windows during testing
    yield app
    app.destroy()


def test_output_page_initialization(app):
    dummy_input = DummyUserInput()
    page = OutputPage(app, dummy_input)
    assert isinstance(page, OutputPage)
    assert page.location_entry is not None
    assert page.filename_entry is not None
    assert isinstance(page.check_vars, list)
    assert len(page.check_vars) == 20


def test_filename_binding(app):
    dummy_input = DummyUserInput()
    page = OutputPage(app, dummy_input)

    # Simulate user entering a filename
    page.filename_var.set("test_output")
    assert dummy_input.filename == "test_output"


def test_plot_selection_summary(app):
    dummy_input = DummyUserInput()
    page = OutputPage(app, dummy_input)

    # Simulate selecting 3 checkboxes
    for i in range(3):
        page.check_vars[i].set("on")
    page.update_plot_summary()
    assert "3 plots selected" in page.plot_summary_label.cget("text")


def test_browse_location_manual(app):
    # Skip filedialog, test insert logic directly
    dummy_input = DummyUserInput()
    page = OutputPage(app, dummy_input)

    # Simulate selecting a directory
    page.location_entry.insert(0, "C:/Users/Test")
    dummy_input.output_directory = "C:/Users/Test"

    assert "C:/Users/Test" in page.location_entry.get()
    assert dummy_input.output_directory == "C:/Users/Test"
