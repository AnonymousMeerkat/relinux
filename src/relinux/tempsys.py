'''
Generates a temporary filesystem to hack on
@author: lkjoel
'''

from relinux import logger, config, configutils, fsutil, pwdmanip
#import os, stat

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
    fsutil.adrm(tmpsys + "/var/lib/apt/lists/", {"excludes":True,"remdirs":False}, ["*.gpg", "*lock*", "*partial*"])
    # Remove all files in these directories (but not directories inside them)
    for i in ["/etc/NetworkManager/system-connections/", "/var/run", "/var/log", "/var/mail", "/var/spool",
              "/var/lock", "/var/backups", "/var/tmp", "/var/crash", "/var/lib/ubiquity"]:
        fsutil.adrm(tmpsys + i, {"excludes":False,"remdirs":False}, None)
    # Create the logs
    for i in ["dpkg.log", "lastlog", "mail.log", "syslog", "auth.log", "daemon.log", "faillog",
                      "lpr.log", "mail.warn", "user.log", "boot", "debug", "mail.err", "messages", "wtmp",
                      "bootstrap.log", "dmesg", "kern.log", "mail.info"]:
        fsutil.touch(tmpsys + "/var/log/" + i)
    # Setup the password and group stuff
    passwdf = tmpsys + "/etc/passwd"
    passwdfile = open(passwdf, "r")
    passwdstat = fsutil.getStat(passwdf)
    passwdbuffer = configutils.getBuffer(passwdfile)
    passwdfile.close()
    passwdfile = open(passwdf, "w")
    ppe = pwdmanip.parsePasswdEntries(passwdbuffer)
    # Users to "delete" on the live system
    usrs = pwdmanip.getPPByUID("[5-9][0-9][0-9]", ppe)
    usrs.extend(pwdmanip.getPPByUID("[1-9][0-9][0-9][0-9]", ppe))
    usrs.extend(pwdmanip.getPPByUID("999", ppe))
    # Rewrite the password file
    for i in ppe:
        if not i in usrs:
            passwdfile.write(pwdmanip.PPtoEntry(i))
    fsutil.copystat(passwdstat, passwdf)
    passwdfile.close()
    # Now for the group file
    groupf = tmpsys + "/etc/group"
    groupfile = open(groupf, "r")
    groupstat = fsutil.getStat(groupf)
    groupbuffer = configutils.getBuffer(groupf)
    groupfile.close()
    groupfile = open(groupf, "w")
    pge = pwdmanip.parseGroupEntries(groupbuffer)
    for i in pge:
        addme = True
        for x in usrs:
            if i["group"] == x["user"]:
                addme = False
                return
            if x["user"] in i["users"]:
                i["users"].remove(x["user"])
        if addme == True:
            groupfile.write(pwdmanip.PGtoEntry(i))
    fsutil.copystat(groupstat, groupf)
    groupfile.close()
    
