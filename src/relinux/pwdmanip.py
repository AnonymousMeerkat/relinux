'''
Password and group file manipulation
@author: Anonymous Meerkat
'''

from relinux import configutils
import re

# Checks if something matched (shorthand way of writing 
def checkMatched(m):
    return configutils.checkMatched(m)

# Returns a parsed list of /etc/passwd entries (i.e. PP Entry)
def parsePasswdEntries(buffer):
    patt = re.compile("^(.*?):(.*?):(.*?):(.*?):(.*?):(.*?):(.*?).*")
    returnme = []
    for i in buffer:
        m = patt.match(i)
        if checkMatched(m):
            buff = {}
            buff["user"] = m.group(1)
            buff["passwd"] = m.group(2) # Usually x (covered in /etc/shadow)
            buff["uid"] = m.group(3)
            buff["gid"] = m.group(4)
            buff["name"] = m.group(5)
            buff["home"] = m.group(6)
            buff["shell"] = m.group(7)
            returnme.append(buff)
    return returnme

# Returns a parsed list of /etc/group entries (i.e. PG Entry)
def parseGroupEntries(buffer):
    patt = re.compile("^(.*?):(.*?):(.*?):(.*?)")
    returnme = []
    for i in buffer:
        m = patt.match(i)
        if checkMatched(m):
            buff = {}
            buff["group"] = m.group(1)
            buff["passwd"] = m.group(2) # Usually x (covered in /etc/gshadow)
            buff["gid"] = m.group(3)
            # We want ["user1", "user2"] instead of "user1,user2"
            buff["users"] = m.group(4).split(",")
            returnme.append(buff)
    return returnme

# Helper function that joins sections together with a custom character
def _join(arr, char):
    returnme = ""
    c = 0
    l = arr.length-1
    for i in arr:
        if c < l:
            returnme = returnme + i + char
        else:
            returnme = returnme + i
        c = c + 1
    return returnme

# The function opposite to parsePasswdEntries
def PPtoEntry(buffer):
    returnme = []
    for i in buffer:
        returnme.append(_join([i["user"], i["passwd"], i["uid"], i["gid"], i["name"], i["home"], i["shell"]], ":"))
    return returnme

# The function opposite to parseGroupEntries
def PGtoEntry(buffer):
    returnme = []
    for i in buffer:
        # Sort of hard to read (at least for me) so I'll split it up
        # returnme.append(
        #     _join([
        #         i["group"],
        #         i["passwd"],
        #         i["gid"],
        #         _join([
        #             i["users"]
        #         ], ",")
        #     ], ":")
        # )
        returnme.append(_join([i["group"], i["passwd"], i["gid"], _join([i["users"]], ",")]))

# Returns a list of entries from a user ID regex (buffer must contain PP entries)
def getPPByUID(regex, buffer):
    patt = re.compile("^.*" + regex + ".*$")
    returnme = []
    for i in buffer:
        m = patt.match(i.uid)
        if checkMatched(m):
            returnme.append(i)
    return returnme
