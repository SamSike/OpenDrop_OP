from customtkinter import *
from utils.config import *
from views.component.option_menu import OptionMenu
from views.component.float_entry import FloatEntry
from views.component.float_combobox import FloatCombobox
from views.component.check_button import CheckButton
from views.helper.style import set_light_only_color
from utils.enums import FittingMethod
LABEL_WIDTH = 200  # Adjust as needed

# ift [User Input]
def create_user_input_fields_ift(self, parent, user_input_data):
    """Create user input fields and return the frame containing them."""
    user_input_frame = CTkFrame(parent)
    set_light_only_color(user_input_frame, "innerframe")
    user_input_frame.grid(row=1, column=0, columnspan=2, sticky="wens", padx=15, pady=15)

    # Configure the grid for the user_input_frame to be resizable
    user_input_frame.grid_rowconfigure(0, weight=0)  # No resizing for the label row
    user_input_frame.grid_rowconfigure(1, weight=1)  # Allow resizing for the input fields row
    user_input_frame.grid_columnconfigure(0, weight=1)  # Allow resizing for the first column
    user_input_frame.grid_columnconfigure(1, weight=1)  # Allow resizing for the second column

    # Create a label for the dynamic content
    label = CTkLabel(user_input_frame, text="User Inputs", font=("Roboto", 16, "bold"))
    label.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")  # Grid for label

    # Create a frame to hold all input fields
    input_fields_frame = CTkFrame(user_input_frame)
    set_light_only_color(input_fields_frame, "entry")
    input_fields_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="wens")  # Grid for input fields frame

    # Configure the grid of the input_fields_frame to be resizable
    input_fields_frame.grid_rowconfigure(0, weight=1)  # Allow first row to resize
    input_fields_frame.grid_rowconfigure(1, weight=1)  # Allow second row to resize
    input_fields_frame.grid_rowconfigure(2, weight=1)  # Allow third row to resize
    input_fields_frame.grid_rowconfigure(3, weight=1)  # Allow fourth row to resize
    input_fields_frame.grid_rowconfigure(4, weight=1)  # Allow fifth row to resize
    input_fields_frame.grid_rowconfigure(5, weight=1)  # Allow sixth row to resize

    input_fields_frame.grid_columnconfigure(0, weight=1)  # Allow first column to resize
    input_fields_frame.grid_columnconfigure(1, weight=1)  # Allow second column to resize

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
    self.needle_region_method = OptionMenu(
        self, input_fields_frame, "Needle Region:", AUTO_MANUAL_OPTIONS, lambda *args: update_needle_region_method(*args), rw=1,
        default_value=user_input_data.needle_region_method
    )
    
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

    # Returning the user input frame
    return user_input_frame

# ift [Analysis Methods]
def create_analysis_checklist_ift(self,parent,user_input_data):

    analysis_clist_frame = CTkFrame(parent)
    set_light_only_color(analysis_clist_frame, "innerframe")
    analysis_clist_frame.grid(row=1, column=0, columnspan=2, sticky="wens", padx=15, pady=15)

    # Create a label for the dynamic content
    label = CTkLabel(analysis_clist_frame, text="Analysis methods", font=("Roboto", 16, "bold"))
    label.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")  # Grid for label

    # Create a frame to hold all input fields
    input_fields_frame = CTkFrame(analysis_clist_frame)
    set_light_only_color(input_fields_frame, "entry")
    input_fields_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="wens")  # Grid for input fields frame

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
    user_input_frame.grid(row=1, column=0, columnspan=2, sticky="wens", padx=15, pady=15)

    # Create a label for the dynamic content
    label = CTkLabel(user_input_frame, text="User Inputs", font=("Roboto", 16, "bold"))
    label.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")

    # Create a frame to hold all input fields
    input_fields_frame = CTkFrame(user_input_frame)
    set_light_only_color(input_fields_frame, "entry")
    input_fields_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="wens")

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

    def update_density_outer(*args):
        user_input_data.density_outer = self.density_outer.get_value()

    def update_needle_diameter(*args):
        user_input_data.needle_diameter_mm = self.needle_diameter.get_value()

    # Create input fields with the associated update methods
    self.drop_ID_method = OptionMenu(
        self, input_fields_frame, "Drop ID method:", DROP_ID_OPTIONS,
        lambda *args: update_drop_id_method(*args), rw=0, default_value=user_input_data.drop_ID_method
    )
    self.threshold_method = OptionMenu(
        self, input_fields_frame, "Threshold value selection method:", THRESHOLD_OPTIONS,
        lambda *args: update_threshold_method(*args), rw=1, default_value=user_input_data.threshold_method
    )
    self.threshold_val = FloatEntry(
        self, input_fields_frame, "Threshold value (ignored if method=Automated):",
        lambda *args: update_threshold_value(*args), rw=2, default_value=user_input_data.threshold_val
    )
    self.baseline_method = OptionMenu(
        self, input_fields_frame, "Baseline selection method:", BASELINE_OPTIONS,
        lambda *args: update_baseline_method(*args), rw=3, default_value=user_input_data.baseline_method
    )
    self.density_outer = FloatEntry(
        self, input_fields_frame, "Continuous density (kg/m³):",
        lambda *args: update_density_outer(*args), rw=4, default_value=user_input_data.density_outer
    )
    self.needle_diameter = FloatCombobox(
        self, input_fields_frame, "Needle diameter (mm):", NEEDLE_OPTIONS,
        lambda *args: update_needle_diameter(*args), rw=5, default_value=user_input_data.needle_diameter_mm
    )

    # Configure grid columns in the input fields frame
    input_fields_frame.grid_columnconfigure(0, minsize=LABEL_WIDTH)

    return user_input_frame

def create_plotting_checklist(self, parent, user_input_data):
    """Create plotting checklist fields and return the frame containing them."""
    # Create the plotting checklist frame
    plotting_clist_frame = CTkFrame(parent)
    set_light_only_color(plotting_clist_frame, "innerframe")
    plotting_clist_frame.grid(row=1, column=2, columnspan=1, sticky="wens", padx=15, pady=15)

    # Create a label for the checklist
    label = CTkLabel(plotting_clist_frame, text="To view during fitting(ignored if method = User-selected)", font=("Roboto", 16, "bold"))
    label.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")  # Grid for label

    # Create a frame to hold all checkbox fields
    input_fields_frame = CTkFrame(plotting_clist_frame)
    set_light_only_color(input_fields_frame, "entry")
    input_fields_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="wens")  # Grid for input fields frame

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
        self, input_fields_frame, "Cropped Images(s)", update_cropped_boole, rw=1, cl=0, state_specify='normal', default_value=user_input_data.cropped_boole
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
    analysis_clist_frame.grid(row=3, columnspan=4, sticky="wens", padx=15, pady=15)

    # Create a label for the analysis checklist
    label = CTkLabel(analysis_clist_frame, text="Analysis methods", font=("Roboto", 16, "bold"))
    label.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")  # Grid for label

    # Create a frame to hold all checkbox fields
    input_fields_frame = CTkFrame(analysis_clist_frame)
    set_light_only_color(input_fields_frame, "entry")
    input_fields_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="wens")  # Grid for input fields frame

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
