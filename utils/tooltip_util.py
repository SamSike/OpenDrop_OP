import tkinter as tk
import platform

def create_tooltip(widget, text: str, position="above-align-left"):
    import tkinter as tk
    import platform

    system = platform.system()
    is_mac = system == "Darwin"

    try:
        bind_target = widget._canvas
    except AttributeError:
        bind_target = widget

    if is_mac:
        tooltip = tk.Label(
            widget.master,
            text=text,
            bg="#f0f0f0",
            font=("Segoe UI", 10),
            justify="left",
            wraplength=350,
            relief="solid",
            borderwidth=1,
        )

        def enter(event):
            margin = 4

            widget_x = widget.winfo_rootx()
            widget_y = widget.winfo_rooty()
            widget_w = widget.winfo_width()
            widget_h = widget.winfo_height()

            master_x = widget.master.winfo_rootx()
            master_y = widget.master.winfo_rooty()

            tooltip.update_idletasks()
            tooltip_w = tooltip.winfo_width()
            tooltip_h = tooltip.winfo_height()

            if position == "above-align-left":
                rel_x = widget_x
                rel_y = widget_y - tooltip_h - margin
            elif position == "below-align-left":
                rel_x = widget_x
                rel_y = widget_y + widget_h + margin
            elif position == "below-align-right":
                rel_x = widget_x + widget_w - tooltip_w
                rel_y = widget_y + widget_h + margin
            else:
                # fallback: above-align-left
                rel_x = widget_x
                rel_y = widget_y - tooltip_h - margin

            place_x = rel_x - master_x
            place_y = rel_y - master_y

            tooltip.place(x=place_x, y=place_y)
            tooltip.lift()

        def leave(event):
            tooltip.place_forget()

        bind_target.bind("<Enter>", enter)
        bind_target.bind("<Leave>", leave)

    else:
        tooltip = tk.Toplevel(widget)
        tooltip.withdraw()
        tooltip.overrideredirect(True)
        tooltip.attributes("-alpha", 0.90)  # semi-transparent

        canvas = tk.Canvas(
            tooltip, background="#e0e0e0", borderwidth=0, highlightthickness=0
        )
        canvas.pack(fill="both", expand=True)

        padding_x, padding_y = 10, 6
        label = tk.Label(
            canvas,
            text=text,
            bg="#e0e0e0",
            font=("Segoe UI", 10),
            justify="left",
            wraplength=250,
            borderwidth=0,
        )
        label.pack(padx=padding_x, pady=padding_y)

        def enter(event):
            tooltip.geometry(f"+{event.x_root + 12}+{event.y_root + 12}")
            tooltip.deiconify()

        def leave(event):
                tooltip.withdraw()

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)
