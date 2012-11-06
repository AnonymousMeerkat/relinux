# -*- coding: utf-8 -*-
'''
OSWeaver Module for relinux
@author: Anonymous Meerkat <meerkatanonymous@gmail.com>
'''

from relinux import threadmanager, config, gui, configutils, fsutil, utilities, logger
'''if config.python3:
    import tkinter as Tkinter
else:
    import Tkinter'''
from PyQt4 import QtGui, QtCore
import os
import copy
import threading

relinuxmodule = True
relinuxmoduleapi = 1
modulename = "OSWeaver"
moduleconfig = ["osweaver.conf"]

# Just in case config.ISOTree doesn't include a /
isotreel = config.ISOTree + "/"
tmpsys = config.TempSys + "/"
aptcache = {}
page = {}
tn = logger.genTN(modulename)


def runThreads(threads, **options):
    threadmanager.threadLoop(threads, **options)


def run(*args):
    global aptcache, page
    configs = config.Configuration["OSWeaver"]
    isodir = configutils.getValue(configs[configutils.isodir])
    config.ISOTree = isodir + "/.ISO_STRUCTURE/"
    config.TempSys = isodir + "/.TMPSYS/"
    aptcache = config.AptCache
    ourgui = config.Gui
    from relinux.modules.osweaver import isoutil, squashfs, tempsys, ui_osweaver, setup
    threads = []
    threads.extend(setup.threads)
    threads.extend(tempsys.threads)
    threads.extend(squashfs.threads)
    threads.extend(isoutil.threads)
    threads_ = utilities.remDuplicates(threads)
    threads = threads_
    '''pagenum = ourgui.wizard.add_tab()
    page = gui.Frame(ourgui.wizard.page(pagenum))
    ourgui.wizard.add_page_body(pagenum, _("OSWeaver"), page)
    page.frame = gui.Frame(page)
    page.details = gui.VerticalScrolledFrame(page, borderwidth = 1, relief = Tkinter.SOLID)
    page.details.output = gui.Label(page.details.interior, text = config.GUIStream.getvalue(), anchor = Tkinter.NW, justify = Tkinter.LEFT)
    def onWrite():
        page.details.output.config(text = config.GUIStream.getvalue())
        page.details.canvas.yview_moveto(1.0)
    config.GUIStream.writefunc.append(onWrite)
    page.details.output.pack(fill = Tkinter.BOTH, expand = True, anchor = Tkinter.NW, side = Tkinter.LEFT)
    page.details.pack(fill = Tkinter.BOTH, expand = True, side = Tkinter.BOTTOM, anchor = Tkinter.SW)
    \'''page.details.buttonstate = True
    def showDetails():
        if page.details.buttonstate:
            page.details.output.pack(fill=Tkinter.BOTH, expand=True, anchor=Tkinter.NW, side=Tkinter.LEFT)
            page.showdetails.config(text="<< Hide details")
            page.details.buttonstate = False
        else:
            page.details.output.pack_forget()
            page.showdetails.config(text="Show details >>")
            page.details.buttonstate = True
    page.showdetails = gui.Button(page, text="Show details >>", command=showDetails)
    page.showdetails.pack(side=Tkinter.BOTTOM, anchor=Tkinter.SW)\'''
    page.progress = gui.Progressbar(page)
    page.progress.pack(fill = Tkinter.X, expand = True, side = Tkinter.BOTTOM,
                          anchor = Tkinter.S)
    page.frame.pack(fill = Tkinter.BOTH, expand = True, anchor = Tkinter.CENTER)
    page.chframe = gui.VerticalScrolledFrame(page.frame)
    page.chframe.pack(fill = Tkinter.BOTH, expand = True, anchor = Tkinter.N)
    page.chframe.boxes = []
    page.chframe.dispthreads = []
    x = 0
    y = 0
    usedeps = gui.Checkbutton(page.chframe.interior, text = "Ignore dependencies")
    usedeps.grid(row = y, column = x)
    y += 1
    label = gui.Label(page.chframe.interior, text = "Select threads to run:")
    label.grid(row = y, column = x)
    y += 1
    class customCheck(gui.Checkbutton):
        def __init__(self, parent, *args, **kw):
            gui.Checkbutton.__init__(self, parent, *args, **kw)
            self.id = len(page.chframe.boxes)
            self.ignoreauto = True
            self.value.trace("w", self.autoSelect)

        def autoSelect(self, *args):
            id_ = self.id
            if self.ignoreauto:
                self.ignoreauto = False
                return
            if self.value.get() < 1:
                return
            if len(threads[id_]["deps"]) <= 0 or usedeps.value.get() > 0:
                return
            tns = []
            for i in threads[id_]["deps"]:
                tns.append(i["tn"])
            for i in range(len(threads)):
                if threads[i]["tn"] in tns:
                    page.chframe.boxes[i].value.set(1)
    for i in threads:
        temp = customCheck(page.chframe.interior, text = i["tn"])
        temp.value.set(1)
        temp.grid(row = y, column = x, sticky = Tkinter.NW)
        page.chframe.boxes.append(temp)
        x += 1
        if x >= 3:
            x = 0
            y += 1
    if x != 0:
        y += 1
    def selBoxes(all_):
        val = 0
        if all_ == None:
            for i in range(len(threads)):
                page.chframe.boxes[i].ignoreauto = True
                if page.chframe.boxes[i].value.get() < 1:
                    page.chframe.boxes[i].value.set(1)
                else:
                    page.chframe.boxes[i].value.set(0)
            return
        if all_:
            val = 1
        for i in range(len(threads)):
            page.chframe.boxes[i].ignoreauto = True
            page.chframe.boxes[i].value.set(val)
    selall = gui.Button(page.chframe.interior, text = "Select all", command = lambda: selBoxes(True))
    selall.grid(row = y, column = x)
    x += 1
    selnone = gui.Button(page.chframe.interior, text = "Select none", command = lambda: selBoxes(False))
    selnone.grid(row = y, column = x)
    x += 1
    togglesel = gui.Button(page.chframe.interior, text = "Toggle", command = lambda: selBoxes(None))
    togglesel.grid(row = y, column = x)
    y += 1
    x = 0
    threadsrunninglabel = gui.Label(page.chframe.interior, text = "Threads running:")
    threadsrunninglabel.grid(row = y, column = x, columnspan = 3)
    y += 1
    page.progress.threads = {}
    def startThreads():
        if os.getuid() != 0:
            page.isnotroot.pack_forget()
            page.isnotroot.pack(fill = Tkinter.X)
            return
        numthreads = 0
        for i in range(len(page.chframe.boxes)):
            if page.chframe.boxes[i].value.get() < 1:
                threads[i]["enabled"] = False
            else:
                threads[i]["enabled"] = True
                numthreads += 1
            tfdeps = False
            if usedeps.value.get() > 0:
                tfdeps = True
        def postStart(threadid, threadsrunning, threads):
            txt = ""
            for i in range(len(threadsrunning)):
                tn = threadmanager.getThread(threadsrunning[i], threads)["tn"]
                if i == len(threadsrunning) - 1:
                    if len(threadsrunning) == 1:
                        txt = tn
                    elif len(threadsrunning) == 2:
                        txt += " and " + tn
                    else:
                        txt += ", and " + tn
                elif i == 0:
                    txt = tn
                else:
                    txt += ", " + tn
            threadsrunninglabel.config(text = "Threads running: " + txt)
        def setProgress(tn, progress):
            page.progress.threads[tn] = progress
            totprogress = 0
            for i in page.progress.threads.keys():
                totprogress += utilities.floatDivision(float(page.progress.threads[i]), 100)
            page.progress.setProgress(utilities.calcPercent(totprogress, numthreads))
        def postEnd(threadid, threadsrunning, threads):
            tn = threadmanager.getThread(threadid, threads)["tn"]
            setProgress(tn, 100)
            postStart(threadid, threadsrunning, threads)
        runThreads(threads, deps = tfdeps, poststart = postStart, postend = postEnd, threadargs = {"setProgress": setProgress})
        # lambda: runThreads(threads)
    page.button = gui.Button(page.frame, text = "Start!", command = startThreads)
    page.button.pack()
    page.isnotroot = gui.Label(page.frame, text = "You are not root!")'''
    page = {}
    page["boxes"] = []
    page["progress"] = {}
    page_container = QtGui.QWidget()
    ui = ui_osweaver.Ui_OSWeaver()
    ui.setupUi(page_container)
    ui.notroot.hide()
    # TODO: Figure out why the terminal is always crashing relinux!
    # Some random error messages that could help debug:
    ##############################################
    # QTextLine: Can't set a line width while not layouting.
    if not configutils.getValue(config.Configuration["Relinux"]["EXPERIMENTFEATURES"]):
        ui.terminal.hide()
    class customMsgBox(QtGui.QMessageBox):
        @QtCore.pyqtSlot(QtCore.QString)
        def realSetText(self, text):
            self.setText(text)
        @QtCore.pyqtSlot(QtCore.QString)
        def setImportance(self, importance):
            icon = None
            if importance == logger.I:
                icon = QtGui.QMessageBox.Information
            elif importance == logger.W:
                icon = QtGui.QMessageBox.Warning
            elif importance == logger.E:
                icon = QtGui.QMessageBox.Critical
            else:
                icon = QtGui.QMessageBox.NoIcon
            self.setIcon(icon)
    ui.msgbox = customMsgBox()
    #ui.terminal.hide()
    class customCheck(QtGui.QCheckBox):
        def __init__(self, *args):
            QtGui.QCheckBox.__init__(self, *args)
            self.ignoreauto = False
            self.id = len(page["boxes"])
            self.value = utilities.eventVar(value = False)
            self.value.trace("w", self.set)
            self.clicked.connect(self.toggled_)

        def toggled_(self, *args):
            self.setChecked(not self.get())  # Toggle checked state
            self.value.set(not self.get())  # Set the state that was wanted (not not)

        def set(self, newvalue):
            if newvalue == self.get():
                return
            self.setChecked(newvalue)
            if self.ignoreauto:
                self.ignoreauto = False
            elif newvalue:
                self.autoSelect()

        def get(self):
            return self.isChecked()

        def autoSelect(self):
            if len(threads[self.id]["deps"]) < 0 or ui.nodepends.isChecked():
                return
            tns = [i["tn"] for i in threads[self.id]["deps"]]
            for i in range(len(threads)):
                if threads[i]["tn"] in tns:
                    page["boxes"][i].set(True)
    x = 0
    y = 0
    for i in threads:
        ch = customCheck(i["tn"], ui.threadstorun)
        ui.gridLayout_2.addWidget(ch, y, x)  # No idea why Qt wants Y before X
        page["boxes"].append(ch)
        x += 1
        if x >= 3:
            x = 0
            y += 1
    # Terrible name, but it's just a function that selects/deselects values from "threevalues"
    # Possible values of "threevalues":
    #   True  - Select All
    #   False - Select None
    #   None  - Toggle Selected
    def tripleSel(threevalues):
        val = False
        tog = False
        if threevalues:  # Select All
            val = True
        elif threevalues is None:
            tog = True
        for i in range(len(page["boxes"])):
            page["boxes"][i].ignoreauto = True
            if tog:
                page["boxes"][i].set(not page["boxes"][i].get())
            else:
                page["boxes"][i].set(val)
    # Run when ui.nodepends is unchecked
    def ignoreDepends():
        for i in range(len(page["boxes"])):
            if page["boxes"][i].get():
                page["boxes"][i].autoSelect()
    # Start running
    def startThreads(*args):
        if os.getuid() != 0:
            ui.notroot.show()
            return
        numthreads = 0
        numthreads2 = 0
        threadmanager.addOptional(threads)
        threadspans = {}
        for i in range(len(page["boxes"])):
            threads[i]["enabled"] = page["boxes"][i].get()
            tn = threads[i]["tn"]
            if threads[i]["enabled"]:
                numthreads += 1
                if threads[i]["threadspan"] < 0:
                    numthreads2 += threadmanager.cpumax
                    threadspans[tn] = threadmanager.cpumax
                else:
                    numthreads2 += threads[i]["threadspan"]
                    threadspans[tn] = threads[i]["threadspan"]
        tfdeps = False
        if ui.nodepends.isChecked():
            tfdeps = True
        def onThreadAdded(threadid, threadsrunning, threads):
            rt = "Threads running: "
            c = 0
            for i in range(len(threadsrunning)):
                tn = threadmanager.getThread(threadsrunning[i], threads)["tn"]
                rt += tn
                if c + 1 < len(threadsrunning) and len(threadsrunning) > 2:
                    rt += ", "
                if c + 2 == len(threadsrunning):
                    if c == 0:
                        rt += " "
                    rt += "and "
                c += 1
            QtCore.QMetaObject.invokeMethod(ui.notroot, "setText",
                                            QtCore.Qt.QueuedConnection,
                                            QtCore.Q_ARG("QString", rt))
            if ui.notroot.isHidden():
                QtCore.QMetaObject.invokeMethod(ui.notroot, "show",
                                            QtCore.Qt.QueuedConnection
                                            )
        def updateProgress():
            totprogress = 0
            for i in page["progress"]:
                totprogress += utilities.floatDivision(float(page["progress"][i]), 100)
            QtCore.QMetaObject.invokeMethod(ui.progress, "setValue",
                                            QtCore.Qt.QueuedConnection,
                                QtCore.Q_ARG("int", utilities.calcPercent(totprogress, numthreads2)))
        def setProgress(tn, progress):
            ts = threadspans[tn]
            progress *= ts
            if progress > 100 * ts:
                progress = 100 * ts
            elif progress < 0:
                progress = 0
            page["progress"][tn] = progress
            updateProgress()
        def onThreadRemoved(threadid, threadsrunning, threads):
            tn = threadmanager.getThread(threadid, threads)["tn"]
            setProgress(tn, 100)
            onThreadAdded(threadid, threadsrunning, threads)
            page["boxes"][threadid].set(False)
        def showMessage(tn, importance, msg):
            logger.logI(tn, importance, msg)
            QtCore.QMetaObject.invokeMethod(ui.msgbox, "setImportance", QtCore.Qt.QueuedConnection,
                                            QtCore.Q_ARG("QString", importance))
            QtCore.QMetaObject.invokeMethod(ui.msgbox, "realSetText", QtCore.Qt.QueuedConnection,
                                            QtCore.Q_ARG("QString", msg))
            QtCore.QMetaObject.invokeMethod(ui.msgbox, "exec", QtCore.Qt.QueuedConnection)
        def onThreadsEnd(threadids, threadsdone, threads):
            if len(threadsdone) >= numthreads and False:
                pass
        for i in page["progress"]:
            page["progress"][i] = 0
        updateProgress()
        runThreads(threads, deps = tfdeps, poststart = onThreadAdded, postend = onThreadRemoved, threadargs = {"setProgress": setProgress, "showMessage": showMessage},
                   threadsend = onThreadsEnd)

    def onWrite(msg):
        return  # Delete this if you want a GUI terminal (which might crash relinux)
        ui.terminal.moveCursor(QtGui.QTextCursor.End, QtGui.QTextCursor.MoveAnchor)
        QtCore.QMetaObject.invokeMethod(ui.terminal, "insertPlainText",
                                        QtCore.Qt.QueuedConnection,
                            QtCore.Q_ARG("QString", msg.rstrip() + "\n"))
        #ui.terminal.setText(config.GUIStream.getvalue())
    tripleSel(True)
    config.GUIStream.writefunc.append(onWrite)
    ui.selall.clicked.connect(lambda *args: tripleSel(True))
    ui.selnone.clicked.connect(lambda *args: tripleSel(False))
    ui.togsel.clicked.connect(lambda *args: tripleSel(None))
    ui.nodepends.clicked.connect(lambda *args: ignoreDepends() if not ui.nodepends.isChecked() else None)
    ui.startbutton.clicked.connect(startThreads)
    ourgui.addTab(page_container, "OSWeaver")
