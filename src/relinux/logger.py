# -*- coding: utf-8 -*-
"""
Contains streams for logging information
@author: Anonymous Meerkat <meerkatanonymous@gmail.com>
"""

from relinux import config
import copy
#from threading import RLock


# Remove console output from a certain stream
def remConsoleOutput(stream):
    for i in stream:
        if i in config.TermStreams:
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
MDebug = "Debug: "
MTab = "    "
MNewline = "\n"
E = "E"
W = "W"
I = "I"
D = "D"
V = "V"
VV = "VV"


# Writes in all files in list (plus formats the text)
def writeAll(status, lists, tn, importance, text, **options):
    if tn == "" or tn == None or not status:
        return
    text_ = "[" + tn + "] "
    if importance == E:
        text_ += MError
    elif importance == W:
        text_ += MWarning
    elif importance == D:
        text_ += MDebug
    else:
        text_ += ""
    text__ = text_ + text
    text = text__
    for i in lists:
        if i in config.TermStreams and "noterm" in options and options["noterm"]:
            continue
        if i == config.GUIStream and "nogui" in options and options["nogui"]:
            continue
        text_ = copy.copy(text)
        if i in config.TermStreams:
            if hasattr(i, "writefunc"):
                print(True)
            text__ = "\033["
            if importance == E:
                text__ += str(config.TermRed)
            elif importance == W:
                text__ += str(config.TermYellow)
            elif importance == D:
                text__ += str(config.TermGreen)
            '''elif importance == I:
                text__ += config.TermBlue'''
            text__ += "m" + text_ + "\033[" + str(config.TermReset) + "m"
            text_ = text__
        i.write(text_ + MNewline)


# Generates a thread name string
def genTN(tn):
    return tn


# Log to a stream
def log(tn, stream, importance, text, **options):
    args = (tn, importance, text)
    if stream == E:
        logE(*args, **options)
    elif stream == I:
        logI(*args, **options)
    elif stream == V:
        logV(*args, **options)
    elif stream == VV:
        logVV(*args, **options)


# Log to essential stream
def logE(tn, importance, text, **options):
    writeAll(config.EStatus, config.EFiles, tn, importance, text, **options)


# Log to info stream
def logI(tn, importance, text, **options):
    writeAll(config.IStatus, config.IFiles, tn, importance, text, **options)


# Log to verbose stream
def logV(tn, importance, text, **options):
    writeAll(config.VStatus, config.VFiles, tn, importance, text, **options)


# Log to very-verbose stream
def logVV(tn, importance, text, **options):
    writeAll(config.VVStatus, config.VVFiles, tn, importance, text, **options)
