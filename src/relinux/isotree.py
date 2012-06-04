'''
ISO Tree Generator
@author: lkjoel
'''

from relinux import logger, config, fsutil

def genTempSys():
    logger.logI("Generating temporary filesystem tree")
    fsutil.maketree(config.TempSys + "/dev", config.TempSys + "/etc", config.TempSys + "/proc", 
                    config.TempSys + "/tmp", config.TempSys + "/sys", config.TempSys + "/mnt",
                    config.TempSys + "/media/cdrom", config.TempSys + "/var")

def genISOTree():
    logger.logI("Generating ISO Tree")
    fsutil.maketree(config.ISOTree + "/casper", config.ISOTree + "/preseed",
                      config.ISOTree + "/isolinux", config.ISOTree + "/.disk")
    