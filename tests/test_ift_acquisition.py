"""
Head‑less smoke tests for views.ift_acquisition.IftAcquisition
Requires only pytest + Pillow.
"""

# ---------- path & popup stubs ----------
import os, sys, types, tempfile, pytest
ROOT = os.path.abspath(os.path.join(__file__, "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

for m, cls in [
    ("views.component.ctk_input_popup", "CTkInputPopup"),
    ("views.component.ctk_table_popup", "CTkTablePopup"),
]:
    mod = types.ModuleType(m)
    setattr(mod, cls, type(cls, (), {}))
    sys.modules[m] = mod

# ---------- customtkinter stub ----------
ctk = types.ModuleType("customtkinter")
class _W:
    def __init__(self,*a,**k): pass
    def grid_rowconfigure(self,*a,**k): pass
    def grid_columnconfigure(self,*a,**k): pass
    def grid(self,*a,**k): pass
    def pack(self,*a,**k): pass
    def place(self,*a,**k): pass
    def destroy(self): pass
    def configure(self,**k): pass
    def cget(self,k): return ""
    def register(self,f): return f
    def winfo_children(self): return []
class CTk(_W):       pass
class CTkFrame(_W):  pass
class CTkLabel(_W):  pass
class CTkButton(_W):
    def __init__(self,*a,text="",**k):
        super().__init__(); self._t=text
    def configure(self,**k): self._t=k.get("text", self._t)
    def cget(self,k): return self._t if k=="text" else ""
class CTkEntry(_W):
    def bind(self,*a,**k): pass
    def insert(self,*a): pass
    def delete(self,*a): pass
    def get(self): return ""
class CTkOptionMenu(_W): pass
class CTkImage:
    def __init__(self,*a,**k): pass      # <- accepts args now
class _Var:
    def __init__(self,*_,value="",**__):
        self._v=value; self._cbs=[]
    def get(self): return self._v
    def set(self,v): self._v=v; [cb() for cb in self._cbs]
    def trace_add(self,mode,cb): self._cbs.append(cb)

for n,o in dict(CTk=CTk,CTkFrame=CTkFrame,CTkLabel=CTkLabel,
                CTkButton=CTkButton,CTkEntry=CTkEntry,
                CTkOptionMenu=CTkOptionMenu,CTkImage=CTkImage,
                StringVar=_Var).items():
    setattr(ctk,n,o)
sys.modules["customtkinter"] = ctk

# ---------- other dependency stubs ----------
cfg = types.ModuleType("utils.config")
cfg.FILE_SOURCE_OPTIONS_IFT=["Local images"]
cfg.IMAGE_TYPE=[("Image","*.jpg")]
cfg.PATH_TO_SCRIPT = ROOT
sys.modules["utils.config"] = cfg

ih = types.ModuleType("utils.image_handler")
class IH:
    @staticmethod
    def get_fitting_dimensions(w,h,max_width=400,max_height=300):
        scale=min(max_width/w,max_height/h,1)
        return int(w*scale), int(h*scale)
ih.ImageHandler = IH
sys.modules["utils.image_handler"] = ih

vmod = types.ModuleType("utils.validators")
vmod.validate_numeric_input = lambda *a,**k: True
sys.modules["utils.validators"] = vmod

sys.modules["tkinter.filedialog"] = types.ModuleType("tkinter.filedialog")
sys.modules["tkinter.messagebox"] = types.ModuleType("tkinter.messagebox")

# ---------- import target ----------
from PIL import Image
from pathlib import Path
from views import ift_acquisition
ift_acquisition.os = os
IftAcquisition = ift_acquisition.IftAcquisition

# ---------- fixtures ----------
@pytest.fixture(scope="session")
def imgs():
    files=[]
    for i in range(2):
        d=tempfile.mkdtemp(); p=Path(d)/f"img{i}.jpg"
        Image.new("RGB",(10,10)).save(p); files.append(str(p))
    return tuple(files)

class DummyUser:
    def __init__(self):
        self.image_source=None
        self.import_files=()
        self.number_of_frames=None
        self.frame_interval=""

@pytest.fixture
def widget(monkeypatch, imgs):
    sys.modules["tkinter.filedialog"].askopenfilenames=lambda **_:imgs
    root=CTk(); user=DummyUser()
    w=IftAcquisition(root,user)
    w.show_image_source_frame(cfg.FILE_SOURCE_OPTIONS_IFT[0])
    return w,user,imgs

# ---------- tests ----------
def test_select_files(widget):
    w,u,imgs = widget
    w.select_files()
    assert u.import_files == imgs and u.number_of_frames == 2
    assert "2" in w.choose_files_button.cget("text")

def test_frame_interval_var(widget):
    w,u,_ = widget
    w.frame_interval_var.set("4")
    assert u.frame_interval == "4"

def test_widget_type(widget):
    w,_,_ = widget
    assert isinstance(w, IftAcquisition)
