# -*- coding: utf-8 -*-
'''
Anything GUI-related goes here
@author: Anonymous Meerkat
'''

from relinux import config, configutils, logger, utilities
if config.python3:
    import tkinter as Tkinter
    from tkinter import font as tkFont
    from tkinter import filedialog as tkFileDialog
else:
    import Tkinter
    import tkFileDialog
    import tkFont
    from PIL import Image, ImageTk
import time
import threading
import copy
import math
from relinux.__main__ import exitprog


threadname = "GUI"
tn = logger.genTN(threadname)
bg = "#383635"
#bg = "#fff"
#fg = "#000"
fg = "#fff"
lightbg = "#656260"
lightbghover = "#807b79"
lightbgclick = "#595655"
anims = True

normalc = (140, 200, 255)
hoverc = (255, 150, 150)
clickc = (255, 0, 0)


def _rgbtohex(rgb):
    return '#%02x%02x%02x' % rgb

def _setPixel(obj, pixel, x, y, color):
    if obj.busy:
        _setPixel(obj, pixel, x, y, color)
    try:
        obj.coords(pixel, x, y, x + 1, y + 1)
        obj.itemconfig(pixel, fill = color)
    except:
        raise

def _getPixel(obj, x, y, color):
    return obj.create_line(x, y, x + 1, y + 1, fill = color)

def _gradientSC(color1, color2, percent):
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

def _gradient(rgb1, rgb2, percent):
    r1, g1, b1 = rgb1
    r2, g2, b2 = rgb2
    return (_gradientSC(r1, r2, percent), _gradientSC(g1, g2, percent),
            _gradientSC(b1, b2, percent))

class FuncThread(threading.Thread):
    def __init__(self, target, ondie, *args):
        threading.Thread.__init__(self)
        self._target = target
        self._args = args
        self.ondie = ondie

    def run(self):
        self._target(*self._args)
        if self.ondie != None:
            self.ondie()

class glowyFade(threading.Thread):
    def __init__(self, func, color1, color2):
        threading.Thread.__init__(self)
        self.func = func
        self.col1 = color1
        self.col2 = color2
        self.anim = 0.0
        self.time = time.time()
        self.delta = 0
        self.stopme = False

    def stop(self):
        self.stopme = True

    def _getDelta(self):
        thistime = time.time()
        self.delta = thistime - self.time
        self.time = thistime

    def run(self):
        if not anims:
            self.func(self.col2)
        else:
            self.loop()

    def loop(self):
        while self.anim < 1.0 and not self.stopme:
            self._getDelta()
            self.func(_gradient(self.col1, self.col2, self.anim))
            self.anim = self.anim + (0.1 * float((float(self.delta) * 100)))
            time.sleep(0.001)


# Rectangle Renderer for the Glowy theme
class GlowyRectangleRenderer(threading.Thread):
    def __init__(self, obj):
        threading.Thread.__init__(self)
        self.obj = obj
        self.startme = normalc
        self.delta = 0
        self.time = time.time()
        self.stopme = False
        self.rlisf = True
        self.obj.renderlock.trace("w", self._rlfc)

    def stop(self):
        self.stopme = True

    def _getDelta(self):
        thistime = time.time()
        self.delta = thistime - self.time
        self.time = thistime

    def _rlfc(self, *args):
        if self.obj.renderlock.get() == 0 and self.rlisf:
            self.rlisf = False
            self.obj.renderlock.set(1)
            self.loop()

    def run(self):
        if not anims:
            self.obj.anim = 1.0
        self._rlfc()

    def loop(self):
        while True:
            self._getDelta()
            color = normalc
            if self.obj.clicking:
                color = clickc
            elif self.obj.hovering:
                color = hoverc
            if self.obj.anim <= 0.0:
                self.startme = copy.copy(self.obj.lastcolor)
            color = _gradient(self.startme, color, self.obj.anim)
            self.obj.lastcolor = color
            self._line(color)
            self.obj.anim += (0.1 * float((float(self.delta) * 100)))
            if self.stopme or self.obj.anim >= 1.0:
                break
        self.obj.renderlock.set(0)
        if self.obj.finishrenderingcmd != None:
            self.obj.finishrenderingcmd()

    def _line(self, color):
        if self.stopme:
            return
        start = (0, 0, 0)
        for i in range(0, self.obj.width):
            if self.stopme:
                return
            percent = float((float(i) / float(self.obj.width)))
            _setPixel(self.obj, self.obj.c_bottom[i], i, self.obj.height - 1,
                               _rgbtohex(_gradient(start, color, percent)))
        for i in range(0, self.obj.height):
            if self.stopme:
                return
            percent = float((float(i) / float(self.obj.height)))
            _setPixel(self.obj, self.obj.c_right[i], self.obj.width - 1, i,
                                _rgbtohex(_gradient(start, color, percent)))
        self.obj.coords(self.obj.c_left, 0, 0, 0, self.obj.height)
        self.obj.coords(self.obj.c_top, 0, 0, self.obj.width, 0)
        self.obj.itemconfig(self.obj.c_left, fill = _rgbtohex(start))
        self.obj.itemconfig(self.obj.c_top, fill = _rgbtohex(start))


# Glowy component
class Component(Tkinter.Canvas):
    def __init__(self, parent, *args, **kw):
        utilities.setDefault(kw, background = bg, borderwidth = 0, highlightthickness = 0)
        Tkinter.Canvas.__init__(self, parent, *args, **kw)
        self.height = 0
        self.width = 0
        self.anim = 1.0
        self.c_top = self.create_line(0, 0, 0, self.height, fill = "#000")
        self.c_left = self.create_line(0, 0, self.width, 0, fill = "#000")
        self.c_bottom = []
        self.c_right = []
        self.setHeight(self.height)
        self.setWidth(self.width)
        self.finishrenderingcmd = None
        self.renderlock = Tkinter.IntVar()
        self.renderlock.set(0)
        self.busy = False
        self.lastcolor = (0, 0, 0)
        self.currrenderer = None

    def __del__(self):
        self.currrenderer.stop()
        self.busy = False

    def setWidth(self, width):
        self.busy = True
        orig = self.width
        rrange = range(orig, width)
        inverted = False
        if width - orig < 0:
            rrange = range(width, orig)
            inverted = True
        self.width = width
        self.config(width = width)
        self.coords(self.c_top, 0, 0, width, 0)
        if inverted:
            for i in reversed(rrange):
                self.delete(self.c_bottom.pop(i))
        else:
            for i in rrange:
                self.c_bottom.append(_getPixel(self, i, self.height - 1, "#000"))
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
        self.config(height = height)
        self.coords(self.c_left, 0, 0, 0, height)
        if inverted:
            for i in reversed(rrange):
                self.delete(self.c_right.pop(i))
        else:
            for i in rrange:
                self.c_right.append(_getPixel(self, self.width - 1, i, "#000"))
        self.busy = False

    def renderlines(self):
        currr = self.currrenderer != None and self.currrenderer.isAlive()
        if currr:
            self.currrenderer.stop()
            #self.currrenderer.join()
        self.currrenderer = GlowyRectangleRenderer(self)
        self.currrenderer.start()


# Temporary Frame
class Frame(Tkinter.Frame):
    def __init__(self, parent, *args, **kw):
        utilities.setDefault(kw, highlightthickness = 0, borderwidth = 0, background = bg, relief = Tkinter.FLAT)
        Tkinter.Frame.__init__(self, parent, *args, **kw)


# Glowy button
'''
class Button(Tkinter.Canvas):
    def __init__(self, parent, *args, **kw):
        self.command = kw.pop("command", None)
        textset = kw.pop("text", False)
        bindclick = kw.pop("bindclick", True)
        bindunclick = kw.pop("bindunclick", True)
        self.mousedown = kw.pop("mousedown", None)
        utilities.setDefault(kw, background=bg, borderwidth=0, highlightthickness=0)
        Tkinter.Canvas.__init__(self, parent, *args, **kw)
        label = Tkinter.Label(self, text="Unused")
        self.font = tkFont.Font(font=label["font"])
        self.height = 0
        self.width = 0
        self.hovering = False
        self.anim = 1.0
        self.clicking = False
        self.commandvalid = False
        self.text = ""
        self.c_text = self.create_text(self.width / 2, self.height / 2, text=self.text,
                                 font=self.font, fill=fg)
        normalch = _rgbtohex(normalc)
        self.c_left = self.create_line(0, 0, 0, self.height, fill=normalch)
        self.c_top = self.create_line(0, 0, self.width, 0, fill=normalch)
        #self.c_bottom = []
        #self.c_right = []
        self.c_bottom = self.create_line(0, self.height, self.width, self.height, fill=normalch)
        self.c_right = self.create_line(self.width, 0, self.width, self.height, fill=normalch)
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
        self.lastcolor = normalc
        self.renderthread = None
        if textset == False:
            self.setText("")
        else:
            self.setText(textset)
        #self.render()

    def __del__(self):
        if self.renderthread != None and self.renderthread.isAlive():
            self.renderthread.stop()
        self.busy = False

    def render(self, anims=True):
        if self.renderthread != None and self.renderthread.isAlive():
            self.renderthread.stop()
        color = normalc
        if self.hovering:
            color = hoverc
        if self.clicking:
            color = clickc
        if self.lastcolor == color:
            return
        if anims:
            self.renderthread = glowyFade(self.setLineColor, copy.copy(self.lastcolor), color)
            self.renderthread.start()
        else:
            self.setLineColor(color)

    def setLineColor(self, color):
        if self.clicking:
            color = clickc
        self.lastcolor = color
        colorh = _rgbtohex(color)
        self.itemconfig(self.c_top, fill=colorh)
        self.itemconfig(self.c_bottom, fill=colorh)
        self.itemconfig(self.c_left, fill=colorh)
        self.itemconfig(self.c_right, fill=colorh)

    def setWidth(self, width):
        self.busy = True
        self.width = width
        self.config(width=width)
        self.coords(self.c_top, 0, 0, width - 1, 0)
        self.coords(self.c_bottom, 0, self.height - 1, width, self.height - 1)
        self.busy = False

    def setHeight(self, height):
        self.busy = True
        self.height = height
        self.config(height=height)
        self.coords(self.c_left, 0, 0, 0, height - 1)
        self.coords(self.c_right, self.width - 1, 0, self.width - 1, height - 1)
        self.busy = False

    def setText(self, text):
        self.setWidth(self.tk.call("font", "measure", tkFont.NORMAL, "-displayof", self, text) + 12)
        self.setHeight(self.height)
        self.text = text
        self.coords(self.c_text, (self.width) / 2, (self.height) / 2)
        self.itemconfig(self.c_text, text=self.text, font=self.font, fill=fg)

    def hoveringtrue(self, event):
        self.anim = 0.0
        self.hovering = True
        self.commandvalid = True
        self.render()

    def hoveringfalse(self, event):
        self.anim = 0.0
        self.hovering = False
        self.commandvalid = False
        self.render()

    def onclick(self, event):
        self.anim = 1.0
        self.clicking = True
        self.render(False)
        if self.mousedown != None:
            self.mousedown()

    def onunclick(self, event):
        self.anim = 0.0
        self.clicking = False
        self.render()
        if self.command != None and self.commandvalid:
            self.command()
'''

# Temporary Button
class Button(Tkinter.Label):
    def __init__(self, parent, *args, **kw):
        self.command = kw.pop("command", None)
        bindclick = kw.pop("bindclick", True)
        bindunclick = kw.pop("bindunclick", True)
        self.mousedown = kw.pop("mousedown", None)
        utilities.setDefault(kw, background = bg, foreground = fg, borderwidth = 0, pady = 3, padx = 8,
                        highlightbackground = _rgbtohex(normalc), highlightthickness = 1)
        Tkinter.Label.__init__(self, parent, *args, **kw)
        self.lastcolor = normalc
        self.renderthread = None
        self.hovering = False
        self.clicking = False
        self.bind("<Enter>", self.hoveringtrue)
        self.bind("<Leave>", self.hoveringfalse)
        if bindclick:
            self.bind("<ButtonPress-1>", self.onclick)
        if bindunclick:
            self.bind("<ButtonRelease-1>", self.onunclick)

    def render(self, anims1 = True):
        if self.renderthread != None and self.renderthread.isAlive():
            self.renderthread.stop()
        color = normalc
        if self.hovering:
            color = hoverc
        if self.clicking:
            color = clickc
        if anims1:
            self.renderthread = glowyFade(self._setHB, copy.copy(self.lastcolor), color)
            self.renderthread.start()
        else:
            self.renderthread = None
            self._setHB(color, True)

    def _setHB(self, value, override1 = False):
        if self.renderthread == None and not override1:
            return
        self.lastcolor = value
        self.config(highlightbackground = _rgbtohex(value))

    def hoveringtrue(self, *args):
        self.hovering = True
        self.render()

    def hoveringfalse(self, *args):
        self.hovering = False
        self.render()

    def onclick(self, *args):
        self.clicking = True
        self.render(False)
        if self.mousedown != None:
            self.mousedown()

    def onunclick(self, *args):
        self.clicking = False
        self.render()
        if self.command != None and self.hovering:
            self.command()


# Temporary Entry Box
class Entry(Tkinter.Entry):
    def __init__(self, parent, *args, **kw):
        utilities.setDefault(kw, background = bg, foreground = fg, selectbackground = fg,
                    selectforeground = bg, borderwidth = 0, highlightbackground = _rgbtohex(normalc),
                    highlightcolor = _rgbtohex(clickc))
        self.lastcolor = normalc
        self.renderthread = None
        Tkinter.Entry.__init__(self, parent, *args, **kw)
        self.bind("<Enter>", self.hoveringtrue)
        self.bind("<Leave>", self.hoveringfalse)

    def set(self, value):
        self.delete(0, Tkinter.END)
        self.insert(0, value)

    def _setHB(self, value):
        self.lastcolor = value
        self.config(highlightbackground = _rgbtohex(value))

    def hoveringtrue(self, *args):
        if self.renderthread != None and self.renderthread.isAlive():
            self.renderthread.stop()
        self.renderthread = glowyFade(self._setHB, copy.copy(self.lastcolor), hoverc)
        self.renderthread.start()
        #self.config(highlightbackground=_rgbtohex(hoverc))

    def hoveringfalse(self, *args):
        if self.renderthread != None and self.renderthread.isAlive():
            self.renderthread.stop()
        self.renderthread = glowyFade(self._setHB, copy.copy(self.lastcolor), normalc)
        self.renderthread.start()
        #self.config(highlightbackground=_rgbtohex(normalc))


# Temporary Label
class Label(Tkinter.Label):
    def __init__(self, parent, *args, **kw):
        utilities.setDefault(kw, background = bg, foreground = fg, borderwidth = 0, pady = 6, padx = 6,
                    highlightbackground = _rgbtohex(normalc), highlightcolor = _rgbtohex(hoverc))
        Tkinter.Label.__init__(self, parent, *args, **kw)


# Temporary Scrollbar
class GScrollbar(Tkinter.Scrollbar):
    def __init__(self, parent, *args, **kw):
        utilities.setDefault(kw, background = lightbg, borderwidth = 0, relief = Tkinter.FLAT,
                    activebackground = lightbghover, troughcolor = bg)
        if kw.get("showfunc"):
            self.showfunc = kw.pop("showfunc")
        if kw.get("hidefunc"):
            self.hidefunc = kw.pop("hidefunc")
        Tkinter.Scrollbar.__init__(self, parent, *args, **kw)
        self.bind("<ButtonPress-1>", self.onclick)
        self.bind("<ButtonRelease-1>", self.onunclick)

    '''def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            if hasattr(self, "hidefunc"):
                self.hidefunc()
        elif hasattr(self, "showfunc"):
            if hasattr(self, "hidefunc"):
                self.hidefunc()
            self.showfunc()
        Tkinter.Scrollbar.set(self, lo, hi)'''

    def onclick(self, *args):
        self.config(activebackground = lightbgclick)

    def onunclick(self, *args):
        self.config(activebackground = lightbghover)


# Temporary Combobox
class Combobox(Tkinter.OptionMenu):
    def __init__(self, parent, choices):
        self.current = Tkinter.StringVar()
        self.choices = choices
        Tkinter.OptionMenu.__init__(self, parent, self.current, *self.choices)
        self.renderthread = None
        self.lastcolor = normalc
        self.config(background = bg, foreground = fg, borderwidth = 0,
                    highlightthickness = 1, relief = Tkinter.FLAT, highlightbackground = _rgbtohex(normalc),
                    padx = 2, pady = 2, activebackground = bg, activeforeground = fg)
        self["menu"].config(background = fg, foreground = bg, borderwidth = 0,
                            activebackground = bg, activeforeground = fg, relief = Tkinter.FLAT)
        self.bind("<Enter>", self.hoveringtrue)
        self.bind("<Leave>", self.hoveringfalse)

    def set(self, value):
        self.current.set(value)

    def get(self):
        return self.current.get()

    def bind(self, *args):
        if args[0] == "<<ComboboxSelected>>":
            self.current.trace("w", args[1])
        else:
            Tkinter.OptionMenu.bind(self, *args)

    def _setHB(self, value):
        self.lastcolor = value
        self.config(highlightbackground = _rgbtohex(value))

    def hoveringtrue(self, *args):
        if self.renderthread != None and self.renderthread.isAlive():
            self.renderthread.stop()
        self.renderthread = glowyFade(self._setHB, copy.copy(self.lastcolor), hoverc)
        self.renderthread.start()
        #self.config(highlightbackground=_rgbtohex(hoverc))

    def hoveringfalse(self, *args):
        if self.renderthread != None and self.renderthread.isAlive():
            self.renderthread.stop()
        self.renderthread = glowyFade(self._setHB, copy.copy(self.lastcolor), normalc)
        self.renderthread.start()
        #self.config(highlightbackground=_rgbtohex(normalc))


# Glowy Radiobutton (based on the Glowy Button)
class Radiobutton(Button):
    def __init__(self, parent, *args, **kw):
        self.variable = kw.pop("variable", Tkinter.IntVar(0))
        self.value = kw.pop("value", 0)
        utilities.setDefault(kw, bindunclick = False, mousedown = self.select)
        Button.__init__(self, parent, *args, **kw)
        self._callback()
        self.variable.trace("w", self._callback)

    def select(self):
        self.variable.set(self.value)

    def _callback(self, *args):
        if self.variable.get() == self.value:
            self.clicking = True
            self.render(False)
        else:
            self.clicking = False
            self.render(False)


# Glowy Checkbutton
class Checkbutton(Tkinter.Checkbutton):
    def __init__(self, parent, *args, **kw):
        self.value = Tkinter.IntVar()
        utilities.setDefault(kw, background = bg, borderwidth = 0, highlightthickness = 0, foreground = fg,
                             selectcolor = bg, activebackground = bg, activeforeground = fg,
                             variable = self.value)
        Tkinter.Checkbutton.__init__(self, parent, *args, **kw)

# Glowy Notebook
class Notebook(Frame):
    def __init__(self, master = None, *args, **kw):
        self.master = master
        self.pages = []
        self.current = Tkinter.IntVar()
        self.current.set(0)
        self.old = 0
        self.finishedtb = None
        npages = kw.pop('npages', 0)
        utilities.setDefault(kw, background = bg, borderwidth = 0, highlightthickness = 0)
        Frame.__init__(self, master, *args, **kw)
        if npages > 0:
            for page in range(npages):
                self.add_empty_page()
            self.pages[self.current.get()].pack(fill = 'both', expand = 1)
            self._tab_buttons()
        self.current.trace("w", self._select)

    def _tab_buttons(self):
        # Place tab buttons on the pages
        if hasattr(self, "tabframe"):
            self.tabframe.pack_forget()
        self.tabframe = Frame(self, background = bg, borderwidth = 0, highlightthickness = 0)
        self.tabframe.pack(side = "top", fill = "x", padx = 6, pady = 6)
        for indx1, child1 in enumerate(self.pages):
            btn = Radiobutton(self.tabframe, variable = self.current, value = indx1,
                                text = child1.text)
            btn.grid(row = 0, column = indx1)
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
        if self.finishedtb != None:
            self.finishedtb()

    def _select(self, *args):
        self.pages[self.old].pack_forget()
        self.old = self.current.get()
        self.pages[self.current.get()].pack(fill = Tkinter.BOTH, expand = Tkinter.TRUE)

    def close(self):
        self.master.destroy()

    def add_empty_page(self):
        self.pages.append(Frame(self, relief = Tkinter.FLAT))
        self.pages[len(self.pages) - 1].text = ""

    def add_tab(self):
        self.add_empty_page()
        self._tab_buttons()
        return (len(self.pages) - 1)

    def add_page_body(self, tab_id, title, body):
        #self.tab(tab_id, text=title)
        self.pages[tab_id].text = title
        self._tab_buttons()
        body.pack(side = Tkinter.TOP, fill = Tkinter.BOTH, expand = Tkinter.TRUE)
        self.current.set(0)

    def page(self, page_num):
        if page_num < len(self.pages):
            return self.pages[page_num]
        else:
            logger.logI(tn, logger.E, _("Page") + " " + str(page_num) + " " + _("does not exist"))


# Scrolling frame, based on http://Tkinter.unpy.net/wiki/VerticalScrolledFrame
class VerticalScrolledFrame(Frame):
    def __init__(self, parent, *args, **kw):
        utilities.setDefault(kw, background = bg, borderwidth = 0, highlightthickness = 0, relief = Tkinter.FLAT)
        Frame.__init__(self, parent, *args, **kw)
        def showFunc():
            self.vscrollbar.pack(fill = Tkinter.Y, side = Tkinter.RIGHT, expand = Tkinter.FALSE)
        def hideFunc():
            self.vscrollbar.pack_forget()
        self.vscrollbar = GScrollbar(self, orient = Tkinter.VERTICAL)
        self.vscrollbar.pack(fill = Tkinter.Y, side = Tkinter.RIGHT, expand = Tkinter.FALSE)
        self.canvas = Tkinter.Canvas(self, kw, yscrollcommand = self.vscrollbar.set)
        self.canvas.pack(side = Tkinter.LEFT, fill = Tkinter.BOTH, expand = Tkinter.TRUE)
        self.vscrollbar.config(command = self.canvas.yview)
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        self.interior = interior = Frame(self.canvas, kw)
        interior.pack(fill = Tkinter.BOTH, expand = Tkinter.TRUE)
        interior_id = self.canvas.create_window(0, 0, window = interior,
                                           anchor = Tkinter.NW)

        def _configure_interior(event):
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            self.canvas.config(scrollregion = "0 0 %s %s" % size)
            if interior.winfo_reqwidth() != self.canvas.winfo_width():
                self.canvas.config(width = interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != self.canvas.winfo_width():
                self.canvas.itemconfigure(interior_id, width = self.canvas.winfo_width())
        self.canvas.bind('<Configure>', _configure_canvas)


'''class About:
    def __init__(self, master):
        top = self.top = Tkinter.Toplevel(master, background=config.background)
        top.title(config.product + " - " + _("About"))
        w = Tkinter.Label(top, text=config.about_string)
        w.pack(side=Tkinter.TOP, fill=Tkinter.BOTH, expand=True)
        b = Tkinter.Button(top, text=_("Close"), command=top.destroy)
        b.pack(side=Tkinter.BOTTOM)'''


class Wizard(Notebook):
    def __init__(self, master = None, *args, **kw):
        self.master = master
        #self.pages = []
        #self.current = 0
        #npages = kw.pop('npages', 0)
        #utilities.setDefault(kw, background=bg, borderwidth=0, highlightthickness=0)
        Notebook.__init__(self, master, *args, **kw)
        self.finishedtb = self._wizard_buttons
        '''for page in range(npages):
            logger.logVV(tn, logger.I, _("Creating page") + " " + str(page))
            self.add_empty_page()
        #self.pages[0].pack(fill='both', expand=1)
        #self._wizard_buttons()'''

    def _wizard_buttons(self):
        # Place wizard buttons on the pages
        for indx, child in enumerate(self.pages):
            if hasattr(child, "btnframe"):
                child.btnframe.pack_forget()
            child.btnframe = Frame(child)
            child.btnframe.pack(side = "bottom", fill = "x", padx = 6, pady = 12)
            nextbtn = Button(child.btnframe, text = _("Next"), command = self.next_page)
            nextbtn.pack(side = "right", anchor = "e", padx = 6)
            quitbtn = Button(child.btnframe, text = _("Quit"), command = self.close)
            quitbtn.pack(side = "left", anchor = "w", padx = 6)
            if indx > 0:
                prevbtn = Button(child.btnframe, text = _("Previous"),
                    command = self.prev_page)
                prevbtn.pack(side = "right", anchor = "e", padx = 6)
                if indx == len(self.pages) - 1:
                    nextbtn.config(text = "Finish")
                    nextbtn.command = self.close
            '''progressframe = Tkinter.Frame(child)
            progressframe.pack(side="bottom", fill="x", padx=6)
            progress = ttk.Progressbar(progressframe)
            progress.pack(fill="x")'''

    def next_page(self):
        if self.current == len(self.pages):
            return
        self.current.set(self.current.get() + 1)

    def prev_page(self):
        if self.current == 0:
            return
        self.current.set(self.current.get() - 1)

    def close(self):
        #self.master.destroy()
        exitprog()

    '''def add_empty_page(self):
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
            logger.logI(tn, logger.E, _("Page") + " " + str(page_num) + " " + _("does not exist"))'''


class FileSelector(Frame):
    def __init__(self, *args, **kw):
        Frame.__init__(self, *args, **kw)
        self.entry = Entry(self)
        self.button = Button(self, text = "...", command = self._on_button)
        self.button.grid(row = 0, column = 1)
        self.entry.grid(row = 0, column = 0)

    def _on_button(self):
        s = tkFileDialog.askopenfilename()
        if s != "":
            self.entry.delete(0, "end")
            self.entry.insert(0, s)


class YesNo(Frame):
    def __init__(self, *args, **kw):
        if "savevar" in kw:
            self.savevar = kw.pop("savevar")
        if "savefunc" in kw:
            self.savefunc = kw.pop("savefunc")
        Frame.__init__(self, *args, **kw)
        self.v = Tkinter.IntVar()
        self.y = Radiobutton(self, text = _("Yes"), variable = self.v, value = 1)
        self.y.variable.trace("w", self.save)
        self.y.grid(row = 0, column = 0)
        self.n = Radiobutton(self, text = _("No"), variable = self.v, value = 2)
        self.n.variable.trace("w", self.save)
        self.n.grid(row = 0, column = 1)

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

    def save(self, *args):
        if not hasattr(self, "savevar") or not hasattr(self, "savefunc"):
            return
        if self.get():
            self.savefunc(self.savevar, "Yes")
        elif self.get() is False:
            self.savefunc(self.savevar, "No")
        else:
            self.savefunc(self.savevar, "Unknown")


class Choice(Frame):
    def __init__(self, parent, choices, *args, **kw):
        if "savevar" in kw:
            self.savevar = kw.pop("savevar")
        if "savefunc" in kw:
            self.savefunc = kw.pop("savefunc")
        Frame.__init__(self, parent, *args, **kw)
        self.cb = Combobox(self, choices)
        self.entry = Entry(self)
        self.cb.grid(row = 0, column = 0)
        self.cb.bind("<<ComboboxSelected>>", self._on_changed)

    def _on_changed(self, *args):
        if self.cb.get() == configutils.custom:
            self.entry.grid(row = 1, column = 0)
        else:
            self.entry.grid_remove()
        self.save()

    def save(self, *args):
        if not hasattr(self, "savevar") or not hasattr(self, "savefunc"):
            return
        if self.cb.get() == configutils.custom:
            self.savefunc(self.savevar, self.entry.get())
        else:
            self.savefunc(self.savevar, self.cb.get())


class Multiple(Frame):
    def __init__(self, *args, **kw):
        if "savevar" in kw:
            self.savevar = kw.pop("savevar")
        if "savefunc" in kw:
            self.savefunc = kw.pop("savefunc")
        Frame.__init__(self, *args, **kw)
        self.entries = []
        self.pluses = []
        self.minuses = []
        self.dontsave = False
        self.addEntry(0)

    def addEntry(self, row):
        self.entries.insert(row, Entry(self))
        self.pluses.insert(row, Button(self, text = "+", command = lambda: self._plus(row)))
        self.minuses.insert(row, Button(self, text = "-", command = lambda: self._minus(row)))
        self.entries[row].grid(row = row, column = 0)
        self.minuses[row].grid(row = row, column = 1)
        self.pluses[row].grid(row = row, column = 2)
        self.entries[row].bind("<Key>", lambda event: self.save(event, True))
        self.entries[row].bind("<FocusOut>", self.save)
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
        self.dontsave = True
        for i in list(range(len(self.entries))):
            self.remEntry(i)
        if len(arr) > 0:
            for i in list(range(len(arr))):
                self.addEntry(i)
                self.entries[i].delete(0, "end")
                self.entries[i].insert(0, arr[i])
        else:
            self.addEntry(0)
        self.dontsave = False
        self._rePack()

    def _plus(self, row):
        self.addEntry(row + 1)

    def _minus(self, row):
        self.remEntry(row)

    def __rePack(self, c):
        self.pluses[c].command = lambda: self._plus(c)
        self.minuses[c].command = lambda: self._minus(c)
        self.entries[c].grid(row = c, column = 0)
        self.minuses[c].grid(row = c, column = 1)
        self.pluses[c].grid(row = c, column = 2)

    def _rePack(self):
        for c in list(range(len(self.entries))):
            self.__rePack(c)
        self.save()

    def save(self, *args):
        changeme = False
        if len(args) > 1 and hasattr(args[0], "char") and hasattr(args[0], "widget") and args[1]:
            changeme = True
            str_ = args[0].widget.get()
            args[0].widget.set(str_ + args[0].char)
        if not hasattr(self, "savevar") or not hasattr(self, "savefunc") or self.dontsave:
            return
        arr = []
        for i in self.entries:
            if i.get() != "":
                arr.append(i.get())
        str_ = " ".join(arr)
        self.savefunc(self.savevar, str_)
        print(config.Configuration["OSWeaver"][configutils.remafterinst])
        if changeme:
            str_ = args[0].widget.get()
            args[0].widget.set(str_[:len(str_) - 1])


class Progressbar(Tkinter.Canvas):
    def __init__(self, parent, *args, **kw):
        utilities.setDefault(kw, border = 0, highlightthickness = 1, bg = bg, highlightbackground = "black",
                    height = 15)
        Tkinter.Canvas.__init__(self, parent, *args, **kw)
        self.progressbar = self.create_rectangle(0, 0, 0, 0, fill = lightbg)
        self.currprogress = 0
        self.setProgress(0)

    def setProgress(self, newprogress):
        self.currprogress = newprogress
        width = self.winfo_width()
        if width <= 1:
            width = self.winfo_reqwidth()
        calc = float(float(newprogress) / float(100))
        calc1 = int(calc * width)
        self.coords(self.progressbar, 0, 0, calc1, self.winfo_reqheight())

    def getProgress(self):
        return self.currprogress



class Splash(Tkinter.Toplevel):
    def __init__(self, master, func):
        Tkinter.Toplevel.__init__(self, master, relief = Tkinter.SOLID, highlightthickness = 1, highlightcolor = fg)
        self.root = master
        self.root.withdraw()
        self.overrideredirect(Tkinter.TRUE)
        self.progress = Progressbar(self)
        if not config.python3:
            self.image1 = Image.open(config.relinuxdir + "/splash.png")
            self.image2 = Image.open(config.relinuxdir + "/splash_glowy.png")
            self.images = []
            for i in range(0, 11):
                percent = float(float(i) / 10)
                self.images.append(ImageTk.PhotoImage(Image.blend(self.image1, self.image2, percent)))
            #self.image = ImageTk.PhotoImage(Image.blend(self.image1, self.image2, 0.0))
            self.image = self.images[0]
            self.imgw = self.image.width()
            self.imgh = self.image.height()
        else:
            self.image = Tkinter.PhotoImage(file = config.relinuxdir + "/splash.ppm")
            self.imgw = self.image.width()
            self.imgh = self.image.height()
        self.textvar = Tkinter.StringVar()
        self.progresstext = Label(self, textvariable = self.textvar,
                                  height = 15, width = 480, anchor = Tkinter.W)
        self.w = self.imgw
        self.h = self.imgh + 32
        self.x = self.root.winfo_screenwidth() / 2 - self.w / 2
        self.y = self.root.winfo_screenheight() / 2 - self.h / 2
        self.geometry("%dx%d+%d+%d" % (self.w, self.h, self.x, self.y))
        self.panel = Label(self, image = self.image)
        self.panel.pack(side = Tkinter.TOP, fill = Tkinter.BOTH, expand = True)
        self.progress.pack(side = Tkinter.BOTTOM, fill = Tkinter.X, expand = True)
        self.progresstext.pack(side = Tkinter.BOTTOM, fill = Tkinter.X, expand = True)
        self.update()
        self.thread = FuncThread(func, self.endSplash, self)
        self.thread.start()

    def setProgress(self, progress, text):
        progress = int(math.floor(progress))
        if progress > 100:
            progress = 100
        if progress < 0:
            progress = 0
        self.progress.setProgress(progress)
        self.textvar.set(text)
        if not config.python3:
            percent = float(float(progress) / 100)
            self.image = self.images[progress / 10]
            #self.image = ImageTk.PhotoImage(Image.blend(self.image1, self.image2, percent))
            self.panel.configure(image = self.image)
        self.update()

    def endSplash(self):
        self.root.update()
        self.root.deiconify()
        self.withdraw()
        del(self)


class GUI:
    def __init__(self, master):
        self.root = master
        self.root.title(config.product)
        self.wizard = Wizard(self.root, npages = 2)
        self.wizard.master.minsize(400, 350)
        self.wizard.master.maxsize(800, 700)
        self.page1 = Notebook(self.wizard.page(1))
        self.page0 = Label(self.wizard.page(0), text = _("Welcome to relinux 0.4!\nClick next to get started"))
        self.wizard.add_page_body(0, _("Welcome"), self.page0)
        self.wizard.add_page_body(1, _("Configure"), self.page1)
        self.wizard.pack(fill = "both", expand = True)

    def savefunc(self, var, val):
        config.Configuration[var[0]][var[1]][configutils.value] = val

    def fillConfiguration(self, configs):
        c = 0
        for i in configs.keys():
            cur = Frame(self.page1)
            ids = self.page1.add_tab()
            self.page1.add_page_body(ids, i, cur)
            #self.page1.add(cur)
            #self.page1.tab(c, text=i)
            #curr = Tkinter.Frame(cur.interior)
            #curr.pack(side="top", fill="both", expand=1)
            secs = Notebook(cur)
            secs.pack(side = "top", fill = "both", expand = 1)
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
                    frame = VerticalScrolledFrame(secs.page(ids), background = bg, borderwidth = 0,
                                                  highlightthickness = 0)
                    subtabs[category] = frame
                    secs.add_page_body(ids, category, subtabs[category])
                    #secs.tab(subtabs[category], text=category)
                    curr = subtabs[category].interior
                l = Label(curr, text = configutils.getValueP(configs[i][x],
                                                           configutils.name))
                l.grid(row = c1, sticky = Tkinter.W)
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
                    r = YesNo(curr, savevar = (i, x), savefunc = self.savefunc)
                    r.grid(row = c1, column = 1)
                    r.set(configutils.parseBoolean(value))
                elif choices is not None and len(choices) > 0:
                    cb = Choice(curr, choices, savevar = (i, x), savefunc = self.savefunc)
                    cb.grid(row = c1, column = 1)
                    cb.cb.set(value)
                elif types == configutils.filename:
                    e = FileSelector(curr)
                    e.grid(row = c1, column = 1)
                    e.entry.delete(0, "end")
                    e.entry.insert(0, value)
                elif types == configutils.multiple:
                    e = Multiple(curr, savevar = (i, x), savefunc = self.savefunc)
                    e.grid(row = c1, column = 1)
                    e.set(multiple)
                else:
                    e = Entry(curr)
                    e.grid(row = c1, column = 1)
                    e.delete(0, "end")
                    e.insert(0, value)
                c1 = c1 + 1
            c = c + 1
