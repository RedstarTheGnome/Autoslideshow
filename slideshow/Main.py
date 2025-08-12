import tkinter as tk
from tkinter import *
from tkinter import messagebox, filedialog
import subprocess
import sys
import os
import webbrowser
import threading
import time
import logging
import socket
import shutil

# automatically install dependencies ---

def install_dependencies():
    #Checks for required dependencies (Flask and catt) and installs them
    dependencies = ["Flask", "catt"]
    
    # Define a set of the imported modules to quickly check if a module is loaded
    imported_modules = set(sys.modules.keys())
    for package in dependencies:
        try:
            # Check if the package is already imported or available
            if package == "Flask":
                import flask
            elif package == "catt":
                continue
            # If the import succeeds, the package is already installed.
            logging.info(f"Dependency '{package}' is already installed.")

        except ImportError:
            logging.warning(f"Dependency '{package}' not found. Installing now...")
            try:
                # Use subprocess to run the pip install command.
                # `sys.executable` ensures we use the same Python interpreter.
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                logging.info(f"Successfully installed '{package}'.")
            except subprocess.CalledProcessError as e:
                logging.error(f"Failed to install '{package}'. Please install it manually. Error: {e}")
                messagebox.showerror("Installation Error", f"Failed to install '{package}'. Please try running 'pip install {package}' from your terminal.")
                sys.exit(1) 

    # Specifically check for catt.exe since it's a command line tool.
    logging.info("All dependencies have been checked.")
install_dependencies()


# Set up logging for the script to see what's happening
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

master = tk.Tk()

flask_process = None
e1 = tk.Entry(master, width=50) # Image folder path
e2 = tk.Entry(master, width=10) # Time input
e3 = tk.Entry(master, width=10) # Refresh time input

# --- CONFIGURATION FOR CATT ---
CATT_PATH = shutil.which("catt")

if not CATT_PATH:
    log.error("Catt executable not found in system's PATH. Please ensure it is installed correctly.")
    # You might want to handle this error by disabling the cast functionality
    # or exiting the program gracefully.
else:
    log.info(f"Catt executable found at: {CATT_PATH}")

# Dynamically get the local IPv4 address and set the URL
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80)) # Connect to an external host to find the local IP
    local_ip = s.getsockname()[0]
    s.close()
    URL_TO_CAST = f"http://{local_ip}:5000/"
except Exception as e:
    log.error(f"Could not determine local IP address: {e}")
    # Fallback to a common local IP if an error occurs
    URL_TO_CAST = "http://127.0.0.1:5000/"

CHROMECAST_DEVICE_NAME = "Entryway TV"
# --- END CONFIGURATION ---

def browse_folder():
    #Opens a file dialog to select a folder and inserts the path into e1.#
    folder_path = filedialog.askdirectory()
    if folder_path:
        e1.delete(0, END)
        e1.insert(0, folder_path)

def run_catt_command(refresh_time_minutes):
    #Constructs and runs the catt command, then sleeps for the specified time.
    log.info("Starting the cast refresh")

    wait_time_seconds = int(refresh_time_minutes) * 60

    while True:
        try:
            log.info("Starting the cast process with catt...")
            
            command = [
                CATT_PATH,
                "cast_site",
                URL_TO_CAST
            ]

            env = os.environ.copy()
            env["CATT_DEVICE"] = CHROMECAST_DEVICE_NAME
            
            log.info(f"Running command: {command}")
            subprocess.run(command, env=env, check=True)
            log.info("Catt command executed successfully.")

        except subprocess.CalledProcessError as e:
            log.error(f"Failed to run catt command. Error code: {e.returncode}")
            log.error(f"Error output:\n{e.stderr}")
            # Do not break here so the loop can retry
        except FileNotFoundError:
            log.error(f"Catt executable not found at: {CATT_PATH}. Please check the path.")
            break # Exit the loop if the executable is not found.
        except Exception as e:
            log.error(f"An unexpected error occurred: {e}", exc_info=True)

        log.info(f"Cast complete. Waiting for {refresh_time_minutes} minutes before next refresh...")
        time.sleep(wait_time_seconds)

def startShow():
    """Starts the Flask server and the autocast script in separate threads."""
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

    try:
        # Use default values if the fields are empty
        time_seconds = int(time_str) if time_str else 3
        refresh_time_minutes = int(refresh_time_str) if refresh_time_str else 5
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
            
        # Start the Flask server process
        flask_process = subprocess.Popen([
            python_executable, 
            app_path, 
            image_path, 
            str(time_seconds), 
            str(refresh_time_minutes)
        ])
        
        print(f"Flask server started with path: {image_path}, time: {time_seconds}, refresh: {refresh_time_minutes}")
        messagebox.showinfo("Success", "Slideshow server started!")
        
        # Start the catt command in a new thread.
        threading.Thread(target=run_catt_command, args=(refresh_time_minutes,), daemon=True).start()
        
        # This will open the page on the local machine's browser, not cast it.
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
tk.Label(master, text="Refresh Time in Minutes:").grid(row=4, column=1, sticky="w", padx=5, pady=(10, 0))
e3.grid(row=5, column=1, padx=10, pady=(0, 5), sticky="w")
e3.insert(0, "5")

start_button = tk.Button(master, text='Start Slideshow', width=25, command=startShow)
start_button.grid(row=6, column=0, columnspan=2, padx=10, pady=20)

master.grid_columnconfigure(0, weight=1)
master.grid_columnconfigure(1, weight=1)

master.mainloop()