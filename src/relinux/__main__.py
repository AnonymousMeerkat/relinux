# -*- coding: utf-8 -*-
'''
Main relinux script
@author: Anonymous Meerkat <meerkatanonymous@gmail.com>
'''

# TODO: Clean this mess up!

import sys
import os
from PyQt4 import QtGui, QtCore
mainsrcdir = sys.path[0]
srcdir = os.path.abspath(os.path.join(mainsrcdir, os.pardir))
relinuxdir = os.path.abspath(os.path.join(srcdir, os.pardir))
sys.path.append(srcdir)
from relinux import config
import gettext
gettext.install(config.productunix, config.localedir, config.unicode)

config.about_string = (config.product + _(" is a free and open-source Linux ") +
_("distribution creation toolkit.\n\nRelinux ") + config.version +
_(" is written and maintained by ") + config.author_string + _("."))


def exitprog(exitcode = 0):
    sys.exit(exitcode)

def version():
    print(config.version_string)
    sys.exit()

aptops = 4
captop = 0
minis = 0

def main():
    def parsePyHex(string1):
        string = "%x" % string1
        count = 0
        result = ""
        for char in string:
            if count == 0 or count == 2 or count == 4:
                result += char
                if count != 4:
                    result += "."
            elif count == 5:
                if char.lower() == "f":
                    break
                else:
                    result += char.lower()
            elif count == 6:
                result += char
            count += 1
        return result
    if not config.python_ok:
        print(_("Relinux only supports python ") + parsePyHex(config.min_python_version) + "-" +
              parsePyHex(config.max_python_version) + ", " + _("but python ") +
              parsePyHex(sys.hexversion) + " " + _("was used."))
        exitprog(1)
    from argparse import ArgumentParser
    '''tkname = "Tkinter"
    if config.python3:
        tkname = "tkinter"
    Tkinter = __import__(tkname)'''
    #import time
    from relinux import gui, configutils, logger, aptutil, modloader, utilities, fsutil
    config.Arch = fsutil.getArch()
    logger.normal()
    config.GUIStream = utilities.eventStringIO()
    tn = logger.genTN("Main")
    parser = ArgumentParser(prog = "relinux", usage = "%(prog)s [options]")
    parser.add_argument("-V", "--version", action = "store_true",
                      dest = "showversion",
                      help = "show version info")
    parser.add_argument("-q", "--quiet",
                  action = "store_true", dest = "quiet", default = False,
                  help = "log as little as possible to stdout")
    parser.add_argument("-v", "--verbose",
                  action = "store_true", dest = "verbose", default = False,
                  help = "log more to stdout")
    parser.add_argument("-vv", "--veryverbose",
                  action = "store_true", dest = "veryverbose", default = False,
                  help = "log even more to stdout")
    args = parser.parse_args()
    config.EFiles.extend([config.GUIStream, sys.stdout])
    if args.showversion:
        version()
    if not args.quiet:
        config.IFiles.extend([config.GUIStream, sys.stdout])
    if args.verbose:
        config.VFiles.extend([config.GUIStream, sys.stdout])
    if args.veryverbose:
        config.VVFiles.extend([config.GUIStream, sys.stdout])
    #modules = []
    #aptcache = []
    #cbuffer = {}
    '''root = Tkinter.Tk()
    App = None
    def startProg(splash):
        global modules, aptcache, cbuffer, App
        spprogn = 6
        spprog = 0
        def calcPercent(def2 = (spprog, spprogn)):
            return utilities.calcPercent(*def2)
        splash.setProgress(calcPercent((spprog, spprogn)), "Loading modules...")
        modules = []
        modulemetas = modloader.getModules()
        for i in modulemetas:
            modules.append(modloader.loadModule(i))
        spprog += 1
        splash.setProgress(calcPercent((spprog, spprogn)), "Parsing configuration...")
        #buffer1 = utilities.getBuffer(open(relinuxdir + "/relinux.conf"))
        #buffer2 = configutils.compress(buffer1)
        #cbuffer = configutils.parseCompressedBuffer(buffer2, relinuxdir + "/relinux.conf")
        configfiles = [relinuxdir + "/relinux.conf"]
        for i in range(len(modulemetas)):
            for x in modules[i].moduleconfig:
                configfiles.append(os.path.join(os.path.dirname(modulemetas[i]["path"]), x))
        cbuffer = configutils.parseFiles(configfiles)
        config.Configuration = cbuffer
        configutils.saveBuffer(config.Configuration)
        \'''for i in configutils.beautify(buffer1):
            print(i)\'''
        spprog += 1
        splash.setProgress(calcPercent((spprog, spprogn)), "Reading APT Cache...")
        def aptupdate(op, percent):
            global minis
            if percent != None:
                minis += utilities.floatDivision(percent, 100)
            splash.setProgress(calcPercent((utilities.floatDivision(minis + captop, aptops) + spprog, spprogn)),
                               "Reading APT Cache... (" + op + ")")
        def aptdone(op):
            global minis, captop
            minis = 0.0
            captop += 1
        aptcache = aptutil.getCache(aptutil.OpProgress(aptupdate, aptdone))
        config.AptCache = aptcache
        spprog += 1
        splash.setProgress(calcPercent((spprog, spprogn)), "Loading the GUI...")
        App = gui.GUI(root)
        spprog += 1
        splash.setProgress(calcPercent((spprog, spprogn)), "Filling in configuration...")
        App.fillConfiguration(cbuffer)
        spprog += 1
        splash.setProgress(calcPercent((spprog, spprogn)), "Running modules...")
        for i in modules:
            modloader.runModule(i,
                                {"gui": App, "config": cbuffer, "aptcache": aptcache})
        spprog += 1
        splash.setProgress(calcPercent((spprog, spprogn)), "Launching relinux")
    splash = gui.Splash(root, startProg)
    #root.overrideredirect(Tkinter.TRUE) # Coming soon!
    root.mainloop()'''
    App = QtGui.QApplication(sys.argv)
    splash = QtGui.QSplashScreen(QtGui.QPixmap(relinuxdir + "/splash_light.png"))
    splash.show()
    App.processEvents()
    def showMessage(str_):
        splash.showMessage(str_ + "...", QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        App.processEvents()
    showMessage(_("Loading modules"))
    modules = []
    modulemetas = modloader.getModules()
    for i in modulemetas:
        modules.append(modloader.loadModule(i))
    showMessage(_("Loading configuration files"))
    configfiles = [relinuxdir + "/relinux.conf"]
    for i in range(len(modulemetas)):
        for x in modules[i].moduleconfig:
            configfiles.append(os.path.join(os.path.dirname(modulemetas[i]["path"]), x))
    cbuffer = configutils.parseFiles(configfiles)
    config.Configuration = cbuffer
    configutils.saveBuffer(config.Configuration)
    logfilename = configutils.getValue(cbuffer["Relinux"]["LOGFILE"])
    logfile = open(logfilename, "a")
    config.EFiles.append(logfile)
    config.IFiles.append(logfile)
    config.VFiles.append(logfile)
    config.VVFiles.append(logfile)
    logger.logI(tn, logger.I, "===========================")
    logger.logI(tn, logger.I, "=== Started new session ===")
    logger.logI(tn, logger.I, "===========================")
    showMessage(_("Loading APT cache 0%"))
    def aptupdate(op, percent):
        global minis
        if percent:
            minis = int(percent)
        showMessage(_("Loading APT cache") + " (" + op + ") " + str(minis) + "%")
    aptcache = aptutil.getCache(aptutil.OpProgress(aptupdate, None))
    config.AptCache = aptcache
    showMessage(_("Loading stylesheet"))
    App.setStyleSheet(open(mainsrcdir + "/stylesheet.css", "r").read())
    showMessage(_("Loading GUI"))
    gui_ = gui.GUI(App)
    config.Gui = gui_
    showMessage(_("Running modules"))
    for i in modules:
            modloader.runModule(i, {})
    gui_.show()
    splash.finish(gui_)
    exitcode = App.exec_()
    config.ThreadStop = True
    logfile.close()
    sys.exit(exitcode)

if __name__ == '__main__':
    main()
