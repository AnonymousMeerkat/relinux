'''
Setup Dependencies
@author: Anonymous Meerkat <meerkatanonymous@gmail.com>
'''

from relinux import logger, aptutil, configutils, threadmanager, config, fsutil
import os
import copy
import threading

configs = config.Configuration["OSWeaver"]

# Fix installer dependencies
instdepends = {"deps": [], "tn": "Setup"}
class setupInst(threadmanager.Thread):
    def __init__(self, **kw):
        threadmanager.Thread.__init__(self, **kw)
        self.aptcache = copy.copy(config.AptCache)

    def finishfunc(self, event):
        self.quit()

    def runthread(self):
        self.event = threading.Event()
        self.ap = aptutil.AcquireProgress()
        self.ip = aptutil.InstallProgress(lambda: self.finishfunc(self.event))
        logger.logV(self.tn, logger.I, _("Setting up Ubiquity"))
        if os.getenv("KDE_FULL_SESSION") != None:
            aptutil.instPkg(aptutil.getPkg("ubiquity-frontend-kde", self.aptcache))
            aptutil.remPkg(aptutil.getPkg("ubiquity-frontend-gtk", self.aptcache), True)
        else:
            aptutil.remPkg(aptutil.getPkg("ubiquity-frontend-kde", self.aptcache), True)
            aptutil.instPkg(aptutil.getPkg("ubiquity-frontend-gtk", self.aptcache))
        logger.logV(self.tn, logger.I, "Setting up Popularity Contest")
        if configutils.parseBoolean(configutils.getValue(configs[configutils.popcon])):
            aptutil.instPkg(aptutil.getPkg("popularity-contest", self.aptcache))
        else:
            aptutil.remPkg(aptutil.getPkg("popularity-contest", self.aptcache), True)
        aptutil.commitChanges(self.aptcache, self.ap, self.ip)
        self.exec_()
instdepends["thread"] = setupInst


threads = [instdepends]
