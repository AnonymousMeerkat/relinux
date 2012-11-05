# -*- coding: utf-8 -*-
'''
Various APT Utilities
@author: Anonymous Meerkat <meerkatanonymous@gmail.com>
'''

from relinux import logger
import apt
import apt.progress


# Version Comparison Operations
lt = 0x00
le = 0x01
eq = 0x02
ge = 0x03
gt = 0x04

tn = logger.genTN("APT")


# OpProgress implementation
class OpProgress(apt.progress.base.OpProgress):
    def __init__(self, update, finish):
        apt.progress.base.OpProgress.__init__(self)
        self.old_op = ""
        self.updatefunc = update
        self.finishfunc = finish

    def update(self, percent = None):
        apt.progress.base.OpProgress.update(self, percent)
        op = self.op
        if self.major_change and self.old_op:
            op = self.old_op
        if self.updatefunc:
            self.updatefunc(op, percent)
        self.old_op = self.op

    def done(self):
        apt.progress.base.OpProgress.done(self)
        if self.old_op and self.finishfunc:
            self.finishfunc(self.old_op)
        self.old_op = ""


# AcquireProgress implementation
class AcquireProgress(apt.progress.text.AcquireProgress):
    def __init__(self, finishfunc = None):
        apt.progress.text.AcquireProgress.__init__(self)
        self.finishfunc = finishfunc

    def start(self):
        apt.progress.base.AcquireProgress.start(self)

    def stop(self):
        apt.progress.base.AcquireProgress.stop(self)
        ### CODE COPIED FROM ORIGINAL CLASS ###
        self._write((_("Fetched %sB in %s (%sB/s)\n") % (
                    apt.apt_pkg.size_to_str(self.fetched_bytes),
                    apt.apt_pkg.time_to_str(self.elapsed_time),
                    apt.apt_pkg.size_to_str(self.current_cps))).rstrip("\n"))
        ### END CODE COPIED FROM ORIGINAL CLASS ###
        if self.finishfunc:
            self.finishfunc()


# InstallProgress implementation
class InstallProgress(apt.progress.base.InstallProgress):
    def __init__(self, finishfunc = None):
        apt.progress.base.InstallProgress.__init__(self)
        self.finishfunc = finishfunc
        self.ran_finish = False

    def __del__(self):
        apt.progress.base.InstallProgress.finish_update(self)
        if not self.ran_finish:
            self.finishfunc()
            self.ran_finish = True

    def finish_update(self):
        apt.progress.base.InstallProgress.finish_update(self)
        if self.finishfunc:
            self.finishfunc()
            self.ran_finish = True


# Initializes APT
def initApt():
    apt.apt_pkg.init()


# Returns an APT cache
# Note that this can take around 2-30 seconds
def getCache(progress = None):
    if progress:
        return apt.cache.Cache(progress)
    else:
        return apt.cache.Cache()


# Returns a package in an APT cache
def getPkg(pkg, cache):
    return cache[pkg]


# Returns the package version
def getPkgVersion(pkg):
    return pkg.installed.version


# Returns an AcquireProgress
def getAcquireProgress():
    return apt.progress.base.AcquireProgress()


# Returns an InstallProgress
def getInstallProgress():
    return apt.progress.base.InstallProgress()


# Compares versions
def compVersions(v1, v2, operation):
    comp = apt.VersionCompare(v1, v2)
    if operation == lt:
        if comp < 0:
            return True
        else:
            return False
    elif operation == le:
        if comp <= 0:
            return True
        else:
            return False
    elif operation == eq:
        if comp == 0:
            return True
        else:
            return False
    elif operation == ge:
        if comp >= 0:
            return True
        else:
            return False
    elif operation == gt:
        if comp > 0:
            return True
        else:
            return False

# Installs a package
def instPkg(package, upgrade = True):
    print(package.name)
    if package.is_installed:
        if upgrade and package.is_upgradable:
            package.mark_upgrade()
            return True
        else:
            return False
    else:
        package.mark_install(True, True, False)
        return True


# Removes a package
def remPkg(package, purge = True):
    print("REM " + package.name)
    if (package.is_installed or package.marked_install or
        package.marked_reinstall or package.marked_upgrade):
        package.mark_delete(True, purge)
        return True
    else:
        return False


# Commits the changes
def commitChanges(cache, ap, ip):
    logger.logV(tn, logger.D, _("Install count: ") + str(cache.install_count) +
                _("Removal count: ") + str(cache.delete_count))
    return cache.commit(ap, ip)
