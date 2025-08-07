import tkinter as tk
from tkinter import *
from tkinter import messagebox, filedialog
import subprocess
import sys
import os
import webbrowser

master = tk.Tk()

flask_process = None
e1 = tk.Entry(master, width=50) # Increased width for better display of long paths

def browse_folder():
    """Opens a file dialog to select a folder and inserts the path into e1."""
    folder_path = filedialog.askdirectory()
    if folder_path:
        e1.delete(0, END)  # Clear the current content of the entry field
        e1.insert(0, folder_path) # Insert the selected path

def startShow():
    """Starts the Flask server with the specified image path."""
    global flask_process
    image_path = e1.get()
    
    if not image_path:
        messagebox.showerror("Error", "Please enter or browse to an image folder.")
        return

    # Check if the entered path is a valid directory
    if not os.path.isdir(image_path):
        messagebox.showerror("Error", "The entered path is not a valid directory.")
        return

    try:
        python_executable = sys.executable
        
        # Get the directory of the current script (Slideshow.py)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Construct the absolute path to app.py within the same directory
        app_path = os.path.join(current_dir, 'app.py')

        if not os.path.exists(app_path):
            messagebox.showerror("Error", f"Could not find app.py at {app_path}")
            return
            
        flask_process = subprocess.Popen([python_executable, app_path, image_path])
        print(f"Flask server started with path: {image_path}")
        messagebox.showinfo("Success", "Slideshow server started!")
        webbrowser.open('http://127.0.0.1:5000/')
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start slideshow: {e}")

# --- Tkinter GUI Setup ---
master.title('Auto Slideshow')
master.geometry("450x200") # Adjusted size for better layout

info1 = Label(master, text ="Welcome to the Auto Slideshow,")
info2= Label(master, text="Please select the folder containing your images.")
info1.grid(row=0, column=0, columnspan=2, padx=10, pady=5)
info2.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

# Entry and Browse button on the same row
e1.grid(row=2, column=0, padx=10, pady=5)
browse_button = tk.Button(master, text="Browse", command=browse_folder)
browse_button.grid(row=2, column=1, padx=10, pady=5)

start_button = tk.Button(master, text='Start Slideshow', width=25, command=startShow)
start_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

# Configure grid to center the widgets
master.grid_columnconfigure(0, weight=1)
master.grid_columnconfigure(1, weight=1)

master.mainloop()