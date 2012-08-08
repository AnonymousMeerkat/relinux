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
from relinux.__main__ import exitprog


threadname = "GUI"
tn = logger.genTN(threadname)
bg = "#383635"
lightbg = "#656260"
lightbghover = "#807b79"
anims = True

normalc = (140, 200, 255)
hoverc = (255, 150, 150)
clickc = (255, 0, 0)


def _rgbtohex(rgb):
    return '#%02x%02x%02x' % rgb


def _setDefault(lists, **kw):
    for i in kw.keys():
        if not i in lists:
            lists[i] = kw[i]

def _setPixel(obj, pixel, x, y, color):
    if obj.busy:
        _setPixel(obj, pixel, x, y, color)
    obj.coords(pixel, x, y, x + 1, y + 1)
    obj.itemconfig(pixel, fill=color)

def _getPixel(obj, x, y, color):
    return obj.create_line(x, y, x + 1, y + 1, fill=color)

# Rectangle Renderer for the Glowy theme
class GlowyRectangleRenderer(threading.Thread):
    def __init__(self, obj):
        threading.Thread.__init__(self)
        self.obj = obj
        self.startme = normalc
        self.delta = 0
        self.time = time.time()
        self.stopme = False
    
    def stop(self):
        self.stopme = True

    def _gradientSC(self, color1, color2, percent):
        col1 = float(float(color1) / 255)
        col2 = float(float(color2) / 255)
        if percent > 1:
            percent = 1.0
        ans = col1 - ((col1 - col2) * percent)
        fans = int(ans * 255)
        if fans > 255:
            fans = 255
        if fans < 0:
            fans = 0
        return fans

    def _gradient(self, rgb1, rgb2, percent):
        r1, g1, b1 = rgb1
        r2, g2, b2 = rgb2
        return (self._gradientSC(r1, r2, percent), self._gradientSC(g1, g2, percent),
                self._gradientSC(b1, b2, percent))

    def _getDelta(self):
        thistime = time.time()
        self.delta = thistime - self.time
        self.time = thistime

    def run(self):
        if not anims:
            self.obj.anim = 1.0
        self.loop()
    
    def loop(self):
        if self.stopme:
            return
        self._getDelta()
        color = normalc
        if self.obj.clicking:
            if self.obj.anim <= 0.0:
                self.startme = copy.copy(self.obj.lastcolor)
            color = self._gradient(self.startme, clickc, self.obj.anim)
            self.obj.lastcolor = color
            self._line(color)
            return
        elif self.obj.hovering:
            if self.obj.anim <= 0.0:
                self.startme = copy.copy(self.obj.lastcolor)
            color = self._gradient(self.startme, hoverc, self.obj.anim)
            self.obj.lastcolor = color
            self._line(color)
            return
        else:
            if self.obj.anim <= 0.0:
                self.startme = copy.copy(self.obj.lastcolor)
            color = self._gradient(self.startme, normalc, self.obj.anim)
            self.obj.lastcolor = color
            self._line(color)
            return
    
    def _line(self, color):
        if self.stopme:
            return
        start = (0, 0, 0)
        for i in range(0, self.obj.width):
            percent = float((float(i) / float(self.obj.width)))
            _setPixel(self.obj, self.obj.c_bottom[i], i, self.obj.height - 1,
                               _rgbtohex(self._gradient(start, color, percent)))
        for i in range(0, self.obj.height):
            percent = float((float(i) / float(self.obj.height)))
            _setPixel(self.obj, self.obj.c_right[i], self.obj.width - 1, i,
                               _rgbtohex(self._gradient(start, color, percent)))
        self.obj.coords(self.obj.c_left, 0, 0, 0, self.obj.height)
        self.obj.coords(self.obj.c_top, 0, 0, self.obj.width, 0)
        self.obj.itemconfig(self.obj.c_left, fill=_rgbtohex(start))
        self.obj.itemconfig(self.obj.c_top, fill=_rgbtohex(start))
        willloop = False
        if self.obj.anim < 1.0 and not self.stopme:
            self.obj.anim = self.obj.anim + (0.1 * float((float(self.delta) * 100)))
            #time.sleep(float(float(1000 / 100) / 1000))
            willloop = True
        if willloop and not self.stopme:
            self.loop()
        else:
            if self.obj.finishrenderingcmd != None:
                self.obj.finishrenderingcmd()


# Glowy button
class Button(Tkinter.Canvas):
    def __init__(self, parent, *args, **kw):
        self.command = None
        textset = False
        bindclick = True
        bindunclick = True
        self.mousedown = None
        if "command" in kw.keys():
            self.command = kw["command"]
            del(kw["command"])
        if "text" in kw.keys():
            textset = kw["text"]
            del(kw["text"])
        if "bindclick" in kw.keys():
            bindclick = kw["bindclick"]
            del(kw["bindclick"])
        if "bindunclick" in kw.keys():
            bindunclick = kw["bindunclick"]
            del(kw["bindunclick"])
        if "mousedown" in kw.keys():
            self.mousedown = kw["mousedown"]
            del(kw["mousedown"])
        _setDefault(kw, background=bg, borderwidth=0, highlightthickness=0)
        Tkinter.Canvas.__init__(self, parent, *args, **kw)
        label = Tkinter.Label(self, text="Unused")
        self.font = tkFont.Font(font=label["font"])
        self.height = 0
        self.width = 0
        self.hovering = False
        self.anim = 1.0
        self.clicking = False
        self.commandvalid = False
        self.text = "hi"
        self.c_text = self.create_text(self.width / 2, self.height / 2, text=self.text,
                                 font=self.font, fill="white")
        self.c_top = self.create_line(0, 0, 0, self.height, fill="#000")
        self.c_left = self.create_line(0, 0, self.width, 0, fill="#000")
        self.c_bottom = []
        self.c_right = []
        self.setHeight(self.font.actual("size") * -1 + 8)
        self.setWidth(self.width)
        self.bind("<Enter>", self.hoveringtrue)
        self.bind("<Leave>", self.hoveringfalse)
        self.finishrenderingcmd = None
        self.busy = False
        if bindclick:
            self.bind("<ButtonPress-1>", self.onclick)
        if bindunclick:
            self.bind("<ButtonRelease-1>", self.onunclick)
        self.lastcolor = (0, 0, 0)
        self.currrenderer = None
        if textset == False:
            self.setText("")
        else:
            self.setText(textset)
        self.render()
    
    def __del__(self):
        self.currrenderer.stop()
        self.busy = False

    def render(self, linesonly=False):
        currr = self.currrenderer != None and self.currrenderer.isAlive()
        if currr:
            self.currrenderer.stop()
            #self.currrenderer.join()
        if not linesonly:
            #self.create_rectangle(0, 0, self.width, self.height, fill=bg)
            #self.create_text((self.width) / 2, (self.height) / 2, text=self.text,
            #                     font=self.font, fill="white")
            self.coords(self.c_text, (self.width) / 2, (self.height) / 2)
            self.itemconfig(self.c_text, text=self.text, font=self.font, fill="white")
        self.currrenderer = GlowyRectangleRenderer(self)
        self.currrenderer.start()
    
    def setWidth(self, width):
        self.busy = True
        orig = self.width
        rrange = range(orig, width)
        inverted = False
        if width - orig < 0:
            rrange = range(width, orig)
            inverted = True
        self.width = width
        self.config(width=width)
        _updwidth = self.config()["width"]
        updwidth = _updwidth[len(_updwidth) - 1]
        if int(updwidth) != self.width:
            logger.logE(tn, "Width was not able to be updated! " + str(updwidth) + " " + 
                        str(self.width))
        self.coords(self.c_top, 0, 0, width, 0)
        if inverted:
            for i in reversed(rrange):
                self.delete(self.c_bottom.pop(i))
        else:
            for i in rrange:
                self.c_bottom.append(_getPixel(self, i, self.height - 1, "#000"))
        if self.width != len(self.c_bottom):
            logger.logW(tn, "Width was not able to be updated! " + len(self.c_bottom) + " " + 
                        str(self.width))
        self.busy = False
    
    def setHeight(self, height):
        self.busy = True
        orig = self.height
        rrange = range(orig, height)
        inverted = False
        if height - orig < 0:
            rrange = range(height, orig)
            inverted = True
        self.height = height
        self.config(height=height)
        self.coords(self.c_left, 0, 0, 0, height)
        if inverted:
            for i in reversed(rrange):
                self.delete(self.c_right.pop(i))
        else:
            for i in rrange:
                self.c_right.append(_getPixel(self, self.width - 1, i, "#000"))
        self.busy = False

    def setText(self, text):
        if self.currrenderer != None and self.currrenderer.isAlive():
            self.currrenderer.stop()
        self.setWidth(self.tk.call("font", "measure", tkFont.NORMAL, "-displayof", self, text) + 12)
        self.setHeight(self.height)
        self.text = text
        self.render()
    
    def hoveringtrue(self, event):
        self.anim = 0.0
        self.hovering = True
        self.commandvalid = True
        self.render(True)
    
    def hoveringfalse(self, event):
        self.anim = 0.0
        self.hovering = False
        self.commandvalid = False
        self.render(True)
    
    def onclick(self, event):
        self.anim = 1.0
        self.clicking = True
        self.render(True)
        if self.mousedown != None:
            self.mousedown()
    
    def onunclick(self, event):
        self.anim = 0.0
        self.clicking = False
        self.render(True)
        if self.command != None and self.commandvalid:
            self.command()


# Temporary Entry Box
class Entry(Tkinter.Entry):
    def __init__(self, parent, *args, **kw):
        _setDefault(kw, background=bg, foreground="white", selectbackground="white",
                    selectforeground=bg, borderwidth=0, highlightbackground=_rgbtohex(normalc),
                    highlightcolor=_rgbtohex(hoverc))
        Tkinter.Entry.__init__(self, parent, *args, **kw)


# Temporary Label
class Label(Tkinter.Label):
    def __init__(self, parent, *args, **kw):
        _setDefault(kw, background=bg, foreground="white", borderwidth=0,
                    highlightbackground=_rgbtohex(normalc), highlightcolor=_rgbtohex(hoverc))
        Tkinter.Label.__init__(self, parent, *args, **kw)


# Temporary Scrollbar
class GScrollbar(Tkinter.Scrollbar):
    def __init__(self, parent, *args, **kw):
        _setDefault(kw, background=lightbg, borderwidth=0, relief=Tkinter.FLAT,
                    activebackground=lightbghover, troughcolor=bg)
        Tkinter.Scrollbar.__init__(self, parent, *args, **kw)


# Temporary Combobox
class Combobox(Tkinter.OptionMenu):
    def __init__(self, parent, choices):
        self.current = Tkinter.StringVar()
        self.choices = choices
        Tkinter.OptionMenu.__init__(self, parent, self.current, *self.choices)
        self.config(background=bg, foreground="white", borderwidth=0,
                    highlightthickness=1, relief=Tkinter.FLAT, highlightbackground=_rgbtohex(normalc),
                    padx=2, pady=2, activebackground=bg, activeforeground="white")
        self["menu"].config(background="white", foreground=bg, borderwidth=0,
                            activebackground=bg, activeforeground="white", relief=Tkinter.FLAT)
        self.bind("<Enter>", self.hoveringtrue)
        self.bind("<Leave>", self.hoveringfalse)
    
    def set(self, value):
        self.current.set(value)
    
    def hoveringtrue(self, *args):
        self.config(highlightbackground=_rgbtohex(hoverc))
    
    def hoveringfalse(self, *args):
        self.config(highlightbackground=_rgbtohex(normalc))


# Glowy Radiobutton (based on the Glowy Button)
class Radiobutton(Button):
    def __init__(self, parent, *args, **kw):
        self.variable = kw.pop("variable", None)
        self.value = kw.pop("value", 0)
        _setDefault(kw, bindunclick=False, mousedown=self.select)
        Button.__init__(self, parent, *args, **kw)
        self.finishrenderingcmd = self.finishrendering
        self.render()
        self.notfirst = False

    def select(self):
        self.variable.set(self.value)
    
    def finishrendering(self):
        if not self.notfirst:
            self._callback()
            self.variable.trace("w", self._callback)
            self.notfirst = True
            self.finishrenderingcmd = None

    def _callback(self, *args):
        if self.variable.get() == self.value:
            self.clicking = True
            self.render(True)
        else:
            self.clicking = False
            self.render(True)


# Glowy Notebook
class Notebook(Tkinter.Frame):
    def __init__(self, master=None, *args, **kw):
        self.master = master
        self.pages = []
        self.current = Tkinter.IntVar()
        self.current.set(0)
        self.old = 0
        npages = kw.pop('npages', 0)
        _setDefault(kw, background=bg, borderwidth=0, highlightthickness=0)
        Tkinter.Frame.__init__(self, master, *args, **kw)
        if npages > 0:
            for page in range(npages):
                self.add_empty_page()
            self.pages[self.current.get()].pack(fill='both', expand=1)
            self._tab_buttons()
        self.current.trace("w", self._select)

    def _tab_buttons(self):
        # Place tab buttons on the pages
        #for indx, child in enumerate(self.pages):
            if hasattr(self, "btnframe"):
                self.btnframe.pack_forget()
            self.btnframe = Tkinter.Frame(self, background=bg, borderwidth=0, highlightthickness=0)
            self.btnframe.pack(side="top", fill="x", padx=6, pady=6)
            for indx1, child1 in enumerate(self.pages):
                btn = Radiobutton(self.btnframe, variable=self.current, value=indx1, text=child1.text)
                btn.grid(row=0, column=indx1)
            '''nextbtn = Button(child.btnframe, text=_("Next"), command=self._select)
            nextbtn.pack(side="right", anchor="e", padx=6)
            quitbtn = Button(child.btnframe, text=_("Quit"), command=self.close)
            quitbtn.pack(side="left", anchor="w", padx=6)
            if indx > 0:
                prevbtn = Button(child.btnframe, text=_("Previous"),
                    command=self._select)
                prevbtn.pack(side="right", anchor="e", padx=6)
                if indx == len(self.pages) - 1:
                    nextbtn.setText("Finish")
                    nextbtn.command = self.close'''
    
    def _select(self, *args):
        self.pages[self.old].pack_forget()
        self.old = self.current.get()
        self.pages[self.current.get()].pack(fill=Tkinter.BOTH, expand=Tkinter.TRUE)

    def close(self):
        self.master.destroy()

    def add_empty_page(self):
        self.pages.append(Tkinter.Frame(self, background=bg, borderwidth=0, highlightthickness=0, relief=Tkinter.FLAT))
        self.pages[len(self.pages) - 1].text = ""

    def add_tab(self):
        self.add_empty_page()
        self._tab_buttons()
        return (len(self.pages) - 1)

    def add_page_body(self, tab_id, title, body):
        #self.tab(tab_id, text=title)
        self.pages[tab_id].text = title
        self._tab_buttons()
        body.pack(side=Tkinter.TOP, fill=Tkinter.BOTH, expand=Tkinter.TRUE)
        self.current.set(0)

    def page(self, page_num):
        if page_num < len(self.pages):
            return self.pages[page_num]
        else:
            logger.logE(tn, _("Page") + " " + str(page_num) + " " + _("does not exist"))


# Scrolling frame, based on http://Tkinter.unpy.net/wiki/VerticalScrolledFrame
class VerticalScrolledFrame(Tkinter.Frame):
    def __init__(self, parent, *args, **kw):
        _setDefault(kw, background=bg, borderwidth=0, highlightthickness=0, relief=Tkinter.FLAT)
        Tkinter.Frame.__init__(self, parent, *args, **kw)
        vscrollbar = GScrollbar(self, orient=Tkinter.VERTICAL)
        vscrollbar.pack(fill=Tkinter.Y, side=Tkinter.RIGHT, expand=Tkinter.FALSE)
        canvas = Tkinter.Canvas(self, kw, yscrollcommand=vscrollbar.set)
        canvas.pack(side=Tkinter.LEFT, fill=Tkinter.BOTH, expand=Tkinter.TRUE)
        vscrollbar.config(command=canvas.yview)
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)
        self.interior = interior = Tkinter.Frame(canvas, kw)
        interior.pack(fill=Tkinter.BOTH, expand=Tkinter.TRUE)
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


'''class About:
    def __init__(self, master):
        top = self.top = Tkinter.Toplevel(master, background=config.background)
        top.title(config.product + " - " + _("About"))
        w = Tkinter.Label(top, text=config.about_string)
        w.pack(side=Tkinter.TOP, fill=Tkinter.BOTH, expand=True)
        b = Tkinter.Button(top, text=_("Close"), command=top.destroy)
        b.pack(side=Tkinter.BOTTOM)'''


class Wizard(Tkinter.Frame):
    def on_change_tab(self, *args):
        w = self.select()
        self.current = self.index(w)

    def __init__(self, master=None, *args, **kw):
        self.master = master
        self.pages = []
        self.current = 0
        npages = kw.pop('npages', 3)
        _setDefault(kw, background=bg, borderwidth=0, highlightthickness=0)
        Tkinter.Frame.__init__(self, master, *args, **kw)
        for page in range(npages):
            logger.logVV(tn, _("Creating page") + " " + str(page))
            self.add_empty_page()
        self.pages[0].pack(fill='both', expand=1)
        self._wizard_buttons()
        self.bind("<<NotebookTabChanged>>", self.on_change_tab)

    def _wizard_buttons(self):
        # Place wizard buttons on the pages
        for indx, child in enumerate(self.pages):
            if hasattr(child, "btnframe"):
                child.btnframe.pack_forget()
            child.btnframe = Tkinter.Frame(child, background=bg, borderwidth=0, highlightthickness=0)
            child.btnframe.pack(side="bottom", fill="x", padx=6, pady=12)
            nextbtn = Button(child.btnframe, text=_("Next"), command=self.next_page)
            nextbtn.pack(side="right", anchor="e", padx=6)
            quitbtn = Button(child.btnframe, text=_("Quit"), command=self.close)
            quitbtn.pack(side="left", anchor="w", padx=6)
            if indx > 0:
                prevbtn = Button(child.btnframe, text=_("Previous"),
                    command=self.prev_page)
                prevbtn.pack(side="right", anchor="e", padx=6)
                if indx == len(self.pages) - 1:
                    nextbtn.setText("Finish")
                    nextbtn.command = self.close
            '''progressframe = Tkinter.Frame(child)
            progressframe.pack(side="bottom", fill="x", padx=6)
            progress = ttk.Progressbar(progressframe)
            progress.pack(fill="x")'''
    
    def _switch_page(self, current):
        self.pages[self.current].pack_forget()
        self.current = current
        self.pages[self.current].pack(fill='both', expand=1)

    def next_page(self):
        if self.current == len(self.pages):
            return
        self._switch_page(self.current + 1)

    def prev_page(self):
        if self.current == 0:
            return
        self._switch_page(self.current - 1)

    def close(self):
        #self.master.destroy()
        exitprog()

    def add_empty_page(self):
        self.pages.append(Tkinter.Frame(self, background=bg, borderwidth=0, highlightthickness=0))

    def add_tab(self):
        self.add_empty_page()
        self._wizard_buttons()
        return (len(self.pages) - 1)

    def add_page_body(self, tab_id, title, body):
        #self.tab(tab_id, text=title)
        body.pack(side='top', fill='both', padx=6, pady=12, expand=1)

    def page(self, page_num):
        if page_num < len(self.pages):
            return self.pages[page_num]
        else:
            logger.logE(tn, _("Page") + " " + str(page_num) + " " + _("does not exist"))


class FileSelector(Tkinter.Frame):
    def __init__(self, *args, **kw):
        if not "background" in kw.keys():
            kw["background"] = bg
        if not "borderwidth" in kw.keys():
            kw["borderwidth"] = 0
        if not "highlightthickness" in kw.keys():
            kw["highlightthickness"] = 0
        Tkinter.Frame.__init__(self, *args, **kw)
        self.entry = Entry(self)
        self.button = Button(self, text="...", command=self._on_button)
        self.button.grid(row=0, column=1)
        self.entry.grid(row=0, column=0)

    def _on_button(self):
        s = tkFileDialog.askopenfilename()
        if s != "":
            self.entry.delete(0, "end")
            self.entry.insert(0, s)


class YesNo(Tkinter.Frame):
    def __init__(self, *args, **kw):
        _setDefault(kw, background=bg, borderwidth=0, highlightthickness=0)
        Tkinter.Frame.__init__(self, *args, **kw)
        self.v = Tkinter.IntVar()
        self.y = Radiobutton(self, text=_("Yes"), variable=self.v, value=1)
        self.y.grid(row=0, column=0)
        self.n = Radiobutton(self, text=_("No"), variable=self.v, value=2)
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
    def __init__(self, parent, choices, *args, **kw):
        _setDefault(kw, background=bg, borderwidth=0, highlightthickness=0)
        Tkinter.Frame.__init__(self, parent, *args, **kw)
        self.cb = Combobox(self, choices)
        self.entry = Entry(self)
        self.cb.grid(row=0, column=0)
        self.cb.bind("<<ComboboxSelected>>", self._on_changed)

    def _on_changed(self, event):
        if self.cb.get() == configutils.custom:
            self.entry.grid(row=1, column=0)
        else:
            self.entry.grid_remove()


class Multiple(Tkinter.Frame):
    def __init__(self, *args, **kw):
        _setDefault(kw, background=bg, borderwidth=0, highlightthickness=0)
        Tkinter.Frame.__init__(self, *args, **kw)
        self.entries = []
        self.pluses = []
        self.minuses = []
        self.addEntry(0)

    def addEntry(self, row):
        self.entries.insert(row, Entry(self))
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
        self.wizard = Wizard(self.root, npages=2)
        self.wizard.master.minsize(400, 350)
        self.wizard.master.maxsize(800, 700)
        self.page1 = Notebook(self.wizard.page(1))
        self.page0 = Label(self.wizard.page(0), text=_("Welcome to relinux 0.4!\nClick on next to get started"))
        self.wizard.add_page_body(0, _("Welcome"), self.page0)
        self.wizard.add_page_body(1, _("Configure"), self.page1)
        self.wizard.add_tab()
        self.page2 = Tkinter.Frame(self.wizard.page(2), background=bg, borderwidth=0, highlightthickness=0)
        Label(self.page2, text="          ").pack()
        Button(self.page2, text="Test").pack()
        self.wizard.add_page_body(2, _("Page 3"), self.page2)
        self.wizard.add_tab()
        self.page3 = Notebook(self.wizard.page(3), npages=1)
        #self.page3.add_tab()
        #self.page3.add_tab(Tkinter.Frame(self.page3, background=bg, borderwidth=0, highlightthickness=0), "hello")
        self.page3.add_page_body(0, "test", Label(self.page3.page(0), text="test"))
        self.page3.add_tab()
        self.page3.add_page_body(1, "test1", Label(self.page3.page(1), text="test1"))
        self.wizard.add_page_body(3, _("Page 4"), self.page3)
        self.wizard.pack(fill="both", expand=True)

    def fillConfiguration(self, configs):
        c = 0
        for i in configs.keys():
            cur = Tkinter.Frame(self.page1)
            ids = self.page1.add_tab()
            self.page1.add_page_body(ids, i, cur)
            #self.page1.add(cur)
            #self.page1.tab(c, text=i)
            #curr = Tkinter.Frame(cur.interior)
            #curr.pack(side="top", fill="both", expand=1)
            secs = Notebook(cur)
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
                        curr = subtabs[category].interior
                if found is False:
                    ids = secs.add_tab()
                    frame = VerticalScrolledFrame(secs.page(ids), background=bg, borderwidth=0,
                                                  highlightthickness=0)
                    subtabs[category] = frame
                    secs.add_page_body(ids, category, subtabs[category])
                    #secs.tab(subtabs[category], text=category)
                    curr = subtabs[category].interior
                l = Label(curr, text=configutils.getValueP(configs[i][x],
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
                    cb = Choice(curr, choices)
                    cb.grid(row=c1, column=1)
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
                    e = Entry(curr)
                    e.grid(row=c1, column=1)
                    e.delete(0, "end")
                    e.insert(0, value)
                c1 = c1 + 1
            c = c + 1
