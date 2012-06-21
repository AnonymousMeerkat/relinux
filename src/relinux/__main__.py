'''
Main relinux script
@author: Anonymous Meerkat
'''

import sys
# Just in case, we will append both this directory and the directory higher than us
sys.path.append("..")
sys.path.append(".")
from relinux import config, gui, configutils
#from .lib import *
from argparse import ArgumentParser
import tkinter


def version():
    print((config.version_string))
    sys.exit()


def main():
    parser = ArgumentParser()
    parser.add_argument("-V", "--version", action="store_true",
                      dest="showversion",
                      help="show version info")
    parser.add_argument("-q", "--quiet",
                  action="store_true", dest="quiet", default=False,
                  help="don't print status messages to stdout")
    parser.add_argument("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print verbose")
    args = parser.parse_args()
    if args.__dict__["showversion"] == True:
        version()
    if args.__dict__["quiet"] == True:
        config.IStatus = False
    if args.__dict__["verbose"] == True:
        config.VStatus = True
    buffer1 = configutils.getBuffer(open("../../relinux.conf"))
    buffer2 = configutils.compress(buffer1)
    buffer = configutils.parseCompressedBuffer(buffer2)
    '''for i in configutils.beautify(buffer1):
        print(i)'''
    root = tkinter.Tk()
    App = gui.GUI(root)
    App.fillConfiguration(buffer)
    root.mainloop()

if __name__ == '__main__':
    main()
