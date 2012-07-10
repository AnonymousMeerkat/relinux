'''
Module Loader
@author: Anonymous Meerkat
'''

import imp
import os
from relinux import config


# Checks if a folder is a module
def isModule(folder):
    if not os.path.isdir(folder):
        return False
    if not "__init__.py" in os.listdir(folder):
        return False
    module = __import__(os.path.join(folder, "__init__"))
    if hasattr(module, "relinuxmodule") and module.relinuxmodule is True:
        return True
    return False


# Returns a list of modules
def getModules():
    returnme = []
    modules = os.listdir(config.ModFolder)
    for i in modules:
        dirs = os.path.join(config.ModFolder, i)
        if not isModule(dirs):
            continue
        file, pathname, desc = imp.find_module("__init__", dirs)
        returnme.append({"name": i, "file": file, "path": pathname, "desc": desc})
    return returnme


# Loads a module
def loadModule(module):
    return imp.load_module("__init__", module.file, module.path, module.desc)
