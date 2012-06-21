'''
Anything GUI-related goes here
@author: Anonymous Meerkat
'''

from tkinter import ttk
import tkinter
import re
from relinux import config, configutils


class VerticalScrolledFrame(tkinter.Frame):
    def __init__(self, parent, *args, **kw):
        tkinter.Frame.__init__(self, parent, *args, **kw)
        vscrollbar = tkinter.Scrollbar(self, orient=tkinter.VERTICAL)
        vscrollbar.pack(fill=tkinter.Y, side=tkinter.RIGHT, expand=tkinter.FALSE)
        canvas = tkinter.Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        canvas.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=tkinter.TRUE)
        vscrollbar.config(command=canvas.yview)
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)
        self.interior = interior = tkinter.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=tkinter.NW)

        def _configure_interior(event):
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)

        return


class About:
    def __init__(self, master):
        top = self.top = tkinter.Toplevel(master, background=config.background)
        top.title(config.product + " - About")
        w = ttk.Label(top, text=config.about_string)
        w.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
        b = ttk.Button(top, text="Close", command=top.destroy)
        b.pack(side=tkinter.BOTTOM)


class Wizard(ttk.Notebook):
    def on_change_tab(self, *args):
        w = self.select()
        self.current = self.index(w)

    def __init__(self, master=None, **kw):
        npages = kw.pop('npages', 3)
        kw['style'] = 'Wizard.TNotebook'
        #ttk.Style(master).layout('Wizard.TNotebook.Tab', '')
        ttk.Notebook.__init__(self, master, **kw)

        self._children = {}

        for page in range(npages):
            self.add_empty_page()

        self.current = 0
        self._wizard_buttons()
        self.bind("<<NotebookTabChanged>>", self.on_change_tab)

    def _wizard_buttons(self):
        """Place wizard buttons in the pages."""
        for indx, child in self._children.items():
            btnframe = ttk.Frame(child)
            btnframe.pack(side='bottom', fill='x', padx=6, pady=12)
            nextbtn = ttk.Button(btnframe, text="Next", command=self.next_page)
            nextbtn.pack(side='right', anchor='e', padx=6)
            quitbtn = ttk.Button(btnframe, text="Quit", command=self.close)
            quitbtn.pack(side="left", anchor="w", padx=6)
            if indx > 0:
                prevbtn = ttk.Button(btnframe, text="Previous",
                    command=self.prev_page)
                prevbtn.pack(side='right', anchor='e', padx=6)
                if indx == len(self._children) - 1:
                    nextbtn.configure(text="Finish", command=self.close)
            progressframe = ttk.Frame(child)
            progressframe.pack(side="bottom", fill="x", padx=6)
            ttk.Progressbar(progressframe).pack(fill="x")

    def next_page(self):
        self.current += 1

    def prev_page(self):
        self.current -= 1

    def close(self):
        self.master.destroy()

    def add_empty_page(self):
        child = tkinter.Frame(self)
        self._children[len(self._children)] = child
        self.add(child)

    def add_page_body(self, tab_id, title, body):
        self.tab(tab_id, text=title)
        body.pack(side='top', fill='both', padx=6, pady=12, expand=1)

    def page_container(self, page_num):
        if page_num in self._children:
            return self._children[page_num]
        else:
            raise KeyError("Invalid page: %s" % page_num)

    def _get_current(self):
        return self._current

    def _set_current(self, curr):
        if curr not in self._children:
            raise KeyError("Invalid page: %s" % curr)

        self._current = curr
        self.select(self._children[self._current])

    current = property(_get_current, _set_current)


class GUI:
    def __init__(self, master):
        self.root = master
        self.root.title(config.product)
        wizard = Wizard(npages=3)
        wizard.master.minsize(400, 350)
        wizard.master.maxsize(800, 700)
        self.page1 = ttk.Notebook(wizard.page_container(1))
        self.page0 = ttk.Label(wizard.page_container(0), text='Welcome to relinux 0.4!\nClick on next to get started')
        self.page2 = ttk.Label(wizard.page_container(2), text='Page 3')
        wizard.add_page_body(0, "Welcome", self.page0)
        wizard.add_page_body(1, "Configure", self.page1)
        wizard.add_page_body(2, "Page 3", self.page2)
        wizard.pack(fill='both', expand=True)

    def fillConfiguration(self, configs):
        c = 0
        for i in configs.keys():
            cur = VerticalScrolledFrame(self.page1)
            self.page1.add(cur)
            self.page1.tab(c, text=i)
            curr = tkinter.Frame(cur.interior)
            curr.pack(side="top", fill="both", expand=1)
            c1 = 0
            for x in configs[i]:
                l = ttk.Label(curr, text=configutils.getValue(configs[i][x], configutils.name))
                l.grid(row=c1, sticky=tkinter.W)
                types = configutils.getValue(configs[i][x], configutils.types)
                value = configutils.getValue(configs[i][x], configutils.value)
                choices = configutils.getChoices(types)
                if types == configutils.yesno:
                    v = tkinter.IntVar()
                    if configutils.parseBoolean(value) == True:
                        v.set(1)
                    elif configutils.parseBoolean(value) == False:
                        v.set(2)
                    r = ttk.Radiobutton(curr, text="Yes", variable=v, value=1)
                    r.grid(row=c1, column=1)
                    r2 = ttk.Radiobutton(curr, text="No", variable=v, value=2)
                    r2.grid(row=c1, column=2)
                elif choices != None and len(choices) > 0:
                    cb = ttk.Combobox(curr)
                    cb.grid(row=c1, column=1)
                    cb.config(values=choices, state="readonly")
                    cb.set(value)
                elif types == configutils.filename:
                    e = ttk.Entry(curr)
                    e.grid(row=c1, column=1)
                    e.insert(0, value)
                    b = ttk.Button(curr, text="...")
                    b.grid(row=c1, column=2)
                else:
                    e = ttk.Entry(curr)
                    e.grid(row=c1, column=1)
                    e.insert(0, value)
                c1 = c1 + 1
            c = c + 1
