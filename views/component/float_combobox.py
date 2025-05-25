import tkinter as tk
from tkinter import ttk
import customtkinter as ctk


class FloatCombobox:
    def __init__(
        self,
        parent,
        frame,
        text_left,
        options_list,
        callback,
        default_value,
        rw=0,
        padx=(5, 5),
        pady=(5, 5),
        width_specify=150,
        label_width=150,
        state_specify="normal",
    ):
        self.label = ctk.CTkLabel(frame, text=text_left, width=label_width, anchor="w")
        self.label.grid(row=rw, column=0, sticky="w", padx=padx, pady=pady)

        self.text_variable = ctk.StringVar()

        if default_value is not None:
            self.default_value = float(default_value)
            self.float_variable = self.default_value
            self.text_variable.set(str(self.default_value))  # Set default value

        if callback:
            self.text_variable.trace_add("write", callback)

        self.combobox = ctk.CTkComboBox(
            frame, variable=self.text_variable, values=options_list
        )
        self.combobox.configure(width=width_specify, state=state_specify)
        self.combobox.grid(row=rw, column=1, sticky="we", padx=padx, pady=pady)

    def get_value(self):
        try:
            value = float("0" + self.text_variable.get())
            self.float_variable = value
            return value
        except ValueError:
            self.set_value(self.float_variable)
            return self.float_variable

    def set_value(self, value):
        self.text_variable.set(str(float(value)))

    def disable(self):
        self.combobox.configure(state="disabled")
        self.label.configure(state="disabled")

    def normal(self):
        self.combobox.configure(state="normal")
        self.label.configure(state="normal")
