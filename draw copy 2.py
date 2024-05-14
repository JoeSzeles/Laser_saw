import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

def main():
    root = tk.Tk()
    root.title("Draw Cut Application")
    root.geometry("1600x1200")  # Adjusted window size for better layout

    # Menu frame for inputs at the top of the window
    menu_frame = tk.Frame(root)
    menu_frame.pack(side='top', fill='x', expand=False)

    # Variables for machine and material dimensions with default values
    machine_width = tk.IntVar(value=410)
    machine_height = tk.IntVar(value=860)

    # Canvas setup; dimensions will be updated via a function
    canvas = tk.Canvas(root, bg='white')
    canvas.pack(fill='both', expand=True)

    # Function to update canvas size based on machine dimensions
    def update_canvas():
        mw, mh = machine_width.get(), machine_height.get()
        canvas.config(width=mw, height=mh)
        canvas.delete("all")  # Clear previous drawings
        # Draw the maximum cutting area
        canvas.create_rectangle(2.5, 2.5, mw - 2.5, mh - 2.5, outline="blue", width=1)

    # Function to clear all lines from the canvas
    def clear_lines():
        canvas.delete("line")  # Assumes all lines are tagged with 'line' when created


    # Machine width and height entries
    machine_width_label = ttk.Label(menu_frame, text="Machine Width (mm):")
    machine_width_label.pack(side='left', padx=5)
    machine_width_entry = ttk.Entry(menu_frame, textvariable=machine_width, width=7)
    machine_width_entry.pack(side='left', padx=5)

    machine_height_label = ttk.Label(menu_frame, text="Machine Height (mm):")
    machine_height_label.pack(side='left', padx=5)
    machine_height_entry = ttk.Entry(menu_frame, textvariable=machine_height, width=7)
    machine_height_entry.pack(side='left', padx=5)

    confirm_machine_button = ttk.Button(menu_frame, text="Set Machine Size", command=update_canvas)
    confirm_machine_button.pack(side='left', padx=5)

    material_x_label = ttk.Label(menu_frame, text="Material Width (mm):")
    material_x_label.pack(side='left', padx=5)
    material_x_entry = ttk.Entry(menu_frame, width=7)
    material_x_entry.pack(side='left', padx=5)

    material_y_label = ttk.Label(menu_frame, text="Material Height (mm):")
    material_y_label.pack(side='left', padx=5)
    material_y_entry = ttk.Entry(menu_frame, width=7)
    material_y_entry.pack(side='left', padx=5)

    confirm_button = ttk.Button(menu_frame, text="Set Material", command=lambda: draw_material())
    confirm_button.pack(side='left', padx=5)

    draw_line_button = ttk.Button(menu_frame, text="Enable Draw Line", command=lambda: toggle_line_drawing())
    draw_line_button.pack(side='left', padx=5)
    # Additional button to clear lines
    clear_lines_button = ttk.Button(menu_frame, text="Clear Lines", command=clear_lines)
    clear_lines_button.pack(side='left', padx=5)

    # Functions to handle drawing and material settings
    line_start = None
    def handle_left_click(event):
        nonlocal line_start
        if line_start is None:
            line_start = (event.x, event.y)
            canvas.create_oval(event.x-2, event.y-2, event.x+2, event.y+2, fill="green")
        else:
            # Tagging lines with 'line' for easy removal
            canvas.create_line(line_start[0], line_start[1], event.x, event.y, fill="green", width=2, tags="line")
            line_start = (event.x, event.y)

    def handle_right_click(event):
        nonlocal line_start
        line_start = None

    def draw_material():
        canvas.delete("material_area")
        try:
            material_width = int(material_x_entry.get())
            material_height = int(material_y_entry.get())
            if 0 < material_width <= machine_width.get() and 0 < material_height <= machine_height.get():
                x1 = 2.5
                y1 = machine_height.get() - material_height - 2.5
                canvas.create_rectangle(x1, y1, x1 + material_width, y1 + material_height, outline="red", width=2, fill="light grey", tags="material_area")
            else:
                messagebox.showerror("Error", "Material dimensions must fit within the specified machine dimensions.")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid integer dimensions.")

    def toggle_line_drawing():
        if canvas.bind("<Button-1>"):
            canvas.unbind("<Button-1>")
            canvas.unbind("<Button-3>")
            draw_line_button.config(text="Enable Draw Line")
        else:
            canvas.bind("<Button-1>", handle_left_click)
            canvas.bind("<Button-3>", handle_right_click)
            draw_line_button.config(text="Disable Draw Line")

    # Initialize the canvas with the default machine size
    update_canvas()

    root.mainloop()

if __name__ == "__main__":
    main()
