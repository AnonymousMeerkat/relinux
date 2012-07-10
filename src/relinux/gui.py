'''
Anything GUI-related goes here
@author: Anonymous Meerkat
'''

from tkinter import ttk
from tkinter import filedialog
import tkinter
from relinux import config, configutils, logger


threadname = "GUI"
tn = logger.genTN(threadname)


# Scrolling frame, source: http://tkinter.unpy.net/wiki/VerticalScrolledFrame
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
        top.title(config.product + " - " + _("About"))
        w = tkinter.Label(top, text=config.about_string)
        w.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
        b = tkinter.Button(top, text=_("Close"), command=top.destroy)
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
            logger.logVV(tn, _("Creating page") + " " + str(page))
            self.add_empty_page()

        self.current = 0
        self._wizard_buttons()
        self.bind("<<NotebookTabChanged>>", self.on_change_tab)

    def _wizard_buttons(self):
        # Place wizard buttons on the pages
        for indx, child in self._children.items():
            if hasattr(child, "btnframe"):
                child.btnframe.pack_forget()
            child.btnframe = tkinter.Frame(child)
            child.btnframe.pack(side="bottom", fill="x", padx=6, pady=12)
            nextbtn = tkinter.Button(child.btnframe, text=_("Next"), command=self.next_page)
            nextbtn.pack(side="right", anchor="e", padx=6)
            quitbtn = tkinter.Button(child.btnframe, text=_("Quit"), command=self.close)
            quitbtn.pack(side="left", anchor="w", padx=6)
            if indx > 0:
                prevbtn = tkinter.Button(child.btnframe, text=_("Previous"),
                    command=self.prev_page)
                prevbtn.pack(side="right", anchor="e", padx=6)
                if indx == len(self._children) - 1:
                    nextbtn.configure(text=_("Finish"), command=self.close)
            '''progressframe = tkinter.Frame(child)
            progressframe.pack(side="bottom", fill="x", padx=6)
            progress = ttk.Progressbar(progressframe)
            progress.pack(fill="x")'''

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

    def add_tab(self):
        self.add_empty_page()
        self._wizard_buttons()
        return (len(self._children) - 1)

    def add_page_body(self, tab_id, title, body):
        self.tab(tab_id, text=title)
        body.pack(side='top', fill='both', padx=6, pady=12, expand=1)

    def page_container(self, page_num):
        if page_num in self._children:
            return self._children[page_num]
        else:
            logger.logE(tn, _("Page") + " " + str(page_num) + " " + _("does not exist"))

    def _get_current(self):
        return self._current

    def _set_current(self, curr):
        if curr not in self._children:
            logger.logE(tn, _("Page") + " " + curr + " " + _("does not exist"))
        self._current = curr
        self.select(self._children[self._current])

    current = property(_get_current, _set_current)


class FileSelector(tkinter.Frame):
    def __init__(self, *args, **kwargs):
        tkinter.Frame.__init__(self, *args, **kwargs)
        self.entry = tkinter.Entry(self)
        self.button = tkinter.Button(self, text="...",  command=self._on_button)
        self.button.grid(row=0, column=1)
        self.entry.grid(row=0, column=0)

    def _on_button(self):
        s = filedialog.askopenfilename()
        if s != "":
            self.entry.delete(0, "end")
            self.entry.insert(0, s)


class YesNo(tkinter.Frame):
    def __init__(self, *args, **kwargs):
        tkinter.Frame.__init__(self, *args, **kwargs)
        self.v = tkinter.IntVar()
        self.y = tkinter.Radiobutton(self, text=_("Yes"), variable=self.v, value=1)
        self.y.grid(row=0, column=0)
        self.n = tkinter.Radiobutton(self, text=_("No"), variable=self.v, value=2)
        self.n.grid(row=0, column=1)

    def set(self, bools):
        if bools is True:
            self.v.set(1)
        elif bools is False:
            self.v.set(2)
        else:
            self.v.set(0)

    def get(self):
        if self.v.get() == 1:
            return True
        elif self.v.get() == 2:
            return False
        else:
            return None


class Choice(tkinter.Frame):
    def __init__(self, *args, **kwargs):
        tkinter.Frame.__init__(self, *args, **kwargs)
        self.cb = ttk.Combobox(self)
        self.entry = tkinter.Entry(self)
        self.cb.grid(row=0, column=0)
        self.cb.bind("<<ComboboxSelected>>", self._on_changed)

    def _on_changed(self, event):
        if self.cb.get() == configutils.custom:
            self.entry.grid(row=1, column=0)
        else:
            self.entry.grid_remove()


class Multiple(tkinter.Frame):
    def __init__(self, *args, **kwargs):
        tkinter.Frame.__init__(self, *args, **kwargs)
        self.entries = []
        self.pluses = []
        self.minuses = []
        self.addEntry(0)

    def addEntry(self, row):
        self.entries.insert(row, tkinter.Entry(self))
        self.pluses.insert(row, tkinter.Button(self, text="+", foreground="darkgreen", command=lambda: self._plus(row)))
        self.minuses.insert(row, tkinter.Button(self, text="-", foreground="darkred", command=lambda: self._minus(row)))
        self.entries[row].grid(row=row, column=0)
        self.minuses[row].grid(row=row, column=1)
        self.pluses[row].grid(row=row, column=2)
        self._rePack()

    def remEntry(self, row):
        self.entries[row].grid_remove()
        self.minuses[row].grid_remove()
        self.pluses[row].grid_remove()
        del(self.entries[row])
        del(self.minuses[row])
        del(self.pluses[row])
        self._rePack()

    def set(self, arr):
        for i in list(range(len(self.entries))):
            self.remEntry(i)
        if len(arr) > 0:
            for i in list(range(len(arr))):
                self.addEntry(i)
                self.entries[i].delete(0, "end")
                self.entries[i].insert(0, arr[i])
        else:
            self.addEntry(0)

    def _plus(self, row):
        self.addEntry(row + 1)

    def _minus(self, row):
        self.remEntry(row)

    def __rePack(self, c):
        self.pluses[c].config(command=lambda: self._plus(c))
        self.minuses[c].config(command=lambda: self._minus(c))
        self.entries[c].grid(row=c, column=0)
        self.minuses[c].grid(row=c, column=1)
        self.pluses[c].grid(row=c, column=2)

    def _rePack(self):
        for c in list(range(len(self.entries))):
            self.__rePack(c)


class GUI:
    def __init__(self, master):
        self.root = master
        self.root.title(config.product)
        self.wizard = Wizard(npages=2)
        self.wizard.master.minsize(400, 350)
        self.wizard.master.maxsize(800, 700)
        self.page1 = ttk.Notebook(self.wizard.page_container(1))
        self.page0 = tkinter.Label(self.wizard.page_container(0), text=_("Welcome to relinux 0.4!\nClick on next to get started"))
        self.wizard.add_page_body(0, _("Welcome"), self.page0)
        self.wizard.add_page_body(1, _("Configure"), self.page1)
        self.wizard.add_tab()
        self.page2 = tkinter.Label(self.wizard.page_container(2), text=_("Page 3"))
        self.wizard.add_page_body(2, _("Page 3"), self.page2)
        self.wizard.pack(fill="both", expand=True)

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
                l = tkinter.Label(curr, text=configutils.getValue(configs[i][x], configutils.name))
                l.grid(row=c1, sticky=tkinter.W)
                types = configutils.getValue(configs[i][x], configutils.types)
                value = configutils.getValue(configs[i][x], configutils.value)
                choices = configutils.getChoices(types)
                multiple = configutils.getMultipleValues(value)
                if types == configutils.yesno:
                    #v = tkinter.IntVar()
                    #r = ttk.Radiobutton(curr, text="Yes", variable=v, value=1)
                    #r.grid(row=c1, column=1)
                    #r2 = ttk.Radiobutton(curr, text="No", variable=v, value=2)
                    #r2.grid(row=c1, column=2)
                    r = YesNo(curr)
                    r.grid(row=c1, column=1)
                    r.set(configutils.parseBoolean(value))
                elif choices is not None and len(choices) > 0:
                    cb = Choice(curr)
                    cb.grid(row=c1, column=1)
                    cb.cb.config(values=choices, state="readonly")
                    cb.cb.set(value)
                elif types == configutils.filename:
                    e = FileSelector(curr)
                    e.grid(row=c1, column=1)
                    e.entry.delete(0, "end")
                    e.entry.insert(0, value)
                elif types == configutils.multiple:
                    e = Multiple(curr)
                    e.grid(row=c1, column=1)
                    e.set(multiple)
                else:
                    e = tkinter.Entry(curr)
                    e.grid(row=c1, column=1)
                    e.delete(0, "end")
                    e.insert(0, value)
                c1 = c1 + 1
            c = c + 1
