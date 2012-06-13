"""
Contains streams for logging information
@author: Anonymous Meerkat
"""

from relinux import config
from threading import RLock

EBuffer = ""
IBuffer = ""
VBuffer = ""
VVBuffer = ""


# Generates a thread name string
def genTN(tn):
    return "[" + tn + "] "


# Log to essential stream
def logE(tn, text):
    if config.EStatus is True:
        RLock.acquire()
        text = tn + text
        EBuffer = EBuffer + text
        RLock.release()


# Log to info stream
def logI(tn, text):
    if config.IStatus is True:
        RLock.acquire()
        text = tn + text
        IBuffer = IBuffer + text
        RLock.release()


# Log to verbose stream
def logV(tn, text):
    if config.VStatus is True:
        RLock.acquire()
        text = tn + text
        VBuffer = VBuffer + text
        RLock.release()


# Log to very-verbose stream
def logVV(tn, text):
    if config.VVStatus is True:
        RLock.acquire()
        text = tn + text
        VVBuffer = VVBuffer + text
        RLock.release()
