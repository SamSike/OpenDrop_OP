from modules.core.classes import ExperimentalSetup, ExperimentalDrop
from modules.preprocessing.ExtractData import ExtractedData
from utils.image_handler import ImageHandler
from utils.config import LEFT_ANGLE, RIGHT_ANGLE, BASELINE_INTERCEPTS, CONTACT_POINTS, TANGENT_LINES, FIT_SHAPE, BASELINE, FIT_SHAPE
from utils.enums import FittingMethod
from views.helper.theme import get_system_text_color
from views.component.CTkXYFrame import CTkXYFrame
from views.helper.style import set_light_only_color

from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkEntry, CTkComboBox, CTkImage, CTkRadioButton, IntVar, StringVar
from matplotlib.backends.backend_agg import FigureCanvasAgg
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import io
import os
import math
import cv2
import matplotlib.pyplot as plt


class CaAnalysis(CTkFrame):
    def __init__(self, parent, user_input_data, **kwargs):
        super().__init__(parent, **kwargs)
        self.user_input_data = user_input_data

        self.grid_columnconfigure(0, weight=1)  # Let table expand
        # Prevent images_frame from expanding
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)

        self.image_handler = ImageHandler()

        self.num_of_processed = 0
        self.cropped_images = {}              # Cropped pictures
        self.cropped_angle_images = {}        # Crop diagram after superimposing angles
        self.left_angles = []
        self.right_angles = []

        self.available_methods = {}   # {index: [methods]}

        self.preformed_methods = {
            key: value for key, value in user_input_data.analysis_methods_ca.items() if value
        }

        self.table_data = []
        self.create_table(
            parent=self,
            rows=user_input_data.number_of_frames,
            columns=len(self.preformed_methods) + 1,
            headers=["Index"] + list(self.preformed_methods.keys()),
        )

        self.visualisation_container = CTkFrame(self)
        self.visualisation_container.grid(
            row=0, column=1, sticky="nsew", padx=15, pady=(10, 0))

        self.image_wrapper_frame = CTkFrame(
            self.visualisation_container, fg_color="transparent")
        set_light_only_color(self.image_wrapper_frame, "outerframe")
        self.image_wrapper_frame.grid(row=1, column=0, sticky="ewsn")

        self.current_index = 0
        self.highlight_row(self.current_index)
        self.initialize_image_display(self.image_wrapper_frame)

    def create_table(self, parent, rows, columns, headers):
        table_frame = CTkXYFrame(parent)
        set_light_only_color(table_frame, "outerframe")
        table_frame.grid(row=0, column=0, pady=(10, 0), padx=15, sticky='nsew')

        for col in range(columns):
            header_label = CTkLabel(
                table_frame, text=headers[col], font=("Roboto", 14, "bold"))
            header_label.grid(row=0, column=col, padx=10, pady=5)

        self.table_data = []
        for row in range(1, rows + 1):
            row_data = []
            for col in range(columns):
                text = ""
                if col == 0:
                    text = row
                cell_label = CTkLabel(
                    table_frame, text=text, font=("Roboto", 12))
                cell_label.grid(row=row, column=col,
                                padx=10, pady=5, sticky="w")
                row_data.append(cell_label)
            self.table_data.append(row_data)

        self.table_data[self.num_of_processed][1].configure(text="PROCESSING...")

        if isinstance(table_frame, CTkXYFrame):
            table_frame.update_idletasks()
            table_frame.onFrameConfigure(table_frame.xy_canvas)

    def receive_output(self, num_of_processed: int, experimental_drop: ExperimentalDrop = None):
        """Process results and display contact angles"""
        self.num_of_processed = num_of_processed
        index = num_of_processed - 1

        if hasattr(experimental_drop, 'contact_angles'):
            contact_angles = experimental_drop.contact_angles

        # Update table data
        for method in contact_angles.keys():
            preformed_method_list = list(self.preformed_methods.keys())

            if method in preformed_method_list:
                column_index = preformed_method_list.index(method)+1
                result = contact_angles[method]
                
                if LEFT_ANGLE in result and RIGHT_ANGLE in result:
                    self.table_data[index][column_index].configure(
                        text=f"({result[LEFT_ANGLE]:.2f}, {result[RIGHT_ANGLE]:.2f})")
                else:
                    print(
                        f"Missing angle data, available keys: {result.keys()}")

        # Get cropped image and process contact angles
        try:
            image_path = self.user_input_data.import_files[index]

            # Get cropped image from experimental_drop
            cropped_cv = None
            if experimental_drop is not None and hasattr(experimental_drop, 'cropped_image'):
                cropped_cv = experimental_drop.cropped_image

            # Convert to PIL image and save
            if cropped_cv is not None:
                # Convert OpenCV image to PIL format
                if isinstance(cropped_cv, np.ndarray):
                    # OpenCV format(BGR) to PIL format(RGB)
                    if cropped_cv.ndim == 3 and cropped_cv.shape[2] == 3:
                        cropped_rgb = cv2.cvtColor(
                            cropped_cv, cv2.COLOR_BGR2RGB)
                        cropped_pil = Image.fromarray(cropped_rgb)
                    else:
                        cropped_pil = Image.fromarray(cropped_cv)

                    # Save cropped image
                    self.cropped_images[index] = cropped_pil
                    print(
                        f"Successfully saved cropped image, size: {cropped_pil.size}")

            # Check for contact angle data
            if hasattr(experimental_drop, 'contact_angles'):
                available_methods = []

                # Initialize cropped_angle_images dictionary for this index
                if index not in self.cropped_angle_images:
                    self.cropped_angle_images[index] = {}

                # Process each method and create corresponding annotations
                for method in contact_angles.keys():
                    # Check if method is in preformed_methods
                    # Handle both string and enum cases
                    method_in_preformed = False
                    if isinstance(method, str):
                        method_in_preformed = method in self.preformed_methods
                    elif hasattr(method, 'value'):
                        method_in_preformed = method.value in self.preformed_methods or method in self.preformed_methods
                    else:
                        method_in_preformed = method in self.preformed_methods

                    if not method_in_preformed:
                        continue
                        
                    angles_data = contact_angles[method]
                    # print(f"Processing method '{method}' data")

                    # Process annotation for specific method
                    success = self.process_method_annotation(
                        method, angles_data, index)
                    if success:
                        # Add method to available methods list - use display name
                        if isinstance(method, str):
                            available_methods.append(method)
                        elif hasattr(method, 'value'):
                            available_methods.append(method.value)
                        else:
                            available_methods.append(str(method))

                # Save available methods list
                self.available_methods[index] = available_methods

                # Update UI if this is the currently displayed image
                if self.current_index == index:
                    self.update_method_dropdown()
                    if self.show_angles_var.get() == 1:
                        self.display_current_image()

        except Exception as e:
            print(f"Error processing contact angle data: {e}")
            import traceback
            traceback.print_exc()

        # Update processing status display
        if self.num_of_processed < self.user_input_data.number_of_frames:
            self.table_data[self.num_of_processed][1].configure(text="PROCESSING...")
        
        # Save first method's angles (for compatibility)
        try:
            for method, res in contact_angles.items():
                if LEFT_ANGLE in res and RIGHT_ANGLE in res:
                    self.left_angles.append(res[LEFT_ANGLE])
                    self.right_angles.append(res[RIGHT_ANGLE])
                    break
        except Exception as e:
            print("[WARN] save failed:", e)

    def process_method_annotation(self, method, angles_data, index: int):
        """Process annotation for a specific method"""
        try:
            # Get angle values
            left_angle = angles_data.get(LEFT_ANGLE)
            right_angle = angles_data.get(RIGHT_ANGLE)

            if left_angle is None or right_angle is None:
                print(f"Method {method} missing angle data")
                return False

            # Convert method to FittingMethod enum if it's a string
            if isinstance(method, str):
                for fitting_method in FittingMethod:
                    if fitting_method.value == method:
                        method_enum = fitting_method
                        break
                else:
                    method_enum = method
            else:
                method_enum = method

            # Process data based on method type
            if method_enum in [FittingMethod.CIRCLE_FIT, FittingMethod.ELLIPSE_FIT]:
                # Special handling for circle/ellipse fit
                if BASELINE_INTERCEPTS in angles_data:
                    baseline_intercepts = angles_data[BASELINE_INTERCEPTS]
                    self.create_contact_points_and_tangents(
                        angles_data, baseline_intercepts, left_angle, right_angle)

            elif method_enum == FittingMethod.POLYNOMIAL_FIT:
                # Special handling for polynomial fit
                if CONTACT_POINTS in angles_data:
                    self.create_tangent_lines_from_angles(
                        angles_data, left_angle, right_angle)

            elif method_enum == FittingMethod.YL_FIT:
                # Special handling for YL fit
                if FIT_SHAPE in angles_data and BASELINE in angles_data:
                    self.create_yl_annotations(
                        angles_data, left_angle, right_angle)

            # Get contact points and tangent lines
            contact_points = self.get_contact_points(angles_data)
            tangent_lines = self.get_tangent_lines(angles_data)

            if contact_points and tangent_lines and index in self.cropped_images:
                # Create annotated image
                cropped_img = self.cropped_images[index]
                annotated_img = self.draw_on_cropped_image(
                    cropped_img, left_angle, right_angle, contact_points, tangent_lines
                )

                # Save to method-specific dictionary using display name
                display_name = method if isinstance(
                    method, str) else method.value
                self.cropped_angle_images[index][display_name] = annotated_img
                # print(f"Successfully created annotation for method {display_name}")
                return True

        except Exception as e:
            print(f"Error processing method {method}: {e}")

        return False

    def highlight_row(self, row_index: int):
        # Reset all rows to default color
        for row in self.table_data:
            for cell in row:
                cell.configure(text_color=get_system_text_color())

        if 0 <= row_index < len(self.table_data):
            for cell in self.table_data[row_index]:
                cell.configure(text_color="red")

    def initialize_image_display(self, frame):
        """Initialize image display directly in the frame (image_wrapper_frame)."""
        # frame is image_wrapper_frame here

        # --- Configure frame's (image_wrapper_frame) internal grid ---
        # No longer need the nested display_frame
        frame.grid_rowconfigure(0, weight=0)    # Filename row
        # Image row (allow vertical expansion if needed)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_rowconfigure(2, weight=0)    # Toggle frame row
        frame.grid_rowconfigure(3, weight=0)    # Method dropdown row
        frame.grid_rowconfigure(4, weight=0)    # Navigation frame row
        # Single column expands horizontally
        frame.grid_columnconfigure(0, weight=1)

        # --- Create widgets directly in 'frame' ---

        # Image Label
        # Keep original size for now
        self.image_label = CTkLabel(
            frame, text="", fg_color="lightgrey", width=400, height=300)
        self.image_label.grid(row=1, column=0, padx=10, pady=(
            10, 5), sticky="nsew")  # Fills cell in wrapper

        # Filename Label
        file_name = "No image loaded"  # Default text
        if hasattr(self.user_input_data, 'import_files') and self.user_input_data.import_files and self.current_index < len(self.user_input_data.import_files):
            file_name = os.path.basename(
                self.user_input_data.import_files[self.current_index])
        self.name_label = CTkLabel(frame, text=file_name)
        self.name_label.grid(row=0, column=0, pady=(5, 0))  # Above image label

        # Toggle Frame (Radio Buttons)
        self.toggle_frame = CTkFrame(frame)  # Parent is image_wrapper_frame
        set_light_only_color(self.toggle_frame, "innerframe")
        self.toggle_frame.grid(
            row=2, column=0, pady=(5, 0))  # Below image label

        self.show_angles_var = IntVar(value=0)
        self.rb_original = CTkRadioButton(
            self.toggle_frame, text="Original Image", variable=self.show_angles_var, value=0, command=self.toggle_view)
        self.rb_cropped = CTkRadioButton(self.toggle_frame, text="Contact Angles",
                                         variable=self.show_angles_var, value=1, command=self.toggle_view)
        self.rb_chart = CTkRadioButton(self.toggle_frame, text="Line Chart",
                                       variable=self.show_angles_var, value=2, command=self.toggle_view)
        self.rb_original.grid(row=0, column=0, padx=10, pady=5)
        self.rb_cropped.grid(row=0, column=1, padx=10, pady=5)
        self.rb_chart.grid(row=0, column=2, padx=10, pady=5)

        # Method dropdown (only shown in Contact Angles mode)
        self.method_frame = CTkFrame(frame)
        self.method_frame.grid(row=3, column=0, pady=(5, 0))
        self.method_frame.grid_remove()  # Initially hidden

        self.method_label = CTkLabel(self.method_frame, text="Method:")
        self.method_label.grid(row=0, column=0, padx=(10, 5))

        self.selected_method = StringVar()
        self.method_dropdown = CTkComboBox(self.method_frame,
                                           variable=self.selected_method,
                                           command=self.on_method_changed,
                                           width=150)
        self.method_dropdown.grid(row=0, column=1, padx=(5, 10))

        # Navigation Frame
        self.image_navigation_frame = CTkFrame(
            frame)  # Parent is image_wrapper_frame
        set_light_only_color(self.image_navigation_frame, "entry")
        self.image_navigation_frame.grid(row=4, column=0, pady=20)

        # Navigation Buttons (remain the same, parent is image_navigation_frame)
        self.prev_button = CTkButton(
            self.image_navigation_frame, text="<", command=lambda: self.change_image(-1), width=30)
        self.prev_button.grid(row=0, column=0, padx=5, pady=5)
        self.index_entry = CTkEntry(self.image_navigation_frame, width=50)
        self.index_entry.grid(row=0, column=1, padx=5, pady=5)
        self.index_entry.bind(
            "<Return>", lambda e: self.update_index_from_entry())
        num_frames = 0
        if hasattr(self.user_input_data, 'number_of_frames'):
            num_frames = self.user_input_data.number_of_frames
        if num_frames > 0:
            self.index_entry.insert(0, str(self.current_index + 1))
        self.navigation_label = CTkLabel(
            self.image_navigation_frame, text=f" of {num_frames}", font=("Arial", 12))
        self.navigation_label.grid(row=0, column=2, padx=5, pady=5)
        self.next_button = CTkButton(
            self.image_navigation_frame, text=">", command=lambda: self.change_image(1), width=30)
        self.next_button.grid(row=0, column=3, padx=5, pady=5)

        # Load initial image
        if hasattr(self.user_input_data, 'import_files') and self.user_input_data.import_files:
            self.load_image(
                self.user_input_data.import_files[self.current_index])
        else:
            if hasattr(self, 'image_label') and self.image_label:
                self.image_label.configure(text="No images selected")

    def toggle_view(self):
        """Toggle view - controls dropdown visibility"""
        mode = self.show_angles_var.get()

        # Control method dropdown visibility
        if mode == 1:  # Contact Angles mode
            self.method_frame.grid()
            self.update_method_dropdown()
        else:
            self.method_frame.grid_remove()

        self.display_current_image()

    def update_method_dropdown(self):
        """Update method dropdown options"""
        if self.current_index in self.available_methods:
            methods = self.available_methods[self.current_index]
            if methods:
                # Convert method names to display format
                display_methods = []
                for method in methods:
                    if isinstance(method, FittingMethod):
                        # Convert enum to display name
                        display_name = method.value if hasattr(
                            method, 'value') else str(method)
                        display_methods.append(display_name)
                    else:
                        display_methods.append(str(method))

                # Clear and update dropdown values
                self.method_dropdown.configure(values=display_methods)

                # Set default selection
                if not self.selected_method.get() or self.selected_method.get() not in display_methods:
                    self.method_dropdown.set(display_methods[0])
                else:
                    self.method_dropdown.set(self.selected_method.get())
            else:
                self.method_dropdown.configure(values=["No methods available"])
                self.method_dropdown.set("No methods available")
        else:
            self.method_dropdown.configure(values=["Processing..."])
            self.method_dropdown.set("Processing...")

    def on_method_changed(self, selected_method):
        """Called when selected method changes"""
        if self.show_angles_var.get() == 1:  # Only update display in Contact Angles mode
            self.display_current_image()

    def display_current_image(self):
        """0=Original picture 1=Crop + Angle 2=Line picture"""
        mode = self.show_angles_var.get()
        if mode == 0:
            self.display_original_image()
        elif mode == 1:
            self.display_cropped_image()
        else:
            self.display_line_chart()

    def display_original_image(self):
        """Display original image"""
        if hasattr(self, 'current_image') and self.current_image:
            width, height = self.current_image.size
            new_width, new_height = self.image_handler.get_fitting_dimensions(
                width, height)
            self.tk_image = CTkImage(
                self.current_image, size=(new_width, new_height))
            self.image_label.configure(image=self.tk_image)
            self.image_label.image = self.tk_image
        else:
            self.image_label.configure(image=None, text="No image")

    def display_cropped_image(self):
        """Display cropped image with angle annotations - supports multiple methods"""
        selected_method = self.selected_method.get()

        # Try to get annotation image for selected method
        if self.current_index in self.cropped_angle_images:
            method_images = self.cropped_angle_images[self.current_index]

            # Try different possible keys for the method
            img = None
            if selected_method in method_images:
                img = method_images[selected_method]
            else:
                # Try to find matching method by comparing values
                for key, value in method_images.items():
                    if str(key) == selected_method or (hasattr(key, 'value') and key.value == selected_method):
                        img = value
                        break

            if img:
                # Resize and display
                width, height = img.size
                new_width, new_height = self.image_handler.get_fitting_dimensions(
                    width, height)
                self.tk_image = CTkImage(img, size=(new_width, new_height))
                self.image_label.configure(image=self.tk_image)
                self.image_label.image = self.tk_image
                return

        # Fall back to cropped image without annotations
        if self.current_index in self.cropped_images:
            img = self.cropped_images[self.current_index]

            # Resize and display
            width, height = img.size
            new_width, new_height = self.image_handler.get_fitting_dimensions(
                width, height)
            self.tk_image = CTkImage(img, size=(new_width, new_height))
            self.image_label.configure(image=self.tk_image)
            self.image_label.image = self.tk_image
        else:
            self.image_label.configure(
                image=None, text="No cropped image available")

    def display_line_chart(self):
        if not self.left_angles:
            self.image_label.configure(text="No angle data yet", image="")
            return

        frames = list(range(1, len(self.left_angles) + 1))

        fig, ax = plt.subplots(figsize=(5, 4))
        ax.plot(frames, self.left_angles,  marker="o", label="Left θ")
        ax.plot(frames, self.right_angles, marker="o", label="Right θ")
        ax.set_xlabel("Frame")
        ax.set_ylabel("Angle (°)")
        ax.set_xticks(frames)
        ax.set_title("Contact Angles Over Frames")
        ax.legend()
        fig.tight_layout()

        canvas = FigureCanvasAgg(fig)
        canvas.draw()
        w, h = canvas.get_width_height()
        buf = canvas.buffer_rgba()
        img = Image.frombuffer("RGBA", (w, h), buf, "raw",
                               "RGBA", 0, 1).convert("RGB")

        self.tk_image = CTkImage(img, size=(400, 300))
        self.image_label.configure(image=self.tk_image, text="")
        self.image_label.image = self.tk_image
        plt.close(fig)

    def draw_on_cropped_image(self, image, left_angle, right_angle, contact_points, tangent_lines):
        """Draw contact angle annotations on cropped image"""
        img = image.copy()
        draw = ImageDraw.Draw(img)

        if contact_points is not None:
            # Use original calculated coordinates, no offset needed
            left_point = (float(contact_points[0][0]), float(
                contact_points[0][1]))
            right_point = (float(contact_points[1][0]), float(
                contact_points[1][1]))
            left_tangent_start = (
                float(tangent_lines[0][0][0]), float(tangent_lines[0][0][1]))
            left_tangent_end = (
                float(tangent_lines[0][1][0]), float(tangent_lines[0][1][1]))
            right_tangent_start = (
                float(tangent_lines[1][0][0]), float(tangent_lines[1][0][1]))
            right_tangent_end = (
                float(tangent_lines[1][1][0]), float(tangent_lines[1][1][1]))

            # Calculate tangent direction vectors
            left_dir_x = left_tangent_end[0] - left_tangent_start[0]
            left_dir_y = left_tangent_end[1] - left_tangent_start[1]
            right_dir_x = right_tangent_end[0] - right_tangent_start[0]
            right_dir_y = right_tangent_end[1] - right_tangent_start[1]

            # Normalize vectors
            left_len = math.sqrt(left_dir_x**2 + left_dir_y**2)
            right_len = math.sqrt(right_dir_x**2 + right_dir_y**2)

            if left_len > 0:
                left_dir_x /= left_len
                left_dir_y /= left_len

            if right_len > 0:
                right_dir_x /= right_len
                right_dir_y /= right_len

            # Set tangent length
            tangent_length = 80

            # Calculate extended tangent lines
            extended_left_tangent_end = (left_point[0] + left_dir_x * tangent_length,
                                         left_point[1] + left_dir_y * tangent_length)

            extended_right_tangent_end = (right_point[0] + right_dir_x * tangent_length,
                                          right_point[1] + right_dir_y * tangent_length)

            # Draw baseline - connect the two contact points
            baseline_width = 2
            baseline_color = 'yellow'

            # Calculate baseline direction vector
            baseline_dx = right_point[0] - left_point[0]
            baseline_dy = right_point[1] - left_point[1]
            baseline_length = math.sqrt(baseline_dx**2 + baseline_dy**2)

            if baseline_length > 0:
                # Unit direction vector
                baseline_dx /= baseline_length
                baseline_dy /= baseline_length

                # Extend baseline
                baseline_extension = 30
                baseline_left = (left_point[0] - baseline_dx * baseline_extension,
                                 left_point[1] - baseline_dy * baseline_extension)
                baseline_right = (right_point[0] + baseline_dx * baseline_extension,
                                  right_point[1] + baseline_dy * baseline_extension)

                # Draw baseline
                draw.line((baseline_left[0], baseline_left[1], baseline_right[0], baseline_right[1]),
                          fill=baseline_color, width=baseline_width)
            else:
                # Zero length baseline case
                draw.line((left_point[0], left_point[1], right_point[0], right_point[1]),
                          fill=baseline_color, width=baseline_width)

            # Draw contact points (green dots)
            dot_radius = 3
            draw.ellipse((left_point[0]-dot_radius, left_point[1]-dot_radius,
                          left_point[0]+dot_radius, left_point[1]+dot_radius), fill='#39FF14')
            draw.ellipse((right_point[0]-dot_radius, right_point[1]-dot_radius,
                          right_point[0]+dot_radius, right_point[1]+dot_radius), fill='#39FF14')

            # Draw tangent lines (red lines)
            draw.line((left_point[0], left_point[1],
                       extended_left_tangent_end[0], extended_left_tangent_end[1]),
                      fill='red', width=2)
            draw.line((right_point[0], right_point[1],
                       extended_right_tangent_end[0], extended_right_tangent_end[1]),
                      fill='red', width=2)

            # Add angle label text
            try:
                font = ImageFont.truetype("assets/DejaVuSans.ttf", 16)
            except Exception as e:
                print(f"Error loading font: {e}")
                try:
                    font = ImageFont.load_default()
                except Exception as e:
                    print(f"Error loading default font: {e}")
                    font = None

            # Add angle text labels
            left_text = f"θL: {left_angle:.2f}°"
            right_text = f"θR: {right_angle:.2f}°"

            # Set text positions - based on tangent direction
            text_offset = 25
            left_text_pos = (
                left_point[0] + 0.5*text_offset, left_point[1] - 2*text_offset)
            right_text_pos = (
                right_point[0] - 3*text_offset, right_point[1] - 3.5*text_offset)

            draw.text(left_text_pos, left_text, fill='red', font=font)
            draw.text(right_text_pos, right_text, fill='red', font=font)

        return img

    def change_image(self, step):
        """Change displayed image"""
        if self.user_input_data.import_files:
            self.current_index = (
                self.current_index + step) % self.user_input_data.number_of_frames
            # Load the new image
            self.load_image(
                self.user_input_data.import_files[self.current_index])
            self.update_index_entry()  # Update the entry with the current index
            file_name = os.path.basename(
                self.user_input_data.import_files[self.current_index])
            self.name_label.configure(text=file_name)

            self.highlight_row(self.current_index)

            # Update method dropdown
            if self.show_angles_var.get() == 1:
                self.update_method_dropdown()

    def load_image(self, image_path):
        """Load image and prepare for display"""
        try:
            # Load original image
            self.current_image = Image.open(image_path)

            # Display current image
            self.display_current_image()
        except Exception as e:
            print(f"Error loading image: {e}")
            self.current_image = None

    def update_index_from_entry(self):
        """Update current index based on user input"""
        try:
            new_index = int(self.index_entry.get()) - \
                1  # Convert to zero-based index
            if 0 <= new_index < self.user_input_data.number_of_frames:
                self.current_index = new_index
                # Load the new image
                self.load_image(
                    self.user_input_data.import_files[self.current_index])

                # Update filename display
                file_name = os.path.basename(
                    self.user_input_data.import_files[self.current_index])
                self.name_label.configure(text=file_name)

                # Highlight current row
                self.highlight_row(self.current_index)

                # Update method dropdown if in contact angles mode
                if self.show_angles_var.get() == 1:
                    self.update_method_dropdown()
            else:
                print("Index out of range")
        except ValueError:
            print("Invalid input. Please enter a number.")

        self.update_index_entry()  # Update entry display

    def update_index_entry(self):
        """Update index entry to reflect current index"""
        self.index_entry.delete(0, 'end')  # Clear current entry
        # Insert new index (1-based)
        self.index_entry.insert(0, str(self.current_index + 1))

    # Helper functions
    def create_contact_points_and_tangents(self, angles_data, baseline_intercepts, left_angle, right_angle):
        """Create contact points and tangent lines for circle/ellipse fit"""
        # Determine left and right points
        if baseline_intercepts[0][0] < baseline_intercepts[1][0]:
            left_point = baseline_intercepts[0]
            right_point = baseline_intercepts[1]
        else:
            left_point = baseline_intercepts[1]
            right_point = baseline_intercepts[0]

        # Create contact_points
        angles_data[CONTACT_POINTS] = [left_point, right_point]

        # Calculate tangent lines
        left_angle_rad = math.radians(left_angle)
        right_angle_rad = math.radians(180 - right_angle)

        line_length = 50

        left_dx = math.cos(left_angle_rad) * line_length
        left_dy = math.sin(left_angle_rad) * line_length
        right_dx = math.cos(right_angle_rad) * line_length
        right_dy = math.sin(right_angle_rad) * line_length

        # Create tangent lines
        angles_data[TANGENT_LINES] = (
            ((float(left_point[0]), float(left_point[1])),
             (float(left_point[0] + left_dx), float(left_point[1] - left_dy))),
            ((float(right_point[0]), float(right_point[1])),
             (float(right_point[0] + right_dx), float(right_point[1] - right_dy)))
        )

    def create_tangent_lines_from_angles(self, angles_data, left_angle, right_angle):
        """Create tangent lines for polynomial fit"""
        contact_points = angles_data[CONTACT_POINTS]

        # Determine left and right points
        if contact_points[0][0] < contact_points[1][0]:
            left_point = contact_points[0]
            right_point = contact_points[1]
        else:
            left_point = contact_points[1]
            right_point = contact_points[0]

        # Calculate tangent lines
        left_angle_rad = math.radians(left_angle)
        right_angle_rad = math.radians(180 - right_angle)

        line_length = 50

        left_dx = math.cos(left_angle_rad) * line_length
        left_dy = math.sin(left_angle_rad) * line_length
        right_dx = math.cos(right_angle_rad) * line_length
        right_dy = math.sin(right_angle_rad) * line_length

        # Create tangent lines
        angles_data[TANGENT_LINES] = (
            ((float(left_point[0]), float(left_point[1])),
             (float(left_point[0] + left_dx), float(left_point[1] - left_dy))),
            ((float(right_point[0]), float(right_point[1])),
             (float(right_point[0] + right_dx), float(right_point[1] - right_dy)))
        )

    def create_yl_annotations(self, angles_data, left_angle, right_angle):
        """Create annotations for YL fit"""
        fit_shape = angles_data[FIT_SHAPE]
        baseline = angles_data[BASELINE]

        # Extract contact points
        if len(baseline) >= 2:
            left_point = baseline[0]
            right_point = baseline[-1]
        elif len(fit_shape) >= 2:
            left_point = fit_shape[0]
            right_point = fit_shape[len(fit_shape)//2]

        # Create contact_points
        angles_data[CONTACT_POINTS] = [left_point, right_point]

        # Calculate tangent lines
        left_angle_rad = math.radians(left_angle)
        right_angle_rad = math.radians(180 - right_angle)

        line_length = 50

        left_dx = math.cos(left_angle_rad) * line_length
        left_dy = math.sin(left_angle_rad) * line_length
        right_dx = math.cos(right_angle_rad) * line_length
        right_dy = math.sin(right_angle_rad) * line_length

        # Create tangent lines
        angles_data[TANGENT_LINES] = (
            ((float(left_point[0]), float(left_point[1])),
             (float(left_point[0] + left_dx), float(left_point[1] - left_dy))),
            ((float(right_point[0]), float(right_point[1])),
             (float(right_point[0] + right_dx), float(right_point[1] - right_dy)))
        )

    def get_contact_points(self, angles_data):
        """Get contact points from angles_data"""
        for key in [CONTACT_POINTS, 'contact_points', 'tangent contact points', BASELINE_INTERCEPTS]:
            if key in angles_data:
                return angles_data[key]
        return None

    def get_tangent_lines(self, angles_data):
        """Get tangent lines from angles_data"""
        for key in [TANGENT_LINES, 'tangent_lines']:
            if key in angles_data:
                return angles_data[key]
        return None


def extract_method(contact_angles):
    """Extract the first available method from contact angles data"""
    for method in list(FittingMethod):
        if method in contact_angles:
            return method
    return None
