import customtkinter as ctk
from PIL import ImageTk, Image
from utils.image_handler import ImageHandler
import os


class ImageGallery(ctk.CTkFrame):
    def __init__(self, parent, import_files,on_image_change_callback=None):
        # Pass fg_color='transparent' if the parent wrapper already has the desired background
        super().__init__(parent, fg_color='transparent')
        self.filename_label = ctk.CTkLabel(
            self,
            text="",
            font=("Arial", 14),
            text_color="white",
            fg_color="transparent",       
            corner_radius=4,         
            height=30                
        )
        self.filename_label.grid(
            row=0, column=0, columnspan=2,
            pady=(10, 5), padx=10,   
            sticky="ew"              
        )

        self.image_handler = ImageHandler()
        self.image_paths = import_files
        self.current_index = 0
        self.current_image = None # Store the original PIL Image
        self.tk_image = None # Store the CTkImage
        self.on_image_change_callback = on_image_change_callback
        # Remove the extra main_frame, use self (ImageGallery frame) directly for simplicity
        # This makes binding Configure easier and reduces nesting

        # Configure grid for self (ImageGallery frame)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Image display label - Center the label itself within its grid cell
        # The parent (ift_analysis.image_frame_wrapper) will center this whole ImageGallery widget
        # sticky="" (default) or "ns" or "n" or "s" might be better if we don't want label itself to expand
        # Let's try default sticky first. The PIL image size will dictate label size.
        self.image_label = ctk.CTkLabel(self, text="", fg_color="transparent")
        self.image_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        # Navigation buttons frame
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)


        # Previous and Next buttons (place inside button_frame)
        self.prev_button = ctk.CTkButton(
            self.button_frame, text="Previous", command=lambda: self.change_image(-1), width=80, height=25)
        # Use pack for easier centering within the button frame or adjust grid columns
        # self.prev_button.pack(side="left", padx=20, pady=5)
        self.prev_button.grid(row=0, column=0, padx=(20, 5), sticky="e")


        self.next_button = ctk.CTkButton(
            self.button_frame, text="Next", command=lambda: self.change_image(1), width=80, height=25)
        # self.next_button.pack(side="right", padx=20, pady=5)
        self.next_button.grid(row=0, column=1, padx=(5, 20), sticky="w")


        if self.image_paths:
            self.load_image(self.image_paths[self.current_index], path_hint=self.image_paths[self.current_index])
        else:
            # Handle case with no images
            self.image_label.configure(text="No images found")


    def load_image(self, selected_image, path_hint=None):
        """Load the selected image, and optionally provide a path to show filename."""
        print("Loading image: ", selected_image)
        try:
            if isinstance(selected_image, Image.Image):
                self.current_image = selected_image
            else:
                self.current_image = Image.open(selected_image)

            self.display_image()

            if path_hint is not None and isinstance(path_hint, str):
                file_name = os.path.basename(path_hint)
            elif isinstance(selected_image, str):
                file_name = os.path.basename(selected_image)
            else:
                file_name = f"Image {self.current_index + 1} / {len(self.image_paths)}"

            self.filename_label.configure(text=file_name)

        except FileNotFoundError:
            print(f"Error: The image file {selected_image} was not found.")
            self.current_image = None
            self.image_label.configure(image=None, text="Error loading")
        except Exception as e:
            print(f"Error opening image {selected_image}: {e}")
            self.current_image = None
            self.image_label.configure(image=None, text="Error displaying image")


    # RESTORED display_image logic using fixed max_height
    def display_image(self):
        """Display the currently loaded image with fixed size constraints."""
        if self.current_image is None:
            self.image_label.configure(image=None) # Clear image if none loaded
            return

        try:
            original_width, original_height = self.current_image.size

            # Use ImageHandler or similar logic to get fitting dimensions based on max_height
            # Assuming ImageHandler has a method like this, or implement simple scaling
            # --- Using a fixed max_height (e.g., 250) ---
            max_height = 250 # Or another value you prefer
            aspect_ratio = original_width / original_height
            if original_height > max_height:
                new_height = max_height
                new_width = int(new_height * aspect_ratio)
            else:
                new_width = original_width
                new_height = original_height

            # Ensure dimensions are at least 1x1
            new_width = max(1, new_width)
            new_height = max(1, new_height)

            self.tk_image = ctk.CTkImage(
                light_image=self.current_image,
                size=(new_width, new_height))

            self.image_label.configure(image=self.tk_image, text="") # Update label
        except Exception as e:
            print(f"Error creating fixed size CTkImage: {e}")
            self.image_label.configure(image=None, text="Error displaying image")


    def change_image(self, direction):
        """Change the currently displayed image based on the direction."""
        if self.image_paths:
            self.current_index = (self.current_index + direction) % len(self.image_paths)  # Wrap around
        self.load_image(self.image_paths[self.current_index], path_hint=self.image_paths[self.current_index])
            if self.on_image_change_callback:
                self.on_image_change_callback(self.current_index)
    
    def set_image(self, img):
        """Set and display a new image in the gallery."""
        self.current_image = img
        self.display_image()
