from modules.contact_angle.ca_data_processor import CaDataProcessor
from modules.ift.ift_data_processor import IftDataProcessor
from modules.core.classes import ExperimentalSetup, ExperimentalDrop, DropData
from utils.os import resource_path, is_windows
from views.helper.validation import (
    validate_user_input_data_ift,
    validate_user_input_data_cm,
    validate_frame_interval,
)
from views.helper.style import get_color, set_light_only_color
from views.helper.theme import LIGHT_MODE
from views.navigation import create_navigation
from views.acquisition import Acquisition
from views.ift_preparation import IftPreparation
from views.ift_analysis import IftAnalysis
from views.ca_preparation import CaPreparation
from views.ca_analysis import CaAnalysis
from views.main_window import MainWindow
from views.output_page import OutputPage
from utils.enums import FunctionType, Stage, Move, RegionSelect

from customtkinter import CTkFrame, CTkButton, CTkToplevel, get_appearance_mode
from tkinter import messagebox, PhotoImage
from typing import List, Callable
from datetime import datetime
import os


def call_user_input(
    function_type: FunctionType, fitted_drop_data: DropData, main_window: MainWindow
):
    FunctionWindow(function_type, fitted_drop_data, main_window)


class FunctionWindow(CTkToplevel):
    main_window: MainWindow
    ca_processor: CaDataProcessor
    ift_processor: IftDataProcessor
    acquisition_frame: Acquisition
    ca_preparation_frame: CaPreparation
    ca_analysis_frame: CaAnalysis
    ift_preparation_frame: IftPreparation
    ift_analysis_frame: IftAnalysis
    output_frame: OutputPage
    after_ids: List[int]
    button_frame: CTkFrame
    back_button: CTkButton
    next_button: CTkButton
    save_button: CTkButton
    stages: List[Stage]
    current_stage: Stage
    next_stage: Callable[[], None]
    prev_stage: Callable[[], None]

    def __init__(
        self,
        function_type: FunctionType,
        fitted_drop_data: DropData,
        main_window: MainWindow,
    ):
        super().__init__()  # Call the parent class constructor
        self.title(function_type.value)
        self.geometry("1000x750")
        self.minsize(1000, 750)

        # main window
        self.main_window = main_window
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # after callback
        self.after_ids = []
        if get_appearance_mode() == LIGHT_MODE:
            self.FG_COLOR: str = get_color("background")
        else:
            self.FG_COLOR = self.cget("fg_color")

        set_light_only_color(self, "background")

        self.ca_processor = CaDataProcessor()
        self.ift_processor = IftDataProcessor()

        user_input_data: ExperimentalSetup = ExperimentalSetup()
        user_input_data.from_yaml(resource_path("user_config.yaml"))
        experimental_drop: ExperimentalDrop = ExperimentalDrop()

        user_input_data.screen_resolution = [
            self.winfo_screenwidth(),
            self.winfo_screenheight(),
        ]

        self.widgets(
            function_type, user_input_data, experimental_drop, fitted_drop_data
        )

        self.stages = list(Stage)
        self.current_stage = Stage.ACQUISITION

        self.mainloop()  # Start the main loop

    def widgets(
        self,
        function_type: FunctionType,
        user_input_data: ExperimentalSetup,
        experimental_drop: ExperimentalDrop,
        fitted_drop_data: DropData,
    ):
        # Create the navigation bar (progress bar style)
        self.next_stage, self.prev_stage = create_navigation(self)

        # Initialise frame for first stage
        self.acquisition_frame = Acquisition(
            self, user_input_data, function_type, fg_color=self.FG_COLOR
        )
        self.acquisition_frame.pack(fill="both", expand=True)

        # Frame for navigation buttons
        self.button_frame = CTkFrame(self)
        set_light_only_color(self.button_frame, "outerframe")
        self.button_frame.pack(side="bottom", fill="x", pady=10)

        # Add navigation buttons to the button frame
        self.back_button = CTkButton(
            self.button_frame,
            text="Back",
            command=lambda: self.back(function_type, user_input_data),
        )

        self.next_button = CTkButton(
            self.button_frame,
            text="Next",
            command=lambda: self.next(
                function_type, user_input_data, experimental_drop, fitted_drop_data
            ),
        )
        self.next_button.pack(side="right", padx=10, pady=10)

        # Add save button for OutputPage (initially hidden)
        self.save_button = CTkButton(
            self.button_frame,
            text="Save",
            command=lambda: self.save_output(function_type, user_input_data),
        )

    def back(self, function_type: FunctionType, user_input_data: ExperimentalSetup):
        self.update_stage(Move.Back.value)
        # Go back to the previous screen
        if self.current_stage == Stage.ACQUISITION:

            self.back_button.pack_forget()
            self.acquisition_frame.pack(fill="both", expand=True)

            if function_type == FunctionType.INTERFACIAL_TENSION:
                self.ift_preparation_frame.pack_forget()
            else:
                self.ca_preparation_frame.pack_forget()

        elif self.current_stage == Stage.PREPARATION:
            if function_type == FunctionType.INTERFACIAL_TENSION:
                self.ift_preparation_frame.pack(fill="both", expand=True)
                self.ift_analysis_frame.pack_forget()
            else:
                self.ca_preparation_frame.pack(fill="both", expand=True)
                self.ca_analysis_frame.pack_forget()

        elif self.current_stage == Stage.ANALYSIS:
            if function_type == FunctionType.INTERFACIAL_TENSION:
                self.ift_analysis_frame.pack(fill="both", expand=True)
            else:
                self.ca_analysis_frame.pack(fill="both", expand=True)

            self.output_frame.pack_forget()

            # Show the next button and hide the save button when going back
            self.next_button.pack(side="right", padx=10, pady=10)
            self.save_button.pack_forget()

    def next(self, function_type, user_input_data, experimental_drop, fitted_drop_data):
        try:
            self.update_stage(Move.Next.value)
            # Handle the "Next" button functionality
            if self.current_stage == Stage.PREPARATION:

                # First check if the user has imported files
                if not self.check_import(user_input_data):
                    self.update_stage(Move.Back.value)
                    messagebox.showinfo(
                        "No Selection", "Please select at least one file.", parent=self
                    )
                    return

                # Then check if the frame interval is valid
                # if function_type == FunctionType.INTERFACIAL_TENSION:
                if not validate_frame_interval(user_input_data):
                    self.update_stage(Move.Back.value)
                    messagebox.showinfo(
                        "Missing", "Frame Interval is required.", parent=self
                    )
                    return
                self.back_button.pack(side="left", padx=10, pady=10)
                # self.ift_processor.processPreparation(user_input_data)
                # user have selected at least one file
                self.acquisition_frame.pack_forget()
                # Initialise Preparation frame
                if function_type == FunctionType.INTERFACIAL_TENSION:
                    self.ift_preparation_frame = IftPreparation(
                        self,
                        user_input_data,
                        experimental_drop,
                        self.ift_processor,
                        fg_color=self.FG_COLOR,
                    )
                    self.ift_preparation_frame.pack(fill="both", expand=True)

                else:
                    self.ca_preparation_frame = CaPreparation(
                        self, user_input_data, experimental_drop, fg_color=self.FG_COLOR
                    )
                    self.ca_preparation_frame.pack(fill="both", expand=True)

            elif self.current_stage == Stage.ANALYSIS:
                # Validate user input data
                if function_type == FunctionType.INTERFACIAL_TENSION:
                    validation_messages = validate_user_input_data_ift(
                        user_input_data)

                elif function_type == FunctionType.CONTACT_ANGLE:
                    validation_messages = validate_user_input_data_cm(
                        user_input_data, experimental_drop
                    )

                if validation_messages:
                    self.update_stage(Move.Back.value)
                    all_messages = "\n".join(validation_messages)
                    # Show a single pop-up message with all validation messages
                    messagebox.showinfo(
                        "Missing: \n", all_messages, parent=self)
                else:
                    if function_type == FunctionType.INTERFACIAL_TENSION:
                        self.ift_preparation_frame.pack_forget()
                        self.ift_analysis_frame = IftAnalysis(
                            self,
                            user_input_data,
                            self.ift_processor,
                            fg_color=self.FG_COLOR,
                        )
                        self.ift_analysis_frame.pack(fill="both", expand=True)
                        self.withdraw()
                        self.ift_processor.process_data(user_input_data)
                        self.deiconify()
                    else:
                        self.ca_preparation_frame.pack_forget()
                        self.ca_analysis_frame = CaAnalysis(
                            self, user_input_data, fg_color=self.FG_COLOR
                        )
                        self.ca_analysis_frame.pack(fill="both", expand=True)

                        # analysis the given input data and send the output to the ca_analysis_frame for display
                        self.withdraw()
                        self.ca_processor.process_data(
                            fitted_drop_data,
                            user_input_data,
                            callback=self.ca_analysis_frame.receive_output,
                        )
                        self.deiconify()

            elif self.current_stage == Stage.OUTPUT:
                if function_type == FunctionType.INTERFACIAL_TENSION:
                    self.ift_analysis_frame.pack_forget()
                else:
                    self.ca_analysis_frame.pack_forget()

                # Initialise Output frame
                self.output_frame = OutputPage(
                    self, user_input_data, fg_color=self.FG_COLOR
                )

                # Show the OutputPage
                self.output_frame.pack(fill="both", expand=True)

                # Hide the next button and show the save button
                self.next_button.pack_forget()
                self.save_button.pack(side="right", padx=10, pady=10)
        except Exception as e:
            # Catch any unexpected exception and show it
            print(f"[Error] Unexpected exception: {e}")
            messagebox.showerror(
                "Invalid Image",
                f"This image is not suitable for {function_type.value} analysis.\nPlease go back and select another image or application.",
                parent=self,
            )
            self.on_closing()
            return

    def save_output(
        self, function_type: FunctionType, user_input_data: ExperimentalSetup
    ):
        if not user_input_data.output_directory:
            user_input_data.output_directory = os.path.join(
                os.path.join(os.path.expanduser("~")), "OpenDrop", "outputs"
            )

        if user_input_data.output_directory.startswith("~"):
            user_input_data.output_directory = os.path.expanduser(
                user_input_data.output_directory
            )

        # Prepare output path
        os.makedirs(user_input_data.output_directory, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename: str = ""
        if user_input_data.filename:
            filename = f"{user_input_data.filename}_{timestamp}.csv"
        else:
            function_type_formatted = function_type.value.replace(
                " ", "_"
            )  # Interfacial Tension -> Interfacial_Tension
            if (
                user_input_data.drop_id_method == RegionSelect.USER_SELECTED
                or user_input_data.needle_region_method == RegionSelect.USER_SELECTED
            ):
                filename = f"Manual_{function_type_formatted}_{timestamp}.csv"
            else:
                filename = f"Automated_{function_type_formatted}_{timestamp}.csv"

        output_file = os.path.join(user_input_data.output_directory, filename)
        if function_type == FunctionType.INTERFACIAL_TENSION:
            self.ift_processor.save_result(user_input_data, output_file)
        else:
            self.ca_processor.save_result(user_input_data, output_file)

        messagebox.showinfo(
            "Save Successful",
            f"Results have been saved to:\n{output_file}",
            parent=self,
        )
        self.on_closing()

    def update_stage(self, direction: int):
        self.current_stage = self.stages[
            (self.stages.index(self.current_stage) + direction) % len(self.stages)
        ]
        if direction == Move.Next.value:
            self.next_stage()
        elif direction == Move.Back.value:
            self.prev_stage()

    def check_import(self, user_input_data: ExperimentalSetup) -> bool:
        return (
            user_input_data.number_of_frames is not None
            and user_input_data.number_of_frames > 0
            and user_input_data.import_files is not None
            and len(user_input_data.import_files) > 0
            and len(user_input_data.import_files) == user_input_data.number_of_frames
        )

    def register_after(self, delay_ms, callback: Callable):
        after_id = self.after(delay_ms, callback)
        self.after_ids.append(after_id)
        return after_id

    def on_closing(self):
        try:
            # print("Cleaning up after tasks:", self.after_ids)
            # cancel after callback
            for after_id in self.after_ids:
                try:
                    self.after_cancel(after_id)
                except Exception as e:
                    print("after_cancel error:", e)

            # destroy all widgets
            for widget in self.winfo_children():
                try:
                    widget.destroy()
                except Exception as e:
                    print("widget destroy error:", e)

            self.quit()
            self.destroy()

            # show main window
            if self.main_window.winfo_exists():
                self.main_window.deiconify()

        except Exception as e:
            print("on_closing error:", e)
            import sys

            sys.exit(1)
