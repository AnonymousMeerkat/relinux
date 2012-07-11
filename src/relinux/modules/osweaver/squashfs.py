'''
SquashFS Generation
@author: Anonymous Meerkat
'''

from relinux import logger, fsutil, configutils
from relinux.modules.osweaver import isotreel, tmpsys, configs
import os
import threading

threadname = "SquashFS"
tn = logger.genTN(threadname)


# Display a iso9660 error
def dispiso9660(level, maxs, size):
    logger.logE(tn, logger.Error + _("Compressed filesystem is higher than the iso9660 level ") + level +
                    " spec allows (" + fsutil.sizeTrans({"B": maxs}, "M") + _("MB, size is ") +
                    fsutil.sizeTrans({"B": size}, "M") + "MB).")
    logger.logE(tn, logger.Tab + _("Please try to either reduce the amount of data you are generating, or ") +
                _("increase the ISO level"))


# Make the SquashFS checks
def doSFSChecks(file, isolvl):
    logger.logI(tn, _("Checking the compressed filesystem"))
    size = fsutil.getSize(file)
    lvl2 = fsutil.sizeTrans({"G": 4})
    lvl3 = fsutil.sizeTrans({"T": 8})
    if size > lvl2 and isolvl < 3:
        dispiso9660(isolvl, lvl2, size)
    elif size > lvl3 and isolvl >= 3:
        # 8TB OS? That's a bit much xD
        dispiso9660(isolvl, lvl3, size)


# Generate the SquashFS file (has to run after isoutil.genISOTree and tempsys.genTempSys)
gensfs = {"deps": [], "tn": threadname}
class genSFS(threading.Thread):
    def run(self):
        logger.logI(tn, _("Generating compressed filesystem"))
        # Generate the SquashFS file
        # Options:
        # -b 1M                    Use a 1M blocksize (maximum)
        # -no-recovery             No recovery files
        # -always-use-fragments    Fragment blocks for files larger than the blocksize (1M)
        # -comp                    Compression type
        logger.logVV(tn, _("Generating options"))
        opts = "-b 1M -no-recovery -no-duplicates -always-use-fragments"
        opts = opts + " -comp " + configutils.getValue(configs[configutils.sfscomp])
        opts = opts + " " + configutils.getValue(configs[configutils.sfsopts])
        sfsex = "dev etc home media mnt proc sys var usr/lib/ubiquity/apt-setup/generators/40cdrom"
        sfspath = isotreel + "casper/filesystem.squashfs"
        logger.logI(tn, _("Adding the edited /etc and /var to the filesystem"))
        os.system("mksquashfs " + tmpsys + " " + sfspath + " " + opts)
        logger.logI(tn, _("Adding the rest of the system"))
        os.system("mksquashfs / " + sfspath + " " + opts + " -e " + sfsex)
        # Make sure the SquashFS file is OK
        doSFSChecks(sfspath, int(configutils.getValue(configs[configutils.isolevel])))
        # Find the size after it is uncompressed
        logger.logV(tn, _("Writing the size"))
        file = open(isotreel + "casper/filesystem.size", "w")
        file.write(fsutil.getSFSInstSize(sfspath) + "\n")
        file.close()
        # TODO: Discuss on whether to add MD5 sum or not
        # Could prevent problems, but might also prevent the user from editing
gensfs["thread"] = genSFS

threads = [genSFS]
