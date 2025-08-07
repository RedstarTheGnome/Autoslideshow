import tkinter as tk
from tkinter import *
from tkinter import messagebox
import subprocess
import sys
import os 

master = tk.Tk()



flask_process = None
e1 = tk.Entry(master)

def startShow():
    global flask_process
    image_path = e1.get()
    
    if not image_path:
        messagebox.showerror("Error", "Please enter an image file path.")
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
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start slideshow: {e}")



#Tkinter box 


master.title('Auto Slideshow')

info1 = Label(master, text ="Welcome to the Auto slide show, ")
info2= Label(master, text="Please enter the image's location as a file path")
info1.grid(row=1,column=0)
info2.grid(row=2,column=0)
tk.Label(master, text='Enter Image file path:').grid(row=0)
e1.grid(row=3, column=0)

button = tk.Button(master, text='Start Slideshow', width=25, command= startShow)
button.grid(row=4, column=0)
master.geometry("300x200")
master.mainloop()