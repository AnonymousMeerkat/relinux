# -*- coding: utf-8 -*-
'''
ISO Utilities
    - Generates the basic tree
    - Fills it in
    - Creates the ISO and MD5 hashes
@author: Anonymous Meerkat <meerkatanonymous@gmail.com>
'''

from relinux.modules.osweaver import tempsys
from relinux import logger, config, fsutil, configutils, threadmanager, utilities
import shutil
import os
import re
import subprocess
import shlex
import sys


threadname = "ISOTree"
#tn = logger.genTN(threadname)
isotreel = config.ISOTree
configs = config.Configuration["OSWeaver"]
# C True
ct = "1"
# C False
cf = "0"
# ISO Generation Options
# Options:
# -r                     Use the Rock Ridge protocol
# -V label               Label of the ISO
# -cache-inodes          Enable caching inodes and device numbers
# -J                     Use Joliet specification to let pathnames use 64 characters
# -l                     Allow 31-character filenames (Joliet will replace this of course)
# -b bootimage           Boot with the specified image
# -c bootcatalog         Path to generate the boot catalog
# -no-emul-boot          Shows that the boot image specified is a "no emulation" image
#                           This means that the system will not perform any disk emulation when running it
# -boot-load-size 4      Number of virtual sectors to load
# -boot-info-table       Add a boot information table to the boot image
# -o file                Output image
# -input-charset utf-8   Use the UTF-8 input charset
# -iso-level isolevel    ISO Level
isogenopts = ("-r -cache-inodes -J -l -b isolinux/isolinux.bin -c isolinux/boot.cat -no-emul-boot " +
              "-boot-load-size 4 -boot-info-table -input-charset utf-8 -iso-level " +
              configutils.getValue(configs[configutils.isolevel]))


# Returns the disk name of the ISO
def getDiskName():
    return configutils.getValue(configs[configutils.label]) + " - Release " + config.Arch


# Shows a file not found error
def showFileNotFound(files, dirs, tn):
    logger.logE(tn, logger.E, files + " " + _("not found") + ". " + _("Copy") + " " + files +
                " " + _("to") + " " + dirs)


# Copy a file
def copyFile(src, dst, tn, critical = False):
    if os.path.isfile(src):
        shutil.copy2(src, dst)
    elif critical is True:
        splitted = os.path.split(src)
        showFileNotFound(splitted[1], splitted[0], tn)


# C precompiler definition writer
# lists - Dictionary containing all options needed
def defineWriter(files, lists):
    d = open(files, "w")
    for i in lists.keys():
        d.write("#define " + i + " " + lists[i] + "\n")
    d.close()


# Generate the ISO tree
genisotree = {"deps": [], "tn": "ISOTree"}
class genISOTree(threadmanager.Thread):
    def runthread(self):
        logger.logI(self.tn, logger.I, _("Generating ISO Tree"))
        # Make the tree
        print(isotreel)
        fsutil.maketree([isotreel + "casper", isotreel + "preseed",
                          isotreel + "isolinux", isotreel + ".disk"])
genisotree["thread"] = genISOTree


# Copy preseed to the ISO tree
copypreseed = {"deps": [genisotree], "tn": "Preseed"}
class copyPreseed(threadmanager.Thread):
    def runthread(self):
        logger.logV(self.tn, logger.I, _("Copying preseed files to the ISO tree"))
        for i in fsutil.listdir(configutils.getValue(configs[configutils.preseed])):
            logger.logVV(self.tn, logger.I, _("Copying") + " " + i + " " + _("to the ISO tree"))
            copyFile(i, isotreel + "preseed/", self.tn)
copypreseed["thread"] = copyPreseed


# Copy memtest to the ISO tree
copymemtest = {"deps": [genisotree], "tn": "Memtest"}
class copyMemtest(threadmanager.Thread):
    def runthread(self):
        if configutils.parseBoolean(configutils.getValue(configs[configutils.memtest])):
            logger.logV(self.tn, logger.I, _("Copying memtest to the ISO tree"))
            copyFile("/boot/memtest86+.bin", isotreel + "isolinux/memtest", self.tn)
copymemtest["thread"] = copyMemtest


# Copy Syslinux to the ISO tree
copysyslinux = {"deps": [genisotree], "tn": "SysLinux"}
class copySysLinux(threadmanager.Thread):
    def runthread(self):
        logger.logV(self.tn, logger.I, _("Copying ISOLINUX to the ISO tree"))
        copyFile("/usr/lib/syslinux/isolinux.bin", isotreel + "isolinux/", self.tn, True)
        copyFile("/usr/lib/syslinux/vesamenu.c32", isotreel + "isolinux/", self.tn, True)
        logger.logVV(self.tn, logger.I, _("Copying isolinux.cfg to the ISO tree"))
        copyFile(configutils.getValue(configs[configutils.isolinuxfile]), isotreel +
                                      "isolinux/isolinux.cfg", self.tn, True)
        # Edit the isolinux.cfg file to replace the variables
        logger.logV(self.tn, logger.I, _("Editing isolinux.cfg"))
        splash = os.path.basename(configutils.getValue(configs[configutils.splash]))
        shutil.copy2(configutils.getValue(configs[configutils.splash]),
                     isotreel + "isolinux/" + splash)
        for i in [["LABEL", configutils.getValue(configs[configutils.label])],
                  ["SPLASH", splash],
                  ["TIMEOUT", configutils.getValue(configs[configutils.timeout])]]:
            fsutil.ife(fsutil.ife_getbuffers(isotreel + "isolinux/isolinux.cfg"),
                       lambda line: [True, re.sub("\$" + i[0], i[1], line)])
copysyslinux["thread"] = copySysLinux


# Write disk definitions
diskdefines = {"deps": [genisotree], "tn": "DiskDefines"}
class diskDefines(threadmanager.Thread):
    def runthread(self):
        logger.logV(self.tn, logger.I, _("Writing disk definitions"))
        defineWriter(isotreel + "README.diskdefines", {"DISKNAME": getDiskName(),
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
        copyFile(isotreel + "README.diskdefines", isotreel + "casper/README.diskdefines", self.tn)
diskdefines["thread"] = diskDefines


# Generate package manifests
pakmanifest = {"deps": [genisotree], "tn": "Manifest"}
class genPakManifest(threadmanager.Thread):
    def runthread(self):
        # Generate the package manifest
        logger.logV(self.tn, logger.I, _("Generating package manifests"))
        logger.logVV(self.tn, logger.I, _("Generating filesystem.manifest and filesystem.manifest-desktop"))
        writer = open(isotreel + "casper/filesystem.manifest", "w")
        writer_desktop = open(isotreel + "casper/filesystem.manifest-desktop", "w")
        for i in config.AptCache:
            if i.installedVersion == None or len(i.installedVersion) <= 0:
                continue
            name = i.get_fullname(True).strip()
            ver = i.installedVersion.strip()
            strs = name + " " + ver + "\n"
            writer.write(strs)
            if (not name in
                configutils.parseMultipleValues(configutils.getValue(configs[configutils.remafterinst]))):
                writer_desktop.write(strs)
        writer.close()
        writer_desktop.close()
        logger.logVV(self.tn, logger.I, _("Generating filesytem.manifest-remove"))
        writer = open(isotreel + "casper/filesystem.manifest-remove", "w")
        for i in configutils.parseMultipleValues(configutils.getValue(configs[configutils.remafterinst])):
            writer.write(i.strip() + "\n")
        writer.close()
pakmanifest["thread"] = genPakManifest


# Generate the RAMFS
genramfs = {"deps": [genisotree], "tn": "RAMFS"}
class genRAMFS(threadmanager.Thread):
    def runthread(self):
        logger.logV(self.tn, logger.I, _("Generating RAMFS"))
        os.system("mkinitramfs -o " + isotreel + "casper/initrd.gz " +
                  configutils.getKernel(configutils.getValue(configs[configutils.kernel])))
        '''copyFile("/boot/initrd.img-" + configutils.getKernel(configutils.getValue(configs[configutils.kernel])),
                 isotreel + "casper/initrd.gz", self.tn)'''
genramfs["thread"] = genRAMFS


# Copy the kernel
copykernel = {"deps": [genisotree], "tn": "Kernel"}
class copyKernel(threadmanager.Thread):
    def runthread(self):
        logger.logI(self.tn, logger.I, _("Copying the kernel to the ISO tree"))
        copyFile("/boot/vmlinuz-" + configutils.getKernel(configutils.getValue(configs[configutils.kernel])),
                 isotreel + "casper/vmlinuz", self.tn)
copykernel["thread"] = copyKernel


# Generate WUBI
genwubi = {"deps": [genisotree], "tn": "WUBI"}
class genWUBI(threadmanager.Thread):
    def runthread(self):
        if configutils.parseBoolean(configutils.getValue(configs[configutils.enablewubi])) is True:
            logger.logV(self.tn, logger.I, _("Generating the windows autorun.inf"))
            files = open(isotreel + "autorun.inf", "w")
            files.write("[autorun]\n")
            files.write("open=wubi.exe\n")
            files.write("icon=wubi.exe,0\n")
            files.write("label=Install " + configutils.getValue(configs[configutils.sysname]) + "\n")
            files.write("\n")
            files.write("[Content]\n")
            files.write("MusicFiles=false\n")
            files.write("PictureFiles=false\n")
            files.write("VideoFiles=false\n")
            files.close()
genwubi["thread"] = genWUBI


# Make the LiveCD compatible with USB burners
usbcomp = {"deps": [genisotree], "tn": "USB"}
class USBComp(threadmanager.Thread):
    def runthread(self):
        logger.logI(self.tn, logger.I, _("Making the ISO compatible with a USB burner"))
        logger.logVV(self.tn, logger.I, _("Writing .disk/info"))
        files = open(isotreel + ".disk/info", "w")
        files.write(getDiskName() + "\n")
        files.close()
        logger.logV(self.tn, logger.I, _("Making symlink pointing to the ISO root dir"))
        if os.path.lexists(isotreel + "ubuntu"):
            fsutil.rm(isotreel + "ubuntu", False, self.tn)
        os.symlink(isotreel, isotreel + "ubuntu")
        logger.logVV(self.tn, logger.I, _("Writing release notes URL"))
        files = open(isotreel + ".disk/release_notes_url", "w")
        files.write(configutils.getValue(configs[configutils.url]) + "\n")
        files.close()
        logger.logVV(self.tn, logger.I, _("Writing .disk/base_installable"))
        fsutil.touch(isotreel + ".disk/base_installable")
        logger.logVV(self.tn, logger.I, _("Writing CD Type"))
        files = open(isotreel + ".disk/cd_type", "w")
        files.write("full_cd/single\n")
        files.close()
usbcomp["thread"] = USBComp


from relinux.modules.osweaver import squashfs
threads1 = [genisotree, copypreseed, copymemtest, copysyslinux, diskdefines, pakmanifest, genramfs,
            copykernel, genwubi, usbcomp]
githreads = threads1
githreads.extend(tempsys.threads)
githreads.extend(squashfs.threads)


# Generates the ISO
geniso = {"deps": githreads, "tn": "ISO", "threadspan":-1}
class genISO(threadmanager.Thread):
    def runthread(self):
        logger.logI(self.tn, logger.I, _("Starting generation of the ISO image"))
        # Make a last verification on the SquashFS
        squashfs.doSFSChecks(isotreel + "casper/filesystem.squashfs",
                             configutils.getValue(configs[configutils.isolevel]))
        self.setProgress(self.tn, 5)
        # Generate MD5 checksums
        logger.logV(self.tn, logger.I, _("Generating MD5 sums"))
        files = open(isotreel + "md5sum.txt", "w")
        for x in fsutil.listdir(isotreel, {"recurse": True}):
            i = re.sub(r"^ *" + isotreel + "/*", "./", x)
            if not "isolinux" in i and not "md5sum" in i:
                logger.logVV(self.tn, logger.I, _("Writing MD5 sum of") + " " + i)
                fmd5 = fsutil.genFinalMD5(i, x)
                if fmd5 != "" and fmd5 != None:
                    files.write(fmd5)
        files.close()
        self.setProgress(self.tn, 15)
        logger.logI(self.tn, logger.I, _("Generating the ISO"))
        location = (configutils.getValue(configs[configutils.isodir]) + "/" +
                    configutils.getValue(configs[configutils.isolocation]))
        patt = re.compile("^ *([0-9]+)\.?[0-9]*%.*$")
        appnd = "32"
        if sys.maxsize > 2 ** 32:
            appnd = "64"
        os.environ["LD_PRELOAD"] = os.path.split(os.path.realpath(__file__))[0] + "/isatty" + appnd + ".so"
        isocmd = subprocess.Popen(shlex.split(configutils.getValue(configs[configutils.isogenerator]) + " -o " +
                                              location + " " + isogenopts + " -V \"" +
                                              configutils.getValue(configs[configutils.label]) + "\" " + isotreel),
                                  stderr = subprocess.PIPE, universal_newlines = True)
        oldprogress = 0
        while isocmd.poll() is None:
            output = isocmd.stderr.readline()
            match = patt.match(output)
            if match != None:
                progress = int(match.group(1))
                if progress > oldprogress:
                    # 1.4285714285714286 is just 100 / 70
                    self.setProgress(self.tn, 15 + int(utilities.floatDivision(progress, 1.4285714285714286)))
                    oldprogress = progress
            sys.stdout.write(output)
            sys.stdout.flush()
        os.environ["LD_PRELOAD"] = ""
        self.setProgress(self.tn, 85)
        # Generate the MD5 sum
        logger.logV(self.tn, logger.I, _("Generating MD5 sum for the ISO"))
        files = open(location + ".md5", "w")
        files.write(fsutil.genFinalMD5("./" + configutils.getValue(configs[configutils.isolocation]),
                                       location))
        files.close()
        self.setProgress(self.tn, 100)
        msg = "Relinux generated the ISO at " + configutils.getValue(
                            config.Configuration["OSWeaver"][configutils.isolocation])
        msg += "."
        self.showMessage(self.tn, logger.I, msg)
geniso["thread"] = genISO

threads = threads1
threads.append(geniso)
