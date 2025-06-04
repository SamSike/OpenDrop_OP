from opendrop-ml.views.component.preparation import (
    create_plotting_checklist,
    create_analysis_checklist_ift,
    create_user_input_fields_ift,
)
from opendrop-ml.views.component.imageProcessing import ImageApp
from opendrop-ml.views.helper.style import set_light_only_color
from opendrop-ml.modules.ift.ift_data_processor import IftDataProcessor
from opendrop-ml.modules.core.classes import ExperimentalDrop, ExperimentalSetup

import customtkinter as ctk


class IftPreparation(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        user_input_data: ExperimentalSetup,
        experimental_drop: ExperimentalDrop,
        ift_processor: IftDataProcessor,
        **kwargs,
    ):
        super().__init__(parent, **kwargs)

        self.application = "IFT"
        self.user_input_data = user_input_data
        self.experimental_drop = experimental_drop
        self.ift_processor = ift_processor
        self.ift_processor.process_preparation(self.user_input_data)

        # Configure the grid to allow expansion for both columns
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)  # Left column for input fields
        self.grid_columnconfigure(1, weight=1)  # Right column for ImageApp

        # Create the frame for organizing input fields on the left with a background color
        self.input_fields_frame = ctk.CTkFrame(self)
        set_light_only_color(self.input_fields_frame, "outerframe")
        self.input_fields_frame.grid(
            row=0, column=0, sticky="nsew", padx=15, pady=(10, 0)
        )  # Left side for input fields

        # Ensure that the parent frame (input_fields_frame) resizes properly
        self.input_fields_frame.grid_rowconfigure(
            0, weight=1)  # Ensure row 0 expands
        self.input_fields_frame.grid_columnconfigure(
            0, weight=1
        )  # Ensure column 0 expands

        # Create the frame for the right side image processing
        self.image_app_frame = ctk.CTkFrame(self)
        self.image_app_frame.grid(
            row=0, column=1, sticky="nsew", padx=15, pady=(10, 0)
        )  # Right side for ImageApp

        # Instantiate the ImageApp on the right
        self.image_app = ImageApp(
            self.image_app_frame,
            self.user_input_data,
            self.experimental_drop,
            self.application,
        )
        # Pack the image app to fill the frame
        self.image_app.pack(fill="both", expand=True)

        # Create user input fields and analysis fields on the left
        self.create_user_input_fields(self.input_fields_frame)
        self.create_analysis_method_fields(self.input_fields_frame)
        self.create_fitting_view_fields(self.input_fields_frame)

    def create_user_input_fields(self, parent_frame):
        """Create and pack user input fields into the specified parent frame."""
        user_input_frame = create_user_input_fields_ift(
            self, parent_frame, self.user_input_data
        )
        user_input_frame.grid(
            row=0, column=0, sticky="nsew", pady=(10, 0))  # Use row 0
        # user_input_frame.pack(fill="x", expand=True, pady=(10, 0))  # Adjust as needed for your layout

    def create_analysis_method_fields(self, parent_frame):
        """Create and pack analysis method fields into the specified parent frame."""
        analysis_frame = create_analysis_checklist_ift(
            self, parent_frame, self.user_input_data
        )
        analysis_frame.grid(row=1, column=0, sticky="nsew", pady=(10, 0))

    def create_fitting_view_fields(self, parent_frame):
        """Create and pack Statisitcal Output fields into the specified parent frame."""
        fitting_view_frame = create_plotting_checklist(
            self, parent_frame, self.user_input_data
        )
        fitting_view_frame.grid(
            row=2, column=0, sticky="nsew", pady=10)  # Use row 1
