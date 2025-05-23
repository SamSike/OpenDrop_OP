from utils.enums import ThresholdSelect, RegionSelect
from modules.core.classes import ExperimentalDrop, ExperimentalSetup
from modules.ift.ift_data_processor import IftDataProcessor

# frame_interval


def validate_frame_interval(user_input_data: ExperimentalSetup):
    print(user_input_data.import_files)
    if len(user_input_data.import_files) > 1:
        if user_input_data.frame_interval == 0:
            return False
    return True

# def validate_wait_time(user_input_data):
#     if len(user_input_data.import_files) > 1:
#             # Check if wait_time is None or empty
#         if not user_input_data.wait_time:
#              return False
#     return True


def validate_user_input_data_ift(user_input_data: ExperimentalSetup):
    """Validate the user input data and return messages for missing fields."""
    messages = []

    # Ensure if drop region is chosen, it must not be None
    # if user_input_data.drop_id_method != 'Automated' and user_input_data.ift_drop_region is None:
    #     messages.append("Please select drop region")

    # # Ensure if needle region is chosen, it must not be None
    # if user_input_data.needle_region_choice != 'Automated' and user_input_data.ift_needle_region is None:
    #     messages.append("Please select needle region")

    # Check user_input_fields for None values

    required_fields = {
        'drop_density': "Drop Density",
        'needle_diameter_mm': "Needle Diameter"
        # ,'density_outer': "Continuous Density",
        # 'pixel_mm': "Pixel to mm"
    }

    for field, label in required_fields.items():
        # Get the attribute or None if missing
        value = getattr(user_input_data, field, None)
        print(field, " is ", value)
        if value is None:  # Check for both None and empty string
            messages.append(f"{label} is required")

    # Check if analysis_method_fields has at least one method selected
    if not any(user_input_data.analysis_methods_pd.values()):
        messages.append("At least one analysis method must be selected.")

    # Allow user to select regions manually if chosen
    if user_input_data.drop_id_method != RegionSelect.AUTOMATED or user_input_data.needle_region_method != RegionSelect.AUTOMATED:
        IftDataProcessor().process_preparation(user_input_data)

    return messages


def validate_user_input_data_cm(user_input_data: ExperimentalSetup, experimental_drop: ExperimentalDrop):
    """Validate the user input data and return messages for missing fields."""
    messages = []

    # Check user_input_fields for None values
    if user_input_data.threshold_method != ThresholdSelect.AUTOMATED and not user_input_data.threshold_val:
        messages.append("Please enter threshold value")

    if not any(user_input_data.analysis_methods_ca.values()):
        messages.append("At least one analysis method must be selected.")

    # Check if analysis_method_fields has at least one method selected
    if not any(user_input_data.analysis_methods_pd.values()):
        messages.append("At least one analysis method must be selected.")

    return messages
