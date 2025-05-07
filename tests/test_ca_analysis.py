"""
tests for views.ca_analysis.CaAnalysis

• Works with the current OpenDrop_OP directory layout
  (ca_analysis.py lives in views/).
• Stubs out every external dependency so the tests pass
  even on a fresh environment.
"""

# ------------------------------------------------------------------
# 1) Ensure the project root is on PYTHONPATH  ----------------------
# ------------------------------------------------------------------
import sys, os
PROJECT_ROOT = os.path.abspath(os.path.join(__file__, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ------------------------------------------------------------------
# 2) Monkey‑patch external modules that ca_analysis imports ---------
# ------------------------------------------------------------------
import types

# --- utils.config --------------------------------------------------
cfg = types.ModuleType("utils.config")
cfg.LEFT_ANGLE = "left angle"
cfg.RIGHT_ANGLE = "right angle"
sys.modules["utils.config"] = cfg

# --- utils.image_handler ------------------------------------------
class _DummyIH:
    def get_fitting_dimensions(self, w, h):
        return w, h
ih_mod = types.ModuleType("utils.image_handler")
ih_mod.ImageHandler = _DummyIH
sys.modules["utils.image_handler"] = ih_mod

# --- utils.validators (placeholder) --------------------------------
sys.modules["utils.validators"] = types.ModuleType("utils.validators")

# --- views.helper.theme -------------------------------------------
theme_mod = types.ModuleType("views.helper.theme")
theme_mod.get_system_text_color = lambda: "black"
sys.modules["views.helper.theme"] = theme_mod

# --- views.component.CTkXYFrame -----------------------------------
from customtkinter import CTkFrame
xy_mod = types.ModuleType("views.component.CTkXYFrame")
class CTkXYFrame(CTkFrame):     # type: ignore
    pass
xy_mod.CTkXYFrame = CTkXYFrame
sys.modules["views.component.CTkXYFrame"] = xy_mod

# ------------------------------------------------------------------
# 3) Import the module under test -----------------------------------
# ------------------------------------------------------------------
from views.ca_analysis import CaAnalysis

# ------------------------------------------------------------------
# 4) Pytest fixtures & helpers --------------------------------------
# ------------------------------------------------------------------
import tempfile, pytest, numpy as np
from PIL import Image
from customtkinter import CTk

@pytest.fixture(scope="session")
def dummy_image_path():
    """Create a throw‑away RGB image; return its path."""
    tmpdir = tempfile.mkdtemp()
    fpath = os.path.join(tmpdir, "dummy.jpg")
    Image.new("RGB", (100, 80), "white").save(fpath)
    return fpath

class DummyUserInput:
    """Only the attributes accessed by CaAnalysis are provided."""
    def __init__(self, img_path):
        self.analysis_methods_ca = {"tangent fit": True}
        self.import_files = [img_path]
        self.number_of_frames = 1

@pytest.fixture
def tk_root():
    root = CTk()
    root.withdraw()
    yield root
    root.destroy()

# ------------------------------------------------------------------
# 5) Minimal dummy output objects -----------------------------------
# ------------------------------------------------------------------
class DummyExtractedData:
    def __init__(self):
        self.contact_angles = {
            "tangent fit": {
                "left angle": 42.0,
                "right angle": 48.0,
                "contact points": [(0, 0), (1, 1)],
                "tangent lines": (((0, 0), (10, 10)), ((0, 0), (10, -10))),
            }
        }

class DummyExperimentalDrop:
    def __init__(self):
        self.cropped_image = np.zeros((40, 40, 3), dtype=np.uint8)

# ------------------------------------------------------------------
# 6) Tests ----------------------------------------------------------
# ------------------------------------------------------------------
def test_init_smoke(tk_root, dummy_image_path):
    """CaAnalysis instantiates without raising and basic fields exist."""
    ui = DummyUserInput(dummy_image_path)
    page = CaAnalysis(tk_root, ui)

    assert isinstance(page.current_index, int)
    assert page.left_angles == [] and page.right_angles == []


def test_receive_output_updates_lists(tk_root, dummy_image_path):
    ui = DummyUserInput(dummy_image_path)
    page = CaAnalysis(tk_root, ui)

    page.receive_output(DummyExtractedData(), DummyExperimentalDrop())

    assert page.left_angles == [42.0]
    assert page.right_angles == [48.0]
    assert len(page.output) == 1


def test_display_line_chart_handles_empty(tk_root, dummy_image_path):
    """Calling display_line_chart with no data should not crash."""
    ui = DummyUserInput(dummy_image_path)
    page = CaAnalysis(tk_root, ui)

    # Should gracefully show 'No angle data'
    page.display_line_chart()
    assert "No angle data" in page.image_label.cget("text")
