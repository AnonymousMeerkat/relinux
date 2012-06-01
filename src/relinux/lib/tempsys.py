'''
Generates a temporary filesystem to hack on
@author: lkjoel
'''

from relinux.lib import logger, config, maketree
import os, stat

def genTempSys():
    logger.logI("Generating Temporary System")
    maketree.maketree(config.TempSys + "/etc", config.TempSys + "/dev",
                      config.TempSys + "/proc", config.TempSys + "/tmp",
                      config.TempSys + "/sys", config.TempSys + "/mnt",
                      config.TempSys + "/media/cdrom", config.TempSys + "/var")
    os.chmod(config.TempSys + "/tmp", stat.S_IREAD|stat.S_IWRITE|stat.S_IEXEC)
    