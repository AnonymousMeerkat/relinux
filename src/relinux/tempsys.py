'''
Generates a temporary filesystem to hack on
@author: lkjoel
'''

from relinux import logger, config, fsutil
import os, stat

def genTempSys():
    logger.logI("Generating Temporary System")
    fsutil.maketree(config.TempSys + "/etc", config.TempSys + "/dev",
                      config.TempSys + "/proc", config.TempSys + "/tmp",
                      config.TempSys + "/sys", config.TempSys + "/mnt",
                      config.TempSys + "/media/cdrom", config.TempSys + "/var")
    fsutil.chmod(config.TempSys + "/tmp", "1777")
    