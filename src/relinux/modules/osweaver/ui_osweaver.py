# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'modules/osweaver/osweaver.ui'
#
# Created: Thu Nov  1 16:44:11 2012
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_OSWeaver(object):
    def setupUi(self, OSWeaver):
        OSWeaver.setObjectName(_fromUtf8("OSWeaver"))
        OSWeaver.resize(400, 300)
        self.gridLayout = QtGui.QGridLayout(OSWeaver)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.selall = QtGui.QPushButton(OSWeaver)
        self.selall.setObjectName(_fromUtf8("selall"))
        self.gridLayout.addWidget(self.selall, 2, 0, 1, 1)
        self.nodependslabel = QtGui.QLabel(OSWeaver)
        self.nodependslabel.setObjectName(_fromUtf8("nodependslabel"))
        self.gridLayout.addWidget(self.nodependslabel, 0, 0, 1, 1)
        self.nodepends = QtGui.QCheckBox(OSWeaver)
        self.nodepends.setText(_fromUtf8(""))
        self.nodepends.setObjectName(_fromUtf8("nodepends"))
        self.gridLayout.addWidget(self.nodepends, 0, 1, 1, 1)
        self.selnone = QtGui.QPushButton(OSWeaver)
        self.selnone.setObjectName(_fromUtf8("selnone"))
        self.gridLayout.addWidget(self.selnone, 2, 1, 1, 1)
        self.togsel = QtGui.QPushButton(OSWeaver)
        self.togsel.setObjectName(_fromUtf8("togsel"))
        self.gridLayout.addWidget(self.togsel, 2, 2, 1, 1)
        self.startbutton = QtGui.QPushButton(OSWeaver)
        self.startbutton.setObjectName(_fromUtf8("startbutton"))
        self.gridLayout.addWidget(self.startbutton, 3, 0, 1, 3)
        self.notroot = QtGui.QLabel(OSWeaver)
        self.notroot.setObjectName(_fromUtf8("notroot"))
        self.gridLayout.addWidget(self.notroot, 5, 0, 1, 3)
        self.progress = QtGui.QProgressBar(OSWeaver)
        self.progress.setProperty("value", 0)
        self.progress.setObjectName(_fromUtf8("progress"))
        self.gridLayout.addWidget(self.progress, 6, 0, 1, 3)
        self.terminal = QtGui.QPlainTextEdit(OSWeaver)
        self.terminal.setEnabled(True)
        self.terminal.setReadOnly(True)
        self.terminal.setProperty("text", _fromUtf8(""))
        self.terminal.setObjectName(_fromUtf8("terminal"))
        self.gridLayout.addWidget(self.terminal, 8, 0, 1, 3)
        self.threadstorun = QtGui.QGroupBox(OSWeaver)
        self.threadstorun.setObjectName(_fromUtf8("threadstorun"))
        self.gridLayout_2 = QtGui.QGridLayout(self.threadstorun)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.gridLayout.addWidget(self.threadstorun, 1, 0, 1, 3)

        self.retranslateUi(OSWeaver)
        QtCore.QMetaObject.connectSlotsByName(OSWeaver)

    def retranslateUi(self, OSWeaver):
        OSWeaver.setWindowTitle(QtGui.QApplication.translate("OSWeaver", "OSWeaver", None, QtGui.QApplication.UnicodeUTF8))
        self.selall.setText(QtGui.QApplication.translate("OSWeaver", "Select All", None, QtGui.QApplication.UnicodeUTF8))
        self.nodependslabel.setText(QtGui.QApplication.translate("OSWeaver", "Ignore dependencies", None, QtGui.QApplication.UnicodeUTF8))
        self.selnone.setText(QtGui.QApplication.translate("OSWeaver", "Select None", None, QtGui.QApplication.UnicodeUTF8))
        self.togsel.setText(QtGui.QApplication.translate("OSWeaver", "Toggle All", None, QtGui.QApplication.UnicodeUTF8))
        self.startbutton.setText(QtGui.QApplication.translate("OSWeaver", "Start!", None, QtGui.QApplication.UnicodeUTF8))
        self.notroot.setText(QtGui.QApplication.translate("OSWeaver", "You are not root!", None, QtGui.QApplication.UnicodeUTF8))
        self.threadstorun.setTitle(QtGui.QApplication.translate("OSWeaver", "Threads to run:", None, QtGui.QApplication.UnicodeUTF8))

