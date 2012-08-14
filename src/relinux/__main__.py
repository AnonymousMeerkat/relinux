'''
Main relinux script
@author: Anonymous Meerkat <meerkatanonymous@gmail.com>
'''

# TODO: Clean this mess up!

import sys
# Just in case, we will append both this directory and the directory higher than us
sys.path.append("..")
sys.path.append(".")
from relinux import config
import gettext
gettext.install(config.productunix, config.localedir, config.unicode)
from argparse import ArgumentParser
import Tkinter
import time


def exitprog():
    sys.exit()

def version():
    print((config.version_string))
    sys.exit()

aptops = 4
captop = 0
minis = 0.0

def main():
    logger.normal()
    parser = ArgumentParser()
    parser.add_argument("-V", "--version", action="store_true",
                      dest="showversion",
                      help="show version info")
    parser.add_argument("-q", "--quiet",
                  action="store_true", dest="quiet", default=False,
                  help="log as little as possible to stdout")
    parser.add_argument("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="log more to stdout")
    parser.add_argument("-vv", "--veryverbose",
                  action="store_true", dest="veryverbose", default=False,
                  help="log even more to stdout")
    args = parser.parse_args()
    if args.showversion is True:
        version()
    if args.quiet is True:
        logger.quiet()
    if args.verbose is True:
        logger.verbose()
    if args.veryverbose is True:
        logger.veryverbose()
    modules = []
    aptcache = []
    cbuffer = {}
    root = Tkinter.Tk()
    App = None
    def startProg(splash):
        global modules, aptcache, cbuffer
        spprogn = 6
        spprog = 0
        def calcSubPercent(p, p1):
            ans = float(float(p) / p1)
            return ans
        def calcPercent(def2=(spprog, spprogn)):
            ans = float(float(calcSubPercent(*def2)) * float(100))
            return ans
        splash.setProgress(calcPercent((spprog, spprogn)), "Loading modules...")
        modules = modloader.getModules()
        spprog += 1
        splash.setProgress(calcPercent((spprog, spprogn)), "Parsing configuration...")
        buffer1 = configutils.getBuffer(open("../../relinux.conf"))
        buffer2 = configutils.compress(buffer1)
        cbuffer = configutils.parseCompressedBuffer(buffer2)
        '''for i in configutils.beautify(buffer1):
            print(i)'''
        spprog += 1
        splash.setProgress(calcPercent((spprog, spprogn)), "Reading APT Cache...")
        def aptupdate(op, percent):
            global minis
            if percent != None:
                minis += calcSubPercent(percent, 100)
            splash.setProgress(calcPercent((calcSubPercent(minis + captop, aptops) + spprog, spprogn)),
                               "Reading APT Cache... (" + op + ")")
        def aptdone(op):
            global minis, captop
            minis = 0.0
            captop += 1
        aptcache = aptutil.getCache(aptutil.OpProgress(aptupdate, aptdone))
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

if __name__ == '__main__':
    from relinux import gui, configutils, logger, aptutil, modloader
    main()
