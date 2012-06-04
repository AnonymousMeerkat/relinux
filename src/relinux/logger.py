'''
Contains streams for logging information
@author: lkjoel
'''

from relinux import config

# Log to essential stream
def logE(text):
    if config.EStatus is True:
        print(text)

# Log to info stream
def logI(text):
    if config.IStatus is True:
        print(text)

# Log to verbose stream
def logV(text):
    if config.VStatus is True:
        print(text)

# Log to very-verbose stream
def logVV(text):
    if config.VVStatus is True:
        print(text)
