'''
ISO Tree Generator
@author: Anonymous Meerkat
'''

from relinux import logger, config, fsutil, configutils, tempsys
import shutil
import os
import re

# Just in case config.ISOTree doesn't include a /
isotree = config.ISOTree + "/"
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


# Display a iso9660 error
def dispiso9660(level, maxs, size):
    logger.logE(tn, logger.Error + "Compressed filesystem is higher than the iso9660 level " + level + 
                    " spec allows (" + fsutil.sizeTrans({"B": maxs}, "M") + "MB, size is " + 
                    fsutil.sizeTrans({"B": size}, "M") + "MB).")
    logger.logE(tn, logger.Tab + "Please try to either reduce the amount of data you are generating, or " + 
                "increase the ISO level")


# Generate the ISO tree and contents
def getISOTree(configs):
    logger.logI("Generating ISO Tree")
    # Make the tree
    fsutil.maketree([isotree + "casper", isotree + "preseed",
                      isotree + "isolinux", isotree + ".disk"])
    # Copy over the files we need
    for i in configs[configutils.preseed]:
        copyFile(i, isotree + "preseed")
    if configutils.parseBoolean(configs[configutils.memtest]):
        copyFile("/boot/memtest86+.bin", isotree + "isolinux/memtest")
    copyFile("/usr/lib/syslinux/isolinux.bin", isotree + "isolinux/", True)
    copyFile("/usr/lib/syslinux/vesamenu.c32", isotree + "isolinux/", True)
    copyFile(configs[configutils.isolinuxfile], isotree + "isolinux/isolinux.cfg", True)
    # Edit the isolinux.cfg file to replace the variables
    for i in [["LABEL", configs[configutils.label]], ["SPLASH", configs[configutils.splash]],
              ["TIMEOUT", configs[configutils.timeout]]]:
        fsutil.ife(fsutil.ife_getbuffers(isotree + "isolinux/isolinux.cfg"),
                   lambda(line): re.sub("\$" + i[0], i[1], line))
    # Write disk definitions
    defineWriter(isotree + "README.diskdefines", {"DISKNAME": configs[configutils.label] + " - Release " + config.Arch,
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
    copyFile(isotree + "README.diskdefines", isotree + "casper/README.diskdefines")
    # Generate the package manifest
    pkglistu = os.popen("dpkg -l")
    writer = open(isotree + "casper/filesystem.manifest", "w")
    for i in pkglistu:
        splitted = i.split()
        if not splitted[1].strip() in config[configutils.remafterinst]:
            writer.write(splitted[1].strip() + " " + splitted[2].strip() + "\n")
    writer.close()
    writer = open(isotree + "casper/filesystem.manifest-remove", "w")
    for i in config[configutils.remafterinst]:
        writer.write(i.strip() + "\n")
    writer.close()
    # We don't want any differences, so we'll just copy filesystem.manifest to filesystem.manifest-desktop
    copyFile(isotree + "casper/filesystem.manifest", isotree + "casper/filesystem.manifest-desktop")
    # Generate the ramdisk
    os.system("mkinitramfs -o " + isotree + "casper/initrd.gz " + configutils.getKernel(configs[configutils.kernel]))
    copyFile("/boot/vmlinuz-" + configutils.getKernel(configs[configutils.kernel]), isotree + "casper/vmlinuz")
    # Generate the SquashFS file
    # Options:
    # -b 1M                    Use a 1M blocksize (maximum)
    # -no-recovery             No recovery files
    # -always-use-fragments    Fragment blocks for files larger than the blocksize (1M)
    # -comp                    Compression type
    opts = "-b 1M -no-recovery -no-duplicates -always-use-fragments"
    opts = opts + " -comp " + configs[configutils.sfscomp]
    opts = opts + " " + configs[configutils.sfsopts]
    sfsex = "dev etc home media mnt proc sys var usr/lib/ubiquity/apt-setup/generators/40cdrom"
    sfspath = isotree + "casper/filesystem.squashfs"
    os.system("mksquashfs " + tempsys.tmpsys + " " + sfspath + " " + opts)
    os.system("mksquashfs / " + sfspath + " " + opts + " -e " + sfsex)
    # Find the size
    size = fsutil.getSize(sfspath)
    isolvl = int(configs[configutils.isolevel])
    lvl2 = fsutil.sizeTrans({"G": 4})
    lvl3 = fsutil.sizeTrans({"T": 8})
    if size > lvl2 and isolvl < 3:
        dispiso9660(isolvl, lvl2, size)
    elif size > lvl3 and isolvl >= 3:
        # 8TB OS? That's a bit much xD
        dispiso9660(isolvl, lvl3, size)
    # Find the size after it is uncompressed
    file = open(isotree + "casper/filesystem.size", "w")
    file.write(fsutil.getSFSInstSize(sfspath) + "\n")
    file.close()
    # TODO: Discuss on whether to add MD5 sum or not
    # Could prevent problems, but might also prevent the user from editing
