'''
Module Loader
@author: Anonymous Meerkat
'''

import imp
import os
from relinux import config


# Checks if a folder is a module
def isModule(name, file, pathname, desc):
    module = imp.load_module(name, file, pathname, desc)
    if hasattr(module, "relinuxmodule") and module.relinuxmodule is True and hasattr(module, "run") and callable(getattr(module, "run")):
        return True
    return False


# Returns a list of modules
def getModules():
    returnme = []
    modules = os.listdir(config.ModFolder)
    for i in modules:
        dirs = os.path.join(config.ModFolder, i)
        if not os.path.isdir(dirs) or not "__init__.py" in os.listdir(dirs):
            continue
        file, pathname, desc = imp.find_module("__init__", [dirs])
        if not isModule("__init__", file, pathname, desc):
            continue
        returnme.append({"name": i, "file": file, "path": pathname, "desc": desc})
    return returnme


# Loads a module
def loadModule(module):
    return imp.load_module("__init__", module["file"], module["path"], module["desc"])


# Runs a module
def runModule(module, adict):
    module.run(adict)
