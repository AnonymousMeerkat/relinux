'''
ISO Tree Generator
@author: Anonymous Meerkat
'''

from relinux import logger, config, fsutil, configutils, tempsys
import shutil
import os
import re

# Just in case config.ISOTree doesn't include a /
isotreel = config.ISOTree + "/"
threadname = "ISOTree"
tn = logger.genTN(threadname)
# C True
ct = "1"
# C False
cf = "0"


# Shows a file not found error
def showFileNotFound(file, dirs):
    logger.logE(tn, logger.Error + file + " not found. Copy " + file + " to " + dirs)


# Copy a file
def copyFile(src, dst, critical=False):
    if os.path.isfile(src):
        shutil.copy2(src, dst)
    elif critical == True:
        splitted = os.path.split(src)
        showFileNotFound(splitted[1], splitted[0])


# C precompiler definition writer
# lists - Dictionary containing all options needed
def defineWriter(file, lists):
    d = open(file, "w")
    for i in lists.keys():
        d.write("#define " + i + " " + lists[i] + "\n")
    d.close()


# Generate the ISO tree and contents
def getISOTree(configs):
    logger.logI("Generating ISO Tree")
    # Make the tree
    fsutil.maketree([isotreel + "casper", isotreel + "preseed",
                      isotreel + "isolinux", isotreel + ".disk"])
    # Copy over the files we need
    for i in configs[configutils.preseed]:
        copyFile(i, isotreel + "preseed")
    if configutils.parseBoolean(configs[configutils.memtest]):
        copyFile("/boot/memtest86+.bin", isotreel + "isolinux/memtest")
    copyFile("/usr/lib/syslinux/isolinux.bin", isotreel + "isolinux/", True)
    copyFile("/usr/lib/syslinux/vesamenu.c32", isotreel + "isolinux/", True)
    copyFile(configs[configutils.isolinuxfile], isotreel + "isolinux/isolinux.cfg", True)
    # Edit the isolinux.cfg file to replace the variables
    for i in [["LABEL", configs[configutils.label]], ["SPLASH", configs[configutils.splash]],
              ["TIMEOUT", configs[configutils.timeout]]]:
        fsutil.ife(fsutil.ife_getbuffers(isotreel + "isolinux/isolinux.cfg"),
                   lambda(line): re.sub("\$" + i[0], i[1], line))
    # Write disk definitions
    defineWriter(isotreel + "README.diskdefines", {"DISKNAME": configs[configutils.label] + " - Release " + config.Arch,
                                                  "TYPE": "binary",
                                                  "TYPEbinary": ct,
                                                  "ARCH": config.Arch,
                                                  "ARCH" + config.Arch: ct,
                                                  "DISKNUM": "1",
                                                  "DISKNUM1": ct,
                                                  "TOTALNUM": "0",
                                                  "TOTALNUM0": ct
                                                  })
    # For some reason casper needs (or used to need) the diskdefines in its own directory
    copyFile(isotreel + "README.diskdefines", isotreel + "casper/README.diskdefines")
    # Generate the package manifest
    pkglistu = os.popen("dpkg -l")
    writer = open(isotreel + "casper/filesystem.manifest", "w")
    for i in pkglistu:
        splitted = i.split()
        if not splitted[1].strip() in config[configutils.remafterinst]:
            writer.write(splitted[1].strip() + " " + splitted[2].strip() + "\n")
    writer.close()
    writer = open(isotreel + "casper/filesystem.manifest-remove", "w")
    for i in config[configutils.remafterinst]:
        writer.write(i.strip() + "\n")
    writer.close()
    # We don't want any differences, so we'll just copy filesystem.manifest to filesystem.manifest-desktop
    copyFile(isotreel + "casper/filesystem.manifest", isotreel + "casper/filesystem.manifest-desktop")
    # Generate the ramdisk
    os.system("mkinitramfs -o " + isotreel + "casper/initrd.gz " + configutils.getKernel(configs[configutils.kernel]))
    copyFile("/boot/vmlinuz-" + configutils.getKernel(configs[configutils.kernel]), isotreel + "casper/vmlinuz")
