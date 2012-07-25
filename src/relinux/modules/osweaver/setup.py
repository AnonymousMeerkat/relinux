'''
Setup Dependencies
@author: Anonymous Meerkat
'''

from relinux.modules.osweaver import aptcache, config
from relinux import logger, aptutil, configutils
import threading
import os


# Fix installer dependencies
instdepends = {"deps": [], "tn": "SetupUbiquity"}
class setupInst(threading.Thread):
    def __init__(self):
        self.tn = logger.genTN(instdepends["tn"])
        self.depcache = aptutil.getDepCache(aptcache)

    def run(self):
        logger.logV(self.tn, "Setting up Ubiquity")
        if os.getenv("KDE_FULL_SESSION") != None:
            aptutil.instPkg(aptutil.getPkg("ubiquity-frontend-kde", aptcache), self.depcache)
            aptutil.remPkg(aptutil.getPkg("ubiquity-frontend-gtk", aptcache), self.depcache, True)
        else:
            aptutil.remPkg(aptutil.getPkg("ubiquity-frontend-kde", aptcache), self.depcache, True)
            aptutil.instPkg(aptutil.getPkg("ubiquity-frontend-gtk", aptcache), self.depcache)
        if configutils.parseBoolean(config[configutils.popcon]):
            logger.logV(self.tn, "Setting up Popularity Contest")
            aptutil.instPkg(aptutil.getPkg("popularity-contest"), self.depcache)
        else:
            aptutil.remPkg(aptutil.getPkg("popularity-contest"), self.depcache, True)


threads = [setupInst]
