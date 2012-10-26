# -*- coding: utf-8 -*-
'''
Utilities to manage configuration files
@author: Anonymous Meerkat <meerkatanonymous@gmail.com>
'''

import re
from relinux import config, utilities, fsutil
import os
import glob
import copy

# Codes
excludes = "EXCLUDES"
preseed = "PRESEED"
memtest = "MEMTEST"
isolinuxfile = "ISOLINUX"
label = "CDLABEL"
url = "CDURL"
splash = "SPLASHIMAGE"
timeout = "TIMEOUT"
remafterinst = "REMOVEAFTERINSTALL"
username = "USERNAME"
userfullname = "USERSNAME"
host = "HOSTNAME"
casperquiet = "CASPERQUIET"
flavour = "FLAVOUR"
sysname = "SYSNAME"
sysversion = "SYSVERSION"
codename = "SYSCODE"
description = "SYSDESC"
aptlistchange = "ALLOWAPTLISTCHANGE"
kernel = "KERNELVERSION"
sfscomp = "SFSCOMPRESSION"
sfsopts = "SFSOPTIONS"
isolevel = "ISOLEVEL"
enablewubi = "ENABLEWUBI"
isogenerator = "ISOGENERATOR"
isolocation = "ISOFILENAME"
unionfs = "UNIONFS"
popcon = "POPCON"
isodir = "ISODIR"
# Property codes
name = "Name"
desc = "Description"
category = "Category"
types = "Type"
value = "Value"
files = "__files__"

filename = "Filename"
yesno = "Yes/No"
multiple = "Multiple Values"
text = "Text"
choice = "Choice"

custom = "Custom"


# Returns an empty-line-cleaned version of the buffer
def cleanEmptyLines(buffers):
    patt = re.compile("^ *$")
    returnme = []
    for i in buffers:
        m = patt.match(i)
        if not utilities.checkMatched(m):
            returnme.append(i)
    return returnme


# Returns a flat version of the buffer (i.e. no indenting)
def unIndent(buffers):
    returnme = []
    for i in buffers:
        returnme.append(re.sub("^ *", "", i))
    return returnme


# Returns a comment-cleaned version of the buffer
def cleanComments(buffers):
    patt = re.compile("^ *#.*")
    returnme = []
    for i in buffers:
        m = patt.match(i)
        if not utilities.checkMatched(m):
            returnme.append(i)
    return returnme


# Returns a compressed version of the buffer
def compress(buffers):
    buffers = cleanComments(buffers)
    buffers = cleanEmptyLines(buffers)
    return unIndent(buffers)


# Returns the different sections of the buffer
def getSections(buffers):
    patt = re.compile("^ *Section *.*")
    returnme = []
    for i in buffers:
        m = patt.match(i)
        if utilities.checkMatched(m):
            returnme.append(i.split()[1].strip())
    return returnme


# Returns the options of the buffer
def getOptions(buffers):
    patt = re.compile("^ *Option *.*")
    returnme = []
    for i in buffers:
        m = patt.match(i)
        if utilities.checkMatched(m):
            returnme.append(i.split()[1].strip())
    return returnme


# Returns all lines within a section of the buffer (it will not parse them though)
def getLinesWithinSection(buffers, section):
    patt = re.compile("^ *Section *" + section + ".*")
    patte = re.compile("^ *EndSection *.*")
    returnme = []
    x = 0
    for i in buffers:
        m = patt.match(i)
        if utilities.checkMatched(m):
            if x == 1:
                break
            x = 1
            patt = patte
        else:
            if x == 1:
                returnme.append(i)
    return returnme


# Returns all lines within an option of the buffer (it will not parse them though)
def getLinesWithinOption(buffers, option):
    patt = re.compile("^ *Option *" + option + ".*")
    patte = re.compile("^ *EndOption *.*")
    returnme = []
    x = 0
    for i in buffers:
        m = patt.match(i)
        if utilities.checkMatched(m):
            if x == 1:
                break
            x = 1
            patt = patte
        else:
            if x == 1:
                returnme.append(i)
    return returnme


# Returns the parsed properties in a dictionary (the buffer has to be compressed though)
def getProperties(buffers):
    patt = re.compile(r"^ *(.*?):.*")
    returnme = {}
    for i in buffers:
        m = patt.match(i)
        if utilities.checkMatched(m):
            returnme[m.group(1)] = getProperty(buffers, m.group(1))
    return returnme


# Returns the value for an property (it will only show the first result, so you have to run getLinesWithinOption)
def getProperty(buffers, option):
    patt = re.compile("^ *" + option + " *:(.*)")
    for i in buffers:
        m = patt.match(i)
        if utilities.checkMatched(m):
            return m.group(1).strip()
    return ""


# Returns the kernel list
def getKernelList():
    files = glob.glob(os.path.join("/boot/", "initrd.img*"))
    utilities.sort(files)
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
def _getKernel(t, kernelVersion = None):
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
    return os.popen("uname -r").read().strip()


# Returns the kernel specified by the buffer
def getKernel(buffer1):
    buffers = buffer1.lower()
    if buffers == "current":
        return _getKernel(3)
    if buffers == "newest" or buffers == "latest":
        return _getKernel(1)
    if buffers == "oldest":
        return _getKernel(2)
    return _getKernel(0, buffers)


# Temporary key for saving
def saveSort(l):
        if l == name:
            return "a"
        elif l == desc:
            return "b"
        elif l == types:
            return "c"
        elif l == category:
            return "d"
        elif l == value:
            return "e"
        else:
            return l


# Returns a human-readable version of a compressed buffer (if it isn't compressed, it will look weird)
def beautify(buffers):
    returnme = []
    #returnme.append("# " + config.product + " Configuration File")
    returnme.append("")
    returnme.append("")
    for i in utilities.sort(getSections(buffers)):
        returnme.append("Section " + i)
        returnme.append("")
        returnme.append("")
        buffer1 = getLinesWithinSection(buffers, i)
        for x in utilities.sort(getOptions(buffer1)):
            returnme.append("  Option " + x)
            returnme.append("")
            opts = getProperties(getLinesWithinOption(buffer1, x))
            for y in sorted(list(opts.keys()), key = saveSort):
                returnme.append("    " + y + ": " + opts[y])
            returnme.append("")
            returnme.append("  EndOption")
            returnme.append("")
            returnme.append("")
        returnme.append("EndSection")
        returnme.append("")
        returnme.append("")
    return returnme


# Parses a complete compressed configuration file
# Returns a dictionary of dictionaries of dictionaries
# Dict1 = Sections
# Dict2 = Options
# Dict3 = Properties
# Notes: This will take a lot of RAM, and it will take a relatively long time (around 1-3 secs)
#        Try to only use this function once, and distribute the result to the functions who need this
def parseCompressedBuffer(buffers, filename_):
    returnme = {}
    for i in getSections(buffers):
        returnme[i] = {}
        liness = getLinesWithinSection(buffers, i)
        for x in getOptions(liness):
            returnme[i][x] = getProperties(getLinesWithinOption(liness, x))
            if returnme[i][x][types] == filename:
                if not os.path.isabs(returnme[i][x][value]):
                    returnme[i][x][value] = os.path.abspath(
                                                os.path.join(
                                                    os.path.dirname(os.path.abspath(filename_)),
                                                        returnme[i][x][value]))
    return returnme


def parseCompressedBuffers(buffers, filenames):
    returnme = {}
    for i_ in range(len(filenames)):
        temp = parseCompressedBuffer(buffers[i_], filenames[i_])
        fn = filenames[i_]
        for i in temp.keys():
            if not i in returnme:
                returnme[i] = {}
            for x in temp[i].keys():
                if not x in returnme[i]:
                    temp[i][x][files] = [os.path.abspath(fn)]
                    returnme[i][x] = temp[i][x]
                    continue
                for y in temp[i][x].keys():
                    returnme[i][x][y] = temp[i][x][y]
                if not files in returnme[i][x]:
                    returnme[i][x][files] = [os.path.abspath(fn)]
                else:
                    returnme[i][x][files].append(os.path.abspath(fn))
    return returnme


def parseFiles(filenames):
    buffers = []
    for i in filenames:
        buffers.append(compress(utilities.getBuffer(open(i))))
    return parseCompressedBuffers(buffers, filenames)


# Returns a compressed buffer from a parsed buffer
# This is the opposite of parseCompressedBuffer
def compressParsedBuffer(buffers):
    returnme = []
    for i in utilities.sort(list(buffers.keys())):
        returnme.append("Section " + i)
        for x in utilities.sort(list(buffers[i].keys())):
            returnme.append("Option " + x)
            for y in sorted(list(buffers[i][x].keys()), key = saveSort):
                returnme.append(y + ": " + buffers[i][x][y])
            returnme.append("EndOption")
        returnme.append("EndSection")
    return returnme


def saveBuffer(buffers_):
    buffers = copy.deepcopy(buffers_)
    # First step: Sort the items into the files
    files_ = {}
    for i in buffers.keys():
        for x in buffers[i].keys():
            for f in buffers[i][x][files]:
                if not f in files_:
                    files_[f] = {}
                if not i in files_[f]:
                    files_[f][i] = {}
                if not x in files_[f][i]:
                    files_[f][i][x] = {}
            lastfile = os.path.dirname(os.path.abspath(buffers[i][x][files][len(buffers[i][x][files]) - 1]))
            if buffers[i][x][types] == filename:
                buffers[i][x][value] = os.path.relpath(buffers[i][x][value], lastfile)
            '''if buffers[i][x][types] == filename and os.path.dirname(buffers[i][x][value]) == lastfile:
                temp = fsutil.beautifypath(os.curdir + "/" + buffers[i][x][value][len(lastfile):])
                buffers[i][x][value] = temp'''
            for y in buffers[i][x].keys():
                if y == files:
                    continue
                for f in buffers[i][x][files]:
                    files_[f][i][x][y] = buffers[i][x][y]
    # Second step: Compress it into a non-beautified configuration file
    for i in files_.keys():
        temp = compressParsedBuffer(files_[i])
        files_[i] = temp
    # Third step: Beautify it
    for i in files_.keys():
        temp = beautify(files_[i])
        files_[i] = temp
    # Fourth step: Save it
    for i in files_.keys():
        fh = open(i, "w")
        for i in files_[i]:
            fh.write(i + "\n")
        fh.close()

# Option parsing
#################


# Finds the value of a property (buffer is the parsed getProperties buffer)
def getValueP(buffers, propertys):
    for i in buffers.keys():
        if i.lower() == propertys.lower():
            return buffers[i]
    return None


# Returns the value of an option
def getValue(buffers):
    return getValueP(buffers, value)


# Returns a boolean (None if not a boolean)
def parseBoolean(option):
    loption = option.lower()[0]
    if loption == "t" or loption == "y":
        return True
    elif loption == "f" or loption == "n":
        return False
    else:
        return None


# Returns a list from a Multiple Value value
def parseMultipleValues(option):
    return option.split(" ")


# Returns a parsed choice list (None if not a choice list, buffer must be the value of the Type option)
def getChoices(buffers):
    returnme = []
    patt = re.compile("^ *" + choice + " *: *(.*)")
    m = patt.match(buffers.strip())
    if utilities.checkMatched(m):
        for i in m.group(1).split(","):
            si = i.strip()
            returnme.append(si)
    else:
        return None
    return returnme


# Returns a parsed multiple values list (buffer must be the value)
def getMultipleValues(buffers):
    returnme = []
    patt = re.compile("^ *(.*)")
    m = patt.match(buffers.strip())
    if utilities.checkMatched(m):
        for i in m.group(1).split():
            si = i.strip()
            returnme.append(si)
    return returnme
