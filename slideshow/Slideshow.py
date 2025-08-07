import tkinter as tk
from tkinter import *
from tkinter import messagebox
import os
master = tk.Tk()

def startShow():
    os.system("python slideshow/app.py" )

master.title('Auto Slideshow')

tk.Label(master, text='Enter Image file path').grid(row=0)
e1 = tk.Entry(master)
e1.grid(row=0, column=1)



button = tk.Button(master, text='Start Slideshow', width=25, command= startShow)
button.place(x=50,y=50)



master.mainloop()
