from utils.validators import validate_int

import tkinter as tk
import customtkinter as ctk


class IntegerEntry():
    def __init__(self, parent, frame, text_left, callback, default_value, rw=0, cl=0, padx=(5, 5), pady=(5, 5), width_specify=150, label_width=150):
        self.label = ctk.CTkLabel(
            frame, text=text_left, width=label_width, anchor="w")
        self.label.grid(row=rw, column=cl, sticky="w", padx=padx, pady=pady)
        self.text_variable = ctk.StringVar()

        # Fallback to 0 if default_value is None
        if default_value is not None:
            self.text_variable.set(str(int(default_value)))

        if callback:
            self.text_variable.trace_add("write", callback)

        vcmd_int = (parent.register(validate_int),
                    '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.entry = ctk.CTkEntry(
            frame, textvariable=self.text_variable, validate='key', validatecommand=vcmd_int)
        self.entry.configure(width=width_specify)
        self.entry.grid(row=rw, column=cl+1, sticky="we", padx=padx, pady=pady)

    def get_value(self):
        return int("0" + self.text_variable.get())

    def set_value(self, value):
        self.text_variable.set(str(int(value)))

    def disable(self):
        self.entry.configure(state="disabled")
        self.label.configure(state="disabled")

    def normal(self):
        self.entry.configure(state="normal")
        self.label.configure(state="normal")
