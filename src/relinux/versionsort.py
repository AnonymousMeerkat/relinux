'''
sort -V for python (translated from sort.c)
@author: Anonymous Meerkat
'''
from re import *


def order(c):
    if c.isdigit():
        return 0
    elif c.isalpha():
        return c
    elif c == "~":
        return -1
    else:
        return c


def VersionSortCmp(str1, str2):
    str1len = len(str1)
    str2len = len(str2)
    str1pos = 0
    str2pos = 0
    if str1 == str2:
            return 0
    while str1pos < str1len or str2pos < str2len:
        first_diff = 0
        while (str1pos < str1len and str1[str1pos].isdigit()) or (str2pos < str2len and str2[str2pos].isdigit()):
            str1c = 0
            if str1pos != str1len:
                str1c = order(str1[str1pos])
            str2c = 0
            if str2pos != str2len:
                str2c = order(str2[str2pos])
            if str1c != str2c:
                return str1c - str2c
            str1pos = str1pos + 1
            str2pos = str2pos + 1
        while str1[str1pos] == '0':
            str1pos = str1pos + 1
        while str2[str2pos] == '0':
            str2pos = str2pos + 1
        while str1[str1pos].isdigit() and str2[str2pos].isdigit():
            if first_diff == 0:
                first_diff = str1[str1pos] - str2[str2pos]
                str1pos = str1pos + 1
                str2pos = str2pos + 1
        if str1[str1pos].isdigit():
            return 1
        if str2[str2pos].isdigit():
            return -1
        if first_diff != 0:
            return first_diff
    return 0


def VersionSortKey():
    class K(object):
        def __init__(self, obj, *args):
            self.obj = obj

        def __lt__(self, other):
            return VersionSortCmp(self.obj, other.obj) < 0

        def __gt__(self, other):
            return VersionSortCmp(self.obj, other.obj) > 0

        def __eq__(self, other):
            return VersionSortCmp(self.obj, other.obj) == 0

        def __le__(self, other):
            return VersionSortCmp(self.obj, other.obj) <= 0

        def __ge__(self, other):
            return VersionSortCmp(self.obj, other.obj) >= 0

        def __ne__(self, other):
            return VersionSortCmp(self.obj, other.obj) != 0
    return K


def sort_nicely(l):
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in split('([0-9]+)', key)]
    l.sort(key=alphanum_key)
