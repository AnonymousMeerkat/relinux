# -*- coding: utf-8 -*-
'''
SquashFS Generation
@author: Anonymous Meerkat <meerkatanonymous@gmail.com>
'''

from relinux import logger, fsutil, configutils, config, threadmanager, utilities
from relinux.modules.osweaver import tempsys
from relinux.modules.osweaver.isoutil import genisotree, genramfs
import os
import subprocess
import shlex
import re
import sys

threadname = "SquashFS"
tn = logger.genTN(threadname)
isotreel = config.ISOTree
tmpsys = config.TempSys
configs = config.Configuration["OSWeaver"]


# Display a iso9660 error
def dispiso9660(level, maxs, size):
    logger.logE(tn, logger.E, _("Compressed filesystem is higher than the iso9660 level ") + level +
                    " spec allows (" + fsutil.sizeTrans({"B": maxs}, "M") + _("MB, size is ") +
                    fsutil.sizeTrans({"B": size}, "M") + "MB).")
    logger.logE(tn, logger.E, logger.MTab + _("Please try to either reduce the amount of data you are generating, or ") +
                _("increase the ISO level"))


# Make the SquashFS checks
def doSFSChecks(files, isolvl):
    logger.logI(tn, logger.I, _("Checking the compressed filesystem"))
    size = fsutil.getSize(files)
    lvl2 = fsutil.sizeTrans({"G": 4})
    lvl3 = fsutil.sizeTrans({"T": 8})
    if size > lvl2 and isolvl < 3:
        dispiso9660(isolvl, lvl2, size)
    elif size > lvl3 and isolvl >= 3:
        # 8TB OS? That's a bit much xD
        dispiso9660(isolvl, lvl3, size)


# Generate the SquashFS file (has to run after isoutil.genISOTree and tempsys.genTempSys)
tmpthreads = []
tmpthreads.extend(tempsys.threads)
tmpthreads.append(genisotree)
tmpthreads.append(genramfs)
gensfs = {"deps": tmpthreads, "tn": threadname, "threadspan":-1}
class genSFS(threadmanager.Thread):
    def runthread(self):
        logger.logI(tn, logger.I, _("Generating compressed filesystem"))
        # Generate the SquashFS file
        # Options:
        # -b 1M                    Use a 1M blocksize (maximum)
        # -no-recovery             No recovery files
        # -always-use-fragments    Fragment blocks for files larger than the blocksize (1M)
        # -comp                    Compression type
        logger.logVV(tn, logger.I, _("Generating options"))
        opts = "-b 1M -no-recovery -no-duplicates -always-use-fragments"
        opts = opts + " -comp " + configutils.getValue(configs[configutils.sfscomp])
        opts = opts + " " + configutils.getValue(configs[configutils.sfsopts])
        sfsex = "dev etc home media mnt proc sys var run usr/lib/ubiquity/apt-setup/generators/40cdrom tmp"
        sfspath = isotreel + "casper/filesystem.squashfs"
        if os.path.exists(sfspath):
            fsutil.rm(sfspath)
        # This line would match the pattern below: [==========/              ]  70/300  20%
        patt = re.compile("^ *\[=*. *\] *[0-9]*/[0-9]* *([0-9]*)% *$")
        appnd = "32"
        if sys.maxsize > 2 ** 32:
            appnd = "64"
        # Hack to make sure all output is given
        os.environ["LD_PRELOAD"] = os.path.split(os.path.realpath(__file__))[0] + "/isatty" + appnd + ".so"
        logger.logI(tn, logger.I, _("Adding the edited /etc and /var to the filesystem"))
        logger.logI(tn, logger.I, logger.MTab + _("This might take a couple of minutes"))
        sfscmd = subprocess.Popen(shlex.split("mksquashfs " + tmpsys + " " + sfspath + " " + opts),
                                   stdout = subprocess.PIPE, universal_newlines = True)
        oldprogress = 0
        while sfscmd.poll() is None:
            output = sfscmd.stdout.readline()
            match = patt.match(output)
            if match != None:
                sys.stdout.write("\r" + match.group(0))
                sys.stdout.flush()
                progress = int(match.group(1))
                if progress > oldprogress:
                    self.setProgress(tn, int(utilities.floatDivision(progress, 2)))
                    oldprogress = progress
            else:
                logger.logI(tn, logger.I, output.rstrip(), noterm = True, nogui = True)
        sys.stdout.write("\n")
        logger.logI(tn, logger.I, _("Adding the rest of the system (this can take a while)"))
        sfscmd = subprocess.Popen(shlex.split("mksquashfs / " + sfspath + " " + opts + " -e " + sfsex),
                                   stdout = subprocess.PIPE, stderr = subprocess.PIPE,
                                   universal_newlines = True)
        oldprogress = 0
        bufferdata = ""
        while sfscmd.poll() is None:
            output, errput = sfscmd.communicate()
            output = bufferdata + output
            if errput and len(errput.rstrip()) > 0:
                # Make sure the error is seen
                logger.logE(self.tn, logger.E, errput.rstrip() + "\n")
            if "\n" in output:
                # Dang, we need to add extra stuff to bufferdata
                splitted = output.split("\n", 1)
                output = splitted[0]
                bufferdata = splitted[1]
            match = patt.match(output)
            if match != None:
                sys.stdout.write("\r" + match.group(0))
                sys.stdout.flush()
                progress = int(match.group(1))
                if progress > oldprogress:
                    self.setProgress(tn, 50 + int(utilities.floatDivision(progress, 2)))
                    oldprogress = progress
            else:
                logger.logI(tn, logger.I, output.rstrip(), noterm = True, nogui = True)
        sys.stdout.write("\n")
        os.environ["LD_PRELOAD"] = ""
        # Make sure the SquashFS file is OK
        doSFSChecks(sfspath, int(configutils.getValue(configs[configutils.isolevel])))
        # Find the size after it is uncompressed
        logger.logV(tn, logger.I, _("Writing the size"))
        files = open(isotreel + "casper/filesystem.size", "w")
        files.write(str(fsutil.getSFSInstSize(sfspath)) + "\n")
        files.close()
        # TODO: Discuss on whether to add MD5 sum or not
        # Could prevent problems, but might also prevent the user from editing
gensfs["thread"] = genSFS

threads = [gensfs]
