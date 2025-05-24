# views/output_page.py

from modules.core.classes import ExperimentalSetup
from views.helper.style import set_light_only_color

from tkinter import filedialog
import tkinter as tk
import customtkinter as ctk
from utils.tooltip_util import create_tooltip


class OutputPage(ctk.CTkFrame):
    def __init__(self, parent, user_input_data: ExperimentalSetup, **kwargs):
        super().__init__(parent, **kwargs)
        self.user_input_data = user_input_data

        # allow the middle column to expand when resized
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # -----------------------
        # Output Location Section
        # -----------------------
        output_frame = ctk.CTkFrame(self)
        set_light_only_color(output_frame, "outerframe")
        output_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        output_frame.grid_columnconfigure(1, weight=1)

        # Section title
        ctk.CTkLabel(
            output_frame,
            text="Output Location",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        ).grid(row=0, column=0, columnspan=4, padx=10, pady=(10,5), sticky="w")

        # Location row
        ctk.CTkLabel(output_frame, text="Location:", anchor="w") \
           .grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.location_entry = ctk.CTkEntry(output_frame, width=300)
        self.location_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        ctk.CTkButton(
            output_frame, text="Browse", command=self.browse_location
        ).grid(row=1, column=3, padx=10, pady=5)

        # Filename row
        ctk.CTkLabel(output_frame, text="Filename:", anchor="w") \
           .grid(row=2, column=0, sticky="w", padx=10, pady=(5,10))
        self.filename_var = ctk.StringVar()
        self.filename_var.trace_add("write", self.on_filename_change)
        self.filename_entry = ctk.CTkEntry(
            output_frame, width=300, textvariable=self.filename_var
        )
        self.filename_entry.grid(row=2, column=1, padx=10, pady=(5,10), sticky="ew")

        # "❓" help icon next to filename
        help_label = ctk.CTkLabel(
            output_frame,
            text="❓",
            font=ctk.CTkFont(size=16, weight="bold"),
            cursor="question_arrow"
        )
        help_label.grid(row=2, column=2, padx=5, pady=(5,10), sticky="w")

        # Combined tooltip: naming convention + default folder notice
        tooltip_text = (
            "Output files are named as:\n"
            "  Extracted_data_YYYYMMDD_HHMMSS\n\n"
            "Example:\n"
            "Extracted_data_20250524_192455\n\n"
            "Extracted_data: is if there is no specify filename\n"
            "then it will be like this Extracted_data;\n"
            "if there is fill in filename then it will be filename_YYYYMMDD_HHMMSS\n\n"
            "• YYYYMMDD   — extraction date (year-month-day)\n"
            "• HHMMSS     — save time (hour, minute, second)\n\n"
            "Ensures unique filenames for each run.\n\n"
            "If no location is specified, files will be\n"
            "saved to './output' folder by default."
        )
        create_tooltip(help_label, tooltip_text)

        # -----------------------
        # Figure Section (hidden)
        # -----------------------
    
    def browse_location(self):
        """Open a directory chooser and update the location entry."""
        directory = filedialog.askdirectory()
        if directory:
            self.location_entry.delete(0, tk.END)
            self.location_entry.insert(0, directory)
            self.user_input_data.output_directory = directory

    def on_filename_change(self, *args):
        """Store the filename in the user_input_data when changed."""
        self.user_input_data.filename = self.filename_var.get()
