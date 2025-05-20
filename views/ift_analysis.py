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
        parent.grid_columnconfigure(0, weight=1)  # Left column for table
        parent.grid_columnconfigure(
            1, weight=1)  # Right column for visuals

        # Table can be large, so scrollable
        self.table_frame = CTkScrollableFrame(parent)
        self.table_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=(
            10, 0))  # Left side for table

        self.visualisation_frame = CTkFrame(parent)
        self.visualisation_frame.grid(row=0, column=1, padx=10, sticky="nsew")
        self.visualisation_frame.grid_rowconfigure(0, weight=1)
        self.visualisation_frame.grid_rowconfigure(1, weight=1)
        self.visualisation_frame.grid_columnconfigure(0, weight=1)

        self.create_table(self.table_frame)
        self.create_image_frame(self.visualisation_frame)
        self.create_residuals_frame(self.visualisation_frame)

    def create_table(self, parent_frame):
        """Create a table into the parent frame. Headings are: Time, IFT, V, SA, Bond, Worth"""

        # Configure the row and column weights for expansion
        parent_frame.grid_rowconfigure(0, weight=1)
        parent_frame.grid_columnconfigure(0, weight=1)

        paddingX = 5

        headings = ["Time", "IFT (mN/m)", "V (mm^3)", "SA (mm^2)", "Bond", "Worth"]
        for j, heading in enumerate(headings):
            cell = CTkLabel(parent_frame, text=heading)
            cell.grid(row=0, column=j, padx=paddingX, pady=10, sticky="nsew")

        results = self.user_input_data.ift_results
        for i , result in enumerate(results, start=1):
            # Time column
            time_cell = CTkLabel(self.table_frame, text=f"{result[5]}", anchor="center")
            time_cell.grid(row=i, column=0, padx=paddingX, pady=5, sticky="nsew")
            # IFT column
            ift_cell = CTkLabel(self.table_frame, text=f"{result[0]:.1f}", anchor="center")
            ift_cell.grid(row=i, column=1, padx=paddingX, pady=5, sticky="nsew")
            # Volume (V) column
            volume_cell = CTkLabel(self.table_frame, text=f"{result[1]:.2f}", anchor="center")
            volume_cell.grid(row=i, column=2, padx=paddingX, pady=5, sticky="nsew")
            # Surface Area (SA) column
            sa_cell = CTkLabel(self.table_frame, text=f"{result[2]:.2f}", anchor="center")
            sa_cell.grid(row=i, column=3, padx=paddingX, pady=5, sticky="nsew")
            # Bond column
            bond_cell = CTkLabel(self.table_frame, text=f"{result[3]:.4f}", anchor="center")
            bond_cell.grid(row=i, column=4, padx=paddingX, pady=5, sticky="nsew")
            # Worth column
            worth_cell = CTkLabel(self.table_frame, text=f"{result[4]:.4f}", anchor="center")
            worth_cell.grid(row=i, column=5, padx=paddingX, pady=5, sticky="nsew")

        for j in range(len(headings)):
            parent_frame.grid_columnconfigure(j, weight=1)

        # Set row configuration to allow for vertical scrolling
        for i in range(21):  # Adjust the range as needed
            parent_frame.grid_rowconfigure(i, weight=1)

    def create_image_frame(self, parent):
        """Create an Image Gallery that allows back and forth between base images into the parent frame"""
        self.image_frame = ImageGallery(
            parent, self.user_input_data.drop_contour_images,on_image_change_callback=self.update_residual_graph)
        self.image_frame.grid(row=0, column=0, sticky="nsew")

    def create_residuals_frame(self, parent):
        """Create a graph containing residuals into the parent frame. Graph is of same size as the Image Gallery."""

        self.residuals_frame = CTkFrame(parent)
        self.residuals_frame.grid(row=1, column=0, sticky="nsew")

        # Create the figure and axis
        # width, height = self.image_frame.image_label.image.size
        fig, ax = plt.subplots(figsize=(4, 4))
        self.residual_ax = ax  
        self.residual_fig = fig

        self.residual_canvas = FigureCanvasTkAgg(fig, self.residuals_frame)  # ✅ FIXED HERE
        toolbar = NavigationToolbar2Tk(self.residual_canvas, self.residuals_frame)
        toolbar.update()
        self.residual_canvas.get_tk_widget().pack(fill="both", expand=True)
        self.residual_canvas.draw()
        self.update_residual_graph(0)

    def create_graph_tab(self, parent):
        """Create a full sized graph into the parent frame"""

        fig, ax = plt.subplots(figsize=(4, 4))
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
        # self.pd_processor.process_data(self.user_input_data)
        # self.create_table(self.table_frame)
        # self.create_image_frame(self.visualisation_frame)
        # self.create_residuals_frame(self.visualisation_frame)

    def update_residual_graph(self, index):
        if not hasattr(self, 'residual_ax'):
            return  
        self.residual_ax.clear()
        result = self.user_input_data.fit_result[index]
        self.residual_ax.scatter(result.arclengths, result.residuals, color='black')
        self.residual_ax.set_title(f"Residuals for Drop {index + 1}")
        self.residual_ax.set_xlabel("Arclengths")
        self.residual_ax.set_ylabel("Residuals")
        self.residual_canvas.draw_idle()

    def destroy(self):
        plt.close('all')
        return super().destroy()
