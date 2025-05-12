from customtkinter import CTkImage, CTkFrame, CTkScrollableFrame, CTkTabview, CTkLabel
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from views.component.imageGallery import ImageGallery

class IftAnalysis(CTkFrame):
    def __init__(self, parent, user_input_data,ift_processor, **kwargs):
        super().__init__(parent, **kwargs)

        self.user_input_data = user_input_data
        self.ift_processor = ift_processor
        self.ift_processor.process_data(self.user_input_data)
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

        headings = ["Time", "IFT (mN/m)", "Volume (mm^3)", "Surface Area (mm^2)", "Bond", "Worthingtion"]
        for j, heading in enumerate(headings):
            cell = CTkLabel(parent_frame, text=heading)
            cell.grid(row=0, column=j, padx=10, pady=10, sticky="nsew")

        results = self.user_input_data.ift_results
        for i , result in enumerate(results, start=1):
            # Time column
            print (f"Result: {result}")
            time_cell = CTkLabel(self.table_frame, text=f"{result[5]:.4f}", anchor="center")
            time_cell.grid(row=i, column=0, padx=10, pady=5, sticky="nsew")
            # IFT column
            ift_cell = CTkLabel(self.table_frame, text=f"{result[0]:.1f}", anchor="center")
            ift_cell.grid(row=i, column=1, padx=10, pady=5, sticky="nsew")
            # Volume (V) column
            volume_cell = CTkLabel(self.table_frame, text=f"{result[1]:.2f}", anchor="center")
            volume_cell.grid(row=i, column=2, padx=10, pady=5, sticky="nsew")
            # Surface Area (SA) column
            sa_cell = CTkLabel(self.table_frame, text=f"{result[2]:.2f}", anchor="center")
            sa_cell.grid(row=i, column=3, padx=10, pady=5, sticky="nsew")
            # Bond column
            bond_cell = CTkLabel(self.table_frame, text=f"{result[3]:.4f}", anchor="center")
            bond_cell.grid(row=i, column=4, padx=10, pady=5, sticky="nsew")
            # Worth column
            worth_cell = CTkLabel(self.table_frame, text=f"{result[4]:.4f}", anchor="center")
            worth_cell.grid(row=i, column=5, padx=10, pady=5, sticky="nsew")

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
            parent, self.user_input_data.drop_contour_images)
        self.image_frame.grid(row=0, column=0, sticky="nsew")

    def create_residuals_frame(self, parent):
        plt.close('all')
        """Create a graph containing residuals into the parent frame. Graph is of same size as the Image Gallery."""

        # Residuals frame now lives inside its wrapper (parent)
        # No need for self.residuals_frame = CTkFrame(parent) unless more structure needed inside
        # Assume the parent (wrapper) is sufficient

        # Create the figure and axis
        # width, height = self.image_frame.image_label.image.size
        fig, ax = plt.subplots(figsize=(4, 2))
        results = self.user_input_data.fit_result  # List of lists: one list per drop
        idx = [0]

        def show(index):
            ax.clear()
            ax.scatter(results[index].arclengths, results[index].residuals, color='black')  # Example data for the residuals
            ax.set_title(f"Residuals for Drop {index + 1}")
            ax.set_xlabel("Arclengths")
            ax.set_ylabel("Residuals")
            fig.canvas.draw_idle()

        def on_key(event):
            if event.key == 'right':
                idx[0] = (idx[0] + 1) % len(results)
                show(idx[0])
            elif event.key == 'left':
                idx[0] = (idx[0] - 1) % len(results)
                show(idx[0])

        fig.canvas.mpl_connect('key_press_event', on_key)
        show(idx[0])
        # Create a canvas for the figure
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # Create and pack the navigation toolbar, place it in the parent (wrapper) below canvas
        toolbar = NavigationToolbar2Tk(canvas, parent)
        toolbar.update()
        toolbar.pack(side="bottom", fill="x", expand=False) # Pack toolbar at bottom

        # Draw the canvas to show the figure
        canvas.draw()

    def create_graph_tab(self, parent):
        """Create a full sized graph into the parent frame"""

        fig, ax = plt.subplots(figsize=(6, 4))
        results = self.user_input_data.fit_result  # List of lists: one list per drop
        idx = [0]

        def show(index):
            ax.clear()
            ax.scatter(results[index].arclengths, results[index].residuals, color='black')  # Example data for the residuals
            ax.set_title(f"Residuals for Drop {index + 1}")
            ax.set_xlabel("Arclengths")
            ax.set_ylabel("Residuals")
            fig.canvas.draw_idle()

        def on_key(event):
            if event.key == 'right':
                idx[0] = (idx[0] + 1) % len(results)
                show(idx[0])
            elif event.key == 'left':
                idx[0] = (idx[0] - 1) % len(results)
                show(idx[0])

        fig.canvas.mpl_connect('key_press_event', on_key)
        show(idx[0])

        canvas = FigureCanvasTkAgg(fig, parent)
        toolbar = NavigationToolbar2Tk(canvas, parent)
        toolbar.update()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()

    def receive_output(self , user_input_data):
        print("Received output in IftAnalysis")
        # self.user_input_data = user_input_data
        # self.ift_processor.process_data(self.user_input_data)
        # self.create_table(self.table_frame)
        # self.create_image_frame(self.visualisation_frame)
        # self.create_residuals_frame(self.visualisation_frame)

            
    def destroy(self):
        plt.close('all')
        return super().destroy()
