from customtkinter import *
from utils.config import *
from views.component.option_menu import OptionMenu
from views.component.float_entry import FloatEntry
from views.component.float_combobox import FloatCombobox
from views.component.check_button import CheckButton
# Define your options and labels globally or pass them as parameters if preferred
# AUTO_MANUAL_OPTIONS = ["Automated", "User-selected"]  # Example options
LABEL_WIDTH = 200  # Adjust as needed

# ift [User Input]
def create_user_input_fields_ift(self, parent, user_input_data):
    """Create user input fields and return the frame containing them."""
    user_input_frame = CTkFrame(parent, fg_color="red")
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
    input_fields_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="wens", columnspan=2)  # Grid for input fields frame

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
        # self.image_app.update_button_visibility()
        self.image_app.update_image_processing_button()

    def update_needle_region_method(*args):
        user_input_data.needle_region_choice = self.needle_region_method.get_value()    
       

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
        self, input_fields_frame, "Drop Region:", AUTO_MANUAL_OPTIONS, lambda *args: update_drop_region_method(*args), rw=0
    )
    self.needle_region_method = OptionMenu(
        self, input_fields_frame, "Needle Region:", AUTO_MANUAL_OPTIONS, lambda *args: update_needle_region_method(*args), rw=1
    )
    
    self.drop_density_method = FloatEntry(
        self, input_fields_frame, "Drop Density(kg/m³):", lambda *args: update_drop_density(*args), rw=2
    )
    self.continuous_density = FloatEntry(
        self, input_fields_frame, "Continuous density (kg/m):", lambda *args: update_continuous_density(*args), rw=3
    )
    self.needle_diameter = FloatEntry(
        self, input_fields_frame, "Needle Diameter(mm):", lambda *args: update_needle_diameter(*args), rw=4
    )
    self.pixel_mm = FloatEntry(
        self, input_fields_frame, "Pixel scale(px/mm):", lambda *args: update_pixel_mm(*args), rw=5
    )

    # Returning the user input frame
    return user_input_frame

# ift [CheckList Select]
def create_plotting_checklist_ift(self,parent,user_input_data):
    """Create IFT plotting checklist fields and return the frame containing them."""
    # Create the main frame for this section
    plotting_clist_frame = CTkFrame(parent) # Removed fg_color="green" for consistency
    # Ensure this frame expands within its parent cell
    plotting_clist_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=15, pady=15) # Changed sticky to nsew

    # --- Configure plotting_clist_frame's internal grid ---
    plotting_clist_frame.grid_rowconfigure(0, weight=0) # Label row fixed
    plotting_clist_frame.grid_rowconfigure(1, weight=1) # input_fields_frame row expands
    plotting_clist_frame.grid_columnconfigure(0, weight=1) # Column expands

    # Create a label
    label = CTkLabel(plotting_clist_frame, text="To view during fitting", font=("Roboto", 16, "bold"))
    label.grid(row=0, column=0, padx=10, pady=5, sticky="w") # Removed columnspan

    # Create a frame to hold input fields (checkboxes)
    input_fields_frame = CTkFrame(plotting_clist_frame)
    input_fields_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew") # Changed sticky to nsew

    # --- Configure input_fields_frame's internal grid ---
    # Only one checkbox "Residuals" at rw=0, cl=0
    input_fields_frame.grid_rowconfigure(0, weight=1) # Allow row to expand vertically
    input_fields_frame.grid_columnconfigure(0, weight=1) # Allow column to expand horizontally

    def update_residuals_boole(*args):
        # Make sure user_input_data is treated as a dict if using string keys
        # If it's an object, use attribute access user_input_data.residuals_boole
        # Assuming it might be a dict here based on ["residuals"] usage
        if isinstance(user_input_data, dict):
             user_input_data["residuals"] = self.residuals_boole.get_value()
        else:
             user_input_data.residuals_boole = self.residuals_boole.get_value()

    self.residuals_boole = CheckButton(
        self, input_fields_frame, "Residuals", update_residuals_boole, rw=0, cl=0, state_specify='normal')
    # Optional: Add sticky to CheckButton's grid call if needed, e.g., sticky="w"

    return plotting_clist_frame

# ift [Analysis Methods]
def create_analysis_checklist_ift(self,parent,user_input_data):

    analysis_clist_frame = CTkFrame(parent)
    # Ensure the frame itself expands within its parent grid cell
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
    input_fields_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew") # Changed sticky to nsew

    # --- Configure input_fields_frame's internal grid ---
    # Only one checkbox here at rw=0, cl=0
    input_fields_frame.grid_rowconfigure(0, weight=1)
    input_fields_frame.grid_columnconfigure(0, weight=1) # Maybe make checkbox expand? Or keep fixed? Let's try weight=1.

    def update_default_method_boole(*args):
        user_input_data.analysis_methods_pd[INTERFACIAL_TENSION]= self.default_method_boole.get_value()

    self.default_method_boole = CheckButton(
        self, input_fields_frame, "Interfacial Tension", update_default_method_boole, rw=0, cl=0,initial_value=True)
    # Ensure the CheckButton itself is placed correctly (assuming CheckButton handles its internal label placement)
    # If the CheckButton needs explicit sticky:
    # self.default_method_boole.grid(sticky="w") # Example: Align left

    return analysis_clist_frame

def create_user_inputs_cm(self,parent,user_input_data):
    """Create user input fields and return the frame containing them."""
    # Create the user input frame
    user_input_frame = CTkFrame(parent)
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
    input_fields_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

    # Configure the grid of input_fields_frame to be resizable
    for i in range(6):
        input_fields_frame.grid_rowconfigure(i, weight=1)
    input_fields_frame.grid_columnconfigure(0, weight=1)  # Label column
    input_fields_frame.grid_columnconfigure(1, weight=1)  # Widget column

    # Define update functions for each input
    def update_drop_id_method(*args):
        user_input_data.drop_ID_method = self.drop_ID_method.get_value()
        if hasattr(self, 'image_app'):
            self.image_app.update_image_processing_button()

    def update_threshold_method(*args):
        user_input_data.threshold_method = self.threshold_method.get_value()

    def update_threshold_value(*args):
        user_input_data.threshold_val = self.threshold_val.get_value()

    def update_baseline_method(*args):
        user_input_data.baseline_method = self.baseline_method.get_value()

    def update_density_outer(*args):
        user_input_data.density_outer = self.density_outer.get_value()

    def update_needle_diameter(*args):
        user_input_data.needle_diameter_mm = self.needle_diameter.get_value()

    # Create input fields with the associated update methods
    self.drop_ID_method = OptionMenu(
        self, input_fields_frame, "Drop ID method:", DROP_ID_OPTIONS,
        lambda *args: update_drop_id_method(*args), rw=0
    )
    self.threshold_method = OptionMenu(
        self, input_fields_frame, "Threshold value selection method:", THRESHOLD_OPTIONS,
        lambda *args: update_threshold_method(*args), rw=1
    )
    self.threshold_val = FloatEntry(
        self, input_fields_frame, "Threshold value (ignored if method=Automated):",
        lambda *args: update_threshold_value(*args), rw=2
    )
    self.baseline_method = OptionMenu(
        self, input_fields_frame, "Baseline selection method:", BASELINE_OPTIONS,
        lambda *args: update_baseline_method(*args), rw=3
    )
    self.density_outer = FloatEntry(
        self, input_fields_frame, "Continuous density (kg/m³):",
        lambda *args: update_density_outer(*args), rw=4
    )
    self.needle_diameter = FloatCombobox(
        self, input_fields_frame, "Needle diameter (mm):", NEEDLE_OPTIONS,
        lambda *args: update_needle_diameter(*args), rw=5
    )

    return user_input_frame

def create_plotting_checklist_cm(self, parent, user_input_data):
    """Create CM plotting checklist fields and return the frame containing them."""
    # Create the main frame for this section
    plotting_clist_frame = CTkFrame(parent)
    # Ensure this frame expands. Adjust grid position (row, column, columnspan) as needed by the caller (ca_preparation.py)
    # Assuming row=1, column=2, columnspan=1 was intended placement in parent grid
    plotting_clist_frame.grid(row=2, column=0, sticky="nsew", padx=15, pady=15) # Adjusted grid based on ca_preparation call, Changed sticky

    # --- Configure plotting_clist_frame's internal grid ---
    plotting_clist_frame.grid_rowconfigure(0, weight=0) # Label row fixed
    plotting_clist_frame.grid_rowconfigure(1, weight=1) # input_fields_frame row expands
    plotting_clist_frame.grid_columnconfigure(0, weight=1) # Column expands


    # Create a label for the checklist
    label = CTkLabel(plotting_clist_frame, text="To view during fitting", font=("Roboto", 16, "bold"))
    label.grid(row=0, column=0, padx=10, pady=5, sticky="w") # Removed columnspan

    # Create a frame to hold all checkbox fields
    input_fields_frame = CTkFrame(plotting_clist_frame)
    input_fields_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew") # Changed sticky to nsew

    # --- Configure input_fields_frame's internal grid ---
    # Checkboxes are in rows 0, 1, 2 and column 0
    for i in range(3): # Rows 0, 1, 2
        input_fields_frame.grid_rowconfigure(i, weight=1)
    input_fields_frame.grid_columnconfigure(0, weight=1) # Single column expands


    # Define update functions (remain the same)
    def update_residuals_boole(*args):
        user_input_data.residuals_boole = self.residuals_boole.get_value()

    def update_profiles_boole(*args):
        user_input_data.profiles_boole = self.profiles_boole.get_value()

    def update_ift_boole(*args):
        user_input_data.interfacial_tension_boole = self.IFT_boole.get_value()

    # Create check buttons (remain the same)
    self.residuals_boole = CheckButton(
        self, input_fields_frame, "Residuals", update_residuals_boole, rw=0, cl=0, state_specify='normal'
    )
    self.profiles_boole = CheckButton(
        self, input_fields_frame, "Profiles", update_profiles_boole, rw=1, cl=0, state_specify='normal'
    )
    self.IFT_boole = CheckButton(
        self, input_fields_frame, "Physical quantities", update_ift_boole, rw=2, cl=0, state_specify='normal'
    )
    # Optional: Add sticky="w" or similar to the grid calls for each CheckButton if needed for alignment


    return plotting_clist_frame

def create_analysis_checklist_cm(self, parent, user_input_data):
    """Create analysis methods checklist and return the frame containing them."""
    # Create the analysis checklist frame
    analysis_clist_frame = CTkFrame(parent)
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
    input_fields_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew") # Changed sticky to nsew

    # --- Configure input_fields_frame's internal grid ---
    # Checkboxes are in rows 0, 1, 2 and columns 0, 1
    for i in range(3): # Rows 0, 1, 2
        input_fields_frame.grid_rowconfigure(i, weight=1)
    for j in range(2): # Columns 0, 1
        input_fields_frame.grid_columnconfigure(j, weight=1)


    # Define update functions (remain the same)
    def update_tangent_boole(*args):
        user_input_data.analysis_methods_ca[TANGENT_FIT] = self.tangent_boole.get_value()

    def update_second_deg_polynomial_boole(*args):
        user_input_data.analysis_methods_ca[POLYNOMIAL_FIT] = self.second_deg_polynomial_boole.get_value()

    def update_circle_boole(*args):
        user_input_data.analysis_methods_ca[CIRCLE_FIT] = self.circle_boole.get_value()

    def update_ellipse_boole(*args):
        user_input_data.analysis_methods_ca[ELLIPSE_FIT] = self.ellipse_boole.get_value()

    def update_YL_boole(*args):
        user_input_data.analysis_methods_ca[YL_FIT] = self.YL_boole.get_value()

    def update_ML_boole(*args):
        user_input_data.analysis_methods_ca[ML_MODEL] = self.ML_boole.get_value()

    # Create check buttons (remain the same)
    self.tangent_boole = CheckButton(
        self, input_fields_frame, "First-degree polynomial fit", update_tangent_boole, rw=0, cl=0
    )
    self.second_deg_polynomial_boole = CheckButton(
        self, input_fields_frame, "Second-degree polynomial fit", update_second_deg_polynomial_boole, rw=1, cl=0
    )
    self.circle_boole = CheckButton(
        self, input_fields_frame, "Circle fit", update_circle_boole, rw=2, cl=0
    )
    self.ellipse_boole = CheckButton(
        self, input_fields_frame, "Ellipse fit", update_ellipse_boole, rw=0, cl=1
    )
    self.YL_boole = CheckButton(
        self, input_fields_frame, "Young-Laplace fit", update_YL_boole, rw=1, cl=1
    )
    self.ML_boole = CheckButton(
        self, input_fields_frame, "ML model", update_ML_boole, rw=2, cl=1
    )
    # Optionally add sticky="w" or similar to the grid calls for each CheckButton if needed for alignment

    return analysis_clist_frame

if __name__ == "__main__":
    root = CTk()  # Create a CTk instance
    user_input_data = {}  # Initialize the dictionary to hold user input data
    user_input_frame = create_user_input_fields_ift(root, user_input_data)  # Create user input fields
    user_input_frame.pack(fill="both", expand=True)  # Pack the user input frame

    root.mainloop()
