'''
ISO Tree Generator
@author: lkjoel
'''

from relinux.lib import logger, config, maketree

def genISOTree():
    logger.logI("Generating ISO Tree")
    maketree.maketree(config.ISOTree + "/casper", config.ISOTree + "/preseed",
                      config.ISOTree + "/isolinux", config.ISOTree + "/.disk")
    