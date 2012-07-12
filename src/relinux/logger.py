"""
Contains streams for logging information
@author: Anonymous Meerkat
"""

from relinux import config
import sys
#from threading import RLock


# Remove console output from a certain stream
def remConsoleOutput(stream):
    consolestreams = [sys.stderr, sys.stdout]
    for i in stream:
        if i in consolestreams:
            stream.remove(i)


# Set as quiet (nothing but the essential stream)
def quiet():
    config.EStatus = True
    config.WStatus = False
    config.IStatus = False
    config.VStatus = False
    config.VVStatus = False


# Set as normal (essential and info streams)
def normal():
    config.EStatus = True
    config.WStatus = False
    config.IStatus = True
    config.VStatus = False
    config.VVStatus = False


# Set as verbose (essential, info, warning, and verbose streams)
def verbose():
    config.EStatus = True
    config.WStatus = True
    config.IStatus = True
    config.VStatus = True
    config.VVStatus = False


# Set as very-verbose (all streams)
def veryverbose():
    config.EStatus = True
    config.WStatus = True
    config.IStatus = True
    config.VStatus = True
    config.VVStatus = True


'''EBuffer = ""
IBuffer = ""
WBuffer = ""
VBuffer = ""
VVBuffer = ""'''

# Logging presets
MError = "Error! "
MWarning = "Warning! "
MTab = "    "
MNewline = "\n"


# Writes in all files in list
def writeAll(lists, text):
    for i in lists:
        i.write(text)


# Generates a thread name string
def genTN(tn):
    return "[" + tn + "] "


# Log to error stream
def logE(tn, text):
    if config.EStatus is True and not tn == "":
        #RLock.acquire()
        text = tn + text
        writeAll(config.EFiles, text + MNewline)
        #RLock.release()


# Log to info stream
def logI(tn, text):
    if config.IStatus is True and not tn == "":
        #RLock.acquire()
        text = tn + text
        writeAll(config.IFiles, text + MNewline)
        #RLock.release()


# Log to warning stream
def logW(tn, text):
    if config.IStatus is True and not tn == "":
        #RLock.acquire()
        text = tn + text
        writeAll(config.WFiles, text + MNewline)
        #RLock.release()


# Log to verbose stream
def logV(tn, text):
    if config.VStatus is True and not tn == "":
        #RLock.acquire()
        text = tn + text
        writeAll(config.VFiles, text + MNewline)
        #RLock.release()


# Log to very-verbose stream
def logVV(tn, text):
    if config.VVStatus is True and not tn == "":
        #RLock.acquire()
        text = tn + text
        writeAll(config.VVFiles, text + MNewline)
        #RLock.release()
