from utils.os import resource_path, is_windows
from PIL import Image
from tkinter import messagebox
import sys
import signal
import tkinter as tk
import customtkinter as ctk


class MainWindow(ctk.CTk):
    def __init__(self, continue_processing, open_ift_window, open_ca_window):
        super().__init__()
        self.title("OpenDrop-ML")
        self.geometry("800x400")
        self.minsize(width=800, height=400)

        # For .ico files (recommended for Windows)

        if is_windows():
            self.iconbitmap(resource_path("assets/opendrop.ico"))
        else:
            # For .png files (recommended for macOS and Linux)
            icon_path = resource_path("assets/opendrop.png")
            icon_img = tk.PhotoImage(file=icon_path)
            self.iconphoto(True, icon_img)

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
        title_label = ctk.CTkLabel(self, text="OpenDrop-ML", font=("Helvetica", 48))
        title_label.pack(pady=90)
        # self.display_image("views/assets/banner.png")

        # Create main functionality buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack()

        # Bind the buttons to the same functions as in the old code
        self.create_button(
            button_frame,
            "Interfacial Tension",
            open_ift_window,
            resource_path("assets/opendrop-ift.png"),
            0,
        )
        self.create_button(
            button_frame,
            "Contact Angle",
            open_ca_window,
            resource_path("assets/opendrop-conan.png"),
            1,
        )

        # Add information button at bottom-right corner
        info_button = ctk.CTkButton(
            self,
            text="❗",
            command=self.show_info_popup,
            font=("Arial", 12, "bold"),
            fg_color="white",
            text_color="red",
            width=5,
        )
        # Positioned in the bottom-right corner
        info_button.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

        self.mainloop()

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
            compound="left",  # Place text on the right of the image
        )
        button.image = button_photo  # Keep a reference to avoid garbage collection
        button.grid(row=0, column=column, padx=20)

    def run_function(self, func):
        self.withdraw()
        func(self)
        # self.after(100, lambda: self.open_function_window(func))

    # def open_function_window(self, func):
    #     func()
    #     self.after(500, self.check_reopen)

    # def check_reopen(self):
    #     print("Toplevel windows:", [w for w in self.winfo_children() if isinstance(w, ctk.CTkToplevel)])

    #     if not any(isinstance(w, ctk.CTkToplevel) for w in self.winfo_children()):
    #         self.deiconify()
    #     else:
    #         self.after(500, self.check_reopen)

    def show_info_popup(self):
        messagebox.showinfo(
            "Information",
            (
                "OpenDrop-ML is an open-source, cross-platform tool for analyzing liquid droplets in surface science. "
                "It supports both classical geometric fitting and machine learning models (via Conan-ML), providing "
                "automated, high-throughput image analysis for researchers, technicians, and developers.\n\n"
                "Similar to the original OpenDrop tool, OpenDrop-ML offers two main functions:\n"
                "• Interfacial Tension: Measures the force acting at the surface of liquids.\n"
                "• Contact Angle: Measures the angle formed between a liquid and a solid surface."
            ),
            parent=self,
        )

    def close_window(self):
        self.continue_processing["status"] = False
        try:
            self.quit()
            self.destroy()
        except Exception as e:
            print("Error during destroy:", e)
        finally:
            import sys

            sys.exit(0)
