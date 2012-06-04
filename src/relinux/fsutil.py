'''
General filesystem utilities
@author: Anonymous Meerkat
'''

import os, stat

def makedir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def maketree(arr):
    for i in arr:
        makedir(i)

# Helper function for chmod
def _chmod(c, mi):
    returnme = 0x00
    rbit = 0
    wbit = 0
    ebit = 0
    if c == 0:
        return returnme
    elif c == 1:
        rbit = stat.S_IREAD
        wbit = stat.S_IWRITE
        ebit = stat.S_IEXEC
    elif c == 2:
        rbit = stat.S_IRGRP
        wbit = stat.S_IWGRP
        ebit = stat.S_IXGRP
    elif c == 3:
        rbit = stat.S_IROTH
        wbit = stat.S_IWOTH
        ebit = stat.S_IXOTH
    if mi >= 4:
        returnme = rbit
        mi = mi - 4
    if mi >= 2:
        returnme = returnme | wbit
        mi = mi - 2
    if mi >= 1 :
        returnme = returnme | ebit
    print(returnme)
    return returnme

def chmod(file, mod):
    val = 0x00
    m = []
    mi = []
    v = []
    c = 0
    for i in mod:
        m.append(i)
        mi.append(int(i))
        val = val|_chmod(c, mi[c])
        c = c + 1
    print(val)
    os.chmod(file, val)
chmod("../../test.txt", "5506")