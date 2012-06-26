'''
Basic configuration
@author: Anonymous Meerkat
'''

# We should not use any imports in this file
#import os
#from relinux import fsutil

product = "Relinux"
productunix = "relinux"
version = 0.4
version_string = product + " version " + str(version)
about_string = product + _(" is a free software designed to help you make a professional-looking OS easily")

EStatus = True
IStatus = True
VStatus = True
VVStatus = True

# GUI Section
GUIStatus = True
background = "lightgrey"

# Generated section
ISOTree = ""
TempSys = ""
SysVersion = ""  # Should be filled in by: os.popen("/usr/bin/lsb_release -rs").read().strip()
Arch = ""  # Should be filled in by: fsutil.getArch()

# Gettext
localedir = "../../localize/"
unicode = True
language = "en"
