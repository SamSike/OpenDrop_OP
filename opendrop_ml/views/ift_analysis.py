from opendrop_ml.modules.core.classes import ExperimentalSetup
from opendrop_ml.modules.ift.ift_data_processor import IftDataProcessor
from opendrop_ml.views.component.imageGallery import ImageGallery
from opendrop_ml.views.helper.theme import get_system_text_color

from customtkinter import CTkFrame, CTkScrollableFrame, CTkTabview, CTkLabel

# from PIL import Image
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt


class IftAnalysis(CTkFrame):
    def __init__(
        self,
        parent,
        user_input_data: ExperimentalSetup,
        ift_processor: IftDataProcessor,
        **kwargs,
    ):
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
        parent.grid_columnconfigure(1, weight=1)  # Right column for visuals

        # Table can be large, so scrollable
        self.table_frame = CTkScrollableFrame(parent)
        self.table_frame.grid(
            row=0, column=0, sticky="nsew", padx=15, pady=(10, 0)
        )  # Left side for table

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

        parent_frame.grid_rowconfigure(0, weight=1)
        parent_frame.grid_columnconfigure(0, weight=1)

        padding_x = 5
        headings = ["Time", "IFT (mN/m)", "V (mm^3)",
                    "SA (mm^2)", "Bond", "Worth"]

        for j, heading in enumerate(headings):
            cell = CTkLabel(parent_frame, text=heading)
            cell.grid(row=0, column=j, padx=padding_x, pady=10, sticky="nsew")

        results = self.user_input_data.ift_results
        self.table_data = []  # Store each row's labels for later updates

        for i, result in enumerate(results, start=1):
            row_widgets = []
            values = [
                f"{result[5]}",
                f"{result[0]:.1f}",
                f"{result[1]:.2f}",
                f"{result[2]:.2f}",
                f"{result[3]:.4f}",
                f"{result[4]:.4f}",
            ]

            for j, val in enumerate(values):
                label = CTkLabel(self.table_frame, text=val, anchor="center")
                label.grid(row=i, column=j, padx=padding_x,
                           pady=5, sticky="nsew")
                row_widgets.append(label)

            self.table_data.append(row_widgets)

        for j in range(len(headings)):
            parent_frame.grid_columnconfigure(j, weight=1)

        for i in range(len(results) + 1):  # +1 for the header row
            parent_frame.grid_rowconfigure(i, weight=1)

    def create_image_frame(self, parent):
        """Create an Image Gallery that allows back and forth between base images into the parent frame"""
        self.image_frame = ImageGallery(
            parent,
            self.user_input_data.drop_contour_images,
            on_index_change=self.highlight_row,
        )
        self.image_frame.grid(row=0, column=0, sticky="nsew")

    def create_residuals_frame(self, parent):
        """Create a graph containing residuals into the parent frame. Graph is of same size as the Image Gallery."""

        self.residuals_frame = CTkFrame(parent)
        self.residuals_frame.grid(row=1, column=0, sticky="nsew")

        # Create the figure and axis
        # width, height = self.image_frame.image_label.image.size
        fig, ax = plt.subplots(figsize=(4, 4), constrained_layout=True)
        results = self.user_input_data.fit_result  # List of lists: one list per drop
        idx = [0]

        def show(index):
            ax.clear()
            # Example data for the residuals
            ax.scatter(
                results[index].arclengths, results[index].residuals, color="black"
            )
            ax.set_title(f"Residuals for Drop {index + 1}")
            ax.set_xlabel("Arclengths")
            ax.set_ylabel("Residuals")
            fig.canvas.draw_idle()

        def on_key(event):
            if event.key == "right":
                idx[0] = (idx[0] + 1) % len(results)
                show(idx[0])
            elif event.key == "left":
                idx[0] = (idx[0] - 1) % len(results)
                show(idx[0])

        fig.canvas.mpl_connect("key_press_event", on_key)
        show(idx[0])
        # Create a canvas for the figure
        canvas = FigureCanvasTkAgg(fig, self.residuals_frame)

        # Create and pack the navigation toolbar
        toolbar = NavigationToolbar2Tk(canvas, self.residuals_frame)
        toolbar.update()

        # Ensure the canvas is packed after the toolbar
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # Draw the canvas to show the figure
        canvas.draw()

    def create_graph_tab(self, parent):
        """Create a full sized graph into the parent frame"""

        fig, ax = plt.subplots(figsize=(4, 4))
        results = self.user_input_data.fit_result  # List of lists: one list per drop
        idx = [0]

        def show(index):
            ax.clear()
            # Example data for the residuals
            ax.scatter(
                results[index].arclengths, results[index].residuals, color="black"
            )
            ax.set_title(f"Residuals for Drop {index + 1}")
            ax.set_xlabel("Arclengths")
            ax.set_ylabel("Residuals")
            fig.canvas.draw_idle()

        def on_key(event):
            if event.key == "right":
                idx[0] = (idx[0] + 1) % len(results)
                show(idx[0])
            elif event.key == "left":
                idx[0] = (idx[0] - 1) % len(results)
                show(idx[0])

        fig.canvas.mpl_connect("key_press_event", on_key)
        show(idx[0])

        canvas = FigureCanvasTkAgg(fig, parent)
        toolbar = NavigationToolbar2Tk(canvas, parent)
        toolbar.update()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()

    def highlight_row(self, row_index: int):
        # Reset all rows to default color
        for row in self.table_data:
            for cell in row:
                cell.configure(text_color=get_system_text_color())

        if 0 <= row_index < len(self.table_data):
            for cell in self.table_data[row_index]:
                cell.configure(text_color="red")

    def destroy(self):
        plt.close("all")
        return super().destroy()
