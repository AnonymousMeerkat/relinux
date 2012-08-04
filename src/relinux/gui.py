'''
Anything GUI-related goes here
@author: Anonymous Meerkat
'''

import Tkinter
import tkFileDialog
import ttk
import tkFont
import time
import threading
import copy
from relinux import config, configutils, logger


threadname = "GUI"
tn = logger.genTN(threadname)
bg = "#383635"


# Scrolling frame, source: http://Tkinter.unpy.net/wiki/VerticalScrolledFrame
class VerticalScrolledFrame(Tkinter.Frame):
    def __init__(self, parent, *args, **kw):
        Tkinter.Frame.__init__(self, parent, *args, **kw)
        vscrollbar = Tkinter.Scrollbar(self, orient=Tkinter.VERTICAL)
        vscrollbar.pack(fill=Tkinter.Y, side=Tkinter.RIGHT, expand=Tkinter.FALSE)
        canvas = Tkinter.Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        canvas.pack(side=Tkinter.LEFT, fill=Tkinter.BOTH, expand=Tkinter.TRUE)
        vscrollbar.config(command=canvas.yview)
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)
        self.interior = interior = Tkinter.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=Tkinter.NW)

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


class renderer(threading.Thread):
    def __init__(self, obj, hover=False):
        threading.Thread.__init__(self)
        self.obj = obj
        self.hover = hover
        self.normalc = (140, 200, 255)
        self.hoverc = (255, 150, 150)
        self.clickc = (255, 0, 0)
        self.startme = self.normalc
        self.delta = 0
        self.time = time.time()

    def _drawPixel(self, x, y, color):
        self.obj.create_line(x, y, x + 1, y + 1, fill=color)

    def _gradientSC(self, color1, color2, percent):
        col1 = float(float(color1) / 255)
        col2 = float(float(color2) / 255)
        ans = col1 - ((col1 - col2) * percent)
        fans = int(ans * 255)
        if fans > 255:
            fans = 255
        return fans

    def _gradient(self, rgb1, rgb2, percent):
        r1, g1, b1 = rgb1
        r2, g2, b2 = rgb2
        return (self._gradientSC(r1, r2, percent), self._gradientSC(g1, g2, percent),
                self._gradientSC(b1, b2, percent))

    def _rgbtohex(self, rgb):
        return '#%02x%02x%02x' % rgb

    def _getDelta(self):
        thistime = time.time()
        self.delta = thistime - self.time
        self.time = thistime

    def run(self):
        if self.hover:
            self.line()
            return
        self._getDelta()
        self.obj.create_rectangle(0, 0, self.obj.width, self.obj.height, fill=bg)
        self.obj.create_text((self.obj.width) / 2, (self.obj.height) / 2, text=self.obj.text,
                             font=tkFont.NORMAL, fill="white")
        self.line()
    
    def line(self):
        if self.hover:
            self._getDelta()
        start = (0, 0, 0)
        color = self.normalc
        if self.obj.hovering:
            if self.obj.anim <= 0.0:
                self.startme = copy.copy(self.obj.lastcolor)
            color = self._gradient(self.startme, self.hoverc, self.obj.anim)
            self.obj.lastcolor = color
        else:
            if self.obj.anim <= 0.0:
                self.startme = copy.copy(self.obj.lastcolor)
            color = self._gradient(self.startme, self.normalc, self.obj.anim)
            self.obj.lastcolor = color
        if self.obj.clicking:
            color = self.clickc
        for i in range(0, self.obj.width + 1):
            percent = float((float(i) / float(self.obj.width + 1)))
            self._drawPixel(i, self.obj.height, self._rgbtohex(self._gradient(start, color, percent)))
        for i in range(0, self.obj.height + 1):
            percent = float((float(i) / float(self.obj.height + 1)))
            self._drawPixel(self.obj.width, i, self._rgbtohex(self._gradient(start, color, percent)))
        self.obj.create_line(1, 1, 1, self.obj.height + 1, fill=self._rgbtohex(start))
        self.obj.create_line(1, 1, self.obj.width + 1, 1, fill=self._rgbtohex(start))
        if self.obj.anim < 1.0:
            self.obj.anim = self.obj.anim + (0.1 * float((float(self.delta) * 100)))
            #time.sleep(float(float(1000 / 100) / 1000))
            self.line()


# Custom button
class Button(Tkinter.Canvas):
    def __init__(self, parent, *args, **kw):
        self.command = None
        textset = False
        if "command" in kw.keys():
            self.command = kw["command"]
            del kw["command"]
        if "text" in kw.keys():
            textset = kw["text"]
            del kw["text"]
        Tkinter.Canvas.__init__(self, parent, *args, **kw)
        label = Tkinter.Label(self, text="Unused")
        self.height = tkFont.Font(font=label["font"]).actual("size") * -1 + 9
        self.width = 1
        self.hovering = False
        self.anim = 1.0
        self.clicking = False
        self.commandvalid = False
        self.bind("<Enter>", self.hoveringtrue)
        self.bind("<Leave>", self.hoveringfalse)
        self.bind("<ButtonPress-1>", self.onclick)
        self.bind("<ButtonRelease-1>", self.onunclick)
        self.lastcolor = (0, 0, 0)
        if textset == False:
            self.setText("")
        else:
            self.setText(textset)
        renderer(self).start()

    def setText(self, text):
        self.width = self.tk.call("font", "measure", tkFont.NORMAL, "-displayof", self, text) + 9
        self.config(width=(self.width + 2), height=self.height)
        self.text = text
    
    def hoveringtrue(self, event):
        self.anim = 0.0
        self.hovering = True
        self.commandvalid = True
        renderer(self, True).start()
    
    def hoveringfalse(self, event):
        self.anim = 0.0
        self.hovering = False
        self.commandvalid = False
        renderer(self, True).start()
    
    def onclick(self, event):
        self.clicking = True
        renderer(self, True).start()
    
    def onunclick(self, event):
        self.clicking = False
        renderer(self, True).start()
        if self.command != None and self.commandvalid:
            self.command()


class About:
    def __init__(self, master):
        top = self.top = Tkinter.Toplevel(master, background=config.background)
        top.title(config.product + " - " + _("About"))
        w = Tkinter.Label(top, text=config.about_string)
        w.pack(side=Tkinter.TOP, fill=Tkinter.BOTH, expand=True)
        b = Tkinter.Button(top, text=_("Close"), command=top.destroy)
        b.pack(side=Tkinter.BOTTOM)


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
            child.btnframe = Tkinter.Frame(child)
            child.btnframe.pack(side="bottom", fill="x", padx=6, pady=12)
            nextbtn = Button(child.btnframe, text=_("Next"), command=self.next_page)
            nextbtn.pack(side="right", anchor="e", padx=6)
            quitbtn = Button(child.btnframe, text=_("Quit"), command=self.close)
            quitbtn.pack(side="left", anchor="w", padx=6)
            if indx > 0:
                prevbtn = Button(child.btnframe, text=_("Previous"),
                    command=self.prev_page)
                prevbtn.pack(side="right", anchor="e", padx=6)
                if indx == len(self._children) - 1:
                    nextbtn.setText("Finish")
                    nextbtn.command = self.close
            '''progressframe = Tkinter.Frame(child)
            progressframe.pack(side="bottom", fill="x", padx=6)
            progress = ttk.Progressbar(progressframe)
            progress.pack(fill="x")'''

    def next_page(self):
        self.current += 1
        self.select(self.current)

    def prev_page(self):
        self.current -= 1
        self.select(self.current)

    def close(self):
        self.master.destroy()

    def add_empty_page(self):
        child = Tkinter.Frame(self)
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


class FileSelector(Tkinter.Frame):
    def __init__(self, *args, **kwargs):
        Tkinter.Frame.__init__(self, *args, **kwargs)
        self.entry = Tkinter.Entry(self)
        self.button = Button(self, text="...", command=self._on_button)
        self.button.grid(row=0, column=1)
        self.entry.grid(row=0, column=0)

    def _on_button(self):
        s = tkFileDialog.askopenfilename()
        if s != "":
            self.entry.delete(0, "end")
            self.entry.insert(0, s)


class YesNo(Tkinter.Frame):
    def __init__(self, *args, **kwargs):
        Tkinter.Frame.__init__(self, *args, **kwargs)
        self.v = Tkinter.IntVar()
        self.y = Tkinter.Radiobutton(self, text=_("Yes"), variable=self.v, value=1)
        self.y.grid(row=0, column=0)
        self.n = Tkinter.Radiobutton(self, text=_("No"), variable=self.v, value=2)
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


class Choice(Tkinter.Frame):
    def __init__(self, *args, **kwargs):
        Tkinter.Frame.__init__(self, *args, **kwargs)
        self.cb = ttk.Combobox(self)
        self.entry = Tkinter.Entry(self)
        self.cb.grid(row=0, column=0)
        self.cb.bind("<<ComboboxSelected>>", self._on_changed)

    def _on_changed(self, event):
        if self.cb.get() == configutils.custom:
            self.entry.grid(row=1, column=0)
        else:
            self.entry.grid_remove()


class Multiple(Tkinter.Frame):
    def __init__(self, *args, **kwargs):
        Tkinter.Frame.__init__(self, *args, **kwargs)
        self.entries = []
        self.pluses = []
        self.minuses = []
        self.addEntry(0)

    def addEntry(self, row):
        self.entries.insert(row, Tkinter.Entry(self))
        self.pluses.insert(row, Button(self, text="+", command=lambda: self._plus(row)))
        self.minuses.insert(row, Button(self, text="-", command=lambda: self._minus(row)))
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
        self.pluses[c].command = lambda: self._plus(c)
        self.minuses[c].command = lambda: self._minus(c)
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
        self.page0 = Tkinter.Label(self.wizard.page_container(0), text=_("Welcome to relinux 0.4!\nClick on next to get started"))
        self.wizard.add_page_body(0, _("Welcome"), self.page0)
        self.wizard.add_page_body(1, _("Configure"), self.page1)
        self.wizard.add_tab()
        self.page2 = Tkinter.Frame(self.wizard.page_container(2), background=bg)
        Button(self.page2, text="Test", background=bg, borderwidth=0, highlightbackground=bg).pack()
        self.wizard.add_page_body(2, _("Page 3"), self.page2)
        self.wizard.pack(fill="both", expand=True)

    def fillConfiguration(self, configs):
        c = 0
        for i in configs.keys():
            cur = VerticalScrolledFrame(self.page1)
            self.page1.add(cur)
            self.page1.tab(c, text=i)
            #curr = Tkinter.Frame(cur.interior)
            #curr.pack(side="top", fill="both", expand=1)
            secs = ttk.Notebook(cur.interior)
            secs.pack(side="top", fill="both", expand=1)
            c1 = 0
            subtabs = {}
            for x in configs[i]:
                curr = None
                category = configutils.getValueP(configs[i][x], configutils.category)
                found = False
                for y in subtabs.keys():
                    if y == category:
                        found = True
                        curr = subtabs[category]
                if found is False:
                    subtabs[category] = Tkinter.Frame(secs)
                    secs.add(subtabs[category])
                    secs.tab(subtabs[category], text=category)
                    curr = subtabs[category]
                l = Tkinter.Label(curr, text=configutils.getValueP(configs[i][x],
                                                                   configutils.name))
                l.grid(row=c1, sticky=Tkinter.W)
                types = configutils.getValueP(configs[i][x], configutils.types)
                value = configutils.getValueP(configs[i][x], configutils.value)
                choices = configutils.getChoices(types)
                multiple = configutils.getMultipleValues(value)
                if types == configutils.yesno:
                    #v = Tkinter.IntVar()
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
                    e = Tkinter.Entry(curr)
                    e.grid(row=c1, column=1)
                    e.delete(0, "end")
                    e.insert(0, value)
                c1 = c1 + 1
            c = c + 1
