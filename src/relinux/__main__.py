# -*- coding: utf-8 -*-
'''
Main relinux script
@author: Anonymous Meerkat <meerkatanonymous@gmail.com>
'''

# TODO: Clean this mess up!

import sys
import os
mainsrcdir = sys.path[0]
srcdir = os.path.abspath(os.path.join(mainsrcdir, os.pardir))
relinuxdir = os.path.abspath(os.path.join(srcdir, os.pardir))
sys.path.append(srcdir)
from relinux import config
import gettext
gettext.install(config.productunix, config.localedir, config.unicode)


def exitprog(exitcode = 0):
    sys.exit(exitcode)

def version():
    print(config.version_string)
    sys.exit()

aptops = 4
captop = 0
minis = 0.0

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
    tkname = "Tkinter"
    if config.python3:
        tkname = "tkinter"
    Tkinter = __import__(tkname)
    import time
    from relinux import gui, configutils, logger, aptutil, modloader, utilities, fsutil
    config.Arch = fsutil.getArch()
    logger.normal()
    config.GUIStream = utilities.eventStringIO()
    config.EFiles.append(config.GUIStream)
    config.IFiles.append(config.GUIStream)
    config.VFiles.append(config.GUIStream)
    #config.VVFiles.append(config.GUIStream)
    logger.logI(logger.genTN("Main"), logger.I, "Test")
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
    if args.showversion is True:
        version()
    if args.quiet is True:
        logger.quiet()
    if args.verbose is True or True:
        logger.verbose()
    if args.veryverbose is True:
        logger.veryverbose()
    modules = []
    aptcache = []
    cbuffer = {}
    root = Tkinter.Tk()
    App = None
    def startProg(splash):
        global modules, aptcache, cbuffer, App
        spprogn = 6
        spprog = 0
        def calcPercent(def2 = (spprog, spprogn)):
            return utilities.calcPercent(*def2)
        splash.setProgress(calcPercent((spprog, spprogn)), "Loading modules...")
        modules = modloader.getModules()
        spprog += 1
        splash.setProgress(calcPercent((spprog, spprogn)), "Parsing configuration...")
        #buffer1 = utilities.getBuffer(open(relinuxdir + "/relinux.conf"))
        #buffer2 = configutils.compress(buffer1)
        #cbuffer = configutils.parseCompressedBuffer(buffer2, relinuxdir + "/relinux.conf")
        cbuffer = configutils.parseFiles([relinuxdir + "/relinux.conf"])
        config.Configuration = cbuffer
        '''for i in configutils.beautify(buffer1):
            print(i)'''
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
            modloader.runModule(modloader.loadModule(i),
                                {"gui": App, "config": cbuffer, "aptcache": aptcache})
        spprog += 1
        splash.setProgress(calcPercent((spprog, spprogn)), "Launching relinux")
    splash = gui.Splash(root, startProg)
    #root.overrideredirect(Tkinter.TRUE) # Coming soon!
    root.mainloop()
    config.ThreadStop = True

if __name__ == '__main__':
    main()
