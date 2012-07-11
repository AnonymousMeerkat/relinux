'''
Various APT Utilities
@author: Anonymous Meerkat
'''

import apt


# Version Comparison Operations
lt = 0x00
le = 0x01
eq = 0x02
ge = 0x03
gt = 0x04


# Returns an APT cache
# Note that this can take around 2-3 seconds
def getCache():
    return apt.cache.Cache()


# Returns a package in an APT cache
def getPkg(pkg, cache):
    return cache[pkg]


# Returns the package version
def getPkgVersion(pkg):
    return pkg.installed.version


# Compares versions
def compVersions(v1, v2, operation):
    comp = apt.VersionCompare(v1, v2)
    if operation == lt:
        if comp < 0:
            return True
        else:
            return False
    elif operation == le:
        if comp <= 0:
            return True
        else:
            return False
    elif operation == eq:
        if comp == 0:
            return True
        else:
            return False
    elif operation == ge:
        if comp >= 0:
            return True
        else:
            return False
    elif operation == gt:
        if comp > 0:
            return True
        else:
            return False
