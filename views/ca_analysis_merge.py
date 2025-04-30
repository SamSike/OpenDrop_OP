from customtkinter import *
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import io
import os
import math
import cv2
import matplotlib.pyplot as plt                           # ★ 新增
from matplotlib.backends.backend_agg import FigureCanvasAgg  # ★ 新增

from utils.image_handler import ImageHandler
from utils.config import *
from utils.validators import *
from views.helper.theme import get_system_text_color
from views.component.CTkXYFrame import *

class CaAnalysis(CTkFrame):
    def __init__(self, parent, user_input_data, **kwargs):
        super().__init__(parent, **kwargs)
        self.user_input_data = user_input_data

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        
        self.image_handler = ImageHandler()

        self.output = []
        self.cropped_images = {}              # 原有：裁剪后的图
        self.cropped_angle_images = {}        # 原有：叠加角度之后的裁剪图
        self.left_angles  = []                # ★ 新增：保存左角
        self.right_angles = []                # ★ 新增：保存右角
        
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

        self.images_frame = CTkFrame(self)
        self.images_frame.grid(row=0, column=1, sticky="nsew", padx=15, pady=(10, 0))

        self.current_index = 0
        self.highlight_row(self.current_index)
        self.initialize_image_display(self.images_frame)

    # ------------------------------------------------------------------
    #  结果回调
    # ------------------------------------------------------------------
    def receive_output(self, extracted_data, experimental_drop=None):
        """Process results and display contact angles"""
        self.output.append(extracted_data)
        index = len(self.output) - 1

        # ======== 原版更新表格/保存裁剪图的逻辑（未改动，省略） ========
        # ...（这里保留官方全部实现）...
        # Update table data
        for method in extracted_data.contact_angles.keys():
            preformed_method_list = list(self.preformed_methods.keys())
            
            if method in preformed_method_list:
                column_index = preformed_method_list.index(method)+1
                result = extracted_data.contact_angles[method]
                
                if LEFT_ANGLE in result and RIGHT_ANGLE in result:
                    self.table_data[index][column_index].configure(text=f"({result[LEFT_ANGLE]:.2f}, {result[RIGHT_ANGLE]:.2f})")
                else:
                    print(f"Missing angle data, available keys: {result.keys()}")
        
        # Get cropped image and process contact angles
        try:
            image_path = self.user_input_data.import_files[index]
            
            # Get cropped image from experimental_drop
            cropped_cv = None
            print(f"experimental_drop is not None: {experimental_drop is not None}")
            print(f"hasattr(experimental_drop, 'cropped_image'): {hasattr(experimental_drop, 'cropped_image')}")
            if experimental_drop is not None and hasattr(experimental_drop, 'cropped_image'):
                cropped_cv = experimental_drop.cropped_image
                print(f"Retrieved cropped image from experimental_drop")
            
            # Convert to PIL image and save
            if cropped_cv is not None:
                # Convert OpenCV image to PIL format
                if isinstance(cropped_cv, np.ndarray):
                    # OpenCV format(BGR) to PIL format(RGB)
                    if cropped_cv.ndim == 3 and cropped_cv.shape[2] == 3:
                        cropped_rgb = cv2.cvtColor(cropped_cv, cv2.COLOR_BGR2RGB)
                        cropped_pil = Image.fromarray(cropped_rgb)
                    else:
                        cropped_pil = Image.fromarray(cropped_cv)
                    
                    # Save cropped image
                    self.cropped_images[index] = cropped_pil
                    print(f"Successfully saved cropped image, size: {cropped_pil.size}")
            
            # Check for contact angle data
            if hasattr(extracted_data, 'contact_angles'):
                # Find available method
                method_to_use = None
                if 'tangent fit' in extracted_data.contact_angles:
                    method_to_use = 'tangent fit'
                elif 'ellipse fit' in extracted_data.contact_angles:
                    method_to_use = 'ellipse fit'
                elif 'polynomial fit' in extracted_data.contact_angles:
                    method_to_use = 'polynomial fit'
                elif 'circle fit' in extracted_data.contact_angles:
                    method_to_use = 'circle fit'
                elif 'YL fit' in extracted_data.contact_angles:
                    method_to_use = 'YL fit'
                elif ML_MODEL in extracted_data.contact_angles:
                    method_to_use = ML_MODEL
                
                if method_to_use:
                    angles_data = extracted_data.contact_angles[method_to_use]
                    print(f"Using method '{method_to_use}' data, keys: {angles_data.keys()}")

                    # Special handling for ellipse fit only
                    if method_to_use in [ 'ellipse fit', 'circle fit'] and 'baseline intercepts' in angles_data:
                        baseline_intercepts = angles_data['baseline intercepts']
                        
                        # For ellipse fit, determine left and right points
                        if baseline_intercepts[0][0] < baseline_intercepts[1][0]:
                            # The first point is on the left (smaller x-coordinate)
                            left_point = baseline_intercepts[0]
                            right_point = baseline_intercepts[1]
                        else:
                            # The first point is on the right (larger x-coordinate)
                            left_point = baseline_intercepts[1]
                            right_point = baseline_intercepts[0]
                            
                        # Create contact_points from baseline_intercepts
                        angles_data['contact points'] = [left_point, right_point]
                        
                        # Get the angles
                        left_angle = angles_data['left angle']
                        right_angle = angles_data['right angle']
                        
                        left_angle_rad = math.radians(left_angle)
                        right_angle_rad = math.radians(180 - right_angle)

                        # Length of tangent line
                        line_length = 50
                        
                        # Calculate tangent line endpoints
                        left_dx = math.cos(left_angle_rad) * line_length
                        left_dy = math.sin(left_angle_rad) * line_length
                        right_dx = math.cos(right_angle_rad) * line_length
                        right_dy = math.sin(right_angle_rad) * line_length
                        
                        # Create tangent lines in the expected format
                        angles_data['tangent lines'] = (
                            ((float(left_point[0]), float(left_point[1])), 
                            (float(left_point[0] + left_dx), float(left_point[1] - left_dy))),
                            ((float(right_point[0]), float(right_point[1])), 
                            (float(right_point[0] + right_dx), float(right_point[1] - right_dy)))
                        )
                    # Special handling for polynomial fit
                    elif method_to_use == 'polynomial fit' and 'contact points' in angles_data:
                        contact_points = angles_data['contact points']
                        
                        # For polynomial fit, create tangent lines based on the angles
                        if 'left angle' in angles_data and 'right angle' in angles_data:
                            left_angle = angles_data['left angle']
                            right_angle = angles_data['right angle']
                            
                            # Determine left and right points
                            if contact_points[0][0] < contact_points[1][0]:
                                left_point = contact_points[0]
                                right_point = contact_points[1]
                            else:
                                left_point = contact_points[1]
                                right_point = contact_points[0]
                            
                            # Calculate tangent lines using angles
                            left_angle_rad = math.radians(left_angle)
                            right_angle_rad = math.radians(180 - right_angle)
                            
                            line_length = 50
                            
                            # Calculate tangent line endpoints
                            left_dx = math.cos(left_angle_rad) * line_length
                            left_dy = math.sin(left_angle_rad) * line_length
                            right_dx = math.cos(right_angle_rad) * line_length
                            right_dy = math.sin(right_angle_rad) * line_length
                            
                            # Create tangent lines in the expected format
                            angles_data['tangent lines'] = (
                                ((float(left_point[0]), float(left_point[1])), 
                                (float(left_point[0] + left_dx), float(left_point[1] - left_dy))),
                                ((float(right_point[0]), float(right_point[1])), 
                                (float(right_point[0] + right_dx), float(right_point[1] - right_dy)))
                            )
                    elif method_to_use == 'YL fit' and 'fit shape' in angles_data and 'baseline' in angles_data:
                        # For YL fit, extract contact points from the fit shape and baseline
                        fit_shape = angles_data['fit shape']
                        baseline = angles_data['baseline']
                        
                        # The first and last points of the fit shape are likely the contact points
                        # Alternatively, use the first and last points of the baseline
                        if len(baseline) >= 2:
                            left_point = baseline[0]
                            right_point = baseline[-1]
                        elif len(fit_shape) >= 2:
                            left_point = fit_shape[0]
                            right_point = fit_shape[len(fit_shape)//2]  # Middle point might be the right contact point
                        
                        # Create contact_points
                        angles_data['contact points'] = [left_point, right_point]
                        
                        # Get the angles
                        left_angle = angles_data['left angle']
                        right_angle = angles_data['right angle']
                        
                        # Calculate tangent lines using angles
                        left_angle_rad = math.radians(left_angle)
                        right_angle_rad = math.radians(180 - right_angle)
                        
                        line_length = 50
                        
                        # Calculate tangent line endpoints
                        left_dx = math.cos(left_angle_rad) * line_length
                        left_dy = math.sin(left_angle_rad) * line_length
                        right_dx = math.cos(right_angle_rad) * line_length
                        right_dy = math.sin(right_angle_rad) * line_length
                        
                        # Create tangent lines in the expected format
                        angles_data['tangent lines'] = (
                            ((float(left_point[0]), float(left_point[1])), 
                            (float(left_point[0] + left_dx), float(left_point[1] - left_dy))),
                            ((float(right_point[0]), float(right_point[1])), 
                            (float(right_point[0] + right_dx), float(right_point[1] - right_dy)))
                        )
                    # Get left and right angle values
                    left_angle = right_angle = None
                    for key in [LEFT_ANGLE, 'left angle', 'left_angle']:
                        if key in angles_data:
                            left_angle = angles_data[key]
                            break
                    
                    for key in [RIGHT_ANGLE, 'right angle', 'right_angle']:
                        if key in angles_data:
                            right_angle = angles_data[key]
                            break
                    
                    if left_angle is not None and right_angle is not None:
                        # Find contact points data
                        contact_points = None
                        for key in ['contact_points', 'tangent contact points', 'contact points', 'baseline intercepts']:
                            if key in angles_data:
                                if key == 'baseline intercepts':
                                    # Convert baseline intercepts to contact points format
                                    contact_points = angles_data[key]
                                else:
                                    contact_points = angles_data[key]
                                print(f"Found contact points data: {key} = {contact_points}")
                                break
                        
                        # Find tangent line data
                        tangent_lines = None
                        for key in ['tangent lines', 'tangent_lines']:
                            if key in angles_data:
                                tangent_lines = angles_data[key]
                                print(f"Found tangent lines data: {key} = {tangent_lines}")
                                break
                        
                        # Draw annotations on cropped image
                        print(f"Index: {index}")
                        print(f"self.cropped_images:{self.cropped_images}")
                        print(f"Index in self.cropped_images: {index in self.cropped_images}")
                        if contact_points is not None and tangent_lines is not None and index in self.cropped_images:
                            print(f"Creating angle annotations on cropped image")
                            
                            cropped_img = self.cropped_images[index]
                            cropped_with_overlay = self.draw_on_cropped_image(
                                cropped_img, left_angle, right_angle, contact_points, tangent_lines
                            )
                            
                            # Save annotated cropped image
                            self.cropped_angle_images[index] = cropped_with_overlay
                            
                            # Update display
                            if self.current_index == index and self.show_angles_var.get() == 1:
                                self.display_current_image()
                        else:
                            print(f"Cannot create cropped image annotations: missing required data")
                    else:
                        print(f"Image {index+1} missing angle data")
                else:
                    print(f"Image {index+1} has no supported contact angle method")
        except Exception as e:
            print(f"Error processing contact angle data: {e}")
            import traceback
            traceback.print_exc()

        # Update processing status display
        if len(self.output) < self.user_input_data.number_of_frames:
            self.table_data[len(self.output)][1].configure(text="PROCESSING...")
        # ======== 角度缓存：供折线图使用  ========
        try:
            for method, res in extracted_data.contact_angles.items():
                if LEFT_ANGLE in res and RIGHT_ANGLE in res:
                    self.left_angles.append(res[LEFT_ANGLE])
                    self.right_angles.append(res[RIGHT_ANGLE])
                    break
        except Exception as e:
            print("[WARN] 缓存角度失败：", e)

    # ------------------------------------------------------------------
    #  表格高亮（未改动）
    # ------------------------------------------------------------------
    def highlight_row(self, row_index):
        # Reset all rows to default color
        for row in self.table_data:
            for cell in row:
                cell.configure(text_color=get_system_text_color())

        if 0 <= row_index < len(self.table_data):
            for cell in self.table_data[row_index]:
                cell.configure(text_color="red")

    # ------------------------------------------------------------------
    #  图像 / 视图区
    # ------------------------------------------------------------------
    def initialize_image_display(self, frame):
        display_frame = CTkFrame(frame)
        display_frame.grid(sticky="nsew", padx=15, pady=(10, 0))

        self.image_label = CTkLabel(
            display_frame, text="", fg_color="lightgrey", width=400, height=300
        )
        self.image_label.grid(padx=10, pady=(10, 5))

        file_name = os.path.basename(self.user_input_data.import_files[self.current_index])
        self.name_label = CTkLabel(display_frame, text=file_name)
        self.name_label.grid()

        # ------------------ 切换控件：3 个单选 ------------------
        self.toggle_frame = CTkFrame(display_frame)
        self.toggle_frame.grid(pady=(5, 0))

        self.show_angles_var = IntVar(value=0)   # 0=原图 1=裁剪+角度 2=折线图

        self.rb_original = CTkRadioButton(
            self.toggle_frame,
            text="Show Original Image",
            variable=self.show_angles_var,
            value=0,
            command=self.toggle_view,
        )
        self.rb_cropped = CTkRadioButton(
            self.toggle_frame,
            text="Show Contact Angles (Cropped View)",
            variable=self.show_angles_var,
            value=1,
            command=self.toggle_view,
        )
        self.rb_chart = CTkRadioButton(
            self.toggle_frame,
            text="Show Line Chart",
            variable=self.show_angles_var,
            value=2,
            command=self.toggle_view,
        )
        self.rb_original.grid(row=0, column=0, padx=10, pady=5)
        self.rb_cropped.grid(row=0, column=1, padx=10, pady=5)
        self.rb_chart.grid(  row=0, column=2, padx=10, pady=5)

        # ------------------ 图像翻页控件（官方原样） ------------------
        self.image_navigation_frame = CTkFrame(display_frame)
        self.image_navigation_frame.grid(pady=20)

        self.prev_button = CTkButton(
            self.image_navigation_frame, text="<",
            command=lambda: self.change_image(-1), width=30
        )
        self.prev_button.grid(row=0, column=0, padx=5, pady=5)

        self.index_entry = CTkEntry(self.image_navigation_frame, width=50)
        self.index_entry.grid(row=0, column=1, padx=5, pady=5)
        self.index_entry.bind("<Return>", lambda e: self.update_index_from_entry())

        self.navigation_label = CTkLabel(
            self.image_navigation_frame,
            text=f" of {self.user_input_data.number_of_frames}",
            font=("Arial", 12),
        )
        self.navigation_label.grid(row=0, column=2, padx=5, pady=5)

        self.next_button = CTkButton(
            self.image_navigation_frame, text=">",
            command=lambda: self.change_image(1), width=30
        )
        self.next_button.grid(row=0, column=3, padx=5, pady=5)

        self.load_image(self.user_input_data.import_files[self.current_index])

    # ------------------------------------------------------------------
    #  切换视图
    # ------------------------------------------------------------------
    def toggle_view(self):
        self.display_current_image()

    def display_current_image(self):
        """0=原图 1=裁剪+角度 2=折线图"""
        mode = self.show_angles_var.get()
        if mode == 0:
            self.display_original_image()
        elif mode == 1:
            self.display_cropped_image()
        else:
            self.display_line_chart()

    # ------------------------------------------------------------------
    #  原图 / 裁剪图（官方实现未改动，代码略）
    # ------------------------------------------------------------------
    def display_original_image(self):
        """Display original image"""
        if hasattr(self, 'current_image') and self.current_image:
            width, height = self.current_image.size
            new_width, new_height = self.image_handler.get_fitting_dimensions(width, height)
            self.tk_image = CTkImage(self.current_image, size=(new_width, new_height))
            self.image_label.configure(image=self.tk_image)
            self.image_label.image = self.tk_image
        else:
            self.image_label.configure(image=None, text="No image")

    def display_cropped_image(self):
        """Display cropped image with angle annotations"""
        if self.current_index in self.cropped_angle_images:
            # Use cropped image with annotations
            img = self.cropped_angle_images[self.current_index]
            
            # Resize and display
            width, height = img.size
            new_width, new_height = self.image_handler.get_fitting_dimensions(width, height)
            self.tk_image = CTkImage(img, size=(new_width, new_height))
            self.image_label.configure(image=self.tk_image)
            self.image_label.image = self.tk_image
        elif self.current_index in self.cropped_images:
            # Fall back to cropped image without annotations
            img = self.cropped_images[self.current_index]
            
            # Resize and display
            width, height = img.size
            new_width, new_height = self.image_handler.get_fitting_dimensions(width, height)
            self.tk_image = CTkImage(img, size=(new_width, new_height))
            self.image_label.configure(image=self.tk_image)
            self.image_label.image = self.tk_image

    # ------------------------------------------------------------------
    #  折线图
    # ------------------------------------------------------------------
    def display_line_chart(self):
        """把缓存的左右角度画成折线"""
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
        img = Image.frombuffer("RGBA", (w, h), buf, "raw", "RGBA", 0, 1).convert("RGB")

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
            left_point = (float(contact_points[0][0]), float(contact_points[0][1]))
            right_point = (float(contact_points[1][0]), float(contact_points[1][1]))
            left_tangent_start = (float(tangent_lines[0][0][0]), float(tangent_lines[0][0][1]))
            left_tangent_end = (float(tangent_lines[0][1][0]), float(tangent_lines[0][1][1]))
            right_tangent_start = (float(tangent_lines[1][0][0]), float(tangent_lines[1][0][1]))
            right_tangent_end = (float(tangent_lines[1][1][0]), float(tangent_lines[1][1][1]))
            
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
                font = ImageFont.truetype("views/assets/DejaVuSans.ttf", 16)
            except:
                try:
                    font = ImageFont.load_default()
                except:
                    font = None
            
            # Add angle text labels
            left_text = f"θL: {left_angle:.2f}°"
            right_text = f"θR: {right_angle:.2f}°"
            
            # Set text positions - based on tangent direction
            text_offset = 25
            left_text_pos = (left_point[0] + 0.5*text_offset, left_point[1] - 2*text_offset)
            right_text_pos = (right_point[0] - 3*text_offset, right_point[1] - 3.5*text_offset)
            
            draw.text(left_text_pos, left_text, fill='red', font=font)
            draw.text(right_text_pos, right_text, fill='red', font=font)
        
        return img


    # ------------------------------------------------------------------
    #  翻页 / 加载图（官方实现未改动，代码略）
    # ------------------------------------------------------------------
    def change_image(self, step):
        """Change displayed image"""
        if self.user_input_data.import_files:
            self.current_index = (
                self.current_index + direction) % self.user_input_data.number_of_frames
            # Load the new image
            self.load_image(
                self.user_input_data.import_files[self.current_index])
            self.update_index_entry()  # Update the entry with the current index
            file_name = os.path.basename(
                self.user_input_data.import_files[self.current_index])
            self.name_label.configure(text=file_name)

            self.highlight_row(self.current_index)

    def load_image(self, image_path):
        """Load image and prepare for display"""
        try:
            # Load original image
            self.current_image = Image.open(selected_image)
            
            # Display current image
            self.display_current_image()
        except Exception as e:
            print(f"Error loading image: {e}")
            self.current_image = None

    def update_index_from_entry(self):
        """Update current index based on user input"""
        try:
            new_index = int(self.index_entry.get()) - 1  # Convert to zero-based index
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