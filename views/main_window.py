import signal
import sys

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image, ImageTk

class MainWindow(ctk.CTk):
    def __init__(self, continue_processing, open_ift_window, open_ca_window):
        super().__init__()
        self.title("OpenDrop2")
        self.geometry("800x400")
        self.minsize(width=800, height=400)

        self.continue_processing = continue_processing

        # Define a function to handle the SIGINT signal (Ctrl+C)
        def signal_handler(sig, frame):
            print("Exiting...")
            try:
                self.destroy()  # Close the application
            except tk.TclError:
                print("Application already destroyed.")
            sys.exit(0)
        # Attach the signal handler to SIGINT
        signal.signal(signal.SIGINT, signal_handler)

        self.protocol("WM_DELETE_WINDOW", self.close_window)

        # Display title
        title_label = ctk.CTkLabel(
            self, text="OpenDrop2", font=("Helvetica", 48))
        title_label.pack(pady=50)
        # self.display_image("views/assets/banner.png")

        # Create main functionality buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=50)

        # Bind the buttons to the same functions as in the old code
        self.create_button(button_frame, "Interfacial Tension", open_ift_window,"views/assets/opendrop-ift.png",0)
        self.create_button(button_frame, "Contact Angle", open_ca_window,"views/assets/opendrop-conan.png", 1)

        # Add information button at bottom-right corner
        info_button = ctk.CTkButton(self, text="❗", command=self.show_info_popup, font=(
            "Arial", 12, "bold"), fg_color="white", text_color="red", width=5)
        # Positioned in the bottom-right corner
        info_button.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)

        self.mainloop()

    def create_button(self, frame, text, command, column):
        button = ctk.CTkButton(frame, text=text, font=(
            "Helvetica", 24), width=240, height=3, command=lambda: self.run_function(command))
        button.grid(row=0, column=column, padx=20)

    def create_button(self, frame, text, command, image_path, column):
        # Load the image for the button
        button_image = Image.open(image_path)
        button_photo = ctk.CTkImage(button_image, size=(40, 40))

        # Create a CTkButton with image and text
        button = ctk.CTkButton(
            frame, 
            text=text, 
            font=("Helvetica", 24), 
            width=240, 
            height=60, 
            command=lambda: self.run_function(command),
            image=button_photo,
            compound="left"  # Place text on the right of the image
        )
        button.image = button_photo  # Keep a reference to avoid garbage collection
        button.grid(row=0, column=column, padx=20)

    def run_function(self, func):
        # TO DO: change the code to fix the warning
        self.destroy()
        func()
        
        

    def show_info_popup(self):
        messagebox.showinfo(
            "Information", "Interfacial Tension: Measures the force at the surface of liquids.\n\nContact Angle: Measures the angle between the liquid surface and the solid surface.")
        
    def close_window(self):
        self.continue_processing["status"] = False
        self.destroy()

    def display_image(self, image_path):
        # Load the image using PIL
        image = Image.open(image_path)
        photo = ctk.CTkImage(image, size=(300, 200))

        # Create a CTkLabel to display the image
        image_label = ctk.CTkLabel(self, image=photo)
        image_label.image = photo  # Keep a reference to avoid garbage collection
        image_label.pack(pady=20)