'''
Main relinux script
@author: Anonymous Meerkat
'''
from argparse import ArgumentParser
from lib import config, gui
import Tkinter

def version():
    print(config.VERSION_STRING)

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
    root = Tkinter.Tk()
    App = gui.GUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
