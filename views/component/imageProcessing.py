import customtkinter as ctk
from PIL import Image #, ImageTk
from utils.image_handler import ImageHandler
import os
# from modules.image.select_regions import set_drop_region,set_surface_line, correct_tilt,user_ROI
# from modules.core.classes import ExperimentalSetup, ExperimentalDrop, DropData, Tolerances
# from tkinter import messagebox
from modules.image.read_image import get_image
from views.component.check_button import CheckButton
from views.helper.style import set_light_only_color

class ImageApp(ctk.CTkFrame):
    def __init__(self, parent, user_input_data, experimental_drop, application):
        super().__init__(parent)
        set_light_only_color(self, "outerframe")

        self.application = application
        self.user_input_data = user_input_data
        self.experimental_drop = experimental_drop
        # Initialize ImageHandler instance
        self.image_handler = ImageHandler()

        # Load images from the directory
        self.image_paths = user_input_data.import_files  # Load all images
        self.current_index = 0  # To keep track of the currently displayed image
        self.current_image = None # Initialize current_image
        self.tk_image = None      # Initialize tk_image

        # --- Configure ImageApp's own grid ---
        # Make the row and columns where main_frame is placed expandable
        self.grid_rowconfigure(0, weight=1) # Assuming main_frame is in row 0 now (see below)
        self.grid_columnconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self)
        # Place main_frame in ImageApp's grid, row 0, column 0, making it expand
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)

        # --- Configure main_frame's internal grid ---
        # Column 0 will hold everything (display_frame and image_processing_frame)
        self.main_frame.grid_columnconfigure(0, weight=1)
        # Row 0 for display_frame (expandable)
        self.main_frame.grid_rowconfigure(0, weight=1)
        # Row 1 for image_processing_frame (fixed height)
        self.main_frame.grid_rowconfigure(1, weight=0)

        # Call the function to initialize the image display area and buttons
        self.initialize_image_display(self)

    def initialize_image_display(self, frame):
        """Initialize the image display and navigation buttons inside the provided frame (frame is main_frame)."""
        display_frame = ctk.CTkFrame(frame) # Parent is main_frame now
        # Place display_frame in main_frame's grid (row 0)
        set_light_only_color(display_frame, "entry")
        display_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10) # Fill the top row of main_frame

        # --- Configure display_frame's internal grid ---
        display_frame.grid_columnconfigure(0, weight=1) # Single column, expandable
        display_frame.grid_rowconfigure(0, weight=0)    # Row for filename (fixed height)
        display_frame.grid_rowconfigure(1, weight=1)    # Row for image_label (expandable)
        display_frame.grid_rowconfigure(2, weight=0)    # Row for navigation (fixed height)

        # Create a label to display the current image's filename
        filename_text = ""
        if self.image_paths:
             filename_text = os.path.basename(self.image_paths[self.current_index])
        self.name_label = ctk.CTkLabel(display_frame, text=filename_text)
        # Place in display_frame's grid, row 0, centered
        self.name_label.grid(row=0, column=0, padx=10, pady=10, sticky="")

        self.image_label = ctk.CTkLabel(display_frame, text="", fg_color="lightgrey")
        # Place in display_frame's grid, row 1, fill the cell with equal padding
        self.image_label.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Create a frame for image navigation controls
        self.image_navigation_frame = ctk.CTkFrame(display_frame)
        # Place in display_frame's grid, row 2, centered
        set_light_only_color(self.image_navigation_frame, "entry")
        self.image_navigation_frame.grid(row=2, column=0, padx=10, pady=10, sticky="")

        # --- Navigation controls inside image_navigation_frame ---
        # (Layout within this frame remains the same)
        self.prev_button = ctk.CTkButton(self.image_navigation_frame, text="<", command=lambda: self.change_image(-1), width=3)
        self.prev_button.grid(row=0, column=0, padx=5, pady=5)

        self.index_entry = ctk.CTkEntry(self.image_navigation_frame, width=5)
        self.index_entry.grid(row=0, column=1, padx=5, pady=5)
        self.index_entry.bind("<Return>", lambda event: self.update_index_from_entry())
        if self.image_paths:
             self.index_entry.insert(0, str(self.current_index + 1))

        navigation_text = ""
        if self.image_paths:
            navigation_text = f" of {len(self.image_paths)}"
        self.navigation_label = ctk.CTkLabel(self.image_navigation_frame, text=navigation_text, font=("Arial", 12))
        self.navigation_label.grid(row=0, column=2, padx=5, pady=5)

        self.next_button = ctk.CTkButton(self.image_navigation_frame, text=">", command=lambda: self.change_image(1), width=3)
        self.next_button.grid(row=0, column=3, padx=5, pady=5)

        # # Create a separate frame for the "Show Image Processing Steps" checkbox (this is the second section)
        # self.image_processing_frame = ctk.CTkFrame(frame)
        # self.image_processing_frame.grid(sticky="nsew", padx=15, pady=(10, 0))
        self.load_image(self.user_input_data.import_files[self.current_index])

        # # Callback for checkbox to update show_popup
        # def update_pop_bool(*args):
        #     # 1: true, 0: false
        #     print("trigger: ",self.show_popup_var.get_value())
        #     self.user_input_data.show_popup = self.show_popup_var.get_value()

        # # Create the checkbox in the separate frame
        # self.show_popup_var = CheckButton(
        #     self,
        #     self.image_processing_frame,
        #     "Show Image Processing Steps",
        #     update_pop_bool,
        #     rw=1, cl=0,
        #     state_specify='normal'
        # )

        # self.update_image_processing_button()

    def load_images(self):
        """Load all images from the specified directory and return their paths."""
        directory = "experimental_data_set"
        return self.image_handler.get_image_paths(directory)

    def load_image(self, selected_image):
        """Load the selected image and display it with fixed size."""
        try:
            self.current_image = Image.open(selected_image)
            get_image(self.experimental_drop, self.user_input_data, self.current_index)
            # Call display_image directly after loading
            self.display_image()
        except FileNotFoundError:
            print(f"Error: The image file {selected_image} was not found.")
            self.current_image = None
            if hasattr(self, 'image_label'):
                self.image_label.configure(image=None, text=f"Not Found:\n{os.path.basename(selected_image)}")
        except Exception as e:
             print(f"Error loading image {selected_image}: {e}")
             self.current_image = None
             if hasattr(self, 'image_label'):
                self.image_label.configure(image=None, text=f"Error loading:\n{os.path.basename(selected_image)}")

    def display_image(self):
        """Display the currently loaded image with fixed size constraints."""
        if self.current_image is None:
             if hasattr(self, 'image_label'):
                 self.image_label.configure(image=None, text="No Image")
             return

        try:
             original_width, original_height = self.current_image.size

             # --- Define Fixed Size Constraint (e.g., max_height) ---
             max_height = 250 # Adjust this value as needed for this component
             aspect_ratio = original_width / original_height

             if original_height > max_height:
                 new_height = max_height
                 new_width = int(new_height * aspect_ratio)
             else:
                 # Use original size if smaller than max_height
                 new_width = original_width
                 new_height = original_height

             # Ensure dimensions are at least 1x1
             new_width = max(1, new_width)
             new_height = max(1, new_height)

             # Create CTkImage with calculated size
             # Use Pillow's LANCZOS for potentially better downscaling quality
             resized_pil_image = self.current_image.copy()
             resized_pil_image.thumbnail((new_width, new_height), Image.Resampling.LANCZOS)

             self.tk_image = ctk.CTkImage(
                 light_image=resized_pil_image, # Pass the resized PIL image
                 size=(resized_pil_image.width, resized_pil_image.height) # Use actual size after thumbnail
                 )

             if hasattr(self, 'image_label'):
                 self.image_label.configure(image=self.tk_image, text="") # Update label
                 self.image_label.image = self.tk_image # Keep reference

        except Exception as e:
             print(f"Error creating/displaying fixed size CTkImage: {e}")
             if hasattr(self, 'image_label'):
                 self.image_label.configure(image=None, text="Error displaying image")

    def change_image(self, direction):
        """Change the currently displayed image based on the direction."""
        if self.image_paths:
            self.current_index = (self.current_index + direction) % len(self.image_paths)
            # load_image will now handle displaying the fixed size image
            self.load_image(self.image_paths[self.current_index])
            self.update_index_entry()
            file_name = os.path.basename(self.image_paths[self.current_index])
            self.name_label.configure(text=file_name)



    def update_index_from_entry(self):
        """Update current index based on user input in the entry."""
        if not self.image_paths: return
        try:
            new_index = int(self.index_entry.get()) - 1 # Zero-based
            if 0 <= new_index < len(self.image_paths):
                if new_index != self.current_index:
                     self.current_index = new_index
                     # load_image will now handle displaying the fixed size image
                     self.load_image(self.image_paths[self.current_index])
                     file_name = os.path.basename(self.image_paths[self.current_index])
                     self.name_label.configure(text=file_name)
            else:
                print("Index out of range.")
                self.update_index_entry()
        except ValueError:
            print("Invalid input. Please enter a number.")
            self.update_index_entry()

    def update_index_entry(self):
        """Update the index entry to reflect the current index."""
        if not self.image_paths: return
        self.index_entry.delete(0, 'end')
        self.index_entry.insert(0, str(self.current_index + 1))




