import tkinter as tk
from tkinter import *
from tkinter import messagebox, filedialog
import subprocess
import sys
import os
import webbrowser

master = tk.Tk()

flask_process = None
e1 = tk.Entry(master, width=50) # Image folder path
e2 = tk.Entry(master, width=10) # Time input
e3 = tk.Entry(master, width=10) # Refresh time input

def browse_folder():
    """Opens a file dialog to select a folder and inserts the path into e1."""
    folder_path = filedialog.askdirectory()
    if folder_path:
        e1.delete(0, END)
        e1.insert(0, folder_path)

def startShow():
    """Starts the Flask server with the specified image path and timings."""
    global flask_process
    image_path = e1.get()
    time_str = e2.get()
    refresh_time_str = e3.get()

    if not image_path:
        messagebox.showerror("Error", "Please enter or browse to an image folder.")
        return

    if not os.path.isdir(image_path):
        messagebox.showerror("Error", "The entered path is not a valid directory.")
        return

    # Validate that time and refresh time are valid numbers
    try:
        # Use default values if the fields are empty
        time = int(time_str) if time_str else 3000
        refresh_time = int(refresh_time_str) if refresh_time_str else 5000
    except ValueError:
        messagebox.showerror("Error", "Time and Refresh Time must be valid numbers.")
        return

    try:
        python_executable = sys.executable
        current_dir = os.path.dirname(os.path.abspath(__file__))
        app_path = os.path.join(current_dir, 'app.py')

        if not os.path.exists(app_path):
            messagebox.showerror("Error", f"Could not find app.py at {app_path}")
            return
            
        # Pass all parameters as command-line arguments.
        # sys.argv[0] will be app_path,
        # sys.argv[1] will be image_path,
        # sys.argv[2] will be the time,
        # and sys.argv[3] will be the refresh_time.
        flask_process = subprocess.Popen([
            python_executable, 
            app_path, 
            image_path, 
            str(time), 
            str(refresh_time)
        ])
        
        print(f"Flask server started with path: {image_path}, time: {time}, refresh: {refresh_time}")
        messagebox.showinfo("Success", "Slideshow server started!")
        webbrowser.open('http://127.0.0.1:5000/')
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start slideshow: {e}")

# --- Tkinter GUI Setup ---
master.title('Auto Slideshow')
master.geometry("450x300")

info1 = Label(master, text="Welcome to the Auto Slideshow,")
info2 = Label(master, text="Please select the folder containing your images.")
info1.grid(row=0, column=0, columnspan=2, padx=10, pady=5)
info2.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

# Image Folder and Browse button
tk.Label(master, text="Image Folder:").grid(row=2, column=0, sticky="w", padx=10)
e1.grid(row=3, column=0, padx=10, pady=5)
browse_button = tk.Button(master, text="Browse", command=browse_folder)
browse_button.grid(row=3, column=1, padx=10, pady=5)

# Time and Refresh Time inputs
tk.Label(master, text="Time in Seconds:").grid(row=4, column=0, sticky="w", padx=10, pady=(10, 0))
e2.grid(row=5, column=0, padx=10, pady=(0, 5), sticky="w")
e2.insert(0, "3")
tk.Label(master, text="Refresh Time in Minutes:").grid(row=4, column=1, sticky="w", padx=10, pady=(10, 0))
e3.grid(row=5, column=1, padx=10, pady=(0, 5), sticky="w")
e3.insert(0, "5")

start_button = tk.Button(master, text='Start Slideshow', width=25, command=startShow)
start_button.grid(row=6, column=0, columnspan=2, padx=10, pady=20)

master.grid_columnconfigure(0, weight=1)
master.grid_columnconfigure(1, weight=1)

master.mainloop()