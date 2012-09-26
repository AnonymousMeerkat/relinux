# -*- coding: utf-8 -*-
'''
Everything GUI-related is here
@author: Anonymous Meerkat <meerkatanonymous@gmail.com>
'''

import sys
from PyQt4 import QtGui
from ui_mainwindow import Ui_MainWindow
from ui_welcome import Ui_Welcome
from relinux import config

def quitProg(app):
    sys.exit(app.exec_())

class GUI(QtGui.QMainWindow):
    def __init__(self, app):
        QtGui.QMainWindow.__init__(self)
        self.app = app
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.actionAbout_Qt.triggered.connect(app.aboutQt)
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
        self.configTab.notebook1 = QtGui.QTabWidget(self.configTab)
        self.configTab.vlayout.addWidget(self.configTab.notebook1)
        self.fillConfiguration(configs, self.configTab)
        self.ui.moduleNotebook.addTab(self.configTab, "Configuration")

    def fillConfiguration(self, configs, widget):
        # TODO: Clean this mess
        l = chr(108)
        v = chr(118)
        for i in configs.keys():
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
                if not c in self.configTab.notebook1.__dict__[i].nbook.__dict__:
                    fw = QtGui.QWidget(self.configTab.notebook1.__dict__[i].nbook)
                    vb = QtGui.QVBoxLayout(fw)
                    self.configTab.notebook1.__dict__[i].nbook.__dict__[c] = QtGui.QScrollArea(fw)
                    vb.addWidget(self.configTab.notebook1.__dict__[i].nbook.__dict__[c])
                    self.configTab.notebook1.__dict__[i].nbook.__dict__[c].setWidgetResizable(False)
                    self.configTab.notebook1.__dict__[i].nbook.__dict__[c].flayout = QtGui.QFormLayout()
                    self.configTab.notebook1.__dict__[i].nbook.__dict__[c].flayoutC = QtGui.QWidget()
                    self.configTab.notebook1.__dict__[i].nbook.__dict__[c].flayoutC.setLayout(
                            self.configTab.notebook1.__dict__[i].nbook.__dict__[c].flayout)
                    self.configTab.notebook1.__dict__[i].nbook.__dict__[c].flayout.setSizeConstraint(QtGui.QLayout.SetFixedSize);
                    self.configTab.notebook1.__dict__[i].nbook.__dict__[c].setWidget(
                            self.configTab.notebook1.__dict__[i].nbook.__dict__[c].flayoutC)
                    self.configTab.notebook1.__dict__[i].nbook.addTab(
                                        fw, c)
                self.configTab.notebook1.__dict__[i].nbook.__dict__[c].__dict__[n] = {}
                self.configTab.notebook1.__dict__[i].nbook.__dict__[c].__dict__[n][l] = QtGui.QLabel()
                self.configTab.notebook1.__dict__[i].nbook.__dict__[c].__dict__[n][l].setText(n)
                self.configTab.notebook1.__dict__[i].nbook.__dict__[c].__dict__[n][v] = QtGui.QLineEdit()
                self.configTab.notebook1.__dict__[i].nbook.__dict__[c].flayout.addRow(
                        self.configTab.notebook1.__dict__[i].nbook.__dict__[c].__dict__[n][l],
                        self.configTab.notebook1.__dict__[i].nbook.__dict__[c].__dict__[n][v])

    def quit(self, *args):
        quitProg(self.app)

if __name__ == "__main__":
    def _(t):
        return t
    from relinux import modloader, configutils
    import os
    app = QtGui.QApplication([])
    app.setStyleSheet(open("./stylesheet.css", "r").read())
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
    quitProg(app)
