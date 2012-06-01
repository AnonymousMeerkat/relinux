'''
Anything GUI-related goes here
@author: Anonymous Meerkat
'''

import Tkinter
import ttk
import config

style = ttk.Style()
style.configure("TButton", foreground="black", background="white")
style.configure("TLabel", foreground="black", background="white")
style.configure("Frame", foreground="black", background="white")

class About:
    def __init__(self, master):
        top = self.top = Tkinter.Toplevel(master)
        w = ttk.Label(top, text=config.VERSION_STRING)
        w.pack(side=Tkinter.TOP, fill=Tkinter.BOTH, expand=True)
        b = ttk.Button(top, text="Close", command=top.quit)
        b.pack(side=Tkinter.BOTTOM)

class GUI:
    root = 0
    def __init__(self, master):
        self.root = master
        frame = ttk.Frame(self.root)
        frame.pack()

        self.button = ttk.Button(frame, text="QUIT", command=frame.quit)
        self.button.pack(side=Tkinter.LEFT)

        self.hi_there = ttk.Button(frame, text="Hello", command=self.about)
        self.hi_there.pack(side=Tkinter.LEFT)
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
        print "hi there, everyone!"
    
    def about(self):
        return About(self.root)
