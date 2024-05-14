import serial
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import simpledialog
import subprocess
import time


class CNCControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CNC Control App")
        
        # Initialize all necessary attributes before calling create_ui
        self.relative_mode = True
        self.step_size = 1
        self.speed = 150  # Make sure this is initialized before create_ui is called
        self.current_x = 0.0
        self.current_y = 0.0
        self.laser_power = 1000

        try:
            self.setup_serial()
        except Exception as e:
            messagebox.showerror("Serial Connection Error", f"Failed to set up serial connection: {e}")
            return  # Exit the initialization if serial setup fails

        self.create_ui()  # Now it's safe to call create_ui

        # Bind keys and mouse actions
        self.root.bind("<Left>", lambda event: self.move("left"))
        self.root.bind("<Right>", lambda event: self.move("right"))
        self.root.bind("<Up>", lambda event: self.move("up"))
        self.root.bind("<Down>", lambda event: self.move("down"))
        self.root.bind("<MouseWheel>", self.change_laser_power)
        self.root.bind("<Prior>", lambda event: self.change_laser_power(event, increment=10))
        self.root.bind("<Next>", lambda event: self.change_laser_power(event, increment=-10))


        self.update_status_panel()


    def open_draw_app(self):
        subprocess.Popen(["python", "draw.py"])

    def create_ui(self):
        # Ensure all UI components including laser_power_entry are created here
        self.laser_power_entry = ttk.Entry(self.root)
        self.laser_power_entry.pack()



    def setup_serial(self):
        self.serial_port = serial.Serial('COM3', 115200, timeout=1)
        print("Serial port opened on COM3 with baud rate 115200.")
        
    def send_gcode(self, x, y, laser_power):
        gcode_command = f"G1 X{x} Y{y} S{laser_power}"
        self.send_command(gcode_command)

    def send_home(self):
        gcode_home = "G28"  # Marlin G-code for homing
        self.send_command(gcode_home)
        # After homing, reset coordinates to 0,0,0
        self.current_x = 0.0
        self.current_y = 0.0

    def toggle_mode(self):
        self.relative_mode = not self.relative_mode
        mode_text = "Relative" if self.relative_mode else "Absolute"
        self.mode_button.config(text=f"Switch to {mode_text} Mode")

    def abort(self):
        self.send_command("M112")  # Send emergency stop command

    def send_command(self, gcode_command):
        if self.relative_mode:
            gcode_command = "G91\n" + gcode_command + "\nG90\n"  # Wrap the command with relative mode codes
        
            self.serial_port.write(gcode_command.encode() + b'\n')
            self.serial_port.flush()


    def open_gcode_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("G-code Files", "*.gcode")])
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    gcode_lines = f.readlines()
                    for line in gcode_lines:
                        self.send_command(line.strip())
            except Exception as e:
                messagebox.showerror("Error", f"Error opening or sending G-code file: {e}")


    def open_and_send_gcode(self):
        file_path = filedialog.askopenfilename(filetypes=[("G-code Files", "*.gcode")])
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    gcode_lines = f.readlines()
                    # Optionally, confirm before sending
                    if messagebox.askyesno("Confirm", "Send this G-code to the machine?"):
                        for line in gcode_lines:
                            self.send_command(line.strip())
            except Exception as e:
                messagebox.showerror("Error", f"Error opening or sending G-code file: {e}")




    def move(self, direction):
        gcode_command = ""
        if direction == "up":
            gcode_command = f"G1 Y{self.step_size} F{self.speed}"
        elif direction == "down":
            gcode_command = f"G1 Y-{self.step_size} F{self.speed}"
        elif direction == "left":
            gcode_command = f"G1 X-{self.step_size} F{self.speed}"
        elif direction == "right":
            gcode_command = f"G1 X{self.step_size} F{self.speed}"
        self.send_command(gcode_command)

    def set_step_size(self):
        new_step_size = simpledialog.askfloat("Step Size", "Enter step size in mm:")
        if new_step_size is not None:
            self.step_size = new_step_size

    def set_speed(self):
        new_speed = simpledialog.askinteger("Speed", "Enter movement speed (units per minute):")
        if new_speed is not None:
            self.speed = new_speed

    def set_laser_power(self):
        try:
            new_power = int(self.laser_power_entry.get())
            if 0 <= new_power <= 1000:
                self.laser_power = new_power
                self.send_command(f"S{self.laser_power}")
            else:
                messagebox.showerror("Error", "Laser power must be between 0 and 255.")
        except ValueError:
            messagebox.showerror("Error", "Invalid laser power value. Please enter an integer between 0 and 255.")
            
    def change_laser_power(self, event):
        # Determine the direction of scroll (up or down)
        if event.delta > 0:
            # Scrolling up, increase laser power by 1
            self.laser_power += 1
        else:
            # Scrolling down, decrease laser power by 1
            self.laser_power -= 1

        # Ensure laser power is within [0, 255]
        self.laser_power = max(0, min(self.laser_power, 255))

        # Update the laser power entry and send the new laser power command
        self.laser_power_entry.delete(0, tk.END)
        self.laser_power_entry.insert(0, str(self.laser_power))
        self.send_command(f"S{self.laser_power}")
        
    def turn_laser_on(self):
        self.send_command('M3')  # Turn on the laser

    def turn_laser_off(self):
        self.send_command('M5')  # Turn off the laser

    def predefined_cut(self, axis):
        try:
            length = float(self.cut_length_entry.get())
            if 0 <= length:
                if axis == 'X':
                    move_command = f"G1 X{length} F{self.speed} S{self.laser_power}"
                elif axis == 'Y':
                    move_command = f"G1 Y{length} F{self.speed} S{self.laser_power}"

                # Confirm before executing the cut
                if messagebox.askyesno("Confirm Cut", f"Execute a {length}mm cut along the {axis}-axis at speed {self.speed} and laser power {self.laser_power}?"):
                    self.send_command("M3 S" + str(self.laser_power))  # Optional: turn on the laser
                    self.send_command(move_command)
                    self.send_command("M5")  # Optional: turn off the laser after the cut
            else:
                messagebox.showerror("Error", "Length must be greater than 0.")
        except ValueError:
            messagebox.showerror("Error", "Invalid input for length. Please enter a numeric value.")

    def set_speed(self):
        try:
            new_speed = int(self.speed_entry.get())
            if new_speed > 0:
                self.speed = new_speed
                messagebox.showinfo("Success", f"Speed set to {new_speed} units/min.")
            else:
                messagebox.showerror("Error", "Speed must be a positive integer.")
        except ValueError:
            messagebox.showerror("Error", "Invalid speed value. Please enter a valid integer.")



    def set_laser_power(self):
        try:
            new_power = int(self.laser_power_entry.get())
            if 0 <= new_power <= 1000:
                self.laser_power = new_power
                self.send_command(f"S{self.laser_power}")
                messagebox.showinfo("Success", f"Laser power set to {new_power}.")
            else:
                messagebox.showerror("Error", "Laser power must be between 0 and 1000.")
        except ValueError:
            messagebox.showerror("Error", "Invalid laser power value. Please enter an integer between 0 and 1000.")


    def fetch_coordinates(self):
        # Example method to fetch and update coordinates
        try:
            response = self.serial_port.readline().decode().strip()
            # Example response might be "X:123 Y:456"
            parts = response.split()  # This will split by whitespace
            x_part = parts[0]  # "X:123"
            y_part = parts[1]  # "Y:456"
    
            # Parse the coordinate parts
            self.current_x = float(x_part.split(':')[1])
            self.current_y = float(y_part.split(':')[1])
    
            # Assuming connection status is good if we receive data
            self.connected = True
        except Exception as e:
            self.connected = False
            print("Failed to read or parse serial data:", e)
    
        # Schedule the next data fetch (if continuous updates are desired)
        self.root.after(100, self.fetch_coordinates)
    
        # Update the status panel directly or schedule it to be updated
        self.update_status_panel()



    def update_status_panel(self):
        # Schedule this method to be called again after 100 milliseconds
        self.connection_status.config(text="Connection: Connected")
        self.current_coords.config(text=f"Coordinates: X={self.current_x:.2f} Y={self.current_y:.2f}")
        self.current_speed.config(text=f"Speed: {self.speed} units/min")
        self.laser_power_status.config(text=f"Laser Power: {self.laser_power}")
        self.root.after(100, self.update_status_panel)


    def create_ui(self):

        self.gcode_label = ttk.Label(self.root, text="Enter G-code command:")
        self.gcode_entry = ttk.Entry(self.root, width=40)
        self.send_button = ttk.Button(self.root, text="Send G-code", command=self.send_gcode)
        self.home_button = ttk.Button(self.root, text="Home", command=self.send_home)
        self.mode_button = ttk.Button(self.root, text="Switch to Relative Mode", command=self.toggle_mode)
        self.open_file_button = ttk.Button(self.root, text="Open G-code File", command=self.open_gcode_file)
        self.step_button = ttk.Button(self.root, text="Set Step Size", command=self.set_step_size)
        self.speed_button = ttk.Button(self.root, text="Set Speed", command=self.set_speed)

        # Place all buttons in a consistent order
        self.open_file_button.pack(pady=5)
        self.gcode_label.pack(pady=10)
        self.gcode_entry.pack(pady=5)
        self.send_button.pack(pady=10)
        self.home_button.pack(pady=5)
        self.mode_button.pack(pady=5)

        self.up_button = ttk.Button(self.root, text="Y+Up", command=lambda: self.move("up"))
        self.down_button = ttk.Button(self.root, text="Y-Down", command=lambda: self.move("down"))
        self.left_button = ttk.Button(self.root, text="X-Left", command=lambda: self.move("left"))
        self.right_button = ttk.Button(self.root, text="X+Right", command=lambda: self.move("right"))
        self.abort_button = ttk.Button(self.root, text="Abort", command=self.abort)


        self.up_button.pack(pady=5)
        self.down_button.pack(pady=5)
        self.left_button.pack(pady=5)
        self.right_button.pack(pady=5)
        self.step_button.pack(pady=5)
        self.abort_button.pack(pady=5)
        self.speed_button.pack(pady=5)
        
        
        self.z_plus_button = ttk.Button(self.root, text="Z+", command=lambda: self.move_z("Zup"))
        self.z_minus_button = ttk.Button(self.root, text="Z-", command=lambda: self.move_z("Zdown"))
        
        self.z_plus_button.pack(pady=5)
        self.z_minus_button.pack(pady=5)
        

        # Add controls for predefined cuts
        self.cut_length_entry = ttk.Entry(self.root, width=10)
        self.cut_length_entry.pack(pady=5)

        self.cut_x_button = ttk.Button(self.root, text="Cut Horizontal (X-axis)", command=lambda: self.predefined_cut('X'))
        self.cut_x_button.pack(pady=5)

        self.cut_y_button = ttk.Button(self.root, text="Cut Vertical (Y-axis)", command=lambda: self.predefined_cut('Y'))
        self.cut_y_button.pack(pady=5)

        # Add entry and button for setting laser power
        self.laser_power_label = ttk.Label(self.root, text="Set Laser Power (0-1000):")
        self.laser_power_label.pack(pady=5)

        self.laser_power_entry = ttk.Entry(self.root)
        self.laser_power_entry.pack(pady=5)

        self.set_laser_power_button = ttk.Button(self.root, text="Set Power", command=self.set_laser_power)
        self.set_laser_power_button.pack(pady=5)

        self.speed_label = ttk.Label(self.root, text="Set Speed (units/min):")
        self.speed_label.pack(pady=5)

        self.speed_entry = ttk.Entry(self.root)
        self.speed_entry.insert(0, '150')  # Pre-fill with default speed
        self.speed_entry.pack(pady=5)

        self.set_speed_button = ttk.Button(self.root, text="Set Speed", command=self.set_speed)
        self.set_speed_button.pack(pady=5)

        # In your create_ui method, add the button:
        self.draw_cut_button = ttk.Button(self.root, text="Draw Cut", command=self.open_draw_app)
        self.draw_cut_button.pack(pady=5)

        # Status Panel
        self.status_frame = ttk.LabelFrame(self.root, text="Status Panel", padding="10")
        self.status_frame.pack(fill='x', expand='yes', padx=10, pady=10)

        self.connection_status = ttk.Label(self.status_frame, text="Connection: Disconnected")
        self.connection_status.pack(side='top', fill='x')

        self.current_coords = ttk.Label(self.status_frame, text="Coordinates: X=0.0 Y=0.0")
        self.current_coords.pack(side='top', fill='x')

        self.current_speed = ttk.Label(self.status_frame, text=f"Speed: {self.speed} units/min")
        self.current_speed.pack(side='top', fill='x')

        self.laser_power_status = ttk.Label(self.status_frame, text=f"Laser Power: {self.laser_power}")
        self.laser_power_status.pack(side='top', fill='x')
        self.open_file_button = ttk.Button(self.root, text="Open G-code File", command=self.open_gcode_file)
        self.open_file_button.pack(pady=5)
        
        self.send_gcode_button = ttk.Button(self.root, text="Send G-code to Machine", command=self.open_and_send_gcode)
        self.send_gcode_button.pack(pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = CNCControlApp(root)
    #app.update_coordinates()  # Start the coordinate update loop
    root.mainloop()


