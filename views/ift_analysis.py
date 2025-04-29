import csv
import os

from customtkinter import CTkImage, CTkFrame, CTkScrollableFrame, CTkTabview, CTkLabel, CTkButton, CTkEntry
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np

class IftAnalysis(CTkFrame):
    def __init__(self, parent, user_input_data, **kwargs):
        super().__init__(parent, **kwargs)

        self.user_input_data = user_input_data
        self.output = []  # List to store ExtractedData objects
        self.current_index = 0

        self.tab_view = CTkTabview(self)
        self.tab_view.pack(fill="both", expand=True)

        self.tab_view.add("Results")

        self.create_results_tab(self.tab_view.tab("Results"))

    def create_results_tab(self, parent):
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)

        self.table_frame = CTkScrollableFrame(parent)
        self.table_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=(10, 0))

        self.visualisation_frame = CTkFrame(parent)
        self.visualisation_frame.grid(row=0, column=1, padx=10, sticky="nsew")
        self.visualisation_frame.grid_rowconfigure(0, weight=1)
        self.visualisation_frame.grid_rowconfigure(1, weight=0)

        self.create_table()
        self.create_image_and_buttons()
        self.create_page_selector()

    def create_table(self):
        headings = ["Index", "IFT", "V", "SA", "Bond", "Worth"]
        for j, heading in enumerate(headings):
            cell = CTkLabel(self.table_frame, text=heading)
            cell.grid(row=0, column=j, padx=10, pady=10, sticky="nsew")

        self.table_rows = []

    def create_image_and_buttons(self):
        self.image_frame = CTkFrame(self.visualisation_frame)
        self.image_frame.grid(row=0, column=0, sticky="nsew")

        self.fig, self.axs = plt.subplots(3, 1, figsize=(6, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.image_frame)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.image_frame)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.buttons_frame = CTkFrame(self.visualisation_frame)
        self.buttons_frame.grid(row=1, column=0, pady=5)

        self.button_original = CTkButton(self.buttons_frame, text="Show Original Image", command=self.show_original_image)
        self.button_residual = CTkButton(self.buttons_frame, text="Show Processed Image (Residuals)", command=self.show_residual_image)
        self.button_trend = CTkButton(self.buttons_frame, text="Show Trend Chart", command=self.show_trend_chart)
        self.button_fitting_curve = CTkButton(self.buttons_frame, text="Show Residual Fitting Curve", command=self.show_residual_fitting_curve)

        self.button_original.pack(side="left", padx=5)
        self.button_residual.pack(side="left", padx=5)
        self.button_trend.pack(side="left", padx=5)
        self.button_fitting_curve.pack(side="left", padx=5)

    def create_page_selector(self):
        self.page_frame = CTkFrame(self)
        self.page_frame.pack(pady=5)

        self.button_prev = CTkButton(self.page_frame, text="<", width=30, command=self.prev_page)
        self.page_entry = CTkEntry(self.page_frame, width=40)
        self.label_total = CTkLabel(self.page_frame, text="of 0")
        self.button_next = CTkButton(self.page_frame, text=">", width=30, command=self.next_page)

        self.button_prev.pack(side="left", padx=5)
        self.page_entry.pack(side="left", padx=5)
        self.label_total.pack(side="left", padx=5)
        self.button_next.pack(side="left", padx=5)

        self.update_page_selector()

    def update_page_selector(self):
        total = len(self.user_input_data.import_files) if hasattr(self.user_input_data, 'import_files') else 0
        if total == 0:
            total = 1
        self.page_entry.delete(0, "end")
        self.page_entry.insert(0, str(self.current_index + 1))
        self.label_total.configure(text=f"of {total}")

    def prev_page(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_display()

    def next_page(self):
        total = len(self.user_input_data.import_files) if hasattr(self.user_input_data, 'import_files') else 0
        if self.current_index < total - 1:
            self.current_index += 1
            self.update_display()

    def update_table(self):
        for widget in self.table_frame.winfo_children():
            if isinstance(widget, CTkLabel) and widget.grid_info()['row'] != 0:
                widget.destroy()

        self.table_rows.clear()

        for i, data in enumerate(self.output):
            values = [
                f"{i+1}",
                f"{data.interfacial_tension:.2f}",
                f"{data.volume:.2f}",
                f"{data.surface_area:.2f}",
                f"{data.bond_number:.4f}",
                f"{data.worth:.4f}"
            ]
            row = []
            for j, value in enumerate(values):
                label = CTkLabel(self.table_frame, text=value)
                label.grid(row=i+1, column=j, padx=5, pady=5, sticky="nsew")
                row.append(label)
            self.table_rows.append(row)

    def show_original_image(self):
        self.fig.clf()
        ax = self.fig.add_subplot(111)
        try:
            img = Image.open(self.user_input_data.import_files[self.current_index])
            ax.imshow(img, cmap='gray')
            ax.axis('off')
        except Exception:
            ax.text(0.5, 0.5, "No Image Available", ha='center', va='center')
        self.canvas.draw()

    def show_residual_image(self):
        self.fig.clf()
        ax = self.fig.add_subplot(111)
        try:
            residuals = self.output[self.current_index].residuals
            if residuals is not None:
                ax.plot(residuals)
                ax.set_title("Residuals")
            else:
                ax.text(0.5, 0.5, "No residuals yet", ha='center', va='center')
        except Exception:
            ax.text(0.5, 0.5, "No residuals yet", ha='center', va='center')
        self.canvas.draw()

    def show_trend_chart(self):
        self.fig.clf()
        if len(self.output) > 0:
            frames = np.arange(1, len(self.output)+1)
            ift = [data.interfacial_tension for data in self.output]
            v = [data.volume for data in self.output]
            sa = [data.surface_area for data in self.output]

            axs = self.fig.subplots(3, 1, sharex=True)
            axs[0].plot(frames, ift, 'ro-')
            axs[0].set_ylabel('IFT [mN/m]')
            axs[1].plot(frames, v, 'bo-')
            axs[1].set_ylabel('V [mm³]')
            axs[2].plot(frames, sa, 'go-')
            axs[2].set_ylabel('SA [mm²]')
            axs[2].set_xlabel('Frame')
        else:
            self.fig.add_subplot(111).text(0.5, 0.5, "No data to plot", ha='center', va='center')
        self.canvas.draw()

    def show_residual_fitting_curve(self):
        self.fig.clf()
        ax = self.fig.add_subplot(111)
        try:
            residuals = self.output[self.current_index].residuals
            if residuals is not None:
                x = np.linspace(-3, 3, len(residuals))
                ax.scatter(x, residuals, s=10)
                ax.set_title("Residual Fitting Curve")
            else:
                ax.text(0.5, 0.5, "No fitting data", ha='center', va='center')
        except Exception:
            ax.text(0.5, 0.5, "No fitting data", ha='center', va='center')
        self.canvas.draw()

    def update_display(self):
        self.update_page_selector()
        self.show_original_image()

    def receive_output_ift(self, extracted_data):
        print(vars(extracted_data))
        self.output.append(extracted_data)
        self.update_table()
        self.update_display()

    def destroy(self):
        plt.close('all')
        return super().destroy()
