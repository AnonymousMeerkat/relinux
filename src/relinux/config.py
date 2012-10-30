# -*- coding: utf-8 -*-
'''
Basic configuration
@author: Anonymous Meerkat <meerkatanonymous@gmail.com>
'''

# We should not use any imports in this file
#import os
#from relinux import fsutil
import sys
import os

mainsrcdir = sys.path[0]
srcdir = os.path.abspath(os.path.join(mainsrcdir, os.pardir))
relinuxdir = os.path.abspath(os.path.join(srcdir, os.pardir))

min_python_version = 0x020700F0 # 2.7.0 final
max_python_version = 0x040000A0 # 4.0.0a0
#max_python_version = 0x020703F0 # 2.7.3 final
python3_version = 0x030000A0 # 3.0.0a0

min_python = sys.hexversion >= min_python_version
max_python = sys.hexversion <= max_python_version
python_ok = min_python and max_python
python3 = sys.hexversion >= python3_version

product = "Relinux"
productunix = "relinux"
version = "0.4a1"
author_string = "Anonymous Meerkat <meerkatanonymous@gmail.com>"
version_string = product + " version " + str(version)
about_string = ""

TermStreams = [sys.stderr, sys.stdout]

TermBlack = 30
TermRed = 31
TermGreen = 32
TermYellow = 33
TermBlue = 34
TermMagenta = 35
TermCyan = 36
TermWhite = 37

TermReset = 0
TermBold = 1
TermDark = 2
TermUnderline = 4
TermBlink = 5  # I hope this will be unused...
TermReverse = 7
TermConcealed = 8
TermAddForBackground = 10  # Add this to the color you want

EStatus = True
IStatus = True
VStatus = True
VVStatus = True

EFiles = []
IFiles = []
VFiles = []
VVFiles = []

# GUI Section
GUIStream = None
GUIStatus = True
background = "lightgrey"

# Generated
Configuration = None
AptCache = None
Gui = None
ISOTree = ""
TempSys = ""
SysVersion = ""  # Should be filled in by: os.popen("/usr/bin/lsb_release -rs").read().strip()
Arch = ""  # Should be filled in by: fsutil.getArch()

# Gettext
localedir = relinuxdir + "/localize/"
unicode = True
language = "en"

# Threading
ThreadRPS = 1
ThreadStop = False

# Modules
ModFolder = mainsrcdir + "/modules/"
ModAPIVersion = 1
