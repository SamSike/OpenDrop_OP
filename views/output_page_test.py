from views.output_page import OutputPage

from unittest import mock
import pytest


class DummyUserInput:
    def __init__(self):
        self.output_directory = None
        self.filename = None


@pytest.fixture
def output_page():
    dummy_input = DummyUserInput()

    # Completely bypass __init__
    page = OutputPage.__new__(OutputPage)

    # Inject only the attributes we need for testing
    page.user_input_data = dummy_input
    page.location_entry = mock.Mock()
    page.filename_var = mock.Mock()
    page.plot_summary_label = mock.Mock()
    page.check_vars = [mock.Mock(get=mock.Mock(
        return_value="on")) for _ in range(3)]

    return page, dummy_input


def test_browse_location_manual(output_page):
    page, dummy_input = output_page

    page.location_entry.get.return_value = "C:/Users/Test"
    dummy_input.output_directory = "C:/Users/Test"

    assert page.location_entry.get() == "C:/Users/Test"
    assert dummy_input.output_directory == "C:/Users/Test"


def test_on_filename_change(output_page):
    page, dummy_input = output_page

    page.filename_var.get.return_value = "result_file"
    page.on_filename_change()
    assert dummy_input.filename == "result_file"
