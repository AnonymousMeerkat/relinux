'''
General filesystem utilities
@author: Anonymous Meerkat
'''

import os, stat, shutil, fnmatch

def delink(file):
    if os.path.islink(file):
        return os.readlink(file)
    return None

def makedir(dirs):
    if not os.path.exists(dirs):
        os.makedirs(dirs)

def maketree(arr):
    for i in arr:
        makedir(i)

def rm(file):
    rfile = file
    dfile = delink(file)
    if dfile != None:
        file = dfile
    if os.path.isfile(file):
        os.remove(rfile)
    elif os.path.isdir(file):
        shutil.rmtree(rfile)

def rmfiles(arr):
    for i in arr:
        rm(i)

# Helper function for chmod
def _chmod(c, mi):
    returnme = 0x00
    rbit = 0
    wbit = 0
    ebit = 0
    # TODO: Make this code cleaner
    #    Something like this:
    #    rbit = stat.S_IREAD
    #    ...
    #    if c == 0:
    #    ...
    #    if c == 2:
    #        rbit = rbit | SOME_SORT_OF_BIT_FLAG
    #        ...
    if c == 0:
        # These are not read/write/exec bits, but they work the same way
        ebit = stat.S_ISVTX
        wbit = stat.S_ISGID
        rbit = stat.S_ISUID
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
    # Read
    if mi >= 4:
        returnme = rbit
        mi = mi - 4
    # Write
    if mi >= 2:
        returnme = returnme | wbit
        mi = mi - 2
    # Execute
    if mi >= 1 :
        returnme = returnme | ebit
    return returnme

# Implementation of the chmod utility/C function
def chmod(file, mod):
    val = 0x00
    c = 0
    # OR all of the chmod options
    for i in mod:
        # OR this option to val
        val = val | _chmod(c, int(i))
        c = c + 1
    # Chmod it
    os.chmod(file, val)

# Lengthener for files to exclude
def exclude(names, files):
    excludes = []
    for i in files:
        excludes.extend(fnmatch.filter(names, i))
    return excludes

# Filesystem copier (like rsync --exclude... -a SRC DST)
def fscopy(src, dst, excludes):
    # Get a list of all files
    files = os.listdir(src)
    # Exclude the files that are not wanted
    excludes = []
    if len(excludes) > 0:
        excludes = exclude(files, excludes)
    makedir(dst)
    # Copy the files
    for file in files:
        # Make sure we don't copy files that are supposed to be excluded
        if file in excludes:
            continue
        fullpath = os.path.join(src, file)
        newpath = os.path.join(dst, file)
        dfile = delink(fullpath)
        if dfile != None:
            os.symlink(dfile, newpath)
        elif os.path.isdir(fullpath):
            fscopy(fullpath, newpath, excludes)
        else:
            shutil.copy2(fullpath, newpath)
    shutil.copystat(src, dst)
