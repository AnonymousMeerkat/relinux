'''
Main relinux script
@author: Anonymous Meerkat
'''

import sys
# Just in case, we will append both this directory and the directory higher than us
sys.path.append("..")
sys.path.append(".")
from relinux import config
import gettext
gettext.install(config.productunix, config.localedir, config.unicode)
from relinux import gui, configutils, logger, modloader
modules = modloader.getModules()
#from .lib import *
from argparse import ArgumentParser
import tkinter


def version():
    print((config.version_string))
    sys.exit()


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
    buffer1 = configutils.getBuffer(open("../../relinux.conf"))
    buffer2 = configutils.compress(buffer1)
    buffer = configutils.parseCompressedBuffer(buffer2)
    '''for i in configutils.beautify(buffer1):
        print(i)'''
    root = tkinter.Tk()
    App = gui.GUI(root)
    App.fillConfiguration(buffer)
    for i in modules:
        modloader.runModule(modloader.loadModule(i), {"gui": App, "config": buffer})
    root.mainloop()

if __name__ == '__main__':
    main()
