'''
Generates a temporary filesystem to hack on
@author: lkjoel
'''

from relinux import logger, config, configutils, fsutil, pwdmanip
import os
import glob
import shutil
import re
import threading


class TempSys(threading.Thread):
    def __init__(self):
        self.threadname = "TempSys"
        self.tn = logger.genTN(self.threadname)
        self.tmpsys = config.TempSys + "/"

    # Helper function for changing the /etc/group file
    def _parseGroup(self, i, usrs):
        addme = True
        for x in usrs:
            # Removes all groups the "offending" user created for itself
            if i["group"] == x["user"]:
                addme = False
                return
            # Removes the user from all groups it is inside
            if x["user"] in i["users"]:
                i["users"].remove(x["user"])
        if addme is True:
            return [True, pwdmanip.PGtoEntry(i)]
        else:
            return [False, ""]

    # Helper function for changing the /etc/shadow file
    def _parseShadow(self, i, usrs):
        addme = True
        for x in usrs:
            # Removes the "offending" user
            if i["user"] == x["user"]:
                addme = False
                return
        if addme is True:
            return [True, pwdmanip.PStoEntry(i)]
        else:
            return [False, ""]

    # Helper function
    def __varEditor(self, line, lists):
        patt = re.compile("^.*? *([A-Za-z_-]*?)=.*$")
        m = patt.match(line)
        #if configutils.checkMatched(m):
        if m.group(0) is not None:
            for i in lists.keys():
                if m.group(1) == i:
                    lists[i] = None
                    return [True, i + "=" + lists[i]]
        return [False, ""]

    # Casper Variable Editor
    # lists - Dictionary containing all options needed
    def _varEditor(self, file, lists):
        buffers = fsutil.ife_getbuffers(file)
        fsutil.ife(buffers, lambda(line): self.__varEditor(line, lists))
        # In case the file is broken, we'll add the lines needed
        buffers = open(file, "a")
        for i in lists:
            if lists[i] is not None:
                buffers.write("export " + i + "=" + lists[i] + "\n")
        buffers.close()

    def run(self, configs):
        logger.logI(self.tn, "Generating the tree for the temporary filesystem")
        fsutil.maketree([self.tmpsys + "etc", self.tmpsys + "dev",
                          self.tmpsys + "proc", self.tmpsys + "tmp",
                          self.tmpsys + "sys", self.tmpsys + "mnt",
                          self.tmpsys + "media/cdrom", self.tmpsys + "var", self.tmpsys + "home"])
        fsutil.chmod(self.tmpsys + "tmp", "1777")
        logger.logI(self.tn, "Copying files to the temporary filesystem")
        excludes = configs[configutils.excludes]
        fsutil.fscopy("etc", self.tmpsys + "etc", excludes)
        fsutil.fscopy("var", self.tmpsys + "var", excludes)
        logger.logI(self.tn, "Removing unneeded files")
        # Remove these files as they can conflict inside the installed system
        logger.logV(self.tn, "Removing personal configurations")
        fsutil.rmfiles([self.tmpsys + "etc/X11/xorg.conf*", self.tmpsys + "etc/resolv.conf",
                        self.tmpsys + "etc/hosts", self.tmpsys + "etc/hostname", self.tmpsys + "etc/timezone",
                        self.tmpsys + "etc/mtab", self.tmpsys + "etc/fstab",
                        self.tmpsys + "etc/udev/rules.d/70-persistent*",
                        self.tmpsys + "etc/cups/ssl/server.crt", self.tmpsys + "etc/cups/ssl/server.key",
                        self.tmpsys + "etc/ssh/ssh_host_rsa_key", self.tmpsys + "etc/ssh/ssh_host_dsa_key.pub",
                        self.tmpsys + "etc/ssh/ssh_host_dsa_key", self.tmpsys + "etc/ssh/ssh_host_rsa_key.pub",
                        self.tmpsys + "etc/group", self.tmpsys + "etc/passwd", self.tmpsys + "etc/shadow",
                        self.tmpsys + "etc/shadow-", self.tmpsys + "etc/gshadow", self.tmpsys + "etc/gshadow-",
                        self.tmpsys + "etc/wicd/wired-settings.conf", self.tmpsys + "etc/wicd/wireless-settings.conf",
                        self.tmpsys + "etc/printcap", self.tmpsys + "etc/cups/printers.conf"])
        logger.logV(self.tn, "Removing cached lists")
        fsutil.adrm(self.tmpsys + "var/lib/apt/lists/", {"excludes": True, "remdirs": False}, ["*.gpg", "*lock*", "*partial*"])
        logger.logV(self.tn, "Removing temporary files in /var")
        # Remove all files in these directories (but not directories inside them)
        for i in ["etc/NetworkManager/system-connections/", "var/run", "var/log", "var/mail", "var/spool",
                  "var/lock", "var/backups", "var/tmp", "var/crash", "var/lib/ubiquity"]:
            fsutil.adrm(self.tmpsys + i, {"excludes": False, "remdirs": False}, None)
        # Create the logs
        logger.logV(self.tn, "Creating empty logs")
        for i in ["dpkg.log", "lastlog", "mail.log", "syslog", "auth.log", "daemon.log", "faillog",
                          "lpr.log", "mail.warn", "user.log", "boot", "debug", "mail.err", "messages", "wtmp",
                          "bootstrap.log", "dmesg", "kern.log", "mail.info"]:
            logger.logVV(logger.Tab + "Creating " + i)
            fsutil.touch(self.tmpsys + "var/log/" + i)
        # Setup the password and group stuff
        logger.logI(self.tn, "Removing conflicting users")
        passwdf = self.tmpsys + "/etc/passwd"
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
        if config.VVStatus is False:
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
        groupf = self.tmpsys + "etc/group"
        buffers = fsutil.ife_getbuffers(groupf)
        pe = pwdmanip.parseGroupEntries(buffers[3])
        fsutil.ife(buffers, lambda(line): self._parseGroup(line, usrs))
        # Work on both shadow files
        shadowf = self.tmpsys + "etc/shadow"
        gshadowf = self.tmpsys + "etc/gshadow"
        buffers = fsutil.ife_getbuffers(shadowf)
        gbuffers = fsutil.ife_getbuffers(gshadowf)
        pe = pwdmanip.parseShadowEntries(buffers[3])
        buffers[3] = pe
        # If you look carefully (or just do a quick google search :P), you will notice that gshadow files
        # are very similar to group files, so we can just parse them as if they were group files
        pe = pwdmanip.parseGroupEntries(gbuffers[3])
        gbuffers[3] = pe
        logger.logVV("Removing users in /etc/shadow")
        fsutil.ife(buffers, lambda line: self._parseShadow(line, usrs))
        logger.logVV("Removing users in /etc/gshadow")
        fsutil.ife(gbuffers, lambda line: self._parseGroup(line, usrs))
        logger.logI(self.tn, "Applying permissions to casper scripts")
        cbs = "/usr/share/initramfs-tools/scripts/casper-bottom/"
        # This pattern should do the trick
        execme = glob.glob(os.path.join(cbs, "[0-9][0-9]*"))
        for i in execme:
            logger.logVV(self.tn, "chmod 755 " + i)
            fsutil.chmod(i, "755")
        # Edit the casper.conf
        # Strangely enough, casper uses its "quiet" flag if the build system is either Debian or Ubuntu
        if config.VStatus is False:
            logger.logI(self.tn, "Editing casper and LSB configuration files")
        logger.logV(self.tn, "Editing casper.conf")
        buildsys = "Ubuntu"
        if configutils.parseBoolean(configs[configutils.casperquiet]) is False:
            buildsys = ""
        self.varEditor(self.tmpsys + "etc/casper.conf", {"USERNAME": configs[configutils.username],
                                               "USERFULLNAME": configs[configutils.userfullname],
                                               "HOST": configs[configutils.host],
                                               "BUILD_SYSTEM": buildsys,
                                               "FLAVOUR": configs[configutils.flavour]})
        logger.logV(self.tn, "Editing lsb-release")
        self.varEditor(self.tmpsys + "etc/lsb-release", {"DISTRIB_ID": configs[configutils.sysname],
                                               "DISTRIB_RELEASE": configs[configutils.version],
                                               "DISTRIB_CODENAME": configs[configutils.codename],
                                               "DISTRIB_DESCRIPTION": configs[configutils.description]})
        # If the user-setup-apply file does not exist, and there is an alternative, we'll copy it over
        logger.logI(self.tn, "Setting up the installer")
        if os.path.isfile("/usr/lib/ubiquity/user-setup/user-setup-apply.orig") and not os.path.isfile("/usr/lib/ubiquity/user-setup/user-setup-apply"):
            shutil.copy2("/usr/lib/ubiquity/user-setup/user-setup-apply.orig",
                         "/usr/lib/ubiquity/user-setup/user-setup-apply")
        if configutils.parseBoolean(configs[configutils.aptlistchange]) is True:
            fsutil.makedir(self.tmpsys + "usr/share/ubiquity/")
            aptsetup = open(self.tmpsys + "usr/share/ubiquity/apt-setup", "w")
            aptsetup.write("#!/bin/sh\n")
            aptsetup.write("exit\n")
            aptsetup.close()
        else:
            fsutil.makedir(self.tmpsys + "usr/lib/ubiquity/apt-setup/generators/")
            cdrom = open(self.tmpsys + "usr/lib/ubiquity/apt-setup/generators/40cdrom", "w")
            cdrom.write("#!/bin/sh\n")
            cdrom.write("exit\n")
            cdrom.close()
