'''
Generates a temporary filesystem to hack on
@author: lkjoel
'''

from relinux import logger, config, configutils, fsutil, pwdmanip
import os
import glob
import shutil
import re

threadname = "TempSys"
tn = logger.genTN(threadname)
tmpsys = config.TempSys + "/"


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


# Helper function
def _varEditor(line, lists):
    patt = re.compile("^.*? *([A-Za-z_-]*?)=.*$")
    m = patt.match(line)
    #if configutils.checkMatched(m):
    if m.group(0) != None:
        for i in lists.keys():
            if m.group(1) == i:
                lists[i] = None
                return [True, i + "=" + lists[i]]
    return [False, ""]


# Casper Variable Editor
# lists - Dictionary containing all options needed
def varEditor(file, lists):
    buffers = fsutil.ife_getbuffers(file)
    fsutil.ife(buffers, lambda(line): _varEditor(line, lists))
    # In case the file is broken, we'll add the lines needed
    buffers = open(file, "a")
    for i in lists:
        if lists[i] != None:
            buffers.write("export " + i + "=" + lists[i] + "\n")
    buffers.close()


def genTempSys(configs):
    logger.logI(tn, "Generating the tree for the temporary filesystem")
    fsutil.maketree([tmpsys + "etc", tmpsys + "dev",
                      tmpsys + "proc", tmpsys + "tmp",
                      tmpsys + "sys", tmpsys + "mnt",
                      tmpsys + "media/cdrom", tmpsys + "var", tmpsys + "home"])
    fsutil.chmod(tmpsys + "tmp", "1777")
    logger.logI(tn, "Copying files to the temporary filesystem")
    excludes = configs[configutils.excludes]
    fsutil.fscopy("etc", tmpsys + "etc", excludes)
    fsutil.fscopy("var", tmpsys + "var", excludes)
    logger.logI(tn, "Removing unneeded files")
    # Remove these files as they can conflict inside the installed system
    logger.logV(tn, "Removing personal configurations")
    fsutil.rmfiles([tmpsys + "etc/X11/xorg.conf*", tmpsys + "etc/resolv.conf",
                    tmpsys + "etc/hosts", tmpsys + "etc/hostname", tmpsys + "etc/timezone",
                    tmpsys + "etc/mtab", tmpsys + "etc/fstab",
                    tmpsys + "etc/udev/rules.d/70-persistent*",
                    tmpsys + "etc/cups/ssl/server.crt", tmpsys + "etc/cups/ssl/server.key",
                    tmpsys + "etc/ssh/ssh_host_rsa_key", tmpsys + "etc/ssh/ssh_host_dsa_key.pub",
                    tmpsys + "etc/ssh/ssh_host_dsa_key", tmpsys + "etc/ssh/ssh_host_rsa_key.pub",
                    tmpsys + "etc/group", tmpsys + "etc/passwd", tmpsys + "etc/shadow",
                    tmpsys + "etc/shadow-", tmpsys + "etc/gshadow", tmpsys + "etc/gshadow-",
                    tmpsys + "etc/wicd/wired-settings.conf", tmpsys + "etc/wicd/wireless-settings.conf",
                    tmpsys + "etc/printcap", tmpsys + "etc/cups/printers.conf"])
    logger.logV(tn, "Removing cached lists")
    fsutil.adrm(tmpsys + "var/lib/apt/lists/", {"excludes": True, "remdirs": False}, ["*.gpg", "*lock*", "*partial*"])
    logger.logV(tn, "Removing temporary files in /var")
    # Remove all files in these directories (but not directories inside them)
    for i in ["etc/NetworkManager/system-connections/", "var/run", "var/log", "var/mail", "var/spool",
              "var/lock", "var/backups", "var/tmp", "var/crash", "var/lib/ubiquity"]:
        fsutil.adrm(tmpsys + i, {"excludes": False, "remdirs": False}, None)
    # Create the logs
    logger.logV(tn, "Creating empty logs")
    for i in ["dpkg.log", "lastlog", "mail.log", "syslog", "auth.log", "daemon.log", "faillog",
                      "lpr.log", "mail.warn", "user.log", "boot", "debug", "mail.err", "messages", "wtmp",
                      "bootstrap.log", "dmesg", "kern.log", "mail.info"]:
        logger.logVV(logger.Tab + "Creating " + i)
        fsutil.touch(tmpsys + "var/log/" + i)
    # Setup the password and group stuff
    logger.logI(tn, "Removing conflicting users")
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
    logger.logV("Gathering users to remove")
    usrs = pwdmanip.getPPByUID("[5-9][0-9][0-9]", pe)
    usrs.extend(pwdmanip.getPPByUID("[1-9][0-9][0-9][0-9]", pe))
    usrs.extend(pwdmanip.getPPByUID("999", pe))
    if config.VVStatus == False:
        logger.logV("Removing them")
    logger.logVV("Removing users in /etc/passwd")
    fsutil.ife(buffers, lambda line: [True, pwdmanip.PPtoEntry(line)] if not line in usrs else [False, ""])
    # Rewrite the password file
    #for i in ppe:
    #    if not i in usrs:
    #        passwdfile.write(pwdmanip.PPtoEntry(i))
    #fsutil.copystat(passwdstat, passwdf)
    #passwdfile.close()
    # Now for the group file
    logger.logVV("Removing users in /etc/group")
    groupf = tmpsys + "etc/group"
    buffers = fsutil.ife_getbuffers(groupf)
    pe = pwdmanip.parseGroupEntries(buffers[3])
    fsutil.ife(buffers, lambda(line): _parseGroup(line, usrs))
    # Work on both shadow files
    shadowf = tmpsys + "etc/shadow"
    gshadowf = tmpsys + "etc/gshadow"
    buffers = fsutil.ife_getbuffers(shadowf)
    gbuffers = fsutil.ife_getbuffers(gshadowf)
    pe = pwdmanip.parseShadowEntries(buffers[3])
    buffers[3] = pe
    # If you look carefully (or just do a quick google search :P), you will notice that gshadow files
    # are very similar to group files, so we can just parse them as if they were group files
    pe = pwdmanip.parseGroupEntries(gbuffers[3])
    gbuffers[3] = pe
    logger.logVV("Removing users in /etc/shadow")
    fsutil.ife(buffers, lambda line: _parseShadow(line, usrs))
    logger.logVV("Removing users in /etc/gshadow")
    fsutil.ife(gbuffers, lambda line: _parseGroup(line, usrs))
    logger.logI(tn, "Applying permissions to casper scripts")
    cbs = "/usr/share/initramfs-tools/scripts/casper-bottom/"
    # This pattern should do the trick
    execme = glob.glob(os.path.join(cbs, "[0-9][0-9]*"))
    for i in execme:
        logger.logVV(tn, "chmod 755 " + i)
        fsutil.chmod(i, "755")
    # Edit the casper.conf
    # Strangely enough, casper uses its "quiet" flag if the build system is either Debian or Ubuntu
    if config.VStatus == False:
        logger.logI(tn, "Editing casper and LSB configuration files")
    logger.logV(tn, "Editing casper.conf")
    buildsys = "Ubuntu"
    if configutils.parseBoolean(configs[configutils.casperquiet]) == False:
        buildsys = ""
    varEditor(tmpsys + "etc/casper.conf", {"USERNAME": configs[configutils.username],
                                           "USERFULLNAME": configs[configutils.userfullname],
                                           "HOST": configs[configutils.host],
                                           "BUILD_SYSTEM": buildsys,
                                           "FLAVOUR": configs[configutils.flavour]})
    logger.logV(tn, "Editing lsb-release")
    varEditor(tmpsys + "etc/lsb-release", {"DISTRIB_ID": configs[configutils.sysname],
                                           "DISTRIB_RELEASE": configs[configutils.version],
                                           "DISTRIB_CODENAME": configs[configutils.codename],
                                           "DISTRIB_DESCRIPTION": configs[configutils.description]})
    # If the user-setup-apply file does not exist, and there is an alternative, we'll copy it over
    logger.logI(tn, "Setting up the installer")
    if os.path.isfile("/usr/lib/ubiquity/user-setup/user-setup-apply.orig") and not os.path.isfile("/usr/lib/ubiquity/user-setup/user-setup-apply"):
        shutil.copy2("/usr/lib/ubiquity/user-setup/user-setup-apply.orig",
                     "/usr/lib/ubiquity/user-setup/user-setup-apply")
    if configutils.parseBoolean(configs[configutils.aptlistchange]) == True:
        fsutil.makedir(tmpsys + "usr/share/ubiquity/")
        aptsetup = open(tmpsys + "usr/share/ubiquity/apt-setup", "w")
        aptsetup.write("#!/bin/sh\n")
        aptsetup.write("exit\n")
        aptsetup.close()
    else:
        fsutil.makedir(tmpsys + "usr/lib/ubiquity/apt-setup/generators/")
        cdrom = open(tmpsys + "usr/lib/ubiquity/apt-setup/generators/40cdrom", "w")
        cdrom.write("#!/bin/sh\n")
        cdrom.write("exit\n")
        cdrom.close()
