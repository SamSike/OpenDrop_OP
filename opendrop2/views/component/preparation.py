from opendrop2.modules.core.classes import ExperimentalSetup
from opendrop2.views.component.option_menu import OptionMenu
from opendrop2.views.component.float_entry import FloatEntry

# from opendrop2.views.component.float_combobox import FloatCombobox
from opendrop2.views.component.check_button import CheckButton
from opendrop2.views.helper.style import set_light_only_color
from opendrop2.utils.config import (
    AUTO_MANUAL_OPTIONS,
    NEEDLE_OPTIONS,
    DROP_ID_OPTIONS,
    THRESHOLD_OPTIONS,
    BASELINE_OPTIONS,
    INTERFACIAL_TENSION,
)
from opendrop2.utils.enums import FittingMethod
from opendrop2.utils.tooltip_util import create_tooltip
import re
import os
from tkinter import messagebox
from customtkinter import CTk, CTkFrame, CTkLabel, StringVar, CTkButton, CTkComboBox

LABEL_WIDTH = 200  # Adjust as needed

# ift [User Input]


def create_user_input_fields_ift(self, parent, user_input_data: ExperimentalSetup):
    """Create user input fields and return the frame containing them."""
    user_input_frame = CTkFrame(parent)
    set_light_only_color(user_input_frame, "innerframe")
    user_input_frame.grid(
        row=1, column=0, columnspan=2, sticky="nsew", padx=15, pady=15
    )

    # Configure the grid for the user_input_frame to be resizable
    user_input_frame.grid_rowconfigure(0, weight=0)  # No resizing for the label row
    # Allow resizing for the input fields row
    user_input_frame.grid_rowconfigure(1, weight=1)
    # Allow resizing for the first column
    user_input_frame.grid_columnconfigure(0, weight=1)
    # Allow resizing for the second column
    user_input_frame.grid_columnconfigure(1, weight=1)

    # Create a label for the dynamic content
    label = CTkLabel(user_input_frame, text="User Inputs", font=("Roboto", 16, "bold"))
    label.grid(row=0, column=0, padx=10, pady=5, sticky="w")  # Grid for label

    # Create a frame to hold all input fields
    input_fields_frame = CTkFrame(user_input_frame)
    set_light_only_color(input_fields_frame, "entry")
    input_fields_frame.grid(
        row=1, column=0, padx=10, pady=(0, 10), sticky="nsew", columnspan=2
    )  # Grid for input fields frame

    # Configure the grid of the input_fields_frame to be resizable
    for i in range(6):
        input_fields_frame.grid_rowconfigure(i, weight=1)
    # Label column fixed width (anchor='w' handles alignment)
    input_fields_frame.grid_columnconfigure(0, weight=0)
    input_fields_frame.grid_columnconfigure(1, weight=1)  # Widget column expands

    # Update the input value functions
    def update_drop_region_method(*args):
        user_input_data.drop_id_method = self.drop_region_method.get_value()
        # self.image_app.update_image_processing_button()

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
        self,
        input_fields_frame,
        "Drop Region:",
        AUTO_MANUAL_OPTIONS,
        lambda *args: update_drop_region_method(*args),
        rw=0,
        default_value=user_input_data.drop_id_method,
    )
    self.drop_region_method.optionmenu.grid_configure(sticky="ew")

    self.needle_region_method = OptionMenu(
        self,
        input_fields_frame,
        "Needle Region:",
        AUTO_MANUAL_OPTIONS,
        lambda *args: update_needle_region_method(*args),
        rw=1,
        default_value=user_input_data.needle_region_method,
    )
    self.needle_region_method.optionmenu.grid_configure(sticky="ew")

    self.drop_density_method = FloatEntry(
        self,
        input_fields_frame,
        "Drop Density(kg/m³)*:",
        lambda *args: update_drop_density(*args),
        rw=2,
        default_value=user_input_data.drop_density,
    )

    self.continuous_density = FloatEntry(
        self,
        input_fields_frame,
        "Continuous density (kg/m)*:",
        lambda *args: update_continuous_density(*args),
        rw=3,
        default_value=user_input_data.density_outer,
    )

    # Create a frame to hold the needle diameter combobox and management buttons
    needle_frame = CTkFrame(input_fields_frame)
    needle_frame.grid(row=4, column=1, sticky="ew", padx=(5, 5), pady=(5, 5))
    needle_frame.grid_columnconfigure(0, weight=1)  # Combobox takes most space
    # Buttons don't need to stretch
    needle_frame.grid_columnconfigure(1, weight=0)
    # Buttons don't need to stretch
    needle_frame.grid_columnconfigure(2, weight=0)

    # Create needle diameter label
    needle_label = CTkLabel(
        input_fields_frame, text="Needle diameter (mm)*:", width=LABEL_WIDTH, anchor="w"
    )
    needle_label.grid(row=4, column=0, sticky="w", padx=(5, 5), pady=(5, 5))

    # Create needle diameter combobox
    needle_var = StringVar()
    if user_input_data.needle_diameter_mm is not None:
        needle_var.set(str(user_input_data.needle_diameter_mm))

    needle_combobox = CTkComboBox(
        needle_frame, variable=needle_var, values=NEEDLE_OPTIONS, width=110
    )
    needle_combobox.grid(row=0, column=0, sticky="ew", padx=(0, 5))

    # Add/remove button functions
    def add_needle_diameter():
        # Get value directly from the input field, no dialog popup
        new_value = needle_var.get()
        if new_value:
            try:
                # Validate as a valid float
                float_value = float(new_value)
                # Format as string
                formatted_value = str(float_value)

                # Check if already exists
                if formatted_value not in NEEDLE_OPTIONS:
                    # Add to NEEDLE_OPTIONS
                    NEEDLE_OPTIONS.append(formatted_value)
                    # Update combobox
                    needle_combobox.configure(values=NEEDLE_OPTIONS)
                    # Save to config.py
                    save_needle_options_to_config()
            except ValueError:
                # Show error message
                messagebox.showerror("Invalid Input", "Please enter a valid number.")

    def remove_needle_diameter():
        current_value = needle_var.get()
        # Ensure there's a selected value and it's not the last option
        if (
            current_value
            and current_value in NEEDLE_OPTIONS
            and len(NEEDLE_OPTIONS) > 1
        ):
            # Remove from NEEDLE_OPTIONS
            NEEDLE_OPTIONS.remove(current_value)
            # Update combobox
            needle_combobox.configure(values=NEEDLE_OPTIONS)
            # Set to first value
            needle_var.set(NEEDLE_OPTIONS[0])
            # Save to config.py
            save_needle_options_to_config()

    # Add buttons
    add_button = CTkButton(
        needle_frame, text="+", width=30, command=add_needle_diameter
    )
    add_button.grid(row=0, column=1, padx=(0, 5))

    remove_button = CTkButton(
        needle_frame, text="-", width=30, command=remove_needle_diameter
    )
    remove_button.grid(row=0, column=2)

    # Add tooltips
    create_tooltip(
        needle_label, "The needle diameter, used for image scale calibration."
    )
    create_tooltip(add_button, "Add a new needle diameter value")
    create_tooltip(remove_button, "Remove the selected needle diameter value")

    # Create object for update_needle_diameter callback
    def get_needle_value():
        try:
            return float(needle_var.get())
        except ValueError:
            return None

    # Create a compatible object that supports the expected interface
    self.needle_diameter = type(
        "obj",
        (object,),
        {
            "get_value": get_needle_value,
            "set_value": lambda value: (
                needle_var.set(str(value)) if value is not None else None
            ),
            "label": needle_label,
        },
    )

    # Set initial value
    if user_input_data.needle_diameter_mm is not None:
        self.needle_diameter.set_value(user_input_data.needle_diameter_mm)

    # Set up needle_var to call update_needle_diameter
    needle_var.trace_add("write", update_needle_diameter)

    self.pixel_mm = FloatEntry(
        self,
        input_fields_frame,
        "Pixel scale(px/mm):",
        lambda *args: update_pixel_mm(*args),
        rw=5,
        default_value=user_input_data.pixel_mm,
    )

    create_tooltip(
        self.drop_region_method.label,
        "The method to detect the droplet region.",
        "below-align-left",
    )
    create_tooltip(
        self.needle_region_method.label, "The method to detect the needle region."
    )
    create_tooltip(
        self.drop_density_method.label,
        "The density of the droplet in kg/m³. Used for interfacial tension calculation.",
    )
    create_tooltip(
        self.continuous_density.label,
        "The density of the surrounding fluid (e.g., air or oil) in kg/m³.",
        position="left-align-right-top",
    )
    create_tooltip(
        self.pixel_mm.label,
        "The pixel-to-millimeter scale for image-based measurements (optional).",
    )

    # Returning the user input frame
    return user_input_frame


# Add tooltip messages


def add_help_icon(parent, row, column, tooltip_text: str):
    icon = CTkLabel(
        parent,
        text="❓",
        font=("Arial", 12, "bold"),
        cursor="question_arrow",
        text_color="red",
    )
    icon.grid(row=row, column=column, padx=(2, 5), pady=5, sticky="w")
    create_tooltip(icon, tooltip_text, "below-align-right")


# ift [Analysis Methods]


def create_analysis_checklist_ift(self, parent, user_input_data: ExperimentalSetup):

    analysis_clist_frame = CTkFrame(parent)
    # Ensure the frame itself expands within its parent grid cell
    set_light_only_color(analysis_clist_frame, "innerframe")
    analysis_clist_frame.grid(
        row=1, column=0, columnspan=2, sticky="nsew", padx=15, pady=15
    )  # Changed sticky to nsew

    # --- Configure analysis_clist_frame's internal grid ---
    analysis_clist_frame.grid_rowconfigure(0, weight=0)  # Label row fixed
    analysis_clist_frame.grid_rowconfigure(
        1, weight=1
    )  # input_fields_frame row expands
    analysis_clist_frame.grid_columnconfigure(0, weight=1)  # Column expands

    # Create a label for the dynamic content
    label = CTkLabel(
        analysis_clist_frame, text="Analysis methods*", font=("Roboto", 16, "bold")
    )
    label.grid(row=0, column=0, padx=10, pady=5, sticky="w")  # Removed columnspan

    # Create a frame to hold all input fields
    input_fields_frame = CTkFrame(analysis_clist_frame)
    # Make this frame expand within analysis_clist_frame's row 1
    set_light_only_color(input_fields_frame, "entry")
    input_fields_frame.grid(
        row=1, column=0, padx=10, pady=(0, 10), sticky="nsew"
    )  # Changed sticky to nsew

    # --- Configure input_fields_frame's internal grid ---
    # Only one checkbox here at rw=0, cl=0
    input_fields_frame.grid_rowconfigure(0, weight=1)
    # Maybe make checkbox expand? Or keep fixed? Let's try weight=1.
    input_fields_frame.grid_columnconfigure(0, weight=1)

    def update_default_method_boole(*args):
        user_input_data.analysis_methods_pd[INTERFACIAL_TENSION] = (
            self.default_method_boole.get_value()
        )

    self.default_method_boole = CheckButton(
        self,
        input_fields_frame,
        "Interfacial Tension",
        update_default_method_boole,
        rw=0,
        cl=0,
        default_value=user_input_data.analysis_methods_pd[INTERFACIAL_TENSION],
    )

    return analysis_clist_frame


def create_user_inputs_cm(self, parent, user_input_data):
    """Create user input fields and return the frame containing them."""
    # Create the user input frame
    user_input_frame = CTkFrame(parent)
    set_light_only_color(user_input_frame, "innerframe")
    user_input_frame.grid(
        row=1, column=0, columnspan=2, sticky="nsew", padx=15, pady=15
    )

    # Configure user_input_frame's internal grid
    user_input_frame.grid_rowconfigure(0, weight=0)  # Label row fixed
    # input_fields_frame row expands
    user_input_frame.grid_rowconfigure(1, weight=1)
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
        user_input_data.drop_id_method = self.drop_id_method.get_value()
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
    self.drop_id_method = OptionMenu(
        self,
        input_fields_frame,
        "Drop ID method:",
        DROP_ID_OPTIONS,
        lambda *args: update_drop_id_method(*args),
        rw=0,
        default_value=user_input_data.drop_id_method,
    )
    self.drop_id_method.optionmenu.grid_configure(sticky="ew")

    self.threshold_method = OptionMenu(
        self,
        input_fields_frame,
        "Threshold value selection method:",
        THRESHOLD_OPTIONS,
        lambda *args: update_threshold_method(*args),
        rw=1,
        default_value=user_input_data.threshold_method,
    )
    self.threshold_method.optionmenu.grid_configure(sticky="ew")

    self.threshold_val = FloatEntry(
        self,
        input_fields_frame,
        "Threshold value (ignored if method=Automated):",
        lambda *args: update_threshold_value(*args),
        rw=2,
        default_value=user_input_data.threshold_val,
    )
    self.threshold_val.entry.grid_configure(sticky="ew")

    self.baseline_method = OptionMenu(
        self,
        input_fields_frame,
        "Baseline selection method:",
        BASELINE_OPTIONS,
        lambda *args: update_baseline_method(*args),
        rw=3,
        default_value=user_input_data.baseline_method,
    )
    self.baseline_method.optionmenu.grid_configure(sticky="ew")

    create_tooltip(
        self.drop_id_method.label, "The method to identify the droplet region"
    )
    create_tooltip(
        self.threshold_method.label,
        "The method for threshold value selection (automatic or custom).",
    )
    create_tooltip(
        self.threshold_val.label,
        "The threshold value for edge detection (only applicable for the manual threshold value selection).",
    )
    create_tooltip(
        self.baseline_method.label,
        "The baseline detection method for fitting the contact angle.",
    )

    return user_input_frame


def create_plotting_checklist(self, parent, user_input_data):
    """Create plotting checklist fields and return the frame containing them."""
    # Create the plotting checklist frame
    plotting_clist_frame = CTkFrame(parent)
    set_light_only_color(plotting_clist_frame, "innerframe")
    # Ensure this frame expands. Adjust grid position (row, column, columnspan) as needed by the caller (ca_preparation.py)
    # Assuming row=1, column=2, columnspan=1 was intended placement in parent grid
    # Adjusted grid based on ca_preparation call, Changed sticky
    plotting_clist_frame.grid(row=2, column=0, sticky="nsew", padx=15, pady=15)

    # --- Configure plotting_clist_frame's internal grid ---
    plotting_clist_frame.grid_rowconfigure(0, weight=0)  # Label row fixed
    plotting_clist_frame.grid_rowconfigure(
        1, weight=1
    )  # input_fields_frame row expands
    plotting_clist_frame.grid_columnconfigure(0, weight=1)  # Column expands

    # Create a label for the checklist
    label = CTkLabel(
        plotting_clist_frame,
        text="Visible during fitting (method = automated)",
        font=("Roboto", 16, "bold"),
    )
    label.grid(row=0, column=0, padx=(10, 0), pady=5, sticky="w")  # Grid for label

    add_help_icon(
        plotting_clist_frame,
        0,
        1,
        "Additional pop-up images may appear during analysis. Since these must be closed to continue, it is recommended to deselect these options when analyzing a large number of images.",
    )

    # Create a frame to hold all checkbox fields
    input_fields_frame = CTkFrame(plotting_clist_frame)
    set_light_only_color(input_fields_frame, "entry")
    input_fields_frame.grid(
        row=1, column=0, padx=10, pady=(0, 10), sticky="nsew"
    )  # Changed sticky to nsew

    # --- Configure input_fields_frame's internal grid ---
    # Checkboxes are in rows 0, 1, 2 and column 0
    for i in range(3):  # Rows 0, 1, 2
        input_fields_frame.grid_rowconfigure(i, weight=1)
    input_fields_frame.grid_columnconfigure(0, weight=1)  # Single column expands

    # Define update functions for each checkbox
    def update_original_boole(*args):
        user_input_data.original_boole = self.original_boole.get_value()

    def update_cropped_boole(*args):
        user_input_data.cropped_boole = self.cropped_boole.get_value()

    def update_threshold_boole(*args):
        user_input_data.threshold_boole = self.threshold_boole.get_value()

    # Create check buttons with the associated update methods
    self.original_boole = CheckButton(
        self,
        input_fields_frame,
        "Original Image(s)",
        update_original_boole,
        rw=0,
        cl=0,
        state_specify="normal",
        default_value=user_input_data.original_boole,
    )
    self.cropped_boole = CheckButton(
        self,
        input_fields_frame,
        "Cropped Image(s)",
        update_cropped_boole,
        rw=1,
        cl=0,
        state_specify="normal",
        default_value=user_input_data.cropped_boole,
    )
    self.threshold_boole = CheckButton(
        self,
        input_fields_frame,
        "Threhold Image(s)",
        update_threshold_boole,
        rw=2,
        cl=0,
        state_specify="normal",
        default_value=user_input_data.threshold_boole,
    )

    return plotting_clist_frame


def create_analysis_checklist_cm(self, parent, user_input_data):
    """Create analysis methods checklist and return the frame containing them."""
    # Create the analysis checklist frame
    analysis_clist_frame = CTkFrame(parent)
    set_light_only_color(analysis_clist_frame, "innerframe")
    # Ensure the frame itself expands, adjust columnspan if needed based on parent layout
    # Assuming row=3 is correct from previous code. Columnspan 4 seems large, maybe 2 is enough if parent has 2 cols? Let's try 2.
    # Changed sticky, adjusted columnspan
    analysis_clist_frame.grid(row=3, columnspan=2, sticky="nsew", padx=15, pady=15)

    # --- Configure analysis_clist_frame's internal grid ---
    analysis_clist_frame.grid_rowconfigure(0, weight=0)  # Label row fixed
    analysis_clist_frame.grid_rowconfigure(
        1, weight=1
    )  # input_fields_frame row expands
    analysis_clist_frame.grid_columnconfigure(0, weight=1)  # Column expands

    # Create a label for the analysis checklist
    label = CTkLabel(
        analysis_clist_frame, text="Analysis methods*", font=("Roboto", 16, "bold")
    )
    label.grid(row=0, column=0, padx=10, pady=5, sticky="w")  # Removed columnspan

    # Create a frame to hold all checkbox fields
    input_fields_frame = CTkFrame(analysis_clist_frame)
    set_light_only_color(input_fields_frame, "entry")
    input_fields_frame.grid(
        row=1, column=0, padx=10, pady=(0, 10), sticky="nsew"
    )  # Changed sticky to nsew

    # --- Configure input_fields_frame's internal grid ---
    # Checkboxes are in rows 0, 1, 2 and columns 0, 1
    for i in range(3):  # Rows 0, 1, 2
        input_fields_frame.grid_rowconfigure(i, weight=1)
    for j in range(2):  # Columns 0, 1
        input_fields_frame.grid_columnconfigure(j, weight=1)

    # Define update functions for each checkbox
    def update_tangent_boole(*args):
        user_input_data.analysis_methods_ca[FittingMethod.TANGENT_FIT] = (
            self.tangent_boole.get_value()
        )

    def update_second_deg_polynomial_boole(*args):
        user_input_data.analysis_methods_ca[FittingMethod.POLYNOMIAL_FIT] = (
            self.second_deg_polynomial_boole.get_value()
        )

    def update_circle_boole(*args):
        user_input_data.analysis_methods_ca[FittingMethod.CIRCLE_FIT] = (
            self.circle_boole.get_value()
        )

    def update_ellipse_boole(*args):
        user_input_data.analysis_methods_ca[FittingMethod.ELLIPSE_FIT] = (
            self.ellipse_boole.get_value()
        )

    def update_YL_boole(*args):
        user_input_data.analysis_methods_ca[FittingMethod.YL_FIT] = (
            self.YL_boole.get_value()
        )

    def update_ML_boole(*args):
        user_input_data.analysis_methods_ca[FittingMethod.ML_MODEL] = (
            self.ML_boole.get_value()
        )

    # Create check buttons with the associated update methods
    self.tangent_boole = CheckButton(
        self,
        input_fields_frame,
        "First-degree polynomial fit(tangent fit)",
        update_tangent_boole,
        rw=0,
        cl=0,
        default_value=user_input_data.analysis_methods_ca[FittingMethod.TANGENT_FIT],
    )
    self.second_deg_polynomial_boole = CheckButton(
        self,
        input_fields_frame,
        "Second-degree polynomial fit",
        update_second_deg_polynomial_boole,
        rw=1,
        cl=0,
        default_value=user_input_data.analysis_methods_ca[FittingMethod.POLYNOMIAL_FIT],
    )
    self.circle_boole = CheckButton(
        self,
        input_fields_frame,
        "Circle fit",
        update_circle_boole,
        rw=2,
        cl=0,
        default_value=user_input_data.analysis_methods_ca[FittingMethod.CIRCLE_FIT],
    )
    self.ellipse_boole = CheckButton(
        self,
        input_fields_frame,
        "Ellipse fit",
        update_ellipse_boole,
        rw=0,
        cl=1,
        default_value=user_input_data.analysis_methods_ca[FittingMethod.ELLIPSE_FIT],
    )
    self.YL_boole = CheckButton(
        self,
        input_fields_frame,
        "Young-Laplace fit",
        update_YL_boole,
        rw=1,
        cl=1,
        default_value=user_input_data.analysis_methods_ca[FittingMethod.YL_FIT],
    )
    self.ML_boole = CheckButton(
        self,
        input_fields_frame,
        "ML model",
        update_ML_boole,
        rw=2,
        cl=1,
        default_value=user_input_data.analysis_methods_ca[FittingMethod.ML_MODEL],
    )

    return analysis_clist_frame


def save_needle_options_to_config():
    """Save NEEDLE_OPTIONS to config.py file to ensure persistence"""
    try:
        # Get the absolute path to the utils directory
        current_dir = os.path.dirname(os.path.abspath(__file__))  # component directory
        parent_dir = os.path.dirname(current_dir)  # views directory
        root_dir = os.path.dirname(parent_dir)  # project root directory
        config_file_path = os.path.join(root_dir, "utils", "config.py")

        if os.path.exists(config_file_path):
            # Read current file content
            with open(config_file_path, "r", encoding="utf-8") as file:
                content = file.read()

            # Properly format NEEDLE_OPTIONS, ensuring consistent string format
            formatted_options = []
            for option in NEEDLE_OPTIONS:
                formatted_options.append(f"'{option}'")

            needle_options_str = (
                "NEEDLE_OPTIONS = [" + ", ".join(formatted_options) + "]"
            )

            # Use regex to find and replace the NEEDLE_OPTIONS line
            pattern = r"NEEDLE_OPTIONS\s*=\s*\[[^\]]*\]"
            if re.search(pattern, content):
                new_content = re.sub(pattern, needle_options_str, content)

                # Write back to the file to ensure persistence
                with open(config_file_path, "w", encoding="utf-8") as file:
                    file.write(new_content)
                print(f"Successfully saved needle options to {config_file_path}")
                return True
            else:
                print("Could not find NEEDLE_OPTIONS in config file")
                return False
        else:
            print(f"Config file not found: {config_file_path}")
            return False
    except Exception as e:
        print(f"Error saving needle options: {str(e)}")
        messagebox.showerror("Save Error", f"Could not save needle options: {str(e)}")
        return False


if __name__ == "__main__":
    root = CTk()  # Create a CTk instance
    user_input_data = {}  # Initialize the dictionary to hold user input data
    user_input_frame = create_user_input_fields_ift(
        root, user_input_data
    )  # Create user input fields
    # Pack the user input frame
    user_input_frame.pack(fill="both", expand=True)

    root.mainloop()
