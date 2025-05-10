from customtkinter import *
from utils.config import *
from views.component.option_menu import OptionMenu
from views.component.float_entry import FloatEntry
from views.component.float_combobox import FloatCombobox
from views.component.check_button import CheckButton
from views.helper.style import set_light_only_color
from utils.enums import FittingMethod
from utils.tooltip_util import create_tooltip
LABEL_WIDTH = 200  # Adjust as needed

# ift [User Input]
def create_user_input_fields_ift(self, parent, user_input_data):
    """Create user input fields and return the frame containing them."""
    user_input_frame = CTkFrame(parent)
    set_light_only_color(user_input_frame, "innerframe")
    user_input_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=15, pady=15)

    # Configure the grid for the user_input_frame to be resizable
    user_input_frame.grid_rowconfigure(0, weight=0)  # No resizing for the label row
    user_input_frame.grid_rowconfigure(1, weight=1)  # Allow resizing for the input fields row
    user_input_frame.grid_columnconfigure(0, weight=1)  # Allow resizing for the first column
    user_input_frame.grid_columnconfigure(1, weight=1)  # Allow resizing for the second column

    # Create a label for the dynamic content
    label = CTkLabel(user_input_frame, text="User Inputs", font=("Roboto", 16, "bold"))
    label.grid(row=0, column=0, padx=10, pady=5, sticky="w")  # Grid for label

    # Create a frame to hold all input fields
    input_fields_frame = CTkFrame(user_input_frame)
    set_light_only_color(input_fields_frame, "entry")
    input_fields_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew", columnspan=2)  # Grid for input fields frame

    # Configure the grid of the input_fields_frame to be resizable
    for i in range(6):
        input_fields_frame.grid_rowconfigure(i, weight=1)
    input_fields_frame.grid_columnconfigure(0, weight=0)  # Label column fixed width (anchor='w' handles alignment)
    input_fields_frame.grid_columnconfigure(1, weight=1)  # Widget column expands

    # Update the input value functions
    def update_drop_region_method(*args):
        user_input_data.drop_ID_method = self.drop_region_method.get_value()
        self.image_app.update_image_processing_button()

    def update_needle_region_method(*args):
        user_input_data.needle_region_method = self.needle_region_method.get_value()

    def update_drop_density(*args):
        user_input_data.drop_density = self.drop_density_method.get_value() 

    def update_continuous_density(*args):
        user_input_data.density_outer = self.continuous_density.get_value()       

    def update_needle_diameter(*args):
        user_input_data.needle_diameter_mm = self.needle_diameter.get_value()       

    def update_pixel_mm(*args):
        user_input_data.pixel_mm = self.pixel_mm.get_value()      

    # Add input widgets with lambda functions for updates
    self.drop_region_method = OptionMenu(
        self, input_fields_frame, "Drop Region:", AUTO_MANUAL_OPTIONS, lambda *args: update_drop_region_method(*args), rw=0,
        default_value=user_input_data.drop_ID_method
    )
    self.drop_region_method.optionmenu.grid_configure(sticky="ew")

    self.needle_region_method = OptionMenu(
        self, input_fields_frame, "Needle Region:", AUTO_MANUAL_OPTIONS, lambda *args: update_needle_region_method(*args), rw=1,
        default_value=user_input_data.needle_region_method
    )
    self.needle_region_method.optionmenu.grid_configure(sticky="ew")

    self.drop_density_method = FloatEntry(
        self, input_fields_frame, "Drop Density(kg/m³):", lambda *args: update_drop_density(*args), rw=2,
        default_value=user_input_data.drop_density
    )

    self.continuous_density = FloatEntry(
        self, input_fields_frame, "Continuous density (kg/m):", lambda *args: update_continuous_density(*args), rw=3,
        default_value=user_input_data.density_outer
    )

    self.needle_diameter = FloatCombobox(
        self, input_fields_frame, "Needle diameter (mm):", NEEDLE_OPTIONS,
        lambda *args: update_needle_diameter(*args), rw=4, default_value=user_input_data.needle_diameter_mm
    )

    self.pixel_mm = FloatEntry(
        self, input_fields_frame, "Pixel scale(px/mm):", lambda *args: update_pixel_mm(*args), rw=5,
        default_value=user_input_data.pixel_mm
    )

    create_tooltip(self.drop_region_method.label, "The method to detect the droplet region.")
    create_tooltip(self.needle_region_method.label, "The method to detect the needle region.")
    create_tooltip(self.drop_density_method.label, "The density of the droplet in kg/m³. Used for interfacial tension calculation.")
    create_tooltip(self.continuous_density.label, "The density of the surrounding fluid (e.g., air or oil) in kg/m³.")
    create_tooltip(self.needle_diameter.label, "The needle diameter, used for image scale calibration.")
    create_tooltip(self.pixel_mm.label, "The pixel-to-millimeter scale for image-based measurements (optional).")

    # Returning the user input frame
    return user_input_frame

# Add tooltip messages
def add_help_icon(parent, row, column, tooltip_text):
    icon = CTkLabel(parent, text="❓", font=("Arial", 12, "bold"), cursor="question_arrow", text_color="red")
    icon.grid(row=row, column=column, padx=(2, 5), pady=5, sticky="w")
    create_tooltip(icon, tooltip_text)

# ift [Analysis Methods]
def create_analysis_checklist_ift(self,parent,user_input_data):

    analysis_clist_frame = CTkFrame(parent)
    # Ensure the frame itself expands within its parent grid cell
    set_light_only_color(analysis_clist_frame, "innerframe")
    analysis_clist_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=15, pady=15) # Changed sticky to nsew

    # --- Configure analysis_clist_frame's internal grid ---
    analysis_clist_frame.grid_rowconfigure(0, weight=0)  # Label row fixed
    analysis_clist_frame.grid_rowconfigure(1, weight=1)  # input_fields_frame row expands
    analysis_clist_frame.grid_columnconfigure(0, weight=1) # Column expands

    # Create a label for the dynamic content
    label = CTkLabel(analysis_clist_frame, text="Analysis methods", font=("Roboto", 16, "bold"))
    label.grid(row=0, column=0, padx=10, pady=5, sticky="w") # Removed columnspan

    # Create a frame to hold all input fields
    input_fields_frame = CTkFrame(analysis_clist_frame)
    # Make this frame expand within analysis_clist_frame's row 1
    set_light_only_color(input_fields_frame, "entry")
    input_fields_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew") # Changed sticky to nsew

    # --- Configure input_fields_frame's internal grid ---
    # Only one checkbox here at rw=0, cl=0
    input_fields_frame.grid_rowconfigure(0, weight=1)
    input_fields_frame.grid_columnconfigure(0, weight=1) # Maybe make checkbox expand? Or keep fixed? Let's try weight=1.

    def update_default_method_boole(*args):
        user_input_data.analysis_methods_pd[INTERFACIAL_TENSION] = self.default_method_boole.get_value()

    self.default_method_boole = CheckButton(
        self, input_fields_frame, "Interfacial Tension", update_default_method_boole, rw=0, cl=0,
        default_value=user_input_data.analysis_methods_pd[INTERFACIAL_TENSION])
    
    return analysis_clist_frame

def create_user_inputs_cm(self,parent,user_input_data):
    """Create user input fields and return the frame containing them."""
    # Create the user input frame
    user_input_frame = CTkFrame(parent)
    set_light_only_color(user_input_frame, "innerframe")
    user_input_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=15, pady=15)

    # Configure user_input_frame's internal grid
    user_input_frame.grid_rowconfigure(0, weight=0)  # Label row fixed
    user_input_frame.grid_rowconfigure(1, weight=1)  # input_fields_frame row expands
    user_input_frame.grid_columnconfigure(0, weight=1)  # Allow column to expand

    # Create a label for the dynamic content
    label = CTkLabel(user_input_frame, text="User Inputs", font=("Roboto", 16, "bold"))
    label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

    # Create a frame to hold all input fields
    input_fields_frame = CTkFrame(user_input_frame)
    set_light_only_color(input_fields_frame, "entry")
    input_fields_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

    # Configure the grid of input_fields_frame to be resizable
    for i in range(4):
        input_fields_frame.grid_rowconfigure(i, weight=1)
    input_fields_frame.grid_columnconfigure(0, weight=0)  # Label column fixed width
    input_fields_frame.grid_columnconfigure(1, weight=1)  # Widget column expands

    # Define update functions for each input
    def update_drop_id_method(*args):
        user_input_data.drop_ID_method = self.drop_ID_method.get_value()
        # self.image_app.update_image_processing_button()
          # Reset baseline dependencies
        # self.image_app.update_button_visibility()

    def update_threshold_method(*args):
        user_input_data.threshold_method = self.threshold_method.get_value()
        # user_input_data.threshold_val = None
        # self.image_app.update_button_visibility()

    def update_threshold_value(*args):
        user_input_data.threshold_val = self.threshold_val.get_value()

    def update_baseline_method(*args):
        user_input_data.baseline_method = self.baseline_method.get_value()
        # user_input_data.threshold_val = None
        # self.image_app.update_button_visibility()

    # Create input fields with the associated update methods
    self.drop_ID_method = OptionMenu(
        self, input_fields_frame, "Drop ID method:", DROP_ID_OPTIONS,
        lambda *args: update_drop_id_method(*args), rw=0, default_value=user_input_data.drop_ID_method
    )
    self.drop_ID_method.optionmenu.grid_configure(sticky="ew")

    self.threshold_method = OptionMenu(
        self, input_fields_frame, "Threshold value selection method:", THRESHOLD_OPTIONS,
        lambda *args: update_threshold_method(*args), rw=1, default_value=user_input_data.threshold_method
    )
    self.threshold_method.optionmenu.grid_configure(sticky="ew")

    self.threshold_val = FloatEntry(
        self, input_fields_frame, "Threshold value (ignored if method=Automated):",
        lambda *args: update_threshold_value(*args), rw=2, default_value=user_input_data.threshold_val
    )
    self.threshold_val.entry.grid_configure(sticky="ew")

    self.baseline_method = OptionMenu(
        self, input_fields_frame, "Baseline selection method:", BASELINE_OPTIONS,
        lambda *args: update_baseline_method(*args), rw=3, default_value=user_input_data.baseline_method
    )
    self.baseline_method.optionmenu.grid_configure(sticky="ew")

    create_tooltip(self.drop_ID_method.label, "The method to identify the droplet region")
    create_tooltip(self.threshold_method.label, "The method for threshold value selection (automatic or custom).")
    create_tooltip(self.threshold_val.label, "The threshold value for edge detection (only applicable for the manual threshold value selection).")
    create_tooltip(self.baseline_method.label, "The baseline detection method for fitting the contact angle.")

    return user_input_frame

def create_plotting_checklist(self, parent, user_input_data):
    """Create plotting checklist fields and return the frame containing them."""
    # Create the plotting checklist frame
    plotting_clist_frame = CTkFrame(parent)
    set_light_only_color(plotting_clist_frame, "innerframe")
    # Ensure this frame expands. Adjust grid position (row, column, columnspan) as needed by the caller (ca_preparation.py)
    # Assuming row=1, column=2, columnspan=1 was intended placement in parent grid
    plotting_clist_frame.grid(row=2, column=0, sticky="nsew", padx=15, pady=15) # Adjusted grid based on ca_preparation call, Changed sticky

    # --- Configure plotting_clist_frame's internal grid ---
    plotting_clist_frame.grid_rowconfigure(0, weight=0) # Label row fixed
    plotting_clist_frame.grid_rowconfigure(1, weight=1) # input_fields_frame row expands
    plotting_clist_frame.grid_columnconfigure(0, weight=1) # Column expands


    # Create a label for the checklist
    label = CTkLabel(plotting_clist_frame, text="Visible during fitting (method = automated)", font=("Roboto", 16, "bold"))
    label.grid(row=0, column=0, padx=(10,0), pady=5, sticky="w")  # Grid for label

    add_help_icon(plotting_clist_frame, 0, 1, "Additional pop-up images may appear during analysis. Since these must be closed to continue, it is recommended to deselect these options when analyzing a large number of images.")

    # Create a frame to hold all checkbox fields
    input_fields_frame = CTkFrame(plotting_clist_frame)
    set_light_only_color(input_fields_frame, "entry")
    input_fields_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew") # Changed sticky to nsew

    # --- Configure input_fields_frame's internal grid ---
    # Checkboxes are in rows 0, 1, 2 and column 0
    for i in range(3): # Rows 0, 1, 2
        input_fields_frame.grid_rowconfigure(i, weight=1)
    input_fields_frame.grid_columnconfigure(0, weight=1) # Single column expands

    # Define update functions for each checkbox
    def update_original_boole(*args):
        user_input_data.original_boole = self.original_boole.get_value()

    def update_cropped_boole(*args):
        user_input_data.cropped_boole = self.cropped_boole.get_value()

    def update_threshold_boole(*args):
        user_input_data.threshold_boole = self.threshold_boole.get_value()

    # Create check buttons with the associated update methods
    self.original_boole = CheckButton(
        self, input_fields_frame, "Original Image(s)", update_original_boole, rw=0, cl=0, state_specify='normal', default_value=user_input_data.original_boole
    )
    self.cropped_boole = CheckButton(
        self, input_fields_frame, "Cropped Image(s)", update_cropped_boole, rw=1, cl=0, state_specify='normal', default_value=user_input_data.cropped_boole
    )
    self.threshold_boole = CheckButton(
        self, input_fields_frame, "Threhold Image(s)", update_threshold_boole, rw=2, cl=0, state_specify='normal', default_value=user_input_data.threshold_boole
    )

    return plotting_clist_frame

def create_analysis_checklist_cm(self, parent, user_input_data):
    """Create analysis methods checklist and return the frame containing them."""
    # Create the analysis checklist frame
    analysis_clist_frame = CTkFrame(parent)
    set_light_only_color(analysis_clist_frame, "innerframe")
    # Ensure the frame itself expands, adjust columnspan if needed based on parent layout
    # Assuming row=3 is correct from previous code. Columnspan 4 seems large, maybe 2 is enough if parent has 2 cols? Let's try 2.
    analysis_clist_frame.grid(row=3, columnspan=2, sticky="nsew", padx=15, pady=15) # Changed sticky, adjusted columnspan

    # --- Configure analysis_clist_frame's internal grid ---
    analysis_clist_frame.grid_rowconfigure(0, weight=0)  # Label row fixed
    analysis_clist_frame.grid_rowconfigure(1, weight=1)  # input_fields_frame row expands
    analysis_clist_frame.grid_columnconfigure(0, weight=1) # Column expands


    # Create a label for the analysis checklist
    label = CTkLabel(analysis_clist_frame, text="Analysis methods", font=("Roboto", 16, "bold"))
    label.grid(row=0, column=0, padx=10, pady=5, sticky="w") # Removed columnspan

    # Create a frame to hold all checkbox fields
    input_fields_frame = CTkFrame(analysis_clist_frame)
    set_light_only_color(input_fields_frame, "entry")
    input_fields_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew") # Changed sticky to nsew

    # --- Configure input_fields_frame's internal grid ---
    # Checkboxes are in rows 0, 1, 2 and columns 0, 1
    for i in range(3): # Rows 0, 1, 2
        input_fields_frame.grid_rowconfigure(i, weight=1)
    for j in range(2): # Columns 0, 1
        input_fields_frame.grid_columnconfigure(j, weight=1)

    # Define update functions for each checkbox
    def update_tangent_boole(*args):
        user_input_data.analysis_methods_ca[FittingMethod.TANGENT_FIT] = self.tangent_boole.get_value()

    def update_second_deg_polynomial_boole(*args):
        user_input_data.analysis_methods_ca[FittingMethod.POLYNOMIAL_FIT] = self.second_deg_polynomial_boole.get_value()

    def update_circle_boole(*args):
        user_input_data.analysis_methods_ca[FittingMethod.CIRCLE_FIT] = self.circle_boole.get_value()

    def update_ellipse_boole(*args):
        user_input_data.analysis_methods_ca[FittingMethod.ELLIPSE_FIT] = self.ellipse_boole.get_value()

    def update_YL_boole(*args):
        user_input_data.analysis_methods_ca[FittingMethod.YL_FIT] = self.YL_boole.get_value()

    def update_ML_boole(*args):
        user_input_data.analysis_methods_ca[FittingMethod.ML_MODEL] = self.ML_boole.get_value()

    # Create check buttons with the associated update methods
    self.tangent_boole = CheckButton(
        self, input_fields_frame, "First-degree polynomial fit", update_tangent_boole,
        rw=0, cl=0, default_value=user_input_data.analysis_methods_ca[FittingMethod.TANGENT_FIT]
    )
    self.second_deg_polynomial_boole = CheckButton(
        self, input_fields_frame, "Second-degree polynomial fit", update_second_deg_polynomial_boole,
        rw=1, cl=0, default_value=user_input_data.analysis_methods_ca[FittingMethod.POLYNOMIAL_FIT]
    )
    self.circle_boole = CheckButton(
        self, input_fields_frame, "Circle fit", update_circle_boole, rw=2, cl=0,
        default_value=user_input_data.analysis_methods_ca[FittingMethod.CIRCLE_FIT]
    )
    self.ellipse_boole = CheckButton(
        self, input_fields_frame, "Ellipse fit", update_ellipse_boole, rw=0, cl=1,
        default_value=user_input_data.analysis_methods_ca[FittingMethod.ELLIPSE_FIT]
    )
    self.YL_boole = CheckButton(
        self, input_fields_frame, "Young-Laplace fit", update_YL_boole, rw=1, cl=1,
        default_value=user_input_data.analysis_methods_ca[FittingMethod.YL_FIT]
    )
    self.ML_boole = CheckButton(
        self, input_fields_frame, "ML model", update_ML_boole, rw=2, cl=1,
        default_value=user_input_data.analysis_methods_ca[FittingMethod.ML_MODEL]
    )

    return analysis_clist_frame

if __name__ == "__main__":
    root = CTk()  # Create a CTk instance
    user_input_data = {}  # Initialize the dictionary to hold user input data
    user_input_frame = create_user_input_fields_ift(root, user_input_data)  # Create user input fields
    user_input_frame.pack(fill="both", expand=True)  # Pack the user input frame

    root.mainloop()
