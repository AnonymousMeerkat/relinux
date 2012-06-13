'''
Generates a temporary filesystem to hack on
@author: lkjoel
'''

from relinux import logger, config, configutils, fsutil, pwdmanip
#import os, stat

threadname = "TempSys"
tn = logger.genTN(threadname)
tmpsys = config.TempSys


# Helper function for changing the /etc/group file
def _parseGroup(i, usrs):
    addme = True
    for x in usrs:
        # Removes all groups the "offending" user created for itself
        if i["group"] == x["user"]:
            addme = False
            return
        # Removes the user from all groups it is inside
        if x["user"] in i["users"]:
            i["users"].remove(x["user"])
    if addme == True:
        return [True, pwdmanip.PGtoEntry(i)]
    else:
        return [False, ""]


# Helper function for changing the /etc/shadow file
def _parseShadow(i, usrs):
    addme = True
    for x in usrs:
        # Removes the "offending" user
        if i["user"] == x["user"]:
            addme = False
            return
    if addme == True:
        return [True, pwdmanip.PStoEntry(i)]
    else:
        return [False, ""]


def genTempSys(excludes):
    logger.logI(tn, "Generating the tree for the temporary filesystem")
    fsutil.maketree([tmpsys + "/etc", tmpsys + "/dev",
                      tmpsys + "/proc", tmpsys + "/tmp",
                      tmpsys + "/sys", tmpsys + "/mnt",
                      tmpsys + "/media/cdrom", tmpsys + "/var", tmpsys + "/home"])
    fsutil.chmod(tmpsys + "/tmp", "1777")
    logger.logI(tn, "Copying files to the temporary filesystem")
    fsutil.fscopy("/etc", tmpsys + "/etc", excludes)
    fsutil.fscopy("/var", tmpsys + "/var", excludes)
    logger.logI(tn, "Editing files")
    # Remove these files as they can conflict inside the installed system
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
    fsutil.adrm(tmpsys + "/var/lib/apt/lists/", {"excludes": True, "remdirs": False}, ["*.gpg", "*lock*", "*partial*"])
    # Remove all files in these directories (but not directories inside them)
    for i in ["/etc/NetworkManager/system-connections/", "/var/run", "/var/log", "/var/mail", "/var/spool",
              "/var/lock", "/var/backups", "/var/tmp", "/var/crash", "/var/lib/ubiquity"]:
        fsutil.adrm(tmpsys + i, {"excludes": False, "remdirs": False}, None)
    # Create the logs
    for i in ["dpkg.log", "lastlog", "mail.log", "syslog", "auth.log", "daemon.log", "faillog",
                      "lpr.log", "mail.warn", "user.log", "boot", "debug", "mail.err", "messages", "wtmp",
                      "bootstrap.log", "dmesg", "kern.log", "mail.info"]:
        fsutil.touch(tmpsys + "/var/log/" + i)
    # Setup the password and group stuff
    passwdf = tmpsys + "/etc/passwd"
    #passwdfile = open(passwdf, "r")
    #passwdstat = fsutil.getStat(passwdf)
    #passwdbuffer = configutils.getBuffer(passwdfile)
    #passwdfile.close()
    #passwdfile = open(passwdf, "w")
    buffers = fsutil.ife_getbuffers(passwdf)
    pe = pwdmanip.parsePasswdEntries(buffers[3])
    buffers[3] = pe
    # Users to "delete" on the live system
    usrs = pwdmanip.getPPByUID("[5-9][0-9][0-9]", pe)
    usrs.extend(pwdmanip.getPPByUID("[1-9][0-9][0-9][0-9]", pe))
    usrs.extend(pwdmanip.getPPByUID("999", pe))
    fsutil.ife(buffers, lambda(line): [True, pwdmanip.PPtoEntry(line)] if not line in usrs else [False, ""])
    # Rewrite the password file
    #for i in ppe:
    #    if not i in usrs:
    #        passwdfile.write(pwdmanip.PPtoEntry(i))
    #fsutil.copystat(passwdstat, passwdf)
    #passwdfile.close()
    # Now for the group file
    groupf = tmpsys + "/etc/group"
    buffers = fsutil.ife_getbuffers(groupf)
    pe = pwdmanip.parseGroupEntries(buffers[3])
    fsutil.ife(buffers, lambda(line): _parseGroup(line, usrs))
    # Work on both shadow files
    shadowf = tmpsys + "/etc/shadow"
    gshadowf = tmpsys + "/etc/gshadow"
    buffers = fsutil.ife_getbuffers(shadowf)
    gbuffers = fsutil.ife_getbuffers(gshadowf)
    pe = pwdmanip.parseShadowEntries(buffers[3])
    buffers[3] = pe
    # If you look carefully (or just do a quick google search :P), you will notice that gshadow files
    # are very similar to group files, so we can just parse them as if they were group files
    pe = pwdmanip.parseGroupEntries(gbuffers[3])
    gbuffers[3] = pe
    fsutil.ife(buffers, lambda(line): _parseShadow(line, usrs))
    fsutil.ife(gbuffers, lambda(line): _parseGroup(line, usrs))
