'''
Generates a temporary filesystem to hack on
@author: lkjoel
'''

from relinux import logger, config, fsutil
import os, stat

threadname = "TempSys"
tn = logger.genTN(threadname)
tmpsys = config.TempSys

def genTempSys(excludes):
    logger.logI(tn, "Generating the tree for the temporary filesystem")
    fsutil.maketree([tmpsys + "/etc", tmpsys + "/dev",
                      tmpsys + "/proc", tmpsys + "/tmp",
                      tmpsys + "/sys", tmpsys + "/mnt",
                      tmpsys + "/media/cdrom", tmpsys + "/var"])
    fsutil.chmod(tmpsys + "/tmp", "1777")
    logger.logI(tn, "Copying files to the temporary filesystem")
    fsutil.fscopy("/etc", tmpsys + "/etc", excludes)
    fsutil.fscopy("/var", tmpsys + "/var", excludes)
    logger.logI(tn, "Editing files")
    fsutil.rmfiles([tmpsys + "/etc/X11/xorg.conf*", tmpsys + "/etc/resolv.conf",
                    tmpsys + "/etc/hosts", tmpsys + "/etc/hostname", tmpsys + "/etc/timezone",
                    tmpsys + "/etc/mtab", tmpsys + "/etc/fstab",
                    tmpsys + "/etc/udev/rules.d/70-persistent*",
                    tmpsys + "/etc/cups/ssl/server.crt", tmpsys + "/etc/cups/ssl/server.key",
                    tmpsys + "/etc/ssh/ssh_host_rsa_key", tmpsys + "/etc/ssh/ssh_host_dsa_key.pub",
                    tmpsys + "/etc/ssh/ssh_host_dsa_key", tmpsys + "/etc/ssh/ssh_host_rsa_key.pub",
                    tmpsys + "/etc/group", tmpsys + "/etc/passwd", tmpsys + "/etc/shadow",
                    tmpsys + "/etc/shadow-", tmpsys + "/etc/gshadow", tmpsys + "/etc/gshadow-",
                    tmpsys + "/etc/wicd/wired-settings.conf", tmpsys + "/etc/wicd/wireless-settings.conf",
                    tmpsys + "/etc/printcap", tmpsys + "/etc/cups/printers.conf"])
    