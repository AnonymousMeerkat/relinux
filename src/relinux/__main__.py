'''
Main relinux script
@author: Anonymous Meerkat
'''
from relinux import config, gui, configutils
#sys.path.append("./lib/.")
#from .lib import *
from argparse import ArgumentParser
from tkinter import *

def version():
    print((config.version_string))

def main():
    parser = ArgumentParser()
    parser.add_argument("-v", "--version", action="store_true",
                      dest="showversion",
                      help="show version info")
    parser.add_argument("-q", "--quiet",
                  action="store_false", dest="verbose", default=True,
                  help="don't print status messages to stdout")
    args = parser.parse_args()
    if args.__dict__["showversion"] is True:
        version()
    if args.__dict__["verbose"] is False:
        config.IStatus = False
    buffer = configutils.getBuffer(open("../../fastweaver.conf"))
    buffer1 = configutils.compress(buffer)
    for i in configutils.beautify(buffer1):
        print(i)
    root = Tk()
    App = gui.GUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
