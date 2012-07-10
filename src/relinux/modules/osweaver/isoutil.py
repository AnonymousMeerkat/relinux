'''
ISO Utilities
    - Generates the basic tree
    - Fills it in
    - Creates the ISO and MD5 hashes
@author: Anonymous Meerkat
'''

from relinux import logger, config, fsutil, configutils
from relinux.modules.osweaver import squashfs
import shutil
import os
import re
import threading

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
    logger.logE(tn, logger.Error + file + " " + _("not found") + "." + _("Copy") + " " + file +
                " " + _("to") + " " + dirs)


# Copy a file
def copyFile(src, dst, critical=False):
    if os.path.isfile(src):
        shutil.copy2(src, dst)
    elif critical is True:
        splitted = os.path.split(src)
        showFileNotFound(splitted[1], splitted[0])


# C precompiler definition writer
# lists - Dictionary containing all options needed
def defineWriter(file, lists):
    d = open(file, "w")
    for i in lists.keys():
        d.write("#define " + i + " " + lists[i] + "\n")
    d.close()


# Generate the ISO tree
class genISOTree(threading.Thread):
    def run(self):
        logger.logI(tn, _("Generating ISO Tree"))
        # Make the tree
        fsutil.maketree([isotreel + "casper", isotreel + "preseed",
                          isotreel + "isolinux", isotreel + ".disk"])


# Generate the ISO contents (has to run after genISOTree)
class genISOContents(threading.Thread):
    def run(self, configs):
        logger.logI(tn, _("Generating ISO Contents"))
        # Copy over the files we need
        logger.logI(tn, _("Copying over files we need"))
        logger.logV(tn, _("Copying preseed files to the ISO tree"))
        for i in configs[configutils.preseed]:
            logger.logVV(tn, _("Copying") + " " + i + " " + _("to the ISO tree"))
            copyFile(i, isotreel + "preseed")
        if configutils.parseBoolean(configs[configutils.memtest]):
            logger.logV(tn, _("Copying memtest to the ISO tree"))
            copyFile("/boot/memtest86+.bin", isotreel + "isolinux/memtest")
        logger.logV(tn, _("Copying ISOLINUX to the ISO tree"))
        copyFile("/usr/lib/syslinux/isolinux.bin", isotreel + "isolinux/", True)
        copyFile("/usr/lib/syslinux/vesamenu.c32", isotreel + "isolinux/", True)
        logger.logVV(tn, _("Copying isolinux.cfg to the ISO tree"))
        copyFile(configs[configutils.isolinuxfile], isotreel + "isolinux/isolinux.cfg", True)
        # Edit the isolinux.cfg file to replace the variables
        logger.logV(_("Editing isolinux.cfg"))
        for i in [["LABEL", configs[configutils.label]], ["SPLASH", configs[configutils.splash]],
                  ["TIMEOUT", configs[configutils.timeout]]]:
            fsutil.ife(fsutil.ife_getbuffers(isotreel + "isolinux/isolinux.cfg"),
                       lambda(line): re.sub("\$" + i[0], i[1], line))
        # Write disk definitions
        logger.logI(tn, _("Generating files"))
        logger.logV(tn, _("Writing disk definitions"))
        diskname = configs[configutils.label] + " - Release " + config.Arch
        defineWriter(isotreel + "README.diskdefines", {"DISKNAME": diskname,
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
        logger.logV(tn, _("Generating package manifests"))
        logger.logVV(tn, _("Generating filesystem.manifest"))
        pkglistu = os.popen("dpkg -l")
        writer = open(isotreel + "casper/filesystem.manifest", "w")
        for i in pkglistu:
            splitted = i.split()
            if not splitted[1].strip() in config[configutils.remafterinst]:
                writer.write(splitted[1].strip() + " " + splitted[2].strip() + "\n")
        writer.close()
        logger.logVV(tn, _("Generating filesytem.manifest-remove"))
        writer = open(isotreel + "casper/filesystem.manifest-remove", "w")
        for i in config[configutils.remafterinst]:
            writer.write(i.strip() + "\n")
        writer.close()
        # We don't want any differences, so we'll just copy filesystem.manifest to filesystem.manifest-desktop
        logger.logVV(tn, _("Generating filesystem.manifest-desktop"))
        copyFile(isotreel + "casper/filesystem.manifest", isotreel + "casper/filesystem.manifest-desktop")
        # Generate the ramdisk
        logger.logV(tn, _("Generating ramdisk"))
        os.system("mkinitramfs -o " + isotreel + "casper/initrd.gz " + configutils.getKernel(configs[configutils.kernel]))
        logger.logI(tn, _("Copying the kernel to the ISO tree"))
        copyFile("/boot/vmlinuz-" + configutils.getKernel(configs[configutils.kernel]), isotreel + "casper/vmlinuz")
        if configutils.parseBoolean(configs[configutils.enablewubi]) is True:
            logger.logV(tn, _("Generating the windows autorun.inf"))
            file = open(isotreel + "autorun.inf", "w")
            file.write("[autorun]\n")
            file.write("open=wubi.exe\n")
            file.write("icon=wubi.exe,0\n")
            file.write("label=Install " + configs[configutils.sysname] + "\n")
            file.write("\n")
            file.write("[Content]\n")
            file.write("MusicFiles=false\n")
            file.write("PictureFiles=false\n")
            file.write("VideoFiles=false\n")
            file.close()
        logger.logI(tn, _("Making the ISO compatible with a USB burner"))
        logger.logVV(tn, _("Writing .disk/info"))
        file = open(isotreel + ".disk/info", "w")
        file.write(diskname)
        file.close()
        # No idea why this is needed
        logger.logV(tn, _("Making symlink pointing to the ISO root dir"))
        os.symlink(isotreel + "ubuntu", isotreel)
        logger.logVV(tn, _("Writing release notes URL"))
        file = open(isotreel + ".disk/release_notes_url", "w")
        file.write(configs[configutils.url] + "\n")
        file.close()
        logger.logVV(tn, _("Writing .disk/base_installable"))
        fsutil.touch(isotreel + ".disk/base_installable")
        logger.logVV(tn, _("Writing CD Type"))
        file = open(isotreel + ".disk/cd_type", "w")
        file.write("full_cd/single\n")
        file.close()


# Generates the ISO
class genISO(threading.Thread):
    def run(self, configs):
        logger.logI(tn, _("Starting generation of the ISO image"))
        # Make a last verification on the SquashFS
        squashfs.doSFSChecks(isotreel + "casper/filesystem.squashfs", configs[configutils.isolevel])
        # Generate MD5 checksums
        logger.logV(tn, _("Generating MD5 sums"))
        file = open(isotreel + "md5sum.txt")
        for x in fsutil.listdir(isotreel, {"recurse": True}):
            i = re.sub(r"^ *" + isotreel + ".*", ".", x)
            if i.find("isotree") == -1 and i.find("md5sum") == -1:
                logger.logVV(tn, _("Writing MD5 sum of") + " " + i)
                file.write(fsutil.genFinalMD5(i))
        file.close()
        # Generate the ISO
        # Options:
        # -r                   Use the Rock Ridge protocol
        # -V label             Label of the ISO
        # -cache-inodes        Enable caching inodes and device numbers
        # -J                   Use Joliet specification to let pathnames use 64 characters
        # -l                   Force usage of 31-character filenames
        # -b bootimage         Boot with the specified image
        # -c bootcatalog       Path to generate the boot catalog
        # -no-emul-boot        Shows that the boot image specified is a "no emulation" image
        #                         This means that the system will not perform any disk emulation when running it
        # -boot-load-size 4    Number of virtual sectors to load
        # -boot-info-table     Add a boot information table at offset 8 in the boot image
        # -o file              Output image
        logger.logI(tn, _("Generating the ISO"))
        os.system(configs[configutils.isogenerator] + " -r -V " + configs[configutils.label] + " -cache-inodes " +
                  "-J -l -b " + isotreel + "isolinux/isolinux.bin -c " + isotreel + "isolinux/boot.cat -no-emul-boot " +
                  "-boot-load-size 4 -boot-info-table -o " + configs[configutils.isolocation])
        # Generate the MD5 sum
        logger.logV(tn, _("Generating MD5 sum for the ISO"))
        file = open(configs[configutils.isolocation] + ".md5", "w")
        file.write(fsutil.genFinalMD5(i))
        file.close()

threads = []
