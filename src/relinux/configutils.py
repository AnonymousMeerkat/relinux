'''
Utilities to manage configuration files
@author: Anonymous Meerkat
'''

from re import *
from relinux import versionsort, config
import os
import glob

# Checks if it matched
def checkMatched(m):
    if m == None or m.group(0) == None:
        return False
    elif m != None and m.group(0) != None:
        return True
    else:
        return False

# Returns an empty-line-cleaned version of the buffer
def cleanEmptyLines(buffer):
    patt = compile("^ *$")
    returnme = []
    for i in buffer:
        m = patt.match(i)
        if not checkMatched(m):
            returnme.append(i)
    return returnme

# Returns a flat version of the buffer (i.e. no indenting)
def unIndent(buffer):
    returnme = []
    for i in buffer:
        returnme.append(sub("^ *", "", i))
    return returnme

# Returns a comment-cleaned version of the buffer
def cleanComments(buffer):
    patt = compile("^ *#.*")
    returnme = []
    for i in buffer:
        m = patt.match(i)
        if not checkMatched(m):
            returnme.append(i)
    return returnme

# Returns a compressed version of the buffer
def compress(buffer):
    buffer = cleanComments(buffer)
    buffer = cleanEmptyLines(buffer)
    return unIndent(buffer)

# Returns the different sections of the buffer
def getSections(buffer):
    patt = compile("^ *Section *.*")
    returnme = []
    for i in buffer:
        m = patt.match(i)
        if checkMatched(m):
            returnme.append(i.split()[1].strip())
    return returnme

# Returns all lines within a section of the buffer (it will not parse them though)
def getLinesWithinSection(buffer, section):
    patt = compile("^ *Section *" + section + ".*")
    patte = compile("^ *EndSection *.*")
    returnme = []
    x = 0
    for i in buffer:
        m = patt.match(i)
        if checkMatched(m):
            if x == 1:
                break
            x = 1
            patt = patte
        else:
            if x == 1:
                returnme.append(i)
    return returnme

# Returns the parsed options in a dictionary (the buffer has to be compressed though)
def getOptions(buffer):
    patt = compile(r"^(.*?):(.*)")
    returnme = {}
    for i in buffer:
        m = patt.match(i)
        if checkMatched(m):
            returnme[m.group(1)] = m.group(2).strip()
    return returnme

# Returns the value for an option (it will only show the first result, so you have to run getLinesWithinSection)
def getOption(buffer, option):
    patt = compile("^ *" + option + " *:.*")
    for i in buffer:
        m = patt.match(i)
        if checkMatched(m):
            return i.split(":")[1].strip()
    return ""

# Returns the kernel list
def getKernelList():
    files = glob.glob(os.path.join("/boot/", "initrd.img*"))
    versionsort.sort_nicely(files)
    returnme = []
    for i in files:
        # Sample kernel version: /boot/initrd.img-3.4.0-3-generic
        #                        0....5....0....5.7
        returnme.append(i[17:])
    return returnme

# Helper function for getKernel
# Types:
#    0 - custom kernel (provide kernelVersion)
#    1 - newest kernel
#    2 - oldest kernel (don't ask me why anyone would want this lol)
#    3 - current kernel
def _getKernel(t, kernelVersion=None):
    files = getKernelList()
    if t == 0:
        for i in files:
            if kernelVersion == i.lower():
                return kernelVersion
        return None
    if t == 1:
        files.reverse()
    if t == 1 or t == 2:
        return files[0]
    return os.popen("uname -r").read()

# Returns the kernel specified by the buffer
def getKernel(buffer1):
    buffer = buffer1.lower()
    if buffer == "current":
        return _getKernel(3)
    if buffer == "newest" or buffer == "latest":
        return _getKernel(1)
    if buffer == "oldest":
        return _getKernel(2)
    return _getKernel(0, buffer)

# Returns a human-readable version of a compressed buffer (if it isn't compressed, it will look weird)
def beautify(buffer):
    returnme = []
    returnme.append("# " + config.product + " Configuration File")
    returnme.append("")
    returnme.append("")
    for i in getSections(buffer):
        returnme.append("Section " + i)
        returnme.append("")
        buffer1 = getLinesWithinSection(buffer, i)
        opts = getOptions(buffer1)
        for i in opts.keys():
            returnme.append("  " + i + ": " + opts[i])
        returnme.append("")
        returnme.append("EndSection")
        returnme.append("")
        returnme.append("")
    return returnme
        
# Returns a buffer from a configuration file
def getBuffer(file):
    returnme = []
    for line in file:
        if not line or line == None:
            break
        returnme.append(line.rstrip())
    print(len(returnme))
    return returnme
