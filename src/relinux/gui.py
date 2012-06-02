'''
Anything GUI-related goes here
@author: Anonymous Meerkat
'''

from tkinter import ttk
import tkinter
from relinux import config

class About:
    def __init__(self, master):
        top = self.top = tkinter.Toplevel(master)
        top.title(config.product + " - About")
        w = ttk.Label(top, text=config.about_string)
        w.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
        b = ttk.Button(top, text="Close", command=top.destroy)
        b.pack(side=tkinter.BOTTOM)

class GUI:
    def __init__(self, master):
        style = ttk.Style()
        style.configure("TButton", foreground="black", background="lightgrey")
        style.configure("TLabel", foreground="black", background="lightgrey")
        style.configure("TFrame", foreground="black", background="lightgrey")
        self.root = master
        self.root.title(config.product)
        frame = tkinter.Frame(self.root, background="lightgrey")
        frame.pack()

        self.button = ttk.Button(frame, text="QUIT", command=frame.quit)
        self.button.grid(row=0)

        self.hi_there = ttk.Button(frame, text="Hello", command=self.about)
        self.hi_there.grid(row=1, column=1)
        #menubar = Tkinter.Menu(master)
        #filemenu = Tkinter.Menu(menubar, tearoff=0)
        #filemenu.add_command(label="Hello!", command=self.say_hi)
        #filemenu.add_separator()
        #filemenu.add_command(label="Exit", command=frame.quit)
        #menubar.add_cascade(label="File", menu=filemenu)
        #helpmenu = Tkinter.Menu(menubar, tearoff=0)
        #helpmenu.add_command(label="About", command=self.about)
        #menubar.add_cascade(label="Help", menu=helpmenu)
        # display the menu
        #master.config(menu=menubar)

    def say_hi(self):
        print("hi there, everyone!")
    
    def about(self):
        return About(self.root)
