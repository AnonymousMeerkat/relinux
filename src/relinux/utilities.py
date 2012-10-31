# -*- coding: utf-8 -*-
'''
Random utilities
@author: Anonymous Meerkat <meerkatanonymous@gmail.com>
'''

from relinux import config
import io
import re


# Check if a string is ASCII or not
def is_ascii(s):
    for c in s:
        if ord(c) >= 128:
            return False
    return True


# Convert a string to UTF-8
def utf8(string):
    if not config.python3:
        if isinstance(string, unicode):
            return string.encode("utf-8")
    if not isinstance(string, str):
        if config.python3 and isinstance(string, bytes):
            string_ = string.decode("utf-8")
            string = string_
        else:
            string_ = str(string)
            string = string_
    if not is_ascii(string):
        if config.python3:
            return string
        return string.decode("utf-8").encode("utf-8")
    return string


# List flattener, based on: http://stackoverflow.com/a/4676482/999400
def flatten(list_):
    nested = True
    while nested:
        iter_ = False
        temp = []
        for element in list_:
            if isinstance(element, list):
                temp.extend(element)
                iter_ = True
            else:
                temp.append(element)
        nested = iter_
        list_ = temp[:]
    return list_


# Joins sections together with a custom character
def join(arr1, char):
    arr = flatten(arr1)
    returnme = ""
    c = 0
    l = len(arr) - 1
    for i in arr:
        if c < l:
            returnme = returnme + i + char
        else:
            returnme = returnme + i
        c = c + 1
    return returnme


# Runs a function on all of the arguments
def runall(func, *args):
    returnme = []
    for i in args:
        returnme.append(func(i))
    return returnme


# UTF-8's a string and returns it
def utf8all(*args):
    if config.python3:
        # Save some time
        return join(args, "")
    return join(runall(utf8, *args), "")


# Sets the default arguments for a dictionary
def setDefault(lists, **kw):
    for i in kw.keys():
        if not i in lists:
            lists[i] = kw[i]


# Checks if regex matched
def checkMatched(m):
    if m is not None and m.group(0) is not None:
        return True
    else:
        return False


# Returns a buffer from a file
def getBuffer(files, strip = True):
    returnme = []
    for line in files:
        if not line or line is None:
            break
        if strip is True:
            line = line.rstrip()
        returnme.append(line)
    return returnme


# Removes duplicates from an array and returns the result
def remDuplicates(arr):
    returnme = []
    for i in arr:
        if not i in returnme:
            returnme.append(i)
    return returnme

# Event-based StringIO
class eventStringIO(io.StringIO):
    def __init__(self):
        io.StringIO.__init__(self)
        self.writefunc = []

    def write(self, msg):
        if config.python3 or isinstance(msg, unicode):
            io.StringIO.write(self, msg)
        else:
            io.StringIO.write(msg.decode("utf-8"))
        if self.writefunc:
            if isinstance(self.writefunc, list):
                for i in self.writefunc:
                    i(msg)
            else:
                self.writefunc(msg)

# Float division for Python 2
def floatDivision(p, p1):
    if config.python3:
        return p / p1
    return float(float(p) / float(p1))

# Percent calculation
def calcPercent(first, second):
    if config.python3:
        return first / second * 100
    return float(float(floatDivision(first, second)) * float(100))


# Alphabetical Sorting
def sort(l):
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    l.sort(key = alphanum_key)
    return l

# ASCIIbetical Sorting
def normal_sort(l):
    l.sort()
    return l

# Event-based variable (based on Tkinter's {String,Int}Var)
class eventVar():
    def __init__(self, **kw):
        self.__value__ = None  # NEVER access this variable unless get() doesn't work
        self.writenotify = []
        self.readnotify = []
        if "value" in kw:
            self.set(kw["value"])

    def set(self, newvalue):
        self.__value__ = newvalue
        for i in self.writenotify:
            i(newvalue)

    def get(self):
        for i in self.readnotify:
            i()
        return self.__value__

    def trace(self, rw, func):
        if rw.lower() == "r":
            self.readnotify.append(func)
        elif rw.lower() == "w":
            self.writenotify.append(func)
