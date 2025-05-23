import tkinter as tk


def create_tooltip(widget, text: str):
    tooltip = tk.Toplevel(widget)
    tooltip.withdraw()
    tooltip.overrideredirect(True)
    tooltip.attributes("-alpha", 0.90)  # semi-transparent

    canvas = tk.Canvas(tooltip, background="#e0e0e0",
                       borderwidth=0, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    padding_x, padding_y = 10, 6
    label = tk.Label(canvas, text=text, bg="#e0e0e0", font=(
        "Segoe UI", 10), justify="left", wraplength=250, borderwidth=0)
    label.pack(padx=padding_x, pady=padding_y)

    def enter(event):
        tooltip.geometry(f"+{event.x_root + 12}+{event.y_root + 12}")
        tooltip.deiconify()

    def leave(event):
        tooltip.withdraw()

    widget.bind("<Enter>", enter)
    widget.bind("<Leave>", leave)
