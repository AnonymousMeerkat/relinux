'''
OSWeaver Module for relinux
@author: Anonymous Meerkat
'''

relinuxmodule = True

from relinux.modules.osweaver import isoutil, squashfs, tempsys

modulename = "OSWeaver"
threads = []
threads.extend(isoutil.threads)
threads.extend(squashfs.threads)
threads.extend(tempsys.threads)
