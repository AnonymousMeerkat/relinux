# -*- coding: utf-8 -*-
'''
Everything GUI-related is here
@author: Anonymous Meerkat <meerkatanonymous@gmail.com>
'''

import sys
from PyQt4 import QtGui, QtCore
from ui_mainwindow import Ui_MainWindow
from ui_welcome import Ui_Welcome
from relinux import config, configutils, logger


tn = logger.genTN("GUI")

def quitProg(app):
    sys.exit(app.exec_())

def saveFunc(var, val):
    if isinstance(val, QtCore.QString):
        val = str(val)
    config.Configuration[str(var[0])][str(var[1])][configutils.value] = val
    configutils.saveBuffer(config.Configuration)

class RelinuxSplash(QtGui.QSplashScreen):
    def __init__(self, *args):
        QtGui.QSplashScreen.__init__(self, *args)
        self.frameid = 0
        self.imageviewer = QtGui.QImageReader()

    def setAnimatedPixmap(self, file_):
        self.imageviewer.setFilename(file_)

    def paintEvent(self, event):
        if not self.imageviewer.canRead():
            return
        painter = QtGui.QPainter(self)
        if self.frameid >= self.imageviewer.imageCount():
            self.frameid = 0
        self.imageviewer.jumpToImage(self.frameid)
        painter.drawImage(self.imageviewer.read())
        self.frameid += 1


class MultipleValues(QtGui.QWidget):
    def __init__(self, thevar):
        QtGui.QWidget.__init__(self)
        self.thevar = thevar
        self.gridlayout = QtGui.QGridLayout()
        self.entries = []
        self.pluses = []
        self.minuses = []
        self.dontsave = False
        self.addEntry(0)
        self.setLayout(self.gridlayout)

    def addEntry(self, row):
        self.entries.insert(row, QtGui.QLineEdit())
        plusbtn = QtGui.QPushButton("+")
        plusbtn.clicked.connect(lambda *args: self._plus(row))
        self.pluses.insert(row, plusbtn)
        minusbtn = QtGui.QPushButton("-")
        minusbtn.clicked.connect(lambda *args: self._minus(row))
        self.minuses.insert(row, minusbtn)
        self.gridlayout.addWidget(self.entries[row], row, 0)
        self.gridlayout.addWidget(self.minuses[row], row, 1)
        self.gridlayout.addWidget(self.pluses[row], row, 2)
        self.entries[row].textEdited.connect(self.save)
        self._rePack()

    def remEntry(self, row):
        self.gridlayout.removeWidget(self.entries[row])
        self.gridlayout.removeWidget(self.minuses[row])
        self.gridlayout.removeWidget(self.pluses[row])
        self.entries[row].deleteLater()
        self.minuses[row].deleteLater()
        self.pluses[row].deleteLater()
        del(self.entries[row])
        del(self.minuses[row])
        del(self.pluses[row])
        self._rePack()

    def set(self, arr):
        self.dontsave = True
        for i in range(len(self.entries)):
            self.remEntry(i)
        if len(arr) > 0:
            for i in range(len(arr)):
                self.addEntry(i)
                self.entries[i].setText(arr[i])
        else:
            self.addEntry(0)
        self.dontsave = False
        self._rePack()

    def _plus(self, row):
        self.addEntry(row + 1)

    def _minus(self, row):
        self.remEntry(row)

    def __rePack(self, c):
        a = [self.pluses[c], self.minuses[c]]
        for i in range(len(a)):
            a[i].clicked.disconnect()
        self.pluses[c].clicked.connect(lambda *args: self._plus(c))
        self.minuses[c].clicked.connect(lambda *args: self._minus(c))
        a = [self.entries[c], self.minuses[c], self.pluses[c]]
        for i in range(len(a)):
            self.gridlayout.removeWidget(a[i])
            self.gridlayout.addWidget(a[i], c, i)

    def _rePack(self):
        for c in range(len(self.entries)):
            self.__rePack(c)
        self.save()

    def save(self):
        if self.dontsave:
            return
        arr = []
        for i in self.entries:
            if str(i.text()).strip() != "":
                arr.append(str(i.text()).strip())
        saveFunc(self.thevar, arr)

class ConfigWidget():
    def __init__(self, widget, thevar):
        self.widget = widget
        self.widget.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding,
                                                        QtGui.QSizePolicy.Fixed)
        def temp(s):
            saveFunc(thevar, s)
        if isinstance(widget, QtGui.QCheckBox):
            # State > 0 = Checked (1 = partially checked, 2 = checked)
            widget.stateChanged.connect(lambda s: temp(True if s > 0 else False))
        elif isinstance(widget, QtGui.QComboBox):
            # As Qt documents that currentIndexChanged can either send an int or a QString,
            # we'll add support for both
            widget.currentIndexChanged.connect(
                            lambda s: temp(widget.itemText(s) if isinstance(s, int) else s))
        elif isinstance(widget, QtGui.QLineEdit):
            # No fancy lambda's are needed here
            widget.textEdited.connect(temp)
        else:
            # Someone obviously doesn't know how to use this class
            pass


class GUI(QtGui.QMainWindow):
    def __init__(self, app):
        QtGui.QMainWindow.__init__(self)
        self.app = app
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.actionAbout_Qt.triggered.connect(app.aboutQt)
        self.ui.actionAbout.triggered.connect(self.showAbout)
        self.ui.actionQuit.triggered.connect(self.quit)
        self.ui.quitBtn.clicked.connect(self.quit)
        self.ui.moduleNotebook.currentChanged.connect(self.updateWizButtons)
        self.ui.nextBtn.clicked.connect(self.nextTab)
        self.ui.prevBtn.clicked.connect(self.prevTab)
        self.welcome_container = QtGui.QWidget()
        self.welcomeTab = Ui_Welcome()
        self.welcomeTab.setupUi(self.welcome_container)
        self.ui.moduleNotebook.insertTab(0, self.welcome_container, "Welcome")
        self.createConfigTab()
        self.updateWizButtons()

    def updateWizButtons(self):
        if self.ui.moduleNotebook.currentIndex() <= 0:
            self.ui.prevBtn.setEnabled(False)
        else:
            self.ui.prevBtn.setEnabled(True)
        if self.isLast():
            self.ui.nextBtn.setText(_("Finish"))
        else:
            self.ui.nextBtn.setText(_("Next"))
        if self.ui.moduleNotebook.currentIndex() < 0:
            self.ui.nextBtn.setEnabled(False)
        else:
            self.ui.nextBtn.setEnabled(True)

    def nextTab(self, *args):
        if self.isLast():
            self.quit()
        else:
            self.chTab(1)

    def prevTab(self, *args):
        self.chTab(-1)

    def chTab(self, amt):
        self.ui.moduleNotebook.setCurrentIndex(self.ui.moduleNotebook.currentIndex() + amt)

    def isLast(self):
        return self.ui.moduleNotebook.count() - 1 <= self.ui.moduleNotebook.currentIndex()

    def createConfigTab(self):
        configs = config.Configuration
        self.configTab = QtGui.QWidget()
        self.configTab.vlayout = QtGui.QVBoxLayout(self.configTab)
        # Master notebook (stores the sections)
        self.configTab.notebook1 = QtGui.QTabWidget(self.configTab)
        self.configTab.vlayout.addWidget(self.configTab.notebook1)
        self.fillConfiguration(configs, self.configTab)
        self.ui.moduleNotebook.addTab(self.configTab, "Configuration")

    def fillConfiguration(self, configs, widget):
        # TODO: Clean this mess, or at least comment it
        l = chr(108)
        v = chr(118)
        for i in configs.keys():
            # If the section is not in the notebook, add it
            if not i in self.configTab.notebook1.__dict__:
                self.configTab.notebook1.__dict__[i] = QtGui.QWidget()
                self.configTab.notebook1.__dict__[i].vlayout = QtGui.QVBoxLayout(
                                                                self.configTab.notebook1.__dict__[i])
                self.configTab.notebook1.__dict__[i].nbook = QtGui.QTabWidget(
                                                                self.configTab.notebook1.__dict__[i])
                self.configTab.notebook1.__dict__[i].vlayout.addWidget(
                                                        self.configTab.notebook1.__dict__[i].nbook)
                self.configTab.notebook1.addTab(self.configTab.notebook1.__dict__[i], i)
            for x in configs[i].keys():
                c = configutils.getValueP(configs[i][x], configutils.category)
                n = configutils.getValueP(configs[i][x], configutils.name)
                t = configutils.getValueP(configs[i][x], configutils.types)
                d = configutils.getValueP(configs[i][x], configutils.desc)
                v_ = configutils.getValue(configs[i][x])
                c_ = configutils.getChoices(t)
                var = (i, x)
                uw = True
                # If the category is not in the section's notebook, add it
                if not c in self.configTab.notebook1.__dict__[i].nbook.__dict__:
                    fw = QtGui.QWidget(self.configTab.notebook1.__dict__[i].nbook)
                    vb = QtGui.QVBoxLayout(fw)
                    self.configTab.notebook1.__dict__[i].nbook.__dict__[c] = QtGui.QScrollArea(fw)
                    vb.addWidget(self.configTab.notebook1.__dict__[i].nbook.__dict__[c])
                    self.configTab.notebook1.__dict__[i].nbook.__dict__[c].setWidgetResizable(True)
                    self.configTab.notebook1.__dict__[i].nbook.__dict__[c].flayout = QtGui.QFormLayout()
                    #self.configTab.notebook1.__dict__[i].nbook.__dict__[c].flayout.setSizeConstraint(
                    #                                            QtGui.QLayout.SetFixedSize)
                    self.configTab.notebook1.__dict__[i].nbook.__dict__[c].flayout.setFieldGrowthPolicy(
                                                        QtGui.QFormLayout.ExpandingFieldsGrow)
                    self.configTab.notebook1.__dict__[i].nbook.__dict__[c].flayout.setLabelAlignment(
                                                                        QtCore.Qt.AlignLeft)
                    #self.configTab.notebook1.__dict__[i].nbook.__dict__[c].flayout.setFormAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop);
                    self.configTab.notebook1.__dict__[i].nbook.__dict__[c].flayoutC = QtGui.QWidget()
                    self.configTab.notebook1.__dict__[i].nbook.__dict__[c].flayoutC.setLayout(
                            self.configTab.notebook1.__dict__[i].nbook.__dict__[c].flayout)
                    self.configTab.notebook1.__dict__[i].nbook.__dict__[c].flayoutC.setSizePolicy(
                                                                QtGui.QSizePolicy.MinimumExpanding,
                                                        QtGui.QSizePolicy.Preferred)
                    self.configTab.notebook1.__dict__[i].nbook.__dict__[c].setWidget(
                            self.configTab.notebook1.__dict__[i].nbook.__dict__[c].flayoutC)
                    self.configTab.notebook1.__dict__[i].nbook.addTab(
                                        fw, c)
                # Add the label
                self.configTab.notebook1.__dict__[i].nbook.__dict__[c].__dict__[n] = {}
                self.configTab.notebook1.__dict__[i].nbook.__dict__[c].__dict__[n][l] = QtGui.QLabel()
                self.configTab.notebook1.__dict__[i].nbook.__dict__[c].__dict__[n][l].setText(n)
                self.configTab.notebook1.__dict__[i].nbook.__dict__[c].__dict__[n][l].setToolTip(d)
                # Add the value
                if t == configutils.yesno:
                    self.configTab.notebook1.__dict__[i].nbook.__dict__[c].__dict__[n][v] = ConfigWidget(QtGui.QCheckBox(), var)
                    if v_:
                        self.configTab.notebook1.__dict__[i].nbook.__dict__[c].__dict__[n][v].widget.setChecked(True)
                elif c_ is not None and len(c_) > 0:
                    self.configTab.notebook1.__dict__[i].nbook.__dict__[c].__dict__[n][v] = ConfigWidget(QtGui.QComboBox(), var)
                    self.configTab.notebook1.__dict__[i].nbook.__dict__[c].__dict__[n][v].widget.clear()
                    c__ = 0
                    for y in c_:
                        self.configTab.notebook1.__dict__[i].nbook.__dict__[c].__dict__[n][v].widget.addItem(y)
                        if y == v_:
                            self.configTab.notebook1.__dict__[i].nbook.__dict__[c].__dict__[n][v].widget.setCurrentIndex(c__)
                        c__ += 1
                elif t == configutils.multiple:
                    if not isinstance(v_, list):
                        # Wut?
                        logger.logE(self.tn, logger.E, "Something went wrong")
                    self.configTab.notebook1.__dict__[i].nbook.__dict__[c].__dict__[n][v] = MultipleValues(var)
                    self.configTab.notebook1.__dict__[i].nbook.__dict__[c].__dict__[n][v].set(v_)
                    uw = False
                else:
                    self.configTab.notebook1.__dict__[i].nbook.__dict__[c].__dict__[n][v] = ConfigWidget(QtGui.QLineEdit(), var)
                    self.configTab.notebook1.__dict__[i].nbook.__dict__[c].__dict__[n][v].widget.setText(v_)
                #self.configTab.notebook1.__dict__[i].nbook.__dict__[c].__dict__[n][v].widget.setSizePolicy(
                #                    QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding))
                if uw:
                    p = self.configTab.notebook1.__dict__[i].nbook.__dict__[c].__dict__[n][v].widget
                else:
                    p = self.configTab.notebook1.__dict__[i].nbook.__dict__[c].__dict__[n][v]
                p.setToolTip(d)
                self.configTab.notebook1.__dict__[i].nbook.__dict__[c].flayout.addRow(
                        self.configTab.notebook1.__dict__[i].nbook.__dict__[c].__dict__[n][l], p)

    def addTab(self, *args):
        self.ui.moduleNotebook.addTab(*args)
        self.updateWizButtons()

    def showAbout(self):
        QtGui.QMessageBox.about(self, config.product, config.about_string)

    def quit(self, *args):
        quitProg(self.app)

# For debug purposes
if __name__ == "__main__":
    def _(t):
        return t
    from relinux import modloader
    import os
    app = QtGui.QApplication([])
    app.setStyleSheet(open("./stylesheet.css", "r").read())
    splash = QtGui.QSplashScreen(QtGui.QPixmap(config.relinuxdir + "splash_light.png"))
    splash.show()
    splash.showMessage("Loading...", QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
    app.processEvents()
    modules = []
    modulemetas = modloader.getModules()
    for i in modulemetas:
        modules.append(modloader.loadModule(i))
    configfiles = [config.relinuxdir + "/relinux.conf"]
    for i in range(len(modulemetas)):
        for x in modules[i].moduleconfig:
            configfiles.append(os.path.join(os.path.dirname(modulemetas[i]["path"]), x))
    cbuffer = configutils.parseFiles(configfiles)
    config.Configuration = cbuffer
    configutils.saveBuffer(config.Configuration)
    gui = GUI(app)
    gui.show()
    splash.finish(gui)
    quitProg(app)
