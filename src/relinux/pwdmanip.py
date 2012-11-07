# -*- coding: utf-8 -*-
'''
Password and group file manipulation
@author: Anonymous Meerkat <meerkatanonymous@gmail.com>
'''

from relinux import configutils, utilities
import re


# Checks if something matched (shorthand way of writing configutils.checkMatched(m))
def checkMatched(m):
    return utilities.checkMatched(m)


# Returns a parsed list of /etc/passwd entries (i.e. PP Entry)
def parsePasswdEntries(buffers):
    patt = re.compile("^(.*?):(.*?):(.*?):(.*?):(.*?):(.*?):(.*?)$")
    returnme = []
    for i in buffers:
        m = patt.match(i)
        if checkMatched(m):
            buff = {}
            buff["user"] = m.group(1)
            buff["passwd"] = m.group(2)  # Usually x (covered in /etc/shadow)
            buff["uid"] = m.group(3)
            buff["gid"] = m.group(4)
            buff["name"] = m.group(5)
            buff["home"] = m.group(6)
            buff["shell"] = m.group(7)
            returnme.append(buff)
    return returnme


# Returns a parsed list of /etc/group entries (i.e. PG Entry)
def parseGroupEntries(buffers):
    patt = re.compile("^(.*?):(.*?):(.*?):(.*?)$")
    returnme = []
    for i in buffers:
        m = patt.match(i)
        if checkMatched(m):
            buff = {}
            buff["group"] = m.group(1)
            buff["passwd"] = m.group(2)  # Usually x (covered in /etc/gshadow)
            buff["gid"] = m.group(3)
            # We want ["user1", "user2"] instead of "user1,user2"
            buff["users"] = m.group(4).split(",")
            returnme.append(buff)
    return returnme


# Returns a parsed list of /etc/shadow entries (i.e. PS Entry)
def parseShadowEntries(buffers):
    patt = re.compile(
        "^(.*?):(.*?):(.*?):(.*?):(.*?):(.*?):(.*?):(.*?):(.*?)$")
    returnme = []
    for i in buffers:
        m = patt.match(i)
        if checkMatched(m):
            buff = {}
            buff["user"] = m.group(1)
            buff["passwd"] = m.group(
                2)  # Now this one actually contains a hash
            buff["lastpwdchange"] = m.group(3)
            buff["minpwdchange"] = m.group(4)
            buff["maxpwdchange"] = m.group(5)
            buff["warnperiod"] = m.group(6)
            buff["inactive"] = m.group(7)
            buff["expire"] = m.group(8)
            buff["reserved"] = m.group(9)
            returnme.append(buff)
    return returnme


# The function opposite to parsePasswdEntries
def PPtoEntry(i):
    return utilities.join(
        [i["user"], i["passwd"], i["uid"], i["gid"], i["name"], i["home"],
         i["shell"]], ":") + "\n"


# The function opposite to parseGroupEntries
def PGtoEntry(i):
    return utilities.join([i["group"], i["passwd"], i["gid"], utilities.join(i["users"], ",")], ":") + "\n"


# The function opposite to parseShadowEntries
def PStoEntry(i):
    return utilities.join(
        [i["user"], i["passwd"], i["lastpwdchange"], i["minpwdchange"],
         i["maxpwdchange"], i[
         "warnperiod"], i["inactive"], i["expire"],
         i["reserved"]], ":") + "\n"


# Returns a list of entries from a user ID regex (buffer must contain PP entries)
def getPPByUID(regex, buffers):
    patt = re.compile("^" + regex + "$")
    returnme = []
    for i in buffers:
        m = patt.match(i["uid"])
        if checkMatched(m):
            returnme.append(i)
    return returnme
