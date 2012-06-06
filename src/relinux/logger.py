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

# Log to essential stream
def logE(text):
    if config.EStatus is True:
        RLock.acquire()
        EBuffer = EBuffer + text
        RLock.release()

# Log to info stream
def logI(text):
    if config.IStatus is True:
        RLock.acquire()
        IBuffer = IBuffer + text
        RLock.release()

# Log to verbose stream
def logV(text):
    if config.VStatus is True:
        RLock.acquire()
        VBuffer = VBuffer + text
        RLock.release()

# Log to very-verbose stream
def logVV(text):
    if config.VVStatus is True:
        RLock.acquire()
        VVBuffer = VVBuffer + text
        RLock.release()
