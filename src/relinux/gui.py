'''
Anything GUI-related goes here
@author: Anonymous Meerkat
'''

from tkinter import ttk
import tkinter
from relinux import config


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

    def next_page(self):
        self.current += 1

    def prev_page(self):
        self.current -= 1

    def close(self):
        self.master.destroy()

    def add_empty_page(self):
        child = ttk.Frame(self)
        self._children[len(self._children)] = child
        self.add(child)

    def add_page_body(self, tab_id, title, body):
        self.tab(tab_id, text=title)
        body.pack(side='top', fill='both', padx=6, pady=12)

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
        page1 = tkinter.Frame(wizard.page_container(1))
        page0 = ttk.Label(wizard.page_container(0), text='Welcome to relinux 0.4!\nClick on next to get started')
        page2 = ttk.Label(wizard.page_container(2), text='Page 3')
        wizard.add_page_body(0, "Welcome", page0)
        wizard.add_page_body(1, "Configure", page1)
        wizard.add_page_body(2, "Page 3", page2)
        wizard.pack(fill='both', expand=True)
