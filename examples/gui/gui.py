import tkinter as tk
from tkinter import messagebox
import re

# Global variables to manage the GUI state
root = None
elements = {}  # Stores references to widgets (labels, entries, etc.)
cliff_vars = {} # Stores data from input fields

def setup(api):
    # Registering the new expanded suite of commands
    api.register_command("window", handle_window)
    api.register_command("title", handle_title)
    api.register_command("label", handle_label)
    api.register_command("input", handle_input)
    api.register_command("button", lambda line, ln: handle_button(line, ln, api))
    api.register_command("get_input", lambda line, ln: handle_get_input(line, ln))
    api.register_command("launch", handle_launch)

def handle_window(line, line_num):
    global root
    if not root:
        root = tk.Tk()
        root.geometry("400x300")

def handle_title(line, line_num):
    match = re.search(r'title\{(.*?)\}', line)
    if match and root:
        root.title(match.group(1).strip('"'))

def handle_label(line, line_num):
    # Syntax: label{"Text Content"}
    match = re.search(r'label\{(.*?)\}', line)
    if match and root:
        text = match.group(1).strip('"')
        lbl = tk.Label(root, text=text, font=("Arial", 10))
        lbl.pack(pady=5)

def handle_input(line, line_num):
    # Syntax: input{"variable_name"}
    match = re.search(r'input\{(.*?)\}', line)
    if match and root:
        var_name = match.group(1).strip('"')
        entry = tk.Entry(root)
        entry.pack(pady=5)
        elements[var_name] = entry # Save reference to pull data later

def handle_button(line, line_num, api):
    # Syntax: button{"Label", "VoidToCall"}
    match = re.search(r'button\{"(.*?)",\s*"(.*?)"\}', line)
    if match and root:
        text, target = match.groups()
        btn = tk.Button(root, text=text, command=lambda: api.execute_block(target, line_num, line))
        btn.pack(pady=10)

def handle_get_input(line, line_num):
    # Syntax: get_input{"variable_name"}
    # Pulls text from the Entry widget and prints it to console
    match = re.search(r'get_input\{(.*?)\}', line)
    if match:
        var_name = match.group(1).strip('"')
        if var_name in elements:
            val = elements[var_name].get()
            print(f"[GUI DATA] {var_name}: {val}")
        else:
            print(f"Runtime Error: Input field '{var_name}' not found.")

def handle_launch(line, line_num):
    if root:
        root.mainloop()