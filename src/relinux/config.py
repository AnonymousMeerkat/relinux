'''
Basic configuration
@author: Anonymous Meerkat
'''

# We should not use any imports in this file
#import os
#from relinux import fsutil
import sys

product = "Relinux"
productunix = "relinux"
version = "0.4a1"
version_string = product + " version " + str(version)
about_string = product + " is a free software designed to help you make a professional-looking OS easily"

EStatus = True
WStatus = True
IStatus = True
VStatus = True
VVStatus = True

EFiles = [sys.stderr]
WFiles = [sys.stdout]
IFiles = [sys.stdout]
VFiles = [sys.stdout]
VVFiles = [sys.stdout]

# GUI Section
GUIStatus = True
background = "lightgrey"

# Generated
ISOTree = ""
TempSys = ""
SysVersion = ""  # Should be filled in by: os.popen("/usr/bin/lsb_release -rs").read().strip()
Arch = ""  # Should be filled in by: fsutil.getArch()

# Gettext
localedir = "../../localize/"
unicode = True
language = "en"

# Threading
ThreadRPS = 10
ThreadStop = False

# Modules
ModFolder = "./modules"
