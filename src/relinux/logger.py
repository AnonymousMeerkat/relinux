"""
Contains streams for logging information
@author: Anonymous Meerkat
"""

from relinux import config
from threading import RLock


# Set as quiet (nothing but the essential stream)
def quiet():
    config.EStatus = True
    config.IStatus = False
    config.VStatus = False
    config.VVStatus = False


# Set as normal (essential and info streams)
def normal():
    config.EStatus = True
    config.IStatus = True
    config.VStatus = False
    config.VVStatus = False


# Set as verbose (essential, info, and verbose streams)
def verbose():
    config.EStatus = True
    config.IStatus = True
    config.VStatus = True
    config.VVStatus = False


# Set as very-verbose (all streams)
def veryverbose():
    config.EStatus = True
    config.IStatus = True
    config.VStatus = True
    config.VVStatus = True


EBuffer = ""
IBuffer = ""
VBuffer = ""
VVBuffer = ""

# Logging presets
Error = "Error! "
Tab = "    "


# Generates a thread name string
def genTN(tn):
    return "[" + tn + "] "


# Log to essential stream
def logE(tn, text):
    if config.EStatus is True and not tn == "":
        RLock.acquire()
        text = tn + text
        EBuffer = EBuffer + text
        RLock.release()


# Log to info stream
def logI(tn, text):
    if config.IStatus is True and not tn == "":
        RLock.acquire()
        text = tn + text
        IBuffer = IBuffer + text
        RLock.release()


# Log to verbose stream
def logV(tn, text):
    if config.VStatus is True and not tn == "":
        RLock.acquire()
        text = tn + text
        VBuffer = VBuffer + text
        RLock.release()


# Log to very-verbose stream
def logVV(tn, text):
    if config.VVStatus is True and not tn == "":
        RLock.acquire()
        text = tn + text
        VVBuffer = VVBuffer + text
        RLock.release()
