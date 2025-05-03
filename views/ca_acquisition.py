from customtkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

from utils.image_handler import ImageHandler
from utils.config import *
from utils.validators import *
from views.component.option_menu import OptionMenu
from views.component.integer_entry import IntegerEntry
import os

class CaAcquisition(CTkFrame):
    def __init__(self, parent, user_input_data, **kwargs):
        super().__init__(parent, **kwargs)

        self.user_input_data = user_input_data
        self.image_handler = ImageHandler()
        self.current_image = None
        self.tk_image = None

        self._resize_job = None
        self.resize_delay_ms = 100

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.input_fields_frame = CTkFrame(self)
        self.input_fields_frame.grid(row=0, column=0, sticky="ns", padx=15, pady=(10, 0))

        image_acquisition_frame = CTkFrame(self.input_fields_frame)
        image_acquisition_frame.grid(sticky="nw", padx=15, pady=10)
        image_acquisition_frame.grid_columnconfigure(2, weight=1)

        self.image_source = OptionMenu(self, image_acquisition_frame, "Image source:",
                                       ["Local images"], self.update_image_source, rw=0)
        self.setup_choose_files_frame(image_acquisition_frame)
        self.edgefinder = OptionMenu(
            self, image_acquisition_frame, "Edge finder:", EDGEFINDER_OPTIONS, self.update_edgefinder, rw=2)
        self.frame_interval = IntegerEntry(
            self, image_acquisition_frame, "frame_interval (s):", self.update_frame_interval, rw=4, cl=0)
        
        self.images_frame = CTkFrame(self, fg_color="transparent")
        self.images_frame.grid(row=0, column=1, sticky="nsew", padx=15, pady=(10, 0))
        self.images_frame.grid_rowconfigure(0, weight=1)
        self.images_frame.grid_columnconfigure(0, weight=1)

    def update_image_source(self, selection):
        print(selection)
        if selection == FILE_SOURCE_OPTIONS_CA[0]:
            self.choose_files_button.configure(state="normal")
        else:
            self.choose_files_button.configure(state="disabled")

        self.user_input_data.image_source = selection

    def update_frame_interval(self, *args):
        self.user_input_data.frame_interval = self.frame_interval.get_value()

    def update_edgefinder(self, *args):
        self.user_input_data.edgefinder = self.edgefinder.get_value()

    def setup_choose_files_frame(self, frame):
        self.choose_files_label = CTkLabel(frame, text="Image Files: ", width=150, anchor="w")
        self.choose_files_label.grid(row=1, column=0, sticky="w", padx=(5, 5), pady=(5, 5))

        self.choose_files_button = CTkButton(
            frame,
            text="Choose File(s)",
            command=self.select_files,
            width=150,
        )
        self.choose_files_button.grid(row=1, column=1, sticky="w", padx=(5, 5), pady=(5, 5))
    

    def select_files(self):
        for widget in self.images_frame.winfo_children():
            widget.destroy()
        self.image_label = None
        self.name_label = None
        self.image_navigation_frame = None
        self.tk_image = None
        self.current_image = None
        if self._resize_job:
            self.after_cancel(self._resize_job)
            self._resize_job = None

        import_files = filedialog.askopenfilenames(
            title="Select Files",
            filetypes=IMAGE_TYPE,
            initialdir=PATH_TO_SCRIPT
        )

        if not import_files:
             self.choose_files_button.configure(text="Choose File(s)")
             return

        self.user_input_data.import_files = import_files
        self.current_index = 0
        num_files = len(self.user_input_data.import_files)
        self.user_input_data.number_of_frames = num_files

        self.choose_files_button.configure(
            text=f"{num_files} File(s) Selected")

        self.initialize_image_display(self.images_frame)


    def initialize_image_display(self, frame):
        display_frame = CTkFrame(frame, fg_color="transparent")
        display_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

        display_frame.grid_columnconfigure(0, weight=1)
        display_frame.grid_rowconfigure(0, weight=0)
        display_frame.grid_rowconfigure(1, weight=1)
        display_frame.grid_rowconfigure(2, weight=0)

        self.image_label = CTkLabel(display_frame, text="", fg_color="lightgrey")
        self.image_label.grid(row=1, column=0, padx=10, pady=(10, 5), sticky="nsew")
        self.image_label.bind('<Configure>', self.on_label_resize)

        file_name = os.path.basename(self.user_input_data.import_files[self.current_index])
        self.name_label = CTkLabel(display_frame, text=file_name)
        self.name_label.grid(row=0, column=0, pady=(5,0))

        self.image_navigation_frame = CTkFrame(display_frame, fg_color="transparent")
        self.image_navigation_frame.grid(row=2, column=0, pady=(5, 10))

        self.prev_button = CTkButton(self.image_navigation_frame, text="<", command=lambda: self.change_image(-1), width=3)
        self.prev_button.grid(row=0, column=0, padx=5, pady=5)

        self.index_entry = CTkEntry(self.image_navigation_frame, width=5)
        self.index_entry.grid(row=0, column=1, padx=5, pady=5)
        self.index_entry.bind("<Return>", lambda event: self.update_index_from_entry())
        self.index_entry.insert(0, str(self.current_index + 1))

        self.navigation_label = CTkLabel(self.image_navigation_frame, text=f" of {self.user_input_data.number_of_frames}", font=("Arial", 12))
        self.navigation_label.grid(row=0, column=2, padx=5, pady=5)

        self.next_button = CTkButton(self.image_navigation_frame, text=">", command=lambda: self.change_image(1), width=3)
        self.next_button.grid(row=0, column=3, padx=5, pady=5)

        self.load_image(self.user_input_data.import_files[self.current_index])

    def load_image(self, selected_image):
        try:
            self.current_image = Image.open(selected_image)
            if hasattr(self, 'image_label') and self.image_label.winfo_exists() and self.image_label.winfo_width() > 1:
                 self._perform_resize()
        except FileNotFoundError:
            print(f"Error: The image file {selected_image} was not found.")
            self.current_image = None
            if hasattr(self, 'image_label') and self.image_label:
                self.image_label.configure(image=None, text=f"Not Found:\n{os.path.basename(selected_image)}")
        except Exception as e:
            print(f"Error loading image {selected_image}: {e}")
            self.current_image = None
            if hasattr(self, 'image_label') and self.image_label:
                self.image_label.configure(image=None, text="Error Loading")

    def display_image(self, target_width, target_height):
        if self.current_image and target_width > 1 and target_height > 1:
            try:
                original_width, original_height = self.current_image.size
                aspect_ratio = original_width / original_height

                new_width = target_width
                new_height = int(new_width / aspect_ratio)
                if new_height > target_height:
                    new_height = target_height
                    new_width = int(new_height * aspect_ratio)

                new_width = max(1, new_width)
                new_height = max(1, new_height)

                resized_pil_image = self.current_image.copy()
                resized_pil_image.thumbnail((new_width, new_height), Image.Resampling.LANCZOS)

                self.tk_image = CTkImage(
                    light_image=resized_pil_image,
                    size=(resized_pil_image.width, resized_pil_image.height)
                    )

                if hasattr(self, 'image_label') and self.image_label:
                    self.image_label.configure(image=self.tk_image, text="")
                    self.image_label.image = self.tk_image
            except Exception as e:
                print(f"Error resizing/displaying image: {e}")
                if hasattr(self, 'image_label') and self.image_label:
                    self.image_label.configure(image=None, text="Display Error")
        elif hasattr(self, 'image_label') and self.image_label:
             self.image_label.configure(image=None, text="No Image")
             self.image_label.image = None

    def _perform_resize(self):
        if not hasattr(self, 'image_label') or not self.image_label.winfo_exists():
            return
        widget_width = self.image_label.winfo_width()
        widget_height = self.image_label.winfo_height()
        pad_x = 0
        pad_y = 0
        target_width = max(1, widget_width - pad_x)
        target_height = max(1, widget_height - pad_y)

        self.display_image(target_width, target_height)
        self._resize_job = None

    def on_label_resize(self, event):
        if self._resize_job:
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(self.resize_delay_ms, self._perform_resize)

    def change_image(self, direction):
        if self.user_input_data.import_files:
            self.current_index = (self.current_index + direction) % self.user_input_data.number_of_frames
            self.load_image(self.user_input_data.import_files[self.current_index])
            self.update_index_entry()
            if hasattr(self, 'name_label') and self.name_label:
                 file_name = os.path.basename(self.user_input_data.import_files[self.current_index])
                 self.name_label.configure(text=file_name)

    def update_index_from_entry(self):
        try:
            new_index = int(self.index_entry.get()) - 1
            if 0 <= new_index < self.user_input_data.number_of_frames:
                if new_index != self.current_index:
                     self.current_index = new_index
                     self.load_image(self.user_input_data.import_files[self.current_index])
                     if hasattr(self, 'name_label') and self.name_label:
                         file_name = os.path.basename(self.user_input_data.import_files[self.current_index])
                         self.name_label.configure(text=file_name)
            else:
                print("Index out of range.")
                self.update_index_entry()
        except ValueError:
            print("Invalid input. Please enter a number.")
            self.update_index_entry()
        except Exception as e:
             print(f"Error updating index: {e}")
             self.update_index_entry()

    def update_index_entry(self):
        if hasattr(self, 'index_entry') and self.index_entry:
            self.index_entry.delete(0, 'end')
            self.index_entry.insert(0, str(self.current_index + 1))

    def destroy(self):
        if self._resize_job:
            self.after_cancel(self._resize_job)
        super().destroy()