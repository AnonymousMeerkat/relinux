'''
General filesystem utilities
@author: Anonymous Meerkat
'''

import os, stat, shutil, fnmatch

# Reads the link location of a file or returns None
def delink(file):
    if os.path.islink(file):
        return os.readlink(file)
    return None

# Lengthener for files to exclude
def exclude(names, files):
    excludes = []
    for i in files:
        excludes.extend(fnmatch.filter(names, i))
    return excludes

# Makes a directory
def makedir(dirs):
    if not os.path.exists(dirs):
        os.makedirs(dirs)

# Makes a directory tree
def maketree(arr):
    for i in arr:
        makedir(i)

# Simple implementation of the touch utility
def touch(file):
    if os.path.exists(file):
        os.utime(file, None)
    else:
        open(file, "w").close()

# Same as maketree, but for files instead
def makefiles(arr):
    for i in arr:
        touch(i)

# Removes a file
# If followlink is True, then it will remove both the link and the origin
def rm(file, followlink=False):
    rfile = file
    dfile = delink(file)
    if dfile != None:
        file = dfile
    if os.path.isfile(file):
        os.remove(rfile)
        if followlink == True and dfile != None:
            os.remove(file)
    elif os.path.isdir(file):
        shutil.rmtree(rfile)
        if followlink == True and dfile != None:
            os.remove(file)

# Removes a list of files
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

# Simple implementation of the chmod utility
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

# Filesystem copier (like rsync --exclude... -a SRC DST)
def fscopy(src, dst, excludes1):
    # Get a list of all files
    files = os.listdir(src)
    # Exclude the files that are not wanted
    excludes = []
    if len(excludes) > 0:
        excludes = shutil.ignore_patterns(files, excludes1)
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

# Removes the contents of a directory with excludes and options
# Current options:
#     excludes (True or False): If True, exclude the files listed in excludes
#     remdirs (True or False): If True, remove directories too
def adrm(dirs, options, excludes1):
    # Get a list of all files inside the directory
    files = os.listdir(dirs)
    excludes = []
    # Exclude the files listed to exclude
    if options.excludes == True:
        excludes = shutil.ignore_patterns(files, excludes1)
    # Remove the wanted files
    for file in files:
        # Make sure we don't remove files that are listed to exclude from removal
        if file in excludes:
            continue
        fullpath = os.path.join(dirs, file)
        dfile = delink(fullpath)
        if dfile != None:
            if os.path.isfile(dfile):
                rm(fullpath)
                continue
        elif os.path.isdir(fullpath):
            adrm(fullpath, options, excludes1)
        else:
            rm(fullpath)
    if options.remdirs == True:
        rm(dirs)

# Returns the stat of a file
def getStat(file):
    return os.stat(file)

# Returns the mode of the stat of a file (can be used like this: getMode(getStat(file))
def getMode(stat):
    return stat.S_IMODE(stat.st_mode)

# Specific implementation of shutil's copystat function
def copystat(stat, dst):
    if hasattr(os, "utime"):
        os.utime(dst, (stat.st_atime, stat.st_mtime))
    if hasattr(os, "chmod"):
        os.chmod(dst, getMode(stat))
    if hasattr(os, "chflags") and hasattr(stat, "st_flags"):
        os.chflags(dst, stat.st_flags)
