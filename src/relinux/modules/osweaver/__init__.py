'''
OSWeaver Module for relinux
@author: Anonymous Meerkat
'''

from relinux.modules.osweaver import isoutil, squashfs, tempsys
from relinux import threadmanager

relinuxmodule = True
modulename = "OSWeaver"

def runThreads():
    threads = []
    threads.extend(isoutil.threads)
    threads.extend(squashfs.threads)
    threads.extend(tempsys.threads)
    threadmanager.threadLoop(threads)
