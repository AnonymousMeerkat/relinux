'''
ISO Tree Generator
@author: lkjoel
'''

from relinux import logger, config, fsutil


def genISOTree():
    logger.logI("Generating ISO Tree")
    fsutil.maketree([config.ISOTree + "/casper", config.ISOTree + "/preseed",
                      config.ISOTree + "/isolinux", config.ISOTree + "/.disk"])


# This function has to be called after tempsys's genTempSys()
def getISOTree2():
    logger.logI("Finishing the ISO Tree")
