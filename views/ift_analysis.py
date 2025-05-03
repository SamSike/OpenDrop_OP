from customtkinter import CTkImage, CTkFrame, CTkScrollableFrame, CTkTabview, CTkLabel
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from views.component.imageGallery import ImageGallery


class IftAnalysis(CTkFrame):
    def __init__(self, parent, user_input_data, **kwargs):
        super().__init__(parent, **kwargs)

        self.user_input_data = user_input_data

        # Create tabs
        self.tab_view = CTkTabview(self)
        self.tab_view.pack(fill="both", expand=True)

        # Add "Results" and "Graphs" tabs
        self.tab_view.add("Results")
        self.tab_view.add("Graphs")

        # Initialize content for each tab
        self.create_results_tab(self.tab_view.tab("Results"))
        self.create_graph_tab(self.tab_view.tab("Graphs"))

    def create_results_tab(self, parent):
        """Create a split frame containing a Table on the left and Residuals with base image on the right into the parent frame"""

        # Configure the grid to allow expansion for both columns
        parent.grid_rowconfigure(0, weight=1)
        # Explicitly set weights to ensure 50/50 split, though weight=1 for both should achieve this
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)

        # Table can be large, so scrollable
        self.table_frame = CTkScrollableFrame(parent)
        # Removed pady=(10, 0) to potentially reduce wasted space, added padx for consistency
        self.table_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # --- Right side container for vertical centering ---
        self.visualisation_container = CTkFrame(parent) # Renamed for clarity
        self.visualisation_container.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        # Configure grid for vertical centering: add spacers top and bottom
        self.visualisation_container.grid_rowconfigure(0, weight=1) # Spacer Top
        self.visualisation_container.grid_rowconfigure(1, weight=0) # Image Frame (no expansion)
        self.visualisation_container.grid_rowconfigure(2, weight=0) # Residuals Frame (no expansion)
        self.visualisation_container.grid_rowconfigure(3, weight=1) # Spacer Bottom
        self.visualisation_container.grid_columnconfigure(0, weight=1) # Allow content to fill horizontally

        # Create and place the actual content frames within the container
        self.image_frame_wrapper = CTkFrame(self.visualisation_container, fg_color="transparent") # Wrapper to hold image gallery
        self.image_frame_wrapper.grid(row=1, column=0, sticky="nsew", pady=(0, 5))

        self.residuals_frame_wrapper = CTkFrame(self.visualisation_container, fg_color="transparent") # Wrapper to hold residuals
        self.residuals_frame_wrapper.grid(row=2, column=0, sticky="nsew", pady=(5, 0))

        # Call creation methods with the new wrappers as parents
        self.create_table(self.table_frame)
        self.create_image_frame(self.image_frame_wrapper) # Pass wrapper instead of container
        self.create_residuals_frame(self.residuals_frame_wrapper) # Pass wrapper instead of container

    def create_table(self, parent_frame):
        """Create a table into the parent frame. Headings are: Time, IFT, V, SA, Bond, Worth"""

        # Configure the row and column weights for expansion
        parent_frame.grid_rowconfigure(0, weight=1)
        parent_frame.grid_columnconfigure(0, weight=1)

        headings = ["Time", "IFT", "V", "SA", "Bond", "Worth"]
        for j, heading in enumerate(headings):
            cell = CTkLabel(parent_frame, text=heading)
            cell.grid(row=0, column=j, padx=10, pady=10, sticky="nsew")

        for i in range(1, 21):  # Adjusted to create more rows for better scrolling
            for j in range(len(headings)):
                cell = CTkLabel(parent_frame, text=f"Cell ({i},{j + 1})")
                cell.grid(row=i, column=j, padx=10, pady=10, sticky="nsew")

        for j in range(len(headings)):
            parent_frame.grid_columnconfigure(j, weight=1)

        # Set row configuration to allow for vertical scrolling
        for i in range(21):  # Adjust the range as needed
            parent_frame.grid_rowconfigure(i, weight=1)

    def create_image_frame(self, parent):
        """Create an Image Gallery that allows back and forth between base images into the parent frame"""
        # parent is image_frame_wrapper from create_results_tab

        # Configure the parent frame (wrapper) to center the ImageGallery instance
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        self.image_frame = ImageGallery(
            parent, self.user_input_data.import_files)

        # Use grid to place ImageGallery inside the wrapper and allow it to expand/center
        # sticky="nsew" allows the ImageGallery frame to resize
        # The internal configure binding in ImageGallery will handle the image itself
        self.image_frame.grid(row=0, column=0, sticky="nsew")

    def create_residuals_frame(self, parent):
        """Create a graph containing residuals into the parent frame. Graph is of same size as the Image Gallery."""

        # Residuals frame now lives inside its wrapper (parent)
        # No need for self.residuals_frame = CTkFrame(parent) unless more structure needed inside
        # Assume the parent (wrapper) is sufficient

        # Create the figure and axis
        fig, ax = plt.subplots(figsize=(4, 2)) # Keep size reasonable
        ax.plot([1, 2, 3], [2, 5, 10])
        ax.set_title('Residuals')
        fig.tight_layout() # Adjust layout to prevent labels overlapping

        # Create a canvas for the figure, place it in the parent (wrapper)
        canvas = FigureCanvasTkAgg(fig, parent) # Use parent directly
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side="top", fill="x", expand=False, pady=(0, 5)) # Pack canvas at top, fill horizontally

        # Create and pack the navigation toolbar, place it in the parent (wrapper) below canvas
        toolbar = NavigationToolbar2Tk(canvas, parent)
        toolbar.update()
        toolbar.pack(side="bottom", fill="x", expand=False) # Pack toolbar at bottom

        # No need to draw canvas here, toolbar creation might trigger it or it happens later

    def create_graph_tab(self, parent):
        """Create a full sized graph into the parent frame"""

        fig, ax = plt.subplots(figsize=(4, 3))
        ax.plot([1, 2, 3], [1, 4, 9])

        # Create the canvas for the figure
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # Create and pack the navigation toolbar
        toolbar = NavigationToolbar2Tk(canvas, parent)
        toolbar.update()
        canvas.draw()

    def receive_output(self , extracted_data):
        self.output.append(extracted_data)

        for method in extracted_data.contact_angles.keys():
            preformed_method_list = list(self.preformed_methods.keys())
            
            if method in preformed_method_list:
                column_index = preformed_method_list.index(method)+1
                result = extracted_data.contact_angles[method]
                self.table_data[len(self.output)-1][column_index].configure(text=f"({result[LEFT_ANGLE]:.2f}, {result[RIGHT_ANGLE]:.2f})")
            else:
                print(f"Unknown method. Skipping the method.")
            

        if len(self.output) < self.user_input_data.number_of_frames:
            self.table_data[len(self.output)][1].configure(text="PROCESSING...")
            
    def destroy(self):
        plt.close('all')
        return super().destroy()
