
import serial
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import simpledialog
import subprocess
import time

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