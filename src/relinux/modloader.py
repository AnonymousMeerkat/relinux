# -*- coding: utf-8 -*-
'''
Module Loader
@author: Anonymous Meerkat <meerkatanonymous@gmail.com>
'''

import imp
import os
import collections
from relinux import config, logger


tn = logger.genTN("ModLoader")


# Checks if a folder is a module
def isModule(module):
    if (hasattr(module, "relinuxmodule") and hasattr(module, "relinuxmoduleapi") and
        module.relinuxmodule is True and hasattr(module, "run") and
            isinstance(getattr(module, "run"), collections.Callable)):
        return True
    return False


# Checks if a module is compatible with this version of relinux
def isCompatible(module):
    if module.relinuxmoduleapi != config.ModAPIVersion:
        logger.logI(tn, logger.W, _("Module") + " " + module.modulename + " " +
                    _("is incompatible with this relinux version") + " (" + _("relinux version:") + " " +
                    config.version + ", " + _("required version:") + " " + module.relinuxmoduleapi + ")")
        return False
    return True


# Returns a list of modules
def getModules():
    returnme = []
    modules = os.listdir(config.ModFolder)
    for i in modules:
        dirs = os.path.join(config.ModFolder, i)
        if not os.path.isdir(dirs) or not "__init__.py" in os.listdir(dirs):
            continue
        file, pathname, desc = imp.find_module("__init__", [dirs])
        module = imp.load_module("__init__", file, pathname, desc)
        if not isModule(module):
            continue
        loadme = True
        if not isCompatible(module):
            loadme = False
        if loadme:
            returnme.append(
                {"name": i, "file": file, "path": pathname, "desc": desc})
        else:
            logger.logI(tn, logger.W, _("Module") + " " +
                        module.modulename + " " + _("will not be loaded"))
    return returnme


# Loads a module
def loadModule(module):
    return imp.load_module("__init__", module["file"], module["path"], module["desc"])


# Runs a module
def runModule(module, adict):
    module.run(adict)
