# -*- coding: utf-8 -*-
'''
Generates a temporary filesystem to hack on
@author: Anonymous Meerkat <meerkatanonymous@gmail.com>
'''

from relinux import logger, config, configutils, fsutil, pwdmanip, aptutil, numrange, utilities, threadmanager
from relinux.modules.osweaver import aptcache
import os
import shutil
import re
import copy

tmpsys = config.TempSys
configs = config.Configuration["OSWeaver"]
#tmpsystree = "TempSysTree"
#cpetcvar = "EtcVar"
#remconfig = "RemConfig"
#remcachedlists = "RemCachedLists"
#remtempvar = "RemTempVar"
#genvarlogs = "GenVarLogs"
#remusers = "RemUsers"


# Generate the tree for the tempsys
tmpsystree = {"deps": [], "tn": "TempSysTree"}
class genTempSysTree(threadmanager.Thread):
    def progressfunc(self, progress):
        self.setProgress(self.tn, progress)

    def runthread(self):
        logger.logI(self.tn, logger.I, _("Generating the tree for the temporary filesystem"))
        # Clean the TMPSYS tree, if it exists
        fsutil.rm(tmpsys)
        self.progressfunc(20)
        # Generate the tree
        fsutil.maketree([tmpsys + "etc", tmpsys + "dev",
                          tmpsys + "proc", [tmpsys + "tmp", 0o1777],
                          tmpsys + "sys", tmpsys + "mnt",
                          tmpsys + "media/cdrom", tmpsys + "var", tmpsys + "home",
                          tmpsys + "run"], self.tn, lambda p: self.progressfunc(20 + p / (5 / 3)))
        fsutil.chmod(tmpsys + "tmp", 0o1777, self.tn)
tmpsystree["thread"] = genTempSysTree


# Copy the contents of /etc/ and /var/ to the tempsys
cpetcvar = {"deps": [tmpsystree], "tn": "EtcVar", "threadspan":-1}
class copyEtcVar(threadmanager.Thread):
    def progressfunc(self, progress):
        self.setProgress(self.tn, progress)

    def runthread(self):
        logger.logI(self.tn, logger.I, _("Copying files to the temporary filesystem"))
        excludes = configutils.getValue(configs[configutils.excludes])
        varexcludes = excludes
        # Exclude all log files (*.log *.log.*), PID files (to show that no daemons are running),
        # backup and old files (for obvious reasons), and any .deb files that a person might have downloaded
        varexcludes.extend(["*.log", "*.log.*", "*.pid", "*/pid", "*.bak", "*.[0-9].gz", "*.deb"])
        fsutil.fscopy("/etc", tmpsys + "etc", excludes, self.tn,
                      progressfunc = lambda p: self.progressfunc(p / 2))
        fsutil.fscopy("/var", tmpsys + "var", varexcludes, self.tn,
                      progressfunc = lambda p: self.progressfunc(50 + p / 2))
        #logger.logV(self.tn, logger.I, _("Moving some directories to /run"))
        #fsutil.fscopy(tmpsys + "var/run/", tmpsys + "run/")
        #fsutil.rm(tmpsys + "var/run/")
        #fsutil.fscopy(tmpsys + "var/lock/", tmpsys + "run/lock/")
        #fsutil.rm(tmpsys + "var/lock/")
        #fsutil.symlink(tmpsys + "run/", tmpsys + "var/run/")
        #fsutil.symlink(tmpsys + "run/lock/", tmpsys + "var/lock/")
cpetcvar["thread"] = copyEtcVar


# Remove configuration files that can break the installed/live system
remconfig = {"deps": [cpetcvar], "tn": "RemConfig"}
class remConfig(threadmanager.Thread):
    def progressfunc(self, p):
        self.setProgress(self.tn, p)

    def runthread(self):
        # Remove these files as they can conflict inside the installed system
        logger.logV(self.tn, logger.I, _("Removing personal configurations that can break the installed system"))
        fsutil.rmfiles([tmpsys + "etc/X11/xorg.conf*", tmpsys + "etc/resolv.conf",
                        tmpsys + "etc/hosts", tmpsys + "etc/hostname", tmpsys + "etc/timezone",
                        tmpsys + "etc/mtab", tmpsys + "etc/fstab",
                        tmpsys + "etc/udev/rules.d/70-persistent*",
                        tmpsys + "etc/cups/ssl/server.crt", tmpsys + "etc/cups/ssl/server.key",
                        tmpsys + "etc/ssh/ssh_host_rsa_key", tmpsys + "etc/ssh/ssh_host_dsa_key.pub",
                        tmpsys + "etc/ssh/ssh_host_dsa_key", tmpsys + "etc/ssh/ssh_host_rsa_key.pub",
#                        tmpsys + "etc/group", tmpsys + "etc/passwd", tmpsys + "etc/shadow",
#                        tmpsys + "etc/shadow-", tmpsys + "etc/gshadow", tmpsys + "etc/gshadow-",
                        tmpsys + "etc/wicd/wired-settings.conf",
                        tmpsys + "etc/wicd/wireless-settings.conf", tmpsys + "etc/printcap",
                        tmpsys + "etc/cups/printers.conf"], self.tn, self.progressfunc)
remconfig["thread"] = remConfig


# Remove cached lists
remcachedlists = {"deps": [cpetcvar], "tn": "RemCachedLists"}
class remCachedLists(threadmanager.Thread):
    def progressfunc(self, p):
        self.setProgress(self.tn, p)

    def runthread(self):
        logger.logV(self.tn, logger.I, _("Removing cached lists"))
        fsutil.adrm(tmpsys + "var/lib/apt/lists/", excludes = ["*.gpg", "*lock*", "*partial*"],
                    remdirs = False, remsymlink = True, remfullpath = False, remoriginal = False,
                    tn = self.tn, progressfunc = self.progressfunc)
remcachedlists["thread"] = remCachedLists


# Remove temporary files in /var
remtempvar = {"deps": [cpetcvar], "tn": "RemTempVar"}
class remTempVar(threadmanager.Thread):
    def progressfunc(self, p):
        self.setProgress(self.tn, p)

    def runthread(self):
        logger.logV(self.tn, logger.I, _("Removing temporary files in /var"))
        # Remove all files in these directories (but not directories inside them)
        a = ["etc/NetworkManager/system-connections/", "var/run", "var/log", "var/mail",
                  "var/spool", "var/lock", "var/backups", "var/tmp", "var/crash", "var/lib/ubiquity"]
        la = len(a)
        inc = 100 / la
        rinc = inc / 100
        for i in range(la):
            fsutil.adrm(tmpsys + a[i], excludes = [], remdirs = False, remsymlink = False,
                        remfullpath = False, remoriginal = False, tn = self.tn,
                        progressfunc = lambda p: self.progressfunc(inc * i + p * rinc))
remtempvar["thread"] = remTempVar


# Generate logs in /var/log
genvarlogs = {"deps": [cpetcvar], "tn": "GenVarLogs"}
class genVarLogs(threadmanager.Thread):
    def runthread(self):
        # Create the logs
        logger.logV(self.tn, logger.I, _("Creating empty logs"))
        a = ["dpkg.log", "lastlog", "mail.log", "syslog", "auth.log", "daemon.log", "faillog",
                          "lpr.log", "mail.warn", "user.log", "boot", "debug", "mail.err", "messages", "wtmp",
                          "bootstrap.log", "dmesg", "kern.log", "mail.info"]
        la = len(a)
        inc = 100 / la
        for i in range(la):
            logger.logVV(self.tn, logger.I, logger.MTab + _("Creating") + " " + a[i])
            fsutil.touch(tmpsys + "var/log/" + a[i])
            self.setProgress(self.tn, (i + 1) * inc)
genvarlogs["thread"] = genVarLogs


# Edit passwd and shadow files to remove users
remusers = {"deps": [cpetcvar], "tn": "RemUsers"}
class remUsers(threadmanager.Thread):
    # Helper function for changing the /etc/group file
    def _parseGroup(self, i, usrs):
        addme = True
        for x in usrs:
            # Removes all groups the "offending" user created for itself
            if i["group"] == x["user"]:
                addme = False
                break
            # Removes the user from all groups it is inside
            if x["user"] in i["users"]:
                i["users"].remove(x["user"])
        if addme:
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
                break
        if addme:
            return [True, pwdmanip.PStoEntry(i)]
        else:
            return [False, ""]

    def runthread(self):
        # Setup the password and group stuff
        logger.logI(self.tn, logger.I, _("Removing conflicting users"))
        passwdf = tmpsys + "etc/passwd"
        #passwdfile = open(passwdf, "r")
        #passwdstat = fsutil.getStat(passwdf)
        #passwdbuffer = configutils.getBuffer(passwdfile)
        #passwdfile.close()
        #passwdfile = open(passwdf, "w")
        buffers = fsutil.ife_getbuffers(passwdf)
        pe = pwdmanip.parsePasswdEntries(buffers[3])
        buffers[3] = pe
        # Users to "delete" on the live system
        logger.logV(self.tn, logger.I, _("Gathering users to remove"))
        nobody = ""
        for x in pe:
            if x["user"] == "nobody":
                nobody = x
        max_uid = 1999
        sysrange = 500
        if not isinstance(nobody, dict):
            logger.logV(self.tn, logger.E, _("User 'nobody' could not be found!"))
        else:
            nuid = int(nobody["uid"])
            if nuid <= 100:
                # nobody has been assigned to the conventional system UID range
                max_uid = 1999
                sysrange = 100
            elif nuid < 500:
                # nobody has been assigned to the RHEL system UID range
                max_uid = 1999
                sysrange = 500
            elif nuid >= 65530 and nuid <= 65535:
                # nobody has been assigned to the highest possible unsigned short integer (16 bit) range
                max_uid = nuid - 1
                sysrange = 555
            elif nuid >= 32766:
                # nobody has been assigned to the highest possible signed short integer (16 bit) range
                max_uid = nuid - 1
                sysrange = 500
            else:
                max_uid = 1999
                sysrange = 555
        usrs = pwdmanip.getPPByUID(numrange.gen_num_range(sysrange, max_uid), pe)
        if config.VVStatus is False:
            logger.logV(self.tn, logger.I, _("Removing them"))
        logger.logVV(self.tn, logger.I, _("Removing users in /etc/passwd"))
        fsutil.ife(buffers, lambda line: [True, pwdmanip.PPtoEntry(line)] if not line in usrs else [False, ""])
        # Rewrite the password file
        #for i in ppe:
        #    if not i in usrs:
        #        passwdfile.write(pwdmanip.PPtoEntry(i))
        #fsutil.copystat(passwdstat, passwdf)
        #passwdfile.close()
        # Now for the group file
        logger.logVV(self.tn, logger.I, _("Removing users in /etc/group"))
        groupf = tmpsys + "etc/group"
        buffers = fsutil.ife_getbuffers(groupf)
        pe = pwdmanip.parseGroupEntries(buffers[3])
        buffers[3] = pe
        fsutil.ife(buffers, lambda line: self._parseGroup(line, usrs))
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
        logger.logVV(self.tn, logger.I, _("Removing users in /etc/shadow"))
        fsutil.ife(buffers, lambda line: self._parseShadow(line, usrs))
        logger.logVV(self.tn, logger.I, _("Removing users in /etc/gshadow"))
        fsutil.ife(gbuffers, lambda line: self._parseGroup(line, usrs))
        logger.logV(self.tn, logger.I, _("Creating backups"))
        shutil.copy2(tmpsys + "etc/passwd", tmpsys + "etc/passwd-")
        shutil.copy2(tmpsys + "etc/group", tmpsys + "etc/group-")
        shutil.copy2(tmpsys + "etc/shadow", tmpsys + "etc/shadow-")
        shutil.copy2(tmpsys + "etc/gshadow", tmpsys + "etc/gshadow-")
remusers["thread"] = remUsers


# Edits casper.conf
casperconf = {"deps": [cpetcvar], "tn": "casper.conf"}
class CasperConfEditor(threadmanager.Thread):
    # Helper function
    def _varEditor(self, line, lists):
        patt = re.compile("^.*? *([A-Za-z_-]*?)=.*$")
        m = patt.match(line)
        if utilities.checkMatched(m):
            for i in lists.keys():
                if m.group(1) == i:
                    bak = copy.copy(lists[i])
                    lists[i] = None
                    return [True, "export " + i + "=\"" + bak + "\"\n"]
        patt = re.compile("^ *#.*$")
        m = patt.match(line)
        if utilities.checkMatched(m):
            return [True, line]
        patt = re.compile("^ *$")
        m = patt.match(line)
        if utilities.checkMatched(m):
            return [True, line]
        return [False, ""]

    # Casper Variable Editor
    # lists - Dictionary containing all options needed
    def varEditor(self, files, lists):
        buffers = fsutil.ife_getbuffers(files)
        fsutil.ife(buffers, lambda line: self._varEditor(line, lists))
        # In case the file is broken, we'll add the lines needed
        buffers = open(files, "a")
        for i in lists:
            if lists[i] is not None:
                buffers.write("export " + i + "=\"" + lists[i] + "\"\n")
        buffers.close()

    def runthread(self):
        # Edit the casper.conf
        # Strangely enough, casper uses the "quiet" flag if the build system is either Debian or Ubuntu
        if config.VStatus is False:
            logger.logI(self.tn, logger.I, _("Editing casper and LSB configuration files"))
        logger.logV(self.tn, logger.I, _("Editing casper.conf"))
        buildsys = "Ubuntu"
        if configutils.getValue(configs[configutils.casperquiet]) is False:
            buildsys = ""
        unionfs = configutils.getValue(configs[configutils.unionfs])
        if unionfs == "overlayfs" and aptutil.compVersions(aptutil.getPkgVersion(aptutil.getPkg("casper", aptcache)), "1.272", aptutil.lt):
            logger.logI(self.tn, logger.W, _("Using DEFAULT instead of overlayfs"))
            unionfs = "DEFAULT"
        self.varEditor(tmpsys + "etc/casper.conf", {
                                            "USERNAME": configutils.getValue(configs[configutils.username]),
                                            "USERFULLNAME":
                                                configutils.getValue(configs[configutils.userfullname]),
                                            "HOST": configutils.getValue(configs[configutils.host]),
                                            "BUILD_SYSTEM": buildsys,
                                            "FLAVOUR": configutils.getValue(configs[configutils.flavour]),
                                            "UNIONFS": unionfs})
        logger.logI(self.tn, logger.I, _("Applying permissions to casper scripts"))
        # Make sure the casper scripts work
        cbs = "/usr/share/initramfs-tools/scripts/casper-bottom/"
        for i in fsutil.listdir(cbs):
            fsutil.chmod(i, 0o755, self.tn)
        logger.logV(self.tn, logger.I, _("Editing lsb-release"))
        self.varEditor(tmpsys + "etc/lsb-release", {
                                    "DISTRIB_ID": configutils.getValue(configs[configutils.sysname]),
                                    "DISTRIB_RELEASE": configutils.getValue(configs[configutils.sysversion]),
                                    "DISTRIB_CODENAME": configutils.getValue(configs[configutils.codename]),
                                    "DISTRIB_DESCRIPTION":
        configutils.getValue(configs[configutils.description])})
casperconf["thread"] = CasperConfEditor


# Sets up Ubiquity
ubiquitysetup = {"deps": [cpetcvar], "tn": "Ubiquity"}
class UbiquitySetup(threadmanager.Thread):
    def runthread(self):
        # If the user-setup-apply file does not exist, and there is an alternative, we'll copy it over
        logger.logI(self.tn, logger.I, _("Setting up the installer"))
        if (os.path.isfile("/usr/lib/ubiquity/user-setup/user-setup-apply.orig") and not
            os.path.isfile("/usr/lib/ubiquity/user-setup/user-setup-apply")):
            shutil.copy2("/usr/lib/ubiquity/user-setup/user-setup-apply.orig",
                         "/usr/lib/ubiquity/user-setup/user-setup-apply")
        if (True or
            configutils.getValue(configs[configutils.aptlistchange])):
            if not os.path.exists("/usr/share/ubiquity/apt-setup.relinux-backup"):
                os.rename("/usr/share/ubiquity/apt-setup",
                          "/usr/share/ubiquity/apt-setup.relinux-backup")
            aptsetup = open("/usr/share/ubiquity/apt-setup", "w")
            aptsetup.write("#!/bin/sh\n")
            aptsetup.write("exit\n")
            aptsetup.close()
ubiquitysetup["thread"] = UbiquitySetup


# Thread list
threads = [tmpsystree, cpetcvar, remconfig, remcachedlists, remtempvar, genvarlogs, remusers,
           casperconf, ubiquitysetup]
